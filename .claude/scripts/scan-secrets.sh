#!/usr/bin/env bash
# scan-secrets.sh - block-on-finding secret scanner for staged or named files
# usage: scan-secrets.sh <path> [path ...]
#        scan-secrets.sh --staged
# exit codes: 0 clean, 1 finding, 2 invocation error
set -euo pipefail

ALLOWLIST="$(dirname "$0")/scan-secrets.allowlist"

if [ "$#" -eq 0 ]; then
  echo "usage: scan-secrets.sh <path> [path ...]  |  --staged" >&2
  exit 2
fi

if [ "$1" = "--staged" ]; then
  paths=()
  while IFS= read -r line; do
    paths+=("$line")
  done < <(git diff --name-only --cached)
else
  paths=("$@")
fi

if [ "${#paths[@]}" -eq 0 ]; then exit 0; fi

# Build the disjunction. Order matters: most specific first.
# Covers: AWS, GitHub, Slack, Anthropic, OpenAI, Supabase, Vercel,
# private keys, absolute personal paths, and generic password/secret pairs.
patterns=(
  'AKIA[0-9A-Z]{16}'
  'gh[ps]_[A-Za-z0-9]{36,}'
  'xox[baprs]-[A-Za-z0-9-]{10,}'
  'sk-ant-[A-Za-z0-9_-]{32,}'
  'sk-[A-Za-z0-9]{32,}'
  'sbp_[A-Za-z0-9]{40,}'
  'service_role'
  'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}'
  '-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----'
  '/Users/[a-z][a-z0-9._-]+/'
  '(password|passwd|secret|api[_-]?key|service[_-]?role)[[:space:]]*[:=][[:space:]]*['"'"'"][^'"'"'"]{4,}['"'"'"]'
)
joined="$(IFS='|'; echo "${patterns[*]}")"

found=0
for p in "${paths[@]}"; do
  [ -f "$p" ] || continue
  # Skip the allowlist itself and binary blobs
  case "$p" in
    *scan-secrets.allowlist) continue ;;
    *.png|*.jpg|*.jpeg|*.gif|*.svg|*.ico|*.pdf|*.zip|*.tar|*.gz|*.lock|*.jar) continue ;;
    *.pptx|*.docx|*.xlsx|*.key|*.numbers|*.pages) continue ;;
    *.mp4|*.mov|*.avi|*.mp3|*.wav|*.flac|*.webm) continue ;;
    *.psd|*.ai|*.cdr|*.sketch|*.fig) continue ;;
    *.woff|*.woff2|*.ttf|*.eot|*.otf) continue ;;
    # .env.example is intentionally committed with placeholder values
    *.env.example) continue ;;
  esac
  if matches="$(grep -nEH "$joined" "$p" 2>/dev/null || true)"; then
    [ -z "$matches" ] && continue
    while IFS= read -r line; do
      if [ -f "$ALLOWLIST" ] && grep -Fxq "$line" "$ALLOWLIST" 2>/dev/null; then
        continue
      fi
      echo "[secret] $line"
      found=1
    done <<< "$matches"
  fi
done

exit "$found"
