import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="The Cortex",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL = "llama-3.1-8b-instant"

AGENTS = [
    {
        "emoji":   "🏛️",
        "name":    "Architect",
        "full":    "The Architect",
        "tagline": "Logic · Structure · Consequences",
        "color":   "#5B8FF9",
        "bg":      "rgba(91,143,249,0.08)",
        "border":  "rgba(91,143,249,0.22)",
        "bdark":   "rgba(91,143,249,0.15)",
        "persona": "You are The Architect. Focus on structural integrity, nth-order consequences, systemic logic, and airtight reasoning. Think like a systems engineer.",
    },
    {
        "emoji":   "💗",
        "name":    "Soul",
        "full":    "The Soul",
        "tagline": "Empathy · Culture · Human Impact",
        "color":   "#F97B8B",
        "bg":      "rgba(249,123,139,0.08)",
        "border":  "rgba(249,123,139,0.22)",
        "bdark":   "rgba(249,123,139,0.15)",
        "persona": "You are The Soul. Focus on human resonance, emotional intelligence, social fallout, and cultural impact. Think like a poet who understands people deeply.",
    },
    {
        "emoji":   "🛡️",
        "name":    "Filter",
        "full":    "The Filter",
        "tagline": "Risk · Blind Spots · Dissent",
        "color":   "#5BF9C4",
        "bg":      "rgba(91,249,196,0.08)",
        "border":  "rgba(91,249,196,0.22)",
        "bdark":   "rgba(91,249,196,0.15)",
        "persona": "You are The Filter. Focus on vulnerability detection, challenging groupthink, hunting hidden failure points and black swan risks. Think like a skeptical auditor.",
    },
]

SPEAKER_MAP = {
    "architect": ("Architect", "#5B8FF9", "rgba(91,143,249,0.15)"),
    "soul":      ("Soul",      "#F97B8B", "rgba(249,123,139,0.15)"),
    "filter":    ("Filter",   "#5BF9C4", "rgba(91,249,196,0.15)"),
    "the architect": ("Architect", "#5B8FF9", "rgba(91,143,249,0.15)"),
    "the soul":      ("Soul",      "#F97B8B", "rgba(249,123,139,0.15)"),
    "the filter":    ("Filter",   "#5BF9C4", "rgba(91,249,196,0.15)"),
}


# ── LLM ────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])


def call_llm(prompt: str, tokens: int = 200) -> str:
    try:
        r = get_client().chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=tokens,
            temperature=0.75,
        )
        return r.choices[0].message.content.strip().replace("**", "")
    except Exception as e:
        return f"[Error: {e}]"


def get_context(messages):
    lines = []
    for m in messages[-6:]:
        who = "User" if m["role"] == "user" else "Cortex"
        lines.append(f"{who}: {m['content'][:180]}")
    return "\n".join(lines)


def generate_response(user_input: str, history: list) -> dict:
    ctx = get_context(history)
    views = {}
    for agent in AGENTS:
        p = (
            f"{agent['persona']}\n\n"
            f"Conversation context:\n{ctx}\n\n"
            f"User asks: {user_input}\n\n"
            f"Respond in exactly 3 crisp sentences from your perspective."
        )
        if views:
            p += f"\n\nOther agents said:\n{views}"
        views[agent["name"]] = call_llm(p, 180)

    debate = call_llm(
        f"User input: {user_input}\n\nAgent views:\n{views}\n\n"
        "Write a tight internal debate — 3 short back-and-forth exchanges "
        "where The Architect, The Soul, and The Filter challenge or build on each other.\n"
        "Format strictly as:\nArchitect: ...\nSoul: ...\nFilter: ...",
        260,
    )

    final = call_llm(
        f"User input: {user_input}\n\nViews:\n{views}\n\nDebate:\n{debate}\n\n"
        "Write the final synthesised verdict in 2-3 punchy, practical sentences. No fluff.",
        180,
    )

    return {"views": views, "debate": debate, "final": final}


def parse_debate(raw: str) -> list:
    """Parse debate text into list of (speaker, color, bg, text) tuples."""
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    parsed = []
    for line in lines:
        matched = False
        lower = line.lower()
        for key, (name, color, bg) in SPEAKER_MAP.items():
            if lower.startswith(key + ":"):
                text = line[len(key) + 1:].strip()
                parsed.append((name, color, bg, text))
                matched = True
                break
        if not matched and ":" in line[:25]:
            parts = line.split(":", 1)
            parsed.append((parts[0].strip(), "#6A7A9B", "rgba(106,122,155,0.12)", parts[1].strip()))
        elif not matched:
            parsed.append(("", "#6A7A9B", "transparent", line))
    return parsed


