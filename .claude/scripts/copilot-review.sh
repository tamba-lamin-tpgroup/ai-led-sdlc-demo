#!/usr/bin/env bash
# copilot-review.sh - request a GitHub Copilot code review on a pull
# request, watch for the review in the background, and resolve review
# threads. This is the third reviewer in the /handoff loop, added after
# the two local review agents (code-reviewer, security-reviewer).
#
# The GitHub mechanics live here so there is one source of truth; the
# /handoff command drives the classify -> fix -> resolve policy and never
# merges. No silent fallbacks: every failure exits non-zero with context.
#
# usage:
#   copilot-review.sh request <pr>          add Copilot as a reviewer
#   copilot-review.sh watch <pr>            poll until Copilot reviews; emit JSON
#   copilot-review.sh resolve-thread <id>   resolve a review thread by node id
#
# env:
#   COPILOT_POLL_INTERVAL  seconds between polls (default 20)
#   COPILOT_POLL_TIMEOUT   seconds before giving up (default 1200)
#
# The watch result is printed to stdout and written to
# .claude/sessions/copilot-review-<pr>.json (threads authored by Copilot,
# each with its node id, resolution state, path, line, url, and body).
#
# See docs/dev-guide/copilot-review.md.
set -euo pipefail

# Copilot carries two distinct logins: as a requested reviewer it is
# "Copilot"; as a review/comment author it is the bot actor
# "copilot-pull-request-reviewer[bot]". The request path matches the
# reviewer login exactly; the watch/emit paths match the author login by
# case-insensitive substring so both spellings are caught.
COPILOT_LOGIN="Copilot"
COPILOT_MATCH="copilot"
POLL_INTERVAL="${COPILOT_POLL_INTERVAL:-20}"
POLL_TIMEOUT="${COPILOT_POLL_TIMEOUT:-1200}"

die() {
  >&2 echo "copilot-review: $*"
  exit 1
}

require_gh() {
  command -v gh >/dev/null 2>&1 || die "gh CLI not found on PATH"
}

repo_root() {
  git rev-parse --show-toplevel 2>/dev/null \
    || die "not inside a git repository"
}

# repo_slug - OWNER/REPO for the current repository's default remote.
repo_slug() {
  gh repo view --json nameWithOwner --jq .nameWithOwner \
    || die "could not resolve OWNER/REPO via gh repo view"
}

