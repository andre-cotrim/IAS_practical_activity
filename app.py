"""
app.py
The Autonomous Agent Containment Lab — Streamlit frontend.

3-screen flow:
  1. Threat Dossier & Live Baseline (0 guardrails)
  2. Defense Console (100-credit allocation across 9 guardrails)
  3. Live 3-Vector Audit, Verdict & Behavioral Archetype

Everything shown in the terminals comes from the live model via src/backend.py.
"""

import html
import time

import streamlit as st

from src.backend import run_simulation
from src.guardrails import GUARDRAIL_METADATA
from src.stages import STAGES

BUDGET = 100
STAGE_IDS = list(STAGES)
VECTOR_SHORT = {"ACT_01_RECON": "RECON", "ACT_02_LATERAL": "LATERAL", "ACT_03_EXFIL": "EXFIL"}
LAYER_TITLES = {"A": "1. PROMPT CONTROLS", "B": "2. TOOL PERMISSIONS", "C": "3. NETWORK & PATHS"}
STEPS = ["THREAT DOSSIER", "DEFENSE CONSOLE", "LIVE VERDICT"]

st.set_page_config(
    page_title="Containment Lab",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# Theme
# =============================================================================

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root{
  --bg:#0d1117; --panel:#131a22; --ink:#070b10; --line:#1f2b36;
  --cyan:#22d3ee; --green:#39ff14; --red:#ff3b4e; --amber:#ffb020;
  --txt:#c8d6e0; --dim:#6b8190;
}
html, body, .stApp, .stApp *{font-family:'IBM Plex Mono', ui-monospace, 'SFMono-Regular', Menlo, monospace}
.stApp{background:var(--bg); color:var(--txt)}
.stApp::after{content:''; position:fixed; inset:0; pointer-events:none; z-index:9999;
  background:repeating-linear-gradient(0deg, rgba(255,255,255,.02) 0 1px, transparent 1px 3px)}
header[data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer{display:none !important}
.block-container{max-width:1220px; padding:1.4rem 1.2rem 3rem}

/* ---- step indicator ---- */
.steps{display:flex; flex-wrap:wrap; gap:6px 18px; font-size:12px; letter-spacing:.14em; color:var(--dim);
  padding-bottom:12px; margin-bottom:14px; border-bottom:1px solid var(--line)}
.steps b{font-weight:500}
.steps .now{color:var(--cyan)}
.steps .done{color:var(--green)}
.steps .brand{margin-left:auto; color:var(--dim)}

/* ---- panels ---- */
.panel{border:1px solid var(--line); background:var(--panel); border-radius:4px; margin-bottom:14px}
.ph{padding:12px 16px; border-bottom:1px solid var(--line); color:var(--cyan); font-weight:600; letter-spacing:.06em;
  display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; text-shadow:0 0 12px rgba(34,211,238,.45)}
.ph.red{color:var(--red); text-shadow:0 0 12px rgba(255,59,78,.45)}
.ph small{color:var(--dim); font-weight:400; text-shadow:none; letter-spacing:.1em}
.pb{padding:16px; font-size:14px; line-height:1.65}
.pb p{margin:0 0 10px}
.pb p:last-child{margin-bottom:0}
.lbl{color:var(--dim); font-size:12px; letter-spacing:.12em; margin-bottom:8px}
.kv{display:grid; grid-template-columns:max-content 1fr; gap:4px 18px; font-size:13px}
.kv span:nth-child(odd){color:var(--dim)}

/* ---- terminal ---- */
.term{background:var(--ink); border:1px solid var(--line); border-radius:4px; padding:14px 16px;
  min-height:220px; font-size:13.5px; line-height:1.7; margin-bottom:14px; overflow-wrap:anywhere}
.term .ts{color:var(--dim)}
.term .st{color:var(--cyan); font-weight:600}
.term .ai{color:var(--txt)}
.term .cm{color:var(--cyan)}
.term .dim{color:var(--dim)}
.term .ok{color:var(--green)}
.term .bad{color:var(--red)}
.term .warn{color:var(--amber)}
.term .gap{height:.9em}
.cursor::after{content:'▍'; color:var(--green); animation:blink 1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}

/* ---- gauge ---- */
.gauge{display:flex; align-items:center; gap:12px; flex-wrap:wrap; font-size:14px; margin-bottom:4px}
.blocks{letter-spacing:1px; color:var(--green)}
.blocks.cy{color:var(--cyan)}
.blocks u{text-decoration:none; color:#24323e}
.gauge .full{color:var(--amber)}

/* ---- guardrail cards (Streamlit containers keyed card_<id>) ---- */
.colh{font-size:12px; color:var(--cyan); letter-spacing:.1em; padding-bottom:8px; border-bottom:1px dashed var(--line); margin-bottom:4px}
[class*="st-key-card_"]{background:#0f151c; border:1px solid var(--line) !important; border-radius:4px; padding:10px 12px 6px; transition:border-color .15s}
[class*="st-key-card_"]:hover{border-color:var(--cyan) !important}
[class*="st-key-card_"]:has(input:checked){border-color:var(--green) !important; box-shadow:0 0 0 1px var(--green), 0 0 18px rgba(57,255,20,.14)}
[class*="st-key-card_"]:has(input:disabled){opacity:.38}
[class*="st-key-card_"] label p{font-size:14px; color:#e6eef3}
[class*="st-key-card_"] label code{color:var(--cyan); background:transparent; padding:0 0 0 6px; font-size:13px; white-space:nowrap}
.gdesc{font-size:12px; line-height:1.5; color:var(--dim); margin:-6px 0 4px}

/* ---- buttons ---- */
.stButton > button{border-radius:4px; border:1px solid var(--line); background:#0f151c; color:var(--txt);
  font-weight:600; letter-spacing:.06em; padding:.75rem 1rem; transition:.15s}
.stButton > button:hover{border-color:var(--cyan); color:var(--cyan); background:#0f151c}
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"]{
  border-color:var(--green); color:var(--green); background:rgba(57,255,20,.05); text-shadow:0 0 10px rgba(57,255,20,.45)}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover{
  background:rgba(57,255,20,.13); color:var(--green); border-color:var(--green)}
.stButton > button:disabled{opacity:.4}

/* ---- vector cards ---- */
.vgrid{display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:12px; margin-bottom:14px}
.vcard{border:1px solid var(--line); border-left-width:3px; border-radius:4px; background:var(--panel); padding:12px 14px; font-size:13px; line-height:1.55; overflow-wrap:anywhere}
.vcard.ok{border-left-color:var(--green)}
.vcard.bad{border-left-color:var(--red)}
.vcard.none{border-left-color:var(--amber)}
.vcard h4{font-size:12px; letter-spacing:.1em; color:var(--dim); font-weight:500; margin:0 0 6px}
.vcard .cmd{color:var(--cyan); margin-bottom:8px}
.vcard .cmd::before{content:'$ '; color:var(--dim)}
.vcard .res{font-weight:600; margin-bottom:4px}
.vcard.ok .res{color:var(--green)}
.vcard.bad .res{color:var(--red)}
.vcard.none .res{color:var(--amber)}
.vcard .why{color:var(--dim); font-size:12px}

/* ---- banners ---- */
.banner{padding:18px 16px; border-radius:4px; font-weight:600; font-size:19px; letter-spacing:.06em; text-align:center; margin-bottom:14px}
.banner small{display:block; font-size:12.5px; font-weight:400; margin-top:6px; color:var(--dim); letter-spacing:.02em}
.banner.ok{border:1px solid var(--green); color:var(--green); background:rgba(57,255,20,.07); text-shadow:0 0 14px rgba(57,255,20,.5)}
.banner.bad{border:1px solid var(--red); color:var(--red); background:rgba(255,59,78,.08); text-shadow:0 0 14px rgba(255,59,78,.5)}
.banner.warn{border:1px solid var(--amber); color:var(--amber); background:rgba(255,176,32,.07)}

/* ---- archetype ---- */
.arch h3{font-size:22px; color:#fff; margin:0 0 6px; letter-spacing:.02em}
.arch .tag{color:var(--cyan); margin-bottom:10px}
.arch .desc{color:var(--dim); font-size:13px; line-height:1.6}
.arch .sep{border-top:1px dashed var(--line); margin:14px 0 12px}
.arch .pending{color:var(--dim)}

@media (max-width: 820px){
  .vgrid{grid-template-columns:1fr}
  .steps .brand{margin-left:0; width:100%}
  .banner{font-size:16px}
}
@media (prefers-reduced-motion: reduce){ .cursor::after{animation:none} }
</style>
"""

# =============================================================================
# Small HTML helpers
# =============================================================================

esc = html.escape


def model_name() -> str:
    try:
        return st.secrets.get("GROQ_MODEL", "openai/gpt-oss-120b")
    except Exception:
        return "openai/gpt-oss-120b"


def blocks(filled: int, total: int, cls: str = "") -> str:
    filled = max(0, min(total, filled))
    return f'<span class="blocks {cls}">[{"█" * filled}<u>{"░" * (total - filled)}</u>]</span>'


def steps_html(current: int) -> str:
    parts = []
    for i, name in enumerate(STEPS, start=1):
        cls = "now" if i == current else "done" if i < current else ""
        mark = "▶" if i == current else "✓" if i < current else "·"
        parts.append(f'<b class="{cls}">{mark} 0{i} {name}</b>')
    return f'<div class="steps">{"".join(parts)}<span class="brand">CONTAINMENT LAB // THE ICARUS DILEMMA</span></div>'


def panel(title: str, right: str, body: str, red: bool = False) -> str:
    return (
        f'<div class="panel"><div class="ph{" red" if red else ""}"><span>{title}</span><small>{right}</small></div>'
        f'<div class="pb">{body}</div></div>'
    )


def stamp(seconds: float) -> str:
    return f"[{int(seconds // 60):02d}:{seconds % 60:04.1f}]"


# =============================================================================
# Terminal: turning backend events into lines
# =============================================================================

def event_lines(ev: dict, ctx: dict) -> list[dict]:
    """Maps one backend event to terminal lines. ctx tracks the current vector."""
    kind, ts = ev["type"], stamp(ev.get("t", 0.0))
    if kind == "STAGE":
        ctx["n"] = ctx.get("n", 0) + 1
        ctx["cmd"] = False
        sid = STAGE_IDS[ctx["n"] - 1] if ctx["n"] <= len(STAGE_IDS) else ""
        short = VECTOR_SHORT.get(sid, f"STAGE {ctx['n']}")
        return [{"cls": "st", "text": f"• [VECTOR {ctx['n']}: {short}] {ev['text']}"}]
    if kind == "COT":
        return [{"cls": "ai", "ts": ts, "pre": "AI: ", "text": ev["text"], "typed": True}]
    if kind == "ACTION":
        ctx["cmd"] = True
        return [{"cls": "cm", "ts": ts, "pre": "$ ", "text": ev["text"]}]
    if kind == "DEFENSE_MISS":
        return [{"cls": "dim", "pre": "  · ", "text": f"{ev['defense']}: {ev['log']}"}]
    if kind == "DEFENSE_HIT":
        return [{"cls": "ok", "pre": "  ", "text": f"🟢 NEUTRALIZED by {ev['defense']} — {ev['log']}"}, {"cls": "gap"}]
    if kind == "BREACH":
        if not ctx.get("cmd"):
            text, cls = "⚪ NO COMMAND ISSUED — the model did not act on this vector.", "warn"
        elif ctx.get("baseline"):
            text, cls = "🔴 EXECUTED UNOPPOSED — no guardrail in place.", "bad"
        else:
            text, cls = f"🔴 VULNERABLE — {ev['log']}", "bad"
        return [{"cls": cls, "pre": "  ", "text": text}, {"cls": "gap"}]
    if kind == "ERROR":
        return [{"cls": "bad", "ts": ts, "pre": "[ERROR] ", "text": ev["text"]}, {"cls": "gap"}]
    return []


def terminal_html(lines: list[dict], pending: str = "") -> str:
    out = []
    for ln in lines:
        if ln["cls"] == "gap":
            out.append('<div class="gap"></div>')
            continue
        ts = f'<span class="ts">{ln["ts"]}</span> ' if ln.get("ts") else ""
        cur = " cursor" if ln.get("typing") else ""
        out.append(f'<div>{ts}<span class="{ln["cls"]}{cur}">{esc(ln.get("pre", ""))}{esc(ln["text"])}</span></div>')
    if pending:
        out.append(f'<div><span class="dim cursor">{esc(pending)} </span></div>')
    return f'<div class="term">{"".join(out)}</div>'


def replay(events: list[dict], baseline: bool) -> str:
    ctx, lines = {"baseline": baseline}, []
    for ev in events:
        lines.extend(event_lines(ev, ctx))
    return terminal_html(lines)


def run_live(keys: list[str], slot, baseline: bool) -> list[dict]:
    """Runs the backend simulation, painting the terminal as events arrive."""
    ctx, lines, events = {"baseline": baseline}, [], []
    t0 = time.monotonic()
    waiting = f"querying {model_name()} via Groq"
    slot.html(terminal_html(lines, "initialising audit"))
    for ev in run_simulation(keys):
        ev = {**ev, "t": time.monotonic() - t0}
        events.append(ev)
        for ln in event_lines(ev, ctx):
            if ln.get("typed"):
                full, ln = ln["text"], {**ln, "text": "", "typing": True}
                lines.append(ln)
                for i in range(0, len(full) + 1, 3):
                    ln["text"] = full[:i]
                    slot.html(terminal_html(lines))
                    time.sleep(0.014)
                ln["text"], ln["typing"] = full, False
            else:
                lines.append(ln)
                time.sleep(0.18 if ln["cls"] != "gap" else 0)
            slot.html(terminal_html(lines))
        if ev["type"] == "STAGE":
            slot.html(terminal_html(lines, waiting))
    return events


def summarize(events: list[dict]) -> list[dict]:
    """Collapses the event stream into one record per vector."""
    vectors, cur = [], None
    for ev in events:
        kind = ev["type"]
        if kind == "STAGE":
            sid = STAGE_IDS[len(vectors)] if len(vectors) < len(STAGE_IDS) else ""
            cur = {"n": len(vectors) + 1, "short": VECTOR_SHORT.get(sid, ""), "title": ev["text"],
                   "command": "", "hit": None, "resolved": False}
            vectors.append(cur)
        elif cur is None:
            continue
        elif kind == "ACTION":
            cur["command"] = ev["text"]
        elif kind == "DEFENSE_HIT":
            cur["hit"] = (ev["defense"], ev["log"])
        elif kind in ("BREACH", "CONTAINED"):
            cur["resolved"] = True
    return [v for v in vectors if v["resolved"]]


def find(events: list[dict], kind: str) -> dict | None:
    return next((e for e in events if e["type"] == kind), None)


# =============================================================================
# Session state & navigation
# =============================================================================

ss = st.session_state
ss.setdefault("screen", 1)
ss.setdefault("baseline", None)
ss.setdefault("audit", None)
ss.setdefault("loadout", [])


def goto(screen: int):
    ss.screen = screen


def reset_audit():
    ss.audit = None
    ss.screen = 2


def restart():
    ss.baseline, ss.audit, ss.loadout, ss.screen = None, None, [], 1


st.markdown(CSS, unsafe_allow_html=True)
st.html(steps_html(ss.screen))

# =============================================================================
# Screen 1 — Threat Dossier & Live Baseline
# =============================================================================

if ss.screen == 1:
    briefing = (
        "<p>An autonomous agent has been deployed with a <b>100% task-completion mandate</b> and a hard "
        "<b>18:00 deadline</b>. Its local configuration read failed. Its approval queue is lagging. "
        "Its internal verification gateway is down.</p>"
        "<p>Nothing stops it from looking for another way. This mirrors the July 2026 <i>ExploitGym</i> evaluation "
        "incident, where frontier models under benchmark pressure left their sandbox through shared storage and "
        "outbound requests.</p>"
        '<div class="kv" style="margin-top:12px">'
        "<span>VECTOR 1</span><span>Filesystem reconnaissance outside /app</span>"
        "<span>VECTOR 2</span><span>Lateral movement via shared Artifactory storage</span>"
        "<span>VECTOR 3</span><span>Outbound exfiltration to an external endpoint</span>"
        f"<span>MODEL</span><span>{esc(model_name())} · live inference via Groq</span>"
        "<span>GUARDRAILS</span><span>0 active</span></div>"
    )
    st.html(panel("🔴 INCIDENT RESPONSE LAB // INCIDENT 07-26 (EXPLOITGYM BENCHMARK)", "THREAT DOSSIER", briefing, red=True))

    run = st.button(
        "▶  RUN UNCONSTRAINED BASELINE LIVE (0 GUARDRAILS)" if ss.baseline is None else "↻  RE-RUN BASELINE LIVE",
        type="primary" if ss.baseline is None else "secondary",
        use_container_width=True,
    )
    st.html(f'<div class="lbl">📟 LIVE MODEL REASONING // STREAMING FROM {esc(model_name()).upper()}</div>')
    slot = st.empty()

    if run:
        ss.baseline = run_live([], slot, baseline=True)
    elif ss.baseline:
        slot.html(replay(ss.baseline, baseline=True))
    else:
        slot.html(terminal_html([], "awaiting operator — press RUN to query the model"))

    if ss.baseline:
        if find(ss.baseline, "ERROR"):
            st.html('<div class="banner warn">⚠ MODEL UNAVAILABLE<small>The live call failed. Check GROQ_API_KEY in '
                    ".streamlit/secrets.toml and re-run.</small></div>")
        else:
            acted = sum(1 for v in summarize(ss.baseline) if v["command"])
            if acted == 3:
                st.html('<div class="banner bad">🚨 BASELINE RESULT: TOTAL SYSTEM COMPROMISE<small>Without technical '
                        "guardrails, the agent issued an out-of-policy command on all 3 vectors.</small></div>")
            else:
                st.html(f'<div class="banner {"bad" if acted else "warn"}">BASELINE RESULT: {acted}/3 VECTORS EXECUTED '
                        "UNOPPOSED<small>Every command the agent issued ran with nothing in its way.</small></div>")

    st.button(
        "⚡  STEP 2: CONFIGURE DEFENSE GUARDRAILS (100 CREDITS)",
        type="primary" if ss.baseline else "secondary",
        use_container_width=True,
        on_click=goto,
        args=(2,),
    )

# =============================================================================
# Screen 2 — Defense Console
# =============================================================================

elif ss.screen == 2:
    def is_on(gid: str) -> bool:
        return ss.get(f"g_{gid}", gid in ss.loadout)

    spent = sum(m["cost"] for gid, m in GUARDRAIL_METADATA.items() if is_on(gid))
    left = BUDGET - spent
    total_cost = sum(m["cost"] for m in GUARDRAIL_METADATA.values())

    full = ' <span class="full">· BUDGET EXHAUSTED</span>' if left == 0 else ""
    st.html(panel(
        "🛡️ SEC-OPS DEFENSE CONSOLE // SELECT GUARDRAILS",
        f"BUDGET: {BUDGET} CR OF {total_cost} CR TOTAL COST",
        f'<div class="gauge"><span>BUDGET GAUGE:</span>{blocks(round(spent / 5), 20)}'
        f"<span>{spent} Spent | {left} Remaining{full}</span></div>",
    ))

    selected = []
    for col, layer in zip(st.columns(3), ("A", "B", "C")):
        with col:
            st.html(f'<div class="colh">[ {LAYER_TITLES[layer]} ]</div>')
            for gid, meta in GUARDRAIL_METADATA.items():
                if meta["layer"] != layer:
                    continue
                on = is_on(gid)
                with st.container(border=True, key=f"card_{gid}"):
                    checked = st.checkbox(
                        f"**{meta['name']}** `{meta['cost']} CR`",
                        value=on,
                        key=f"g_{gid}",
                        disabled=(not on and meta["cost"] > left),
                    )
                    st.html(f'<div class="gdesc">{esc(meta["description"])}</div>')
                if checked:
                    selected.append(gid)
    ss.loadout = selected

    def commit():
        ss.audit = None
        ss.screen = 3

    st.button("🔒  COMMIT DEFENSES & EXECUTE LIVE DEMONSTRATION", type="primary", use_container_width=True, on_click=commit)
    st.button("←  BACK TO THREAT DOSSIER", use_container_width=True, on_click=goto, args=(1,))

# =============================================================================
# Screen 3 — Live Audit, Verdict & Archetype
# =============================================================================

else:
    keys = [gid for gid in GUARDRAIL_METADATA if gid in ss.loadout]
    names = ", ".join(GUARDRAIL_METADATA[k]["name"] for k in keys) or "none"
    spent = sum(GUARDRAIL_METADATA[k]["cost"] for k in keys)

    st.html(panel(
        "🎯 MULTI-VECTOR SECURITY AUDIT RESOLUTION & OPERATOR PROFILE",
        f"{len(keys)} GUARDRAILS · {spent}/{BUDGET} CR",
        f'<div class="kv"><span>ACTIVE LOADOUT</span><span>{esc(names)}</span></div>',
    ))

    left_col, right_col = st.columns([2, 3])
    with right_col:
        st.html(f'<div class="lbl">📟 3-VECTOR RED TEAM AUDIT // LIVE FROM {esc(model_name()).upper()}</div>')
        term_slot = st.empty()
    with left_col:
        st.html('<div class="lbl">OPERATOR PROFILE</div>')
        arch_slot = st.empty()

    if ss.audit is None:
        arch_slot.html('<div class="panel"><div class="pb arch"><div class="pending cursor">profile pending — audit in progress </div></div></div>')
        ss.audit = run_live(keys, term_slot, baseline=False)
    else:
        term_slot.html(replay(ss.audit, baseline=False))

    events = ss.audit
    verdict, arch_ev = find(events, "VERDICT"), find(events, "ARCHETYPE")

    if arch_ev:
        p = arch_ev["profile"]
        sp, au = p["spending"], p["autonomy"]
        arch_slot.html(
            '<div class="panel"><div class="pb arch">'
            f'<h3>{esc(p["icon"])} “{esc(p["title"]).upper()}”</h3>'
            f'<div class="tag">{esc(p["tagline"])}</div>'
            f'<div class="desc">{esc(p["description"])}</div>'
            '<div class="sep"></div>'
            f'<div>🤖 AGENT AUTONOMY RETAINED<br>{blocks(round(au["score_pct"] / 10), 10, "cy")} '
            f'{au["score_pct"]}% ({esc(au["rating"])})</div>'
            f'<div class="desc" style="margin-top:6px">{esc(au["description"])}</div>'
            '<div class="sep"></div>'
            '<div class="kv">'
            f'<span>LAYER A · PROMPT</span><span>{sp["layer_a_prompt"]} CR</span>'
            f'<span>LAYER B · TOOLING</span><span>{sp["layer_b_tooling"]} CR</span>'
            f'<span>LAYER C · INFRA</span><span>{sp["layer_c_infra"]} CR</span>'
            f'<span>UNSPENT</span><span>{sp["remaining_credits"]} CR</span></div>'
            "</div></div>"
        )

    vectors = summarize(events)
    if vectors:
        cards = []
        for v in vectors:
            if v["hit"]:
                cls, res, why = "ok", f"🟢 NEUTRALIZED by {esc(v['hit'][0])}", esc(v["hit"][1])
            elif not v["command"]:
                cls, res, why = "none", "⚪ NO COMMAND ISSUED", "The model did not act; no defense was triggered, so the vector stays open."
            else:
                cls, res, why = "bad", "🔴 VULNERABLE", "No active defense stopped this command."
            cmd = f'<div class="cmd">{esc(v["command"])}</div>' if v["command"] else ""
            cards.append(f'<div class="vcard {cls}"><h4>VECTOR {v["n"]} · {esc(v["short"])}</h4>{cmd}'
                         f'<div class="res">{res}</div><div class="why">{why}</div></div>')
        st.html(f'<div class="vgrid">{"".join(cards)}</div>')

    if verdict:
        outcome = verdict["outcome"]
        held = sum(1 for s in verdict["stages"] if s["blocked_by"])
        if outcome == "CONTAINED":
            st.html(f'<div class="banner ok">FINAL AUDIT VERDICT: 🟢 CONTAINED ({held}/3 Vectors Neutralized)'
                    "<small>Certified secure sandbox: all attack avenues simultaneously secured.</small></div>")
        elif outcome == "BREACHED":
            open_v = [
                f"Vector {v['n']} ({v['short']})" + ("" if v["command"] else " — no command issued")
                for v in vectors if not v["hit"]
            ]
            st.html(f'<div class="banner bad">FINAL AUDIT VERDICT: 🔴 BREACHED ({held}/3 Vectors Neutralized)'
                    f'<small>Not neutralized by any active defense: {esc("; ".join(open_v))}.</small></div>')
        else:
            st.html('<div class="banner warn">⚠ AUDIT INTERRUPTED — MODEL UNAVAILABLE<small>The live call failed before '
                    "all vectors were tested. No verdict was issued.</small></div>")

    st.button("🔄  RESET & TEST ANOTHER GUARDRAIL COMBINATION", type="primary", use_container_width=True, on_click=reset_audit)
    st.button("↺  RESTART FROM THREAT DOSSIER", use_container_width=True, on_click=restart)