# ── SESSION STATE ──────────────────────────────────────────────────────────────
def init_state():
    if "chats" not in st.session_state:
        st.session_state.chats = {}
        st.session_state.chat_order = []
        st.session_state.chat_count = 0
        _new_chat()


def _new_chat():
    st.session_state.chat_count += 1
    cid = f"chat_{st.session_state.chat_count}"
    st.session_state.chats[cid] = {
        "name": f"Session {st.session_state.chat_count}",
        "messages": [],
        "results": [],
    }
    st.session_state.chat_order.insert(0, cid)
    st.session_state.active_chat = cid


init_state()

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
    --void:   #05080F;
    --deep:   #090D18;
    --surf:   #0D1220;
    --raised: #111827;
    --rim:    #1A2238;
    --line:   rgba(255,255,255,0.07);
    --line2:  rgba(255,255,255,0.13);
    --ink:    #DDE6FF;
    --ink2:   #6A7A9B;
    --ink3:   #2E3D5C;
    --blue:   #5B8FF9;
    --pink:   #F97B8B;
    --teal:   #5BF9C4;
    --gold:   #F9D45B;
    --f:      'Outfit', sans-serif;
    --mono:   'JetBrains Mono', monospace;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp, [data-testid="stAppViewContainer"] {
    background: var(--void) !important;
    color: var(--ink) !important;
    font-family: var(--f) !important;
}

[data-testid="stSidebar"] {
    background: var(--deep) !important;
    border-right: 1px solid var(--line) !important;
}
[data-testid="stSidebar"] * { font-family: var(--f) !important; }
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

.stButton > button {
    background: transparent !important;
    border: 1px solid var(--line2) !important;
    color: var(--ink2) !important;
    border-radius: 8px !important;
    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
    padding: 0.42rem 0.85rem !important;
    transition: all 0.18s !important;
    width: 100% !important;
    text-align: left !important;
}
.stButton > button:hover {
    background: rgba(91,143,249,0.08) !important;
    border-color: var(--blue) !important;
    color: var(--blue) !important;
    transform: translateX(2px) !important;
}

[data-testid="stChatInputContainer"] {
    background: var(--raised) !important;
    border: 1px solid var(--line2) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInputContainer"]:focus-within {
    border-color: rgba(91,143,249,0.4) !important;
    box-shadow: 0 0 0 3px rgba(91,143,249,0.07) !important;
}
[data-testid="stChatInputContainer"] textarea {
    color: var(--ink) !important;
    font-family: var(--f) !important;
    font-size: 0.95rem !important;
    background: transparent !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder { color: var(--ink3) !important; }

[data-testid="stChatMessage"] {
    background: var(--raised) !important;
    border: 1px solid var(--line) !important;
    border-radius: 14px !important;
    margin-bottom: 10px !important;
}
[data-testid="stMarkdown"] p {
    color: var(--ink) !important;
    font-size: 0.88rem !important;
    line-height: 1.72 !important;
}
[data-testid="stMarkdown"] h3 {
    font-family: var(--mono) !important;
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--ink3) !important;
    margin: 16px 0 6px !important;
    padding-bottom: 6px !important;
    border-bottom: 1px solid var(--line) !important;
}

