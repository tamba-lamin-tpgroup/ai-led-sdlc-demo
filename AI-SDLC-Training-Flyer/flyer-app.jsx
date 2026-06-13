/* global React, ReactDOM, DesignCanvas, DCSection, DCArtboard */
const { useState } = React;

/* ----------------------------- tool marks ----------------------------- */
function Sparkle({ s = 26, c = "var(--coral)" }) {
  return (
    <svg width={s} height={s} viewBox="0 0 24 24" fill={c} aria-hidden="true">
      <path d="M12 1.2 L13.9 9.6 L22.8 12 L13.9 14.4 L12 22.8 L10.1 14.4 L1.2 12 L10.1 9.6 Z" />
      <path d="M19 2.5 L19.8 5.4 L22.7 6.2 L19.8 7 L19 9.9 L18.2 7 L15.3 6.2 L18.2 5.4 Z" opacity="0.7" />
    </svg>
  );
}
function GitBranch({ s = 26, c = "var(--navy)" }) {
  return (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="6" y1="3" x2="6" y2="15" /><circle cx="18" cy="6" r="3" /><circle cx="6" cy="18" r="3" /><path d="M18 9a9 9 0 0 1-9 9" />
    </svg>
  );
}
function Triangle({ s = 26, c = "var(--navy)" }) {
  return (
    <svg width={s} height={s} viewBox="0 0 24 24" fill={c} aria-hidden="true"><path d="M12 3.5 L22 20.5 L2 20.5 Z" /></svg>
  );
}
function Globe({ s = 28, c = "#fff" }) {
  return (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="9.2" /><path d="M2.8 12h18.4" /><path d="M12 2.8a14.5 14.5 0 0 1 0 18.4 14.5 14.5 0 0 1 0-18.4" />
    </svg>
  );
}
function Check({ s = 20 }) {
  return (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="11" fill="rgba(130,195,65,.16)" />
      <path d="M7 12.4 L10.4 15.8 L17 8.8" stroke="var(--green-deep)" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function Arrow({ s = 22 }) {
  return (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M4 12h15" /><path d="M13 6l6 6-6 6" />
    </svg>
  );
}

function LinkedIn({ s = 16, c = "var(--azure-deep)" }) {
  return (
    <svg width={s} height={s} viewBox="0 0 24 24" fill={c} aria-hidden="true">
      <path d="M20.45 20.45h-3.56v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.63-1.85 3.36-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.23 0H1.77C.8 0 0 .77 0 1.73v20.54C0 23.23.8 24 1.77 24h20.46c.98 0 1.77-.77 1.77-1.73V1.73C24 .77 23.2 0 22.23 0z" />
    </svg>
  );
}

/* ----------------------------- brand arcs bg ----------------------------- */
function Arcs() {
  return (
    <svg className="fl-arcs" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <defs>
        <linearGradient id="ag1" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#1C9FD8" /><stop offset="1" stopColor="#82C341" />
        </linearGradient>
      </defs>
      <g fill="none" stroke="url(#ag1)" strokeWidth="2.5" opacity="0.10">
        <ellipse cx="860" cy="120" rx="360" ry="150" transform="rotate(-28 860 120)" />
        <ellipse cx="900" cy="160" rx="250" ry="105" transform="rotate(-28 900 160)" />
        <ellipse cx="120" cy="900" rx="320" ry="135" transform="rotate(-24 120 900)" />
      </g>
      <circle cx="978" cy="58" r="6" fill="#82C341" opacity="0.5" />
      <circle cx="40" cy="788" r="6" fill="#1C9FD8" opacity="0.45" />
    </svg>
  );
}

/* ----------------------------- shared bits ----------------------------- */
function Brand({ logo = 44, name = 16, sub = 10.5 }) {
  return (
    <div className="fl-brand">
      <img src="assets/slint-logo.png" width={logo} height={logo} alt="SLINT logo" />
      <div className="fl-brand-tx" style={{ gap: name * 0.18 }}>
        <b style={{ fontSize: name }}>SLINT</b>
        <span style={{ fontSize: sub }}>Sierra Leoneans in Technology</span>
      </div>
    </div>
  );
}

function LivePill({ fs = 12.5, py = 9, px = 16 }) {
  return (
    <span className="fl-pill" style={{ fontSize: fs, padding: `${py}px ${px}px` }}>
      <span className="fl-dot" /> Live&nbsp;·&nbsp;Virtual
    </span>
  );
}

function Pipeline({ scale = 1 }) {
  const box = 56 * scale, mark = 30 * scale;
  const node = (markEl, lab, name, final) => (
    <div className={"fl-node" + (final ? " final" : "")} style={{ gap: 9 * scale }}>
      <div className="nmark" style={{ width: box, height: box, borderRadius: 15 * scale }}>{markEl}</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 3 * scale, alignItems: "center" }}>
        <span className="nname" style={{ fontSize: 16.5 * scale }}>{name}</span>
        <span className="nlab" style={{ fontSize: 10 * scale }}>{lab}</span>
      </div>
    </div>
  );
  const arr = <div className="fl-arrow"><Arrow s={22 * scale} /></div>;
  return (
    <div className="fl-pipe" style={{ padding: `${24 * scale}px ${18 * scale}px`, borderRadius: 18 * scale }}>
      {node(<Sparkle s={mark} />, "AI Coding", "Claude Code")}
      {arr}
      {node(<GitBranch s={mark} />, "Version", "GitHub")}
      {arr}
      {node(<Triangle s={mark} />, "Deploy", "Vercel")}
      {arr}
      {node(<Globe s={mark + 2} />, "Production", "Live App", true)}
    </div>
  );
}