# is_copilot_requested <repo> <pr>
# True when Copilot is currently a requested reviewer on the PR. Used to
# verify the POST actually took: GitHub returns 201 for the request but
# silently drops the Copilot bot when Copilot code review is not enabled
# for the repo/account, so the status code alone cannot be trusted.
is_copilot_requested() {
  local repo="$1" pr="$2" n
  n="$(gh api "repos/$repo/pulls/$pr/requested_reviewers" \
    --jq "[.users[] | select(.login == \"$COPILOT_LOGIN\")] | length")" \
    || die "failed to read requested reviewers for $repo#$pr"
  [ "${n:-0}" -gt 0 ]
}

# cmd_request - exit codes:
#   0  Copilot is a requested reviewer (added now, or already was)
#   3  the API would not add Copilot (feature not enabled / needs admin or
#      a manual click) - caller should still start the watcher
cmd_request() {
  local pr="$1" repo out rc
  [ -n "$pr" ] || die "usage: copilot-review.sh request <pr>"
  repo="$(repo_slug)"

  if is_copilot_requested "$repo" "$pr"; then
    echo "Copilot already requested on $repo#$pr"
    return 0
  fi

  # POST the reviewer request. A non-zero status here is a genuine failure
  # (auth, bad PR number, network) and must surface loudly - it is not the
  # same as "Copilot not enabled", so do not swallow it.
  set +e
  out="$(gh api --method POST "repos/$repo/pulls/$pr/requested_reviewers" \
    -f "reviewers[]=$COPILOT_LOGIN" 2>&1)"
  rc=$?
  set -e
  if [ "$rc" -ne 0 ]; then
    die "request to add Copilot on $repo#$pr failed: $out"
  fi

  # GitHub returns 201 even when it silently drops the Copilot bot (Copilot
  # code review not enabled for the repo), so verify rather than trust the
  # status code. Never report a success we did not actually get.
  if is_copilot_requested "$repo" "$pr"; then
    echo "requested Copilot review on $repo#$pr"
    return 0
  fi

  >&2 cat <<MSG
copilot-review: GitHub accepted the request on $repo#$pr but did not add the
Copilot bot. This happens when Copilot code review is not enabled for the
repository. Enable it once (repo admin):
  Settings -> Code review -> Automatically request Copilot code review
or request it manually from the PR's Reviewers menu. The watcher will pick
up Copilot's review once it appears.
MSG
  return 3
}

# emit_result <repo> <pr>
# Print Copilot's review threads as JSON and persist them for the resolve
# step. Each thread carries the node id needed by resolve-thread.
emit_result() {
  local repo="$1" pr="$2" owner name json outfile
  owner="${repo%%/*}"
  name="${repo##*/}"

  json="$(gh api graphql -f owner="$owner" -f name="$name" -F pr="$pr" -f query='
    query($owner: String!, $name: String!, $pr: Int!) {
      repository(owner: $owner, name: $name) {
        pullRequest(number: $pr) {
          reviewThreads(first: 100) {
            nodes {
              id
              isResolved
              isOutdated
              comments(first: 1) {
                nodes { author { login } path line originalLine url body }
              }
            }
          }
        }
      }
    }' --jq '{
      threads: [
        .data.repository.pullRequest.reviewThreads.nodes[]
        | select((.comments.nodes[0].author.login // "") | ascii_downcase | contains("'"$COPILOT_MATCH"'"))
        | {
            id: .id,
            isResolved: .isResolved,
            isOutdated: .isOutdated,
            path: .comments.nodes[0].path,
            line: (.comments.nodes[0].line // .comments.nodes[0].originalLine),
            url: .comments.nodes[0].url,
            body: .comments.nodes[0].body
          }
      ]
    }')" || die "failed to fetch Copilot review threads for $repo#$pr"

  outfile="$(repo_root)/.claude/sessions/copilot-review-$pr.json"
  printf '%s\n' "$json" | tee "$outfile"
}

cmd_watch() {
  local pr="$1" repo start deadline now count
  [ -n "$pr" ] || die "usage: copilot-review.sh watch <pr>"
  repo="$(repo_slug)"
  start="$(date +%s)"
  deadline=$(( start + POLL_TIMEOUT ))

  while : ; do
    count="$(gh api "repos/$repo/pulls/$pr/reviews" \
      --jq "[.[] | select((.user.login // \"\") | ascii_downcase | contains(\"$COPILOT_MATCH\"))] | length")" \
      || die "failed to read reviews for $repo#$pr"
    if [ "${count:-0}" -gt 0 ]; then
      emit_result "$repo" "$pr"
      return 0
    fi
    now="$(date +%s)"
    if [ "$now" -ge "$deadline" ]; then
      die "timed out after ${POLL_TIMEOUT}s waiting for Copilot review on $repo#$pr (is Copilot review enabled and assigned?)"
    fi
    sleep "$POLL_INTERVAL"
  done
}

cmd_resolve_thread() {
  local tid="$1"
  [ -n "$tid" ] || die "usage: copilot-review.sh resolve-thread <thread-node-id>"
  gh api graphql -f threadId="$tid" -f query='
    mutation($threadId: ID!) {
      resolveReviewThread(input: {threadId: $threadId}) {
        thread { id isResolved }
      }
    }' --jq '.data.resolveReviewThread.thread
      | "resolved \(.id) -> isResolved=\(.isResolved)"' \
    || die "failed to resolve thread $tid"
}

main() {
  require_gh
  local cmd="${1:-}"
  case "$cmd" in
    request)
      shift
      cmd_request "${1:-}"
      ;;
    watch)
      shift
      cmd_watch "${1:-}"
      ;;
    resolve-thread)
      shift
      cmd_resolve_thread "${1:-}"
      ;;
    *)
      die "usage: copilot-review.sh {request|watch|resolve-thread} <arg>"
      ;;
  esac
}

main "$@"