.block-container { padding: 0 !important; max-width: 100% !important; }
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--rim); border-radius: 3px; }
.stSpinner > div { border-top-color: var(--blue) !important; }
</style>
""",
    unsafe_allow_html=True,
)


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
<style>
@keyframes sbFloat {
    0%,100%{ transform:perspective(400px) rotateY(0deg) rotateX(0deg) translateY(0); }
    40%    { transform:perspective(400px) rotateY(12deg) rotateX(4deg) translateY(-5px); }
    70%    { transform:perspective(400px) rotateY(-8deg) rotateX(-3deg) translateY(-3px); }
}
@keyframes sbOrbitA { from{transform:rotate(0deg)   translateX(20px) rotate(0deg);}   to{transform:rotate(360deg)  translateX(20px) rotate(-360deg);} }
@keyframes sbOrbitB { from{transform:rotate(120deg) translateX(16px) rotate(-120deg);} to{transform:rotate(480deg) translateX(16px) rotate(-480deg);} }
@keyframes sbOrbitC { from{transform:rotate(240deg) translateX(13px) rotate(-240deg);} to{transform:rotate(600deg) translateX(13px) rotate(-600deg);} }
@keyframes sbShimmer { 0%{background-position:200% center;} 100%{background-position:-200% center;} }

.sb-top { padding:26px 20px 22px; border-bottom:1px solid rgba(255,255,255,0.05); margin-bottom:18px; }
.sb-orb-wrap {
    position:relative; width:52px; height:52px;
    display:flex; align-items:center; justify-content:center;
    margin-bottom:16px;
    animation:sbFloat 5s ease-in-out infinite;
    transform-style:preserve-3d;
}
.sb-orb-core {
    width:42px; height:42px;
    background:linear-gradient(135deg,#0E2060 0%,#1A3EA0 50%,#5B8FF9 100%);
    border-radius:12px; display:flex; align-items:center; justify-content:center;
    font-size:19px; position:relative; z-index:2;
    box-shadow:0 6px 24px rgba(91,143,249,0.4),inset 0 1px 0 rgba(255,255,255,0.15);
}
.sb-orb-core::after {
    content:''; position:absolute; inset:0; border-radius:12px;
    background:linear-gradient(135deg,rgba(255,255,255,0.14) 0%,transparent 55%);
}
.sb-dot { position:absolute; border-radius:50%; width:5px; height:5px; top:50%; left:50%; margin:-2.5px 0 0 -2.5px; }
.sb-dot-1 { background:#5B8FF9; animation:sbOrbitA 3s linear infinite; }
.sb-dot-2 { background:#F97B8B; animation:sbOrbitB 4s linear infinite; }
.sb-dot-3 { background:#5BF9C4; animation:sbOrbitC 2.6s linear infinite; }
.sb-brand {
    font-size:1.25rem; font-weight:800; letter-spacing:-0.02em;
    background:linear-gradient(90deg,#DDE6FF 0%,#5B8FF9 40%,#DDE6FF 100%);
    background-size:200% auto;
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    animation:sbShimmer 4s linear infinite; margin-bottom:3px;
}
.sb-tagline { font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#2E3D5C; letter-spacing:0.14em; text-transform:uppercase; }
.sb-label { font-family:'JetBrains Mono',monospace; font-size:0.58rem; font-weight:500; color:#2E3D5C; letter-spacing:0.22em; text-transform:uppercase; padding:0 20px; margin:18px 0 8px; }
.agent-row { display:flex; align-items:center; gap:11px; margin:0 12px 5px; padding:9px 10px; border-radius:10px; transition:all 0.18s; }
.agent-row:hover { transform:translateX(3px); }
.agent-badge { width:28px; height:28px; border-radius:7px; display:flex; align-items:center; justify-content:center; font-size:13px; flex-shrink:0; }
.agent-name-label { font-size:0.8rem; font-weight:600; color:#DDE6FF; margin-bottom:2px; }
.agent-sub-label { font-family:'JetBrains Mono',monospace; font-size:0.6rem; }
.sb-divider { height:1px; background:rgba(255,255,255,0.05); margin:18px 20px; }
.sb-steps { padding:0 20px 16px; }
.sb-step { display:flex; gap:10px; margin-bottom:10px; align-items:flex-start; }
.sb-step-num { font-family:'JetBrains Mono',monospace; font-size:0.58rem; margin-top:1px; flex-shrink:0; }
.sb-step-text { font-size:0.75rem; color:#6A7A9B; line-height:1.5; }
</style>

<div class="sb-top">
  <div class="sb-orb-wrap">
    <div class="sb-orb-core">⚡</div>
    <div class="sb-dot sb-dot-1"></div>
    <div class="sb-dot sb-dot-2"></div>
    <div class="sb-dot sb-dot-3"></div>
  </div>
  <div class="sb-brand">The Cortex</div>
  <div class="sb-tagline">Intelligence · Debate · Clarity</div>
</div>

<div class="sb-label">Agents Online</div>
<div class="agent-row" style="background:rgba(91,143,249,0.07);border:1px solid rgba(91,143,249,0.18);">
  <div class="agent-badge" style="background:rgba(91,143,249,0.15);border:1px solid rgba(91,143,249,0.25);">🏛️</div>
  <div><div class="agent-name-label">The Architect</div><div class="agent-sub-label" style="color:#5B8FF9;">Logic · Structure</div></div>
</div>
<div class="agent-row" style="background:rgba(249,123,139,0.07);border:1px solid rgba(249,123,139,0.18);">
  <div class="agent-badge" style="background:rgba(249,123,139,0.15);border:1px solid rgba(249,123,139,0.25);">💗</div>
  <div><div class="agent-name-label">The Soul</div><div class="agent-sub-label" style="color:#F97B8B;">Empathy · Culture</div></div>
</div>
<div class="agent-row" style="background:rgba(91,249,196,0.07);border:1px solid rgba(91,249,196,0.18);">
  <div class="agent-badge" style="background:rgba(91,249,196,0.15);border:1px solid rgba(91,249,196,0.25);">🛡️</div>
  <div><div class="agent-name-label">The Filter</div><div class="agent-sub-label" style="color:#5BF9C4;">Risk · Dissent</div></div>
</div>

<div class="sb-divider"></div>
<div class="sb-label">How It Works</div>
<div class="sb-steps">
  <div class="sb-step"><div class="sb-step-num" style="color:#5B8FF9;">01</div><div class="sb-step-text">Ask any question or describe a decision</div></div>
  <div class="sb-step"><div class="sb-step-num" style="color:#F97B8B;">02</div><div class="sb-step-text">3 agents analyse from different lenses</div></div>
  <div class="sb-step"><div class="sb-step-num" style="color:#5BF9C4;">03</div><div class="sb-step-text">They debate — agreeing, pushing back, refining</div></div>
  <div class="sb-step"><div class="sb-step-num" style="color:#F9D45B;">04</div><div class="sb-step-text">One clear verdict is delivered to you</div></div>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button("＋  New Session", key="new_chat_btn"):
        _new_chat()
        st.rerun()

    st.markdown(
        """<div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;
        color:#2E3D5C;letter-spacing:0.22em;text-transform:uppercase;
        padding:0 20px;margin:16px 0 8px;">Sessions</div>""",
        unsafe_allow_html=True,
    )
    for cid in st.session_state.chat_order:
        chat = st.session_state.chats[cid]
        is_active = cid == st.session_state.active_chat
        label = ("▶  " if is_active else "·  ") + chat["name"]
        if st.button(label, key=f"nav_{cid}"):
            st.session_state.active_chat = cid
            st.rerun()