function Chips({ fs = 14.5, scale = 1 }) {
  const items = [
    ["Agentic AI vs. Chatbots", "var(--azure)"],
    ["AI-Led SDLC", "var(--green)"],
    ["Prompt → Production", "var(--azure-deep)"],
    ["Real-Time Deploy", "var(--coral)"],
  ];
  return (
    <div className="fl-chips" style={{ gap: 10 * scale }}>
      {items.map(([t, c]) => (
        <span className="fl-chip" key={t} style={{ fontSize: fs, padding: `${9 * scale}px ${15 * scale}px`, borderRadius: 999 }}>
          <i style={{ background: c }} />{t}
        </span>
      ))}
    </div>
  );
}

function Host({ ph = 88, scale = 1 }) {
  return (
    <div className="fl-host" style={{ gap: 20 * scale }}>
      <img className="ph" src="assets/host-portrait.jpg" width={ph} height={ph} alt="Tamba Sheku Lamin" style={{ width: ph, height: ph }} />
      <div className="meta" style={{ gap: 5 * scale, maxWidth: 820 }}>
        <span className="role" style={{ fontSize: 11 * scale }}>Hosted by</span>
        <span className="nm" style={{ fontSize: 23 * scale }}>Tamba Sheku Lamin</span>
        <span className="ti" style={{ fontSize: 13.5 * scale }}>Former President, SLINT</span>
        <span className="cred" style={{ fontSize: 12.5 * scale, marginTop: 2 * scale }}>
          Co-Founder &amp; Group CEO, TpGROUP (SL) Ltd · Senior Technology Architect / FDE @ Accenture Song
        </span>
        <a className="lnk" href="https://www.linkedin.com/in/tambalamin/" style={{ fontSize: 12.5 * scale, marginTop: 13 * scale }}>
          <LinkedIn s={15 * scale} /> linkedin.com/in/tambalamin
        </a>
      </div>
    </div>
  );
}

function When({ scale = 1 }) {
  const cell = (k, v) => (
    <div className="cell" style={{ gap: 5 * scale, padding: `0 ${16 * scale}px` }}>
      <span className="k" style={{ fontSize: 10.5 * scale }}>{k}</span>
      <span className="v" style={{ fontSize: 18 * scale }}>{v}</span>
    </div>
  );
  return (
    <div className="fl-when">
      <div style={{ paddingLeft: 0 }}>{cell("Date", "Sat · Jun 13")}</div>
      <div className="div" /> {cell("Time", "2:00 PM EST")}
      <div className="div" /> {cell("Length", "45–90 min")}
    </div>
  );
}

function Cta({ scale = 1, stacked, hidePrice }) {
  return (
    <div style={{ display: "flex", flexDirection: stacked ? "column" : "row", alignItems: stacked ? "flex-start" : "center", gap: 14 * scale }}>
      <span className="fl-cta" style={{ fontSize: 18 * scale, padding: `${15 * scale}px ${26 * scale}px`, borderRadius: 14 * scale }}>
        Register — It’s Free <span className="arr"><Arrow s={20 * scale} /></span>
      </span>
      {!hidePrice && (
        <span className="fl-price" style={{ fontSize: 13.5 * scale }}>
          <b>Free</b> for SLINT members · <b style={{ color: "var(--navy)" }}>$10</b> non-members
        </span>
      )}
    </div>
  );
}