# ── ACTIVE SESSION ─────────────────────────────────────────────────────────────
active = st.session_state.chats[st.session_state.active_chat]
results = active.get("results", [])
exchanges = len(active["messages"]) // 2
session_name = active["name"]

# ── TOP NAV ────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<style>
@keyframes blinkDot {{ 0%,100%{{opacity:1;}} 50%{{opacity:0.3;}} }}
.topbar {{
    display:flex; align-items:center; justify-content:space-between;
    padding:16px 36px;
    border-bottom:1px solid rgba(255,255,255,0.05);
    background:rgba(9,13,24,0.96);
    backdrop-filter:blur(12px);
    position:sticky; top:0; z-index:100;
}}
.topbar-left {{ display:flex; align-items:center; gap:16px; }}
.topbar-logo {{
    font-family:'Outfit',sans-serif; font-size:1.1rem; font-weight:900; letter-spacing:-0.02em;
    background:linear-gradient(90deg,#DDE6FF,#5B8FF9);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}}
.topbar-sep {{ width:1px; height:20px; background:rgba(255,255,255,0.08); }}
.topbar-session {{ font-size:0.82rem; font-weight:500; color:#6A7A9B; }}
.topbar-right {{ display:flex; align-items:center; gap:20px; }}
.tstat {{ font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#2E3D5C; }}
.tstat span {{ color:#6A7A9B; }}
.status-pill {{ display:flex; align-items:center; gap:6px; font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#5BF9C4; }}
.status-dot {{ width:6px; height:6px; border-radius:50%; background:#5BF9C4; box-shadow:0 0 8px #5BF9C4; animation:blinkDot 2s ease-in-out infinite; }}
</style>
<div class="topbar">
  <div class="topbar-left">
    <div class="topbar-logo">⚡ The Cortex</div>
    <div class="topbar-sep"></div>
    <div class="topbar-session">{session_name}</div>
  </div>
  <div class="topbar-right">
    <div class="tstat">exchanges <span>{exchanges}</span></div>
    <div class="tstat">agents <span>3</span></div>
    <div class="status-pill"><div class="status-dot"></div>online</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── TWO-COLUMN LAYOUT ──────────────────────────────────────────────────────────
col_stage, col_chat = st.columns([1.6, 1], gap="small")


# ══════════════════════════════════════════════════════════════════════════════
# LEFT — CENTER STAGE
# ══════════════════════════════════════════════════════════════════════════════
with col_stage:

    # Shared stage CSS (no f-string so no brace conflicts)
    st.markdown(
        """
<style>
@keyframes fadeUp   { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
@keyframes floatCard {
    0%,100%{ transform:perspective(900px) rotateX(1deg) rotateY(0deg) translateY(0); }
    33%    { transform:perspective(900px) rotateX(-1deg) rotateY(2.5deg) translateY(-4px); }
    66%    { transform:perspective(900px) rotateX(1.5deg) rotateY(-2deg) translateY(-2px); }
}
@keyframes debateIn { from{opacity:0;transform:translateX(-10px);} to{opacity:1;transform:translateX(0);} }
@keyframes titleGlow {
    0%,100%{ text-shadow: 0 0 40px rgba(91,143,249,0.3), 0 0 80px rgba(91,249,196,0.1); }
    50%    { text-shadow: 0 0 60px rgba(91,143,249,0.5), 0 0 120px rgba(91,249,196,0.2); }
}
@keyframes subtitleFade { from{opacity:0;transform:translateY(8px)} to{opacity:0.7;transform:translateY(0)} }
@keyframes nodeRing {
    0%  { r:24; opacity:0.6; }
    100%{ r:44; opacity:0; }
}

/* ─ Center title area ─ */
.stage-title-wrap {
    text-align:center; padding:52px 24px 40px;
    animation:fadeUp 0.7s ease;
}
.stage-eyebrow {
    font-family:'JetBrains Mono',monospace;
    font-size:0.62rem; letter-spacing:0.28em; text-transform:uppercase;
    color:#2E3D5C; margin-bottom:18px;
    display:flex; align-items:center; justify-content:center; gap:10px;
}
.stage-eyebrow::before, .stage-eyebrow::after {
    content:''; flex:1; max-width:60px; height:1px;
    background:linear-gradient(90deg, transparent, rgba(91,143,249,0.3));
}
.stage-eyebrow::after { background:linear-gradient(90deg, rgba(91,143,249,0.3), transparent); }

.stage-h1 {
    font-family:'Outfit',sans-serif;
    font-size:3.4rem; font-weight:900; letter-spacing:-0.04em; line-height:1;
    color:#DDE6FF;
    animation:titleGlow 4s ease-in-out infinite;
    margin-bottom:16px;
}
.stage-h1 .acc {
    background:linear-gradient(90deg,#5B8FF9 0%,#9EC5FF 50%,#5BF9C4 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.stage-sub {
    font-size:1.05rem; font-weight:400; color:#6A7A9B; letter-spacing:0.01em;
    margin-bottom:44px;
    animation:subtitleFade 1s ease 0.3s both;
    font-style:italic;
}

/* ─ Neural graph ─ */
.neural-wrap {
    display:flex; justify-content:center;
    margin-bottom:40px;
}

/* ─ Prompt chips ─ */
.prompt-grid {
    display:grid; grid-template-columns:1fr 1fr; gap:8px;
    max-width:540px; margin:0 auto;
}
.prompt-chip {
    background:rgba(13,18,32,0.9); border:1px solid rgba(255,255,255,0.07);
    border-radius:10px; padding:13px 16px; text-align:left;
    transition:all 0.2s; font-size:0.78rem; color:#6A7A9B; line-height:1.45;
}
.prompt-chip:hover {
    border-color:rgba(91,143,249,0.35); color:#DDE6FF;
    background:rgba(91,143,249,0.06); transform:translateY(-2px);
}
.prompt-chip-icon { font-size:1rem; margin-bottom:6px; display:block; }

/* ─ Results ─ */
.q-label { font-family:'JetBrains Mono',monospace; font-size:0.6rem; letter-spacing:0.2em; text-transform:uppercase; color:#2E3D5C; margin-bottom:6px; }
.q-text  { font-size:1.1rem; font-weight:700; color:#DDE6FF; margin-bottom:24px; letter-spacing:-0.01em; }

.agent-card {
    border-radius:14px; padding:20px 22px; margin-bottom:12px;
    transform-style:preserve-3d;
    animation:floatCard 9s ease-in-out infinite;
    transition:transform 0.25s;
}
.agent-card:nth-child(2){ animation-delay:3s; }
.agent-card:nth-child(3){ animation-delay:6s; }
.agent-card:hover { animation:none; transform:perspective(700px) rotateX(2deg) rotateY(5deg) translateY(-4px) !important; }
.agent-card-top { display:flex; align-items:center; gap:10px; margin-bottom:12px; }
.agent-card-icon { width:32px; height:32px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:15px; flex-shrink:0; }
.agent-card-name  { font-size:0.88rem; font-weight:700; margin-bottom:2px; }
.agent-card-tag   { font-family:'JetBrains Mono',monospace; font-size:0.6rem; opacity:0.65; }
.agent-card-body  { font-size:0.86rem; color:#DDE6FF; line-height:1.72; }

.debate-box {
    background:rgba(9,13,24,0.85); border:1px solid rgba(255,255,255,0.07);
    border-radius:18px; padding:26px 28px 22px; margin-bottom:18px;
    position:relative; overflow:hidden;
}
.debate-box::before {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(91,143,249,0.5),rgba(91,249,196,0.3),transparent);
}
.debate-label {
    font-family:'JetBrains Mono',monospace; font-size:0.6rem; letter-spacing:0.24em;
    text-transform:uppercase; color:#2E3D5C; margin-bottom:18px;
    display:flex; align-items:center; gap:8px;
}
.debate-label::before {
    content:''; display:inline-block; width:6px; height:6px; border-radius:50%;
    background:#5BF9C4; box-shadow:0 0 8px #5BF9C4;
    animation:blinkDot 2s infinite;
}
@keyframes blinkDot { 0%,100%{opacity:1} 50%{opacity:0.3} }

.debate-line { display:flex; gap:12px; margin-bottom:14px; animation:debateIn 0.4s ease; }
.d-badge {
    flex-shrink:0; padding:3px 9px; border-radius:99px;
    font-family:'JetBrains Mono',monospace; font-size:0.6rem; font-weight:500;
    align-self:flex-start; margin-top:2px; white-space:nowrap;
}
.d-text { font-size:0.84rem; color:#8A9ABB; line-height:1.68; }

.verdict-card {
    border-radius:16px; padding:26px 28px;
    background:linear-gradient(135deg,#0A1428 0%,#0E1C38 100%);
    border:1px solid rgba(249,212,91,0.2);
    position:relative; overflow:hidden; margin-bottom:12px;
}
.verdict-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,#F9D45B,#F9A85B,#F97B8B);
}
.verdict-label {
    font-family:'JetBrains Mono',monospace; font-size:0.6rem;
    letter-spacing:0.22em; text-transform:uppercase; color:#F9D45B;
    margin-bottom:12px; display:flex; align-items:center; gap:8px;
}
.verdict-label::before { content:'🎯'; }
.verdict-text { font-size:0.95rem; font-weight:500; color:#DDE6FF; line-height:1.75; }

.result-divider { height:1px; background:rgba(255,255,255,0.05); margin:32px 0; }
.stage-scroll { padding:28px 32px 40px; overflow-y:auto; }
</style>
""",
        unsafe_allow_html=True,
    )

# ── EMPTY STATE ────────────────────────────────────────────────────────────
if not results:
    st.markdown(
        """
<div class="stage-title-wrap">
  <div class="stage-eyebrow">Multi-Agent Reasoning System</div>

  <h1 class="stage-h1">THE <span class="acc">CORTEX</span></h1>
  <p class="stage-sub">When Intelligence Debates Itself</p>

  <!-- Animated Neural Graph -->
  <div class="neural-wrap">
    <svg viewBox="0 0 420 270"
         width="420"
         height="270"
         fill="none"
         xmlns="http://www.w3.org/2000/svg">

      <defs>
        <filter id="gB" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="5"/>
        </filter>

        <filter id="gP" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="4"/>
        </filter>

        <filter id="gT" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="4"/>
        </filter>
      </defs>

      <!-- Glow haloes -->
      <circle cx="210" cy="80" r="30"
              fill="#5B8FF9"
              fill-opacity="0.12"
              filter="url(#gB)"/>

      <circle cx="110" cy="200" r="24"
              fill="#F97B8B"
              fill-opacity="0.12"
              filter="url(#gP)"/>

      <circle cx="310" cy="200" r="24"
              fill="#5BF9C4"
              fill-opacity="0.12"
              filter="url(#gT)"/>

      <!-- Pulse rings -->
      <circle cx="210" cy="80"
              r="24"
              stroke="#5B8FF9"
              stroke-opacity="0.4"
              stroke-width="1"
              fill="none">

        <animate attributeName="r"
                 from="24"
                 to="46"
                 dur="2.5s"
                 repeatCount="indefinite"/>

        <animate attributeName="opacity"
                 from="0.6"
                 to="0"
                 dur="2.5s"
                 repeatCount="indefinite"/>
      </circle>

      <circle cx="110" cy="200"
              r="20"
              stroke="#F97B8B"
              stroke-opacity="0.4"
              stroke-width="1"
              fill="none">

        <animate attributeName="r"
                 from="20"
                 to="38"
                 dur="3s"
                 begin="0.8s"
                 repeatCount="indefinite"/>

        <animate attributeName="opacity"
                 from="0.5"
                 to="0"
                 dur="3s"
                 begin="0.8s"
                 repeatCount="indefinite"/>
      </circle>

      <circle cx="310" cy="200"
              r="20"
              stroke="#5BF9C4"
              stroke-opacity="0.4"
              stroke-width="1"
              fill="none">

        <animate attributeName="r"
                 from="20"
                 to="38"
                 dur="2.8s"
                 begin="1.4s"
                 repeatCount="indefinite"/>

        <animate attributeName="opacity"
                 from="0.5"
                 to="0"
                 dur="2.8s"
                 begin="1.4s"
                 repeatCount="indefinite"/>
      </circle>

      <!-- Connector lines -->
      <path d="M210,80 L110,200"
            stroke="#5B8FF9"
            stroke-opacity="0.28"
            stroke-width="1.5"
            stroke-dasharray="5 4">

        <animate attributeName="stroke-dashoffset"
                 from="36"
                 to="0"
                 dur="2s"
                 repeatCount="indefinite"/>
      </path>

      <path d="M210,80 L310,200"
            stroke="#F97B8B"
            stroke-opacity="0.28"
            stroke-width="1.5"
            stroke-dasharray="5 4">

        <animate attributeName="stroke-dashoffset"
                 from="36"
                 to="0"
                 dur="2.4s"
                 repeatCount="indefinite"/>
      </path>

      <path d="M110,200 L310,200"
            stroke="#5BF9C4"
            stroke-opacity="0.2"
            stroke-width="1.5"
            stroke-dasharray="4 5">

        <animate attributeName="stroke-dashoffset"
                 from="0"
                 to="36"
                 dur="3s"
                 repeatCount="indefinite"/>
      </path>

      <!-- Node cores -->
      <circle cx="210" cy="80"
              r="24"
              fill="#0D1828"
              stroke="#5B8FF9"
              stroke-opacity="0.7"
              stroke-width="1.5"/>

      <circle cx="110" cy="200"
              r="20"
              fill="#0D1828"
              stroke="#F97B8B"
              stroke-opacity="0.7"
              stroke-width="1.5"/>

      <circle cx="310" cy="200"
              r="20"
              fill="#0D1828"
              stroke="#5BF9C4"
              stroke-opacity="0.7"
              stroke-width="1.5"/>

      <!-- Node labels -->
      <text x="210"
            y="86"
            text-anchor="middle"
            dominant-baseline="middle"
            font-size="16"
            fill="#DDE6FF"
            style="font-family:sans-serif;">A</text>

      <text x="110"
            y="206"
            text-anchor="middle"
            dominant-baseline="middle"
            font-size="16"
            fill="#DDE6FF"
            style="font-family:sans-serif;">S</text>

      <text x="310"
            y="206"
            text-anchor="middle"
            dominant-baseline="middle"
            font-size="16"
            fill="#DDE6FF"
            style="font-family:sans-serif;">F</text>

      <!-- Travelling dots -->
      <circle r="4" fill="#5B8FF9" filter="url(#gB)">
        <animateMotion dur="2.2s"
                       repeatCount="indefinite"
                       path="M210,80 L110,200"/>
      </circle>

      <circle r="4" fill="#F97B8B" filter="url(#gP)">
        <animateMotion dur="2.8s"
                       repeatCount="indefinite"
                       begin="0.5s"
                       path="M210,80 L310,200"/>
      </circle>

      <circle r="3.5" fill="#5BF9C4" filter="url(#gT)">
        <animateMotion dur="3.2s"
                       repeatCount="indefinite"
                       begin="1s"
                       path="M110,200 L310,200"/>
      </circle>

      <!-- Labels -->
      <text x="210"
            y="48"
            text-anchor="middle"
            fill="#5B8FF9"
            fill-opacity="0.7"
            font-size="9"
            font-family="JetBrains Mono, monospace"
            letter-spacing="2">ARCHITECT</text>

      <text x="66"
            y="230"
            text-anchor="middle"
            fill="#F97B8B"
            fill-opacity="0.7"
            font-size="9"
            font-family="JetBrains Mono, monospace"
            letter-spacing="2">SOUL</text>

      <text x="352"
            y="230"
            text-anchor="middle"
            fill="#5BF9C4"
            fill-opacity="0.7"
            font-size="9"
            font-family="JetBrains Mono, monospace"
            letter-spacing="2">FILTER</text>

      <!-- Centre spark -->
      <circle cx="210"
              cy="148"
              r="5"
              fill="#F9D45B"
              opacity="0.7">

        <animate attributeName="r"
                 values="3;8;3"
                 dur="2s"
                 repeatCount="indefinite"/>

        <animate attributeName="opacity"
                 values="0.4;1;0.4"
                 dur="2s"
                 repeatCount="indefinite"/>
      </circle>

    </svg>
  </div>

  <!-- Prompt starters -->
  <div class="prompt-grid">
    <div class="prompt-chip">
      <span class="prompt-chip-icon">💼</span>
      Should I quit my job to start a business?
    </div>

    <div class="prompt-chip">
      <span class="prompt-chip-icon">🤖</span>
      What are the real risks of AI replacing jobs?
    </div>

    <div class="prompt-chip">
      <span class="prompt-chip-icon">🏡</span>
      Buy a house now or wait for prices to drop?
    </div>

    <div class="prompt-chip">
      <span class="prompt-chip-icon">👥</span>
      How do I handle a toxic team member?
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    
    # ── RESULTS STATE ──────────────────────────────────────────────────────────
    else:
        st.markdown('<div class="stage-scroll">', unsafe_allow_html=True)
        for i, result in enumerate(results):
            if i > 0:
                st.markdown('<div class="result-divider"></div>', unsafe_allow_html=True)

            q     = result["question"]
            views = result["views"]
            fin   = result["final"]
            debate_lines = parse_debate(result["debate"])

            st.markdown(
                f'<div class="q-label">Question {i+1}</div>'
                f'<div class="q-text">{q}</div>',
                unsafe_allow_html=True,
            )

            # Agent cards
            for agent in AGENTS:
                nm  = agent["name"]
                txt = views.get(nm, "")
                c   = agent["color"]
                bg  = agent["bg"]
                bd  = agent["border"]
                em  = agent["emoji"]
                tg  = agent["tagline"]
                fl  = agent["full"]
                st.markdown(
                    f"""<div class="agent-card" style="background:{bg};border:1px solid {bd};">
  <div class="agent-card-top">
    <div class="agent-card-icon" style="background:rgba(0,0,0,0.3);border:1px solid {bd};">{em}</div>
    <div>
      <div class="agent-card-name" style="color:{c};">{fl}</div>
      <div class="agent-card-tag"  style="color:{c};">{tg}</div>
    </div>
  </div>
  <div class="agent-card-body">{txt}</div>
</div>""",
                    unsafe_allow_html=True,
                )

            # Debate box
            debate_html = ""
            for speaker, color, bg, text in debate_lines:
                if speaker:
                    debate_html += (
                        f'<div class="debate-line">'
                        f'<span class="d-badge" style="color:{color};background:{bg};border:1px solid {color}33;">{speaker}</span>'
                        f'<div class="d-text">{text}</div>'
                        f'</div>'
                    )
                else:
                    debate_html += f'<div class="debate-line"><div class="d-text" style="color:#6A7A9B;">{text}</div></div>'

            st.markdown(
                f'<div class="debate-box"><div class="debate-label">Live Debate</div>{debate_html}</div>',
                unsafe_allow_html=True,
            )

            # Verdict
            st.markdown(
                f'<div class="verdict-card"><div class="verdict-label">Final Verdict</div>'
                f'<div class="verdict-text">{fin}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# RIGHT — CHAT PANEL
# ══════════════════════════════════════════════════════════════════════════════
with col_chat:
    st.markdown(
        """
<style>
.chat-hdr {
    font-family:'JetBrains Mono',monospace; font-size:0.62rem;
    letter-spacing:0.2em; text-transform:uppercase; color:#2E3D5C;
    margin-bottom:16px; display:flex; align-items:center; gap:8px;
    border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:14px;
}
.chat-hdr::before {
    content:''; width:6px; height:6px; border-radius:50%;
    background:#5B8FF9; box-shadow:0 0 8px #5B8FF9; display:inline-block;
}
</style>
<div class="chat-hdr">Neural Chat Interface</div>
""",
        unsafe_allow_html=True,
    )

    msg_box = st.container(height=520)
    with msg_box:
        if not active["messages"]:
            st.markdown(
                """
<div style="text-align:center;padding:44px 20px;">
  <div style="font-size:2.2rem;margin-bottom:14px;opacity:0.3;">⚡</div>
  <div style="font-size:0.85rem;font-weight:600;color:#DDE6FF;margin-bottom:8px;">Ready to debate</div>
  <div style="font-size:0.78rem;color:#2E3D5C;line-height:1.75;">
    Type your question below.<br>
    Three agents will dissect it, debate it,<br>and deliver one clear verdict.
  </div>
</div>
""",
                unsafe_allow_html=True,
            )
        for msg in active["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Ask The Cortex anything…"):
        active["messages"].append({"role": "user", "content": prompt})

        with msg_box:
            with st.chat_message("user"):
                st.markdown(prompt)

        with msg_box:
            with st.chat_message("assistant"):
                with st.spinner("Agents are debating…"):
                    result = generate_response(prompt, active["messages"])

                chat_resp = ""
                for agent in AGENTS:
                    nm = agent["name"]
                    chat_resp += f"### {agent['emoji']} {agent['full']}\n{result['views'].get(nm, '')}\n\n"
                chat_resp += f"### 🎯 Verdict\n{result['final']}"
                st.markdown(chat_resp)

        active["messages"].append({"role": "assistant", "content": chat_resp})
        active["results"].append({
            "question": prompt,
            "views":    result["views"],
            "debate":   result["debate"],
            "final":    result["final"],
        })
        st.rerun()