/* ----------------------------- VERTICAL layout ----------------------------- */
function Vertical({ tall }) {
  const pad = tall ? 74 : 68;
  return (
    <div className="fl">
      <Arcs />
      <div className="fl-pad" style={{ padding: pad, gap: tall ? 0 : 0 }}>
        <div className="fl-head"><Brand logo={46} name={17} sub={11} /><LivePill /></div>

        <div style={{ marginTop: tall ? 40 : 30 }}>
          <div className="fl-eyebrow" style={{ fontSize: 13.5, letterSpacing: ".2em" }}>SLINT · Agentic AI Workshop</div>
          <h1 className="fl-title" style={{ fontSize: tall ? 66 : 60, marginTop: 20 }}>
            Build &amp; Deploy a <span className="hl">Live</span> AI-Powered Web App
          </h1>
          <p className="fl-sub" style={{ fontSize: tall ? 22 : 20.5, marginTop: 18 }}>
            A hands-on, live-coding session on Agentic AI and the AI-led software development lifecycle — watch a real app go from idea to the open web.
          </p>
        </div>

        {tall && <div className="grow" />}

        <div style={{ marginTop: tall ? 44 : 30 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
            <span className="fl-seclab" style={{ fontSize: 11.5 }}>The Workflow · Prompt → Production</span>
            <span className="fl-livechip" style={{ fontSize: 11.5, padding: "6px 12px" }}>● Built live on stage</span>
          </div>
          <Pipeline scale={1} />
          <p className="fl-sub" style={{ fontSize: 15.5, marginTop: 14, color: "var(--navy-2)", fontWeight: 600 }}>
            We’ll build <b style={{ color: "var(--azure-deep)" }}>Salone Explorer</b> — a real Sierra Leone tour-guide app — and ship it to production during the session.
          </p>
        </div>

        {tall && (
          <div style={{ marginTop: 38 }}>
            <span className="fl-seclab" style={{ fontSize: 11.5 }}>In This Session</span>
            <div className="fl-list" style={{ gap: "16px 34px", marginTop: 16 }}>
              {[
                "Agentic AI vs. AI chatbots, in practice",
                "The AI-led SDLC, end to end",
                "Live coding inside a real IDE",
                "Claude Code, GitHub & Vercel workflow",
              ].map((t) => (
                <div className="fl-li" key={t} style={{ fontSize: 16 }}><Check s={22} /><span>{t}</span></div>
              ))}
            </div>
          </div>
        )}

        {!tall && <div className="grow" />}

        <div style={{ marginTop: tall ? 30 : 22, paddingTop: tall ? 28 : 20, borderTop: "1.5px solid var(--line-soft)" }}>
          <Host ph={tall ? 100 : 90} />
        </div>

        <div style={{ marginTop: tall ? 26 : 20, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 20 }}>
          <When />
          <Cta hidePrice />
        </div>

        <div style={{ marginTop: 14 }}>
          <div style={{ fontFamily: "'JetBrains Mono',ui-monospace,monospace", fontWeight: 700, fontSize: 14, color: "var(--azure-deep)" }}>Register → bit.ly/slint-ai-workshop</div>
          <div style={{ marginTop: 7, fontSize: 13, color: "var(--muted)", fontWeight: 600 }}>
            <b style={{ color: "var(--green-deep)" }}>Free</b> for SLINT members · <b style={{ color: "var(--navy)" }}>$10</b> non-members · Zoom link emailed after verification.
          </div>
        </div>

        <div className="fl-foot" style={{ marginTop: 18, paddingTop: 16, fontSize: 12.5 }}>
          <span>Co-organized by <b style={{ color: "var(--navy)" }}>Cecil John</b> &amp; the SLINT Executive</span>
          <span className="site">slint.org</span>
        </div>
      </div>
    </div>
  );
}

/* ----------------------------- WIDE layout ----------------------------- */
function Wide() {
  return (
    <div className="fl wide">
      <div className="fl-pad">
        <div className="fl-wcontent" style={{ padding: 52 }}>
          <Arcs />
          <div style={{ position: "relative", zIndex: 2, display: "flex", flexDirection: "column", height: "100%" }}>
            <div className="fl-head"><Brand logo={40} name={15} sub={9.5} /><LivePill fs={11} py={7} px={13} /></div>

            <div style={{ marginTop: 24 }}>
              <div className="fl-eyebrow" style={{ fontSize: 12, letterSpacing: ".2em" }}>SLINT · Agentic AI Workshop</div>
              <h1 className="fl-title" style={{ fontSize: 43, marginTop: 13 }}>
                Build &amp; Deploy a <span className="hl">Live</span><br />AI-Powered Web App
              </h1>
              <p className="fl-sub" style={{ fontSize: 16, marginTop: 12, maxWidth: "30ch" }}>
                Hands-on live coding with Agentic AI — from prompt to production, end to end.
              </p>
            </div>

            <div style={{ marginTop: 20 }}><Pipeline scale={0.74} /></div>

            <div className="grow" />

            <div style={{ marginTop: 18, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16 }}>
              <When scale={0.92} />
              <Cta scale={0.86} hidePrice />
            </div>
            <div style={{ marginTop: 14 }}>
              <div style={{ fontFamily: "'JetBrains Mono',ui-monospace,monospace", fontWeight: 700, fontSize: 12.5, color: "var(--azure-deep)" }}>Register → bit.ly/slint-ai-workshop</div>
              <div style={{ marginTop: 6, fontSize: 12, color: "var(--muted)", fontWeight: 600 }}>
                <b style={{ color: "var(--green-deep)" }}>Free</b> for members · <b style={{ color: "var(--navy)" }}>$10</b> non-members · Zoom link emailed after verification.
              </div>
            </div>
            <div className="fl-foot" style={{ marginTop: 16, paddingTop: 12, fontSize: 11 }}>
              <span>Co-organized by <b style={{ color: "var(--navy)" }}>Cecil John</b> &amp; the SLINT Executive</span>
              <span className="site">slint.org</span>
            </div>
          </div>
        </div>

        <div className="fl-wphoto">
          <img src="assets/host-portrait.jpg" alt="Tamba Sheku Lamin" />
          <div className="scrim" />
          <div className="toppill" style={{ padding: 18 }}></div>
          <div className="plate" style={{ padding: 24 }}>
            <span className="role" style={{ fontSize: 10.5 }}>Hosted by</span>
            <div className="nm" style={{ fontSize: 24, marginTop: 6 }}>Tamba Sheku Lamin</div>
            <div className="ti" style={{ fontSize: 13, marginTop: 4 }}>Former President, SLINT</div>
            <div className="cred" style={{ fontSize: 11.5, marginTop: 7 }}>Co-Founder &amp; Group CEO, TpGROUP (SL) Ltd · Sr. Technology Architect / FDE @ Accenture Song</div>
            <a className="lnk" href="https://www.linkedin.com/in/tambalamin/" style={{ fontSize: 11.5, marginTop: 13 }}><LinkedIn s={14} c="#8fd3f4" /> linkedin.com/in/tambalamin</a>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ----------------------------- single-frame export mode ----------------------------- */
function Frame({ kind }) {
  const dims = { square: [1080, 1080], portrait: [1080, 1350], landscape: [1200, 675] }[kind];
  const inner = kind === "landscape" ? <Wide /> : <Vertical tall={kind === "portrait"} />;
  const exp = window.__EXPORT__;
  const fit = () => {
    const el = document.getElementById("frame");
    if (!el) return;
    const s = Math.min(window.innerWidth / dims[0], window.innerHeight / dims[1]);
    el.style.transform = `translate(-50%,-50%) scale(${s})`;
  };
  React.useEffect(() => { if (exp) return; fit(); window.addEventListener("resize", fit); return () => window.removeEventListener("resize", fit); });
  if (exp) {
    return (
      <div style={{ position: "fixed", inset: 0, background: "#fff", overflow: "hidden" }}>
        <div id={"shot-" + kind} style={{ position: "absolute", top: 0, left: 0, width: dims[0], height: dims[1] }}>
          {inner}
        </div>
      </div>
    );
  }
  return (
    <div style={{ position: "fixed", inset: 0, background: "#0d1620", overflow: "hidden" }}>
      <div id="frame" style={{ position: "absolute", top: "50%", left: "50%", transformOrigin: "center center", width: dims[0], height: dims[1], boxShadow: "0 30px 90px rgba(0,0,0,.5)" }}>
        {inner}
      </div>
    </div>
  );
}

/* ----------------------------- canvas ----------------------------- */
function App() {
  const h = window.__FRAME__ || (window.location.hash || "").replace("#", "");
  if (["square", "portrait", "landscape"].includes(h)) return <Frame kind={h} />;
  return (
    <DesignCanvas>
      <DCSection id="social" title="SLINT Agentic AI Workshop — Social Flyers" subtitle="Same design, three posting-ready sizes">
        <DCArtboard id="square" label="Square · 1080×1080 — Instagram / Facebook / LinkedIn" width={1080} height={1080}>
          <Vertical />
        </DCArtboard>
        <DCArtboard id="portrait" label="Portrait · 1080×1350 — Instagram feed (max reach)" width={1080} height={1350}>
          <Vertical tall />
        </DCArtboard>
        <DCArtboard id="landscape" label="Landscape · 1200×675 — X / Twitter / LinkedIn link" width={1200} height={675}>
          <Wide />
        </DCArtboard>
      </DCSection>
    </DesignCanvas>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
