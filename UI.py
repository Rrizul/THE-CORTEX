import streamlit as st
from groq import Groq
import time

st.set_page_config(
    page_title="Cortex",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL = "llama-3.1-8b-instant"

AGENTS = [
    {
        "key":     "architect",
        "icon":    "⬡",
        "emoji":   "🏛️",
        "name":    "Architect",
        "full":    "The Architect",
        "tagline": "Logic · Structure · Consequences",
        "color":   "#5B8FF9",
        "glow":    "rgba(91,143,249,0.35)",
        "bg":      "rgba(91,143,249,0.07)",
        "border":  "rgba(91,143,249,0.22)",
        "persona": "You are The Architect. Focus on structural integrity, nth-order consequences, systemic logic, and airtight reasoning. Think like an engineer.",
    },
    {
        "key":     "soul",
        "icon":    "◈",
        "emoji":   "💗",
        "name":    "Soul",
        "full":    "The Soul",
        "tagline": "Empathy · Culture · Human Impact",
        "color":   "#F97B8B",
        "glow":    "rgba(249,123,139,0.35)",
        "bg":      "rgba(249,123,139,0.07)",
        "border":  "rgba(249,123,139,0.22)",
        "persona": "You are The Soul. Focus on human resonance, emotional intelligence, social fallout, and cultural impact. Think like a poet who understands people deeply.",
    },
    {
        "key":     "filter",
        "icon":    "◬",
        "emoji":   "🛡️",
        "name":    "Filter",
        "full":    "The Filter",
        "tagline": "Risk · Blind Spots · Dissent",
        "color":   "#5BF9C4",
        "glow":    "rgba(91,249,196,0.35)",
        "bg":      "rgba(91,249,196,0.07)",
        "border":  "rgba(91,249,196,0.22)",
        "persona": "You are The Filter. Focus on vulnerability detection, challenging groupthink, hunting hidden failure points and black swan risks. Think like a skeptical auditor.",
    },
]


# ─── LLM ──────────────────────────────────────────────────────────────────────
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
    """Returns dict with per-agent views, debate, and final conclusion."""
    ctx = get_context(history)
    views = {}

    for agent in AGENTS:
        p = f"""{agent['persona']}

Conversation context:
{ctx}

User asks: {user_input}

Respond in exactly 3 crisp sentences from your perspective."""
        if views:
            p += f"\n\nOther agents said:\n{views}"
        views[agent["name"]] = call_llm(p, 180)

    debate = call_llm(f"""User input: {user_input}

Agent views:
{views}

Write a tight internal debate: 3 short back-and-forth exchanges where The Architect, The Soul, and The Filter challenge or build on each other. Format as:
Architect: ...
Soul: ...
Filter: ...
(one more round if needed)""", 260)

    final = call_llm(f"""User input: {user_input}

Views:
{views}

Debate:
{debate}

Write the final synthesised verdict in 2-3 punchy, practical sentences. No fluff.""", 180)

    return {"views": views, "debate": debate, "final": final}


# ─── STATE ─────────────────────────────────────────────────────────────────────
def init_state():
    if "chats" not in st.session_state:
        st.session_state.chats = {}
        st.session_state.chat_order = []
        st.session_state.chat_count = 0
        _new_chat()
    if "thinking" not in st.session_state:
        st.session_state.thinking = False
    if "last_result" not in st.session_state:
        st.session_state.last_result = None


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

# ─── GLOBAL CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

:root {
    --void:    #05080F;
    --deep:    #090D18;
    --surface: #0D1220;
    --raised:  #111827;
    --rim:     #1A2238;
    --mist:    rgba(255,255,255,0.05);
    --line:    rgba(255,255,255,0.07);
    --line2:   rgba(255,255,255,0.12);
    --ink:     #DDE6FF;
    --ink2:    #6A7A9B;
    --ink3:    #2E3D5C;
    --blue:    #5B8FF9;
    --pink:    #F97B8B;
    --teal:    #5BF9C4;
    --gold:    #F9D45B;
    --f:       'Outfit', sans-serif;
    --mono:    'JetBrains Mono', monospace;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp, [data-testid="stAppViewContainer"] {
    background: var(--void) !important;
    color: var(--ink) !important;
    font-family: var(--f) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--deep) !important;
    border-right: 1px solid var(--line) !important;
}
[data-testid="stSidebar"] * { font-family: var(--f) !important; }
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

/* Global buttons */
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

/* Chat input */
[data-testid="stChatInputContainer"] {
    background: var(--raised) !important;
    border: 1px solid var(--line2) !important;
    border-radius: 14px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stChatInputContainer"]:focus-within {
    border-color: rgba(91,143,249,0.4) !important;
    box-shadow: 0 0 0 3px rgba(91,143,249,0.08) !important;
}
[data-testid="stChatInputContainer"] textarea {
    color: var(--ink) !important;
    font-family: var(--f) !important;
    font-size: 0.95rem !important;
    background: transparent !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder { color: var(--ink3) !important; }

/* Chat messages */
[data-testid="stChatMessage"] {
    background: var(--raised) !important;
    border: 1px solid var(--line) !important;
    border-radius: 14px !important;
    margin-bottom: 10px !important;
    padding: 4px !important;
}
[data-testid="stMarkdown"] p {
    color: var(--ink) !important;
    font-size: 0.88rem !important;
    line-height: 1.7 !important;
}
[data-testid="stMarkdown"] h3 {
    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--ink3) !important;
    margin: 16px 0 5px !important;
    padding-bottom: 5px !important;
    border-bottom: 1px solid var(--line) !important;
}

.block-container { padding: 0 !important; max-width: 100% !important; }
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--rim); border-radius: 3px; }
.stSpinner > div { border-top-color: var(--blue) !important; }
</style>
""", unsafe_allow_html=True)


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<style>
@keyframes logoFloat {
    0%,100%{ transform:perspective(400px) rotateY(0deg) rotateX(0deg) translateY(0); }
    40%    { transform:perspective(400px) rotateY(12deg) rotateX(4deg) translateY(-5px); }
    70%    { transform:perspective(400px) rotateY(-8deg) rotateX(-3deg) translateY(-3px); }
}
@keyframes orbitA {
    from{ transform:rotate(0deg)   translateX(20px) rotate(0deg);   }
    to  { transform:rotate(360deg) translateX(20px) rotate(-360deg);}
}
@keyframes orbitB {
    from{ transform:rotate(120deg) translateX(16px) rotate(-120deg);}
    to  { transform:rotate(480deg) translateX(16px) rotate(-480deg);}
}
@keyframes orbitC {
    from{ transform:rotate(240deg) translateX(13px) rotate(-240deg);}
    to  { transform:rotate(600deg) translateX(13px) rotate(-600deg);}
}
@keyframes shimmer {
    0%  { background-position: 200% center; }
    100%{ background-position: -200% center; }
}

.sb-wrap { padding: 0; }
.sb-top {
    padding: 26px 20px 22px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 18px;
}
.sb-orb-wrap {
    position: relative; width: 52px; height: 52px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 16px;
    animation: logoFloat 5s ease-in-out infinite;
    transform-style: preserve-3d;
}
.sb-orb-core {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #0E2060 0%, #1A3EA0 50%, #5B8FF9 100%);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 19px; position: relative; z-index: 2;
    box-shadow: 0 6px 24px rgba(91,143,249,0.4), inset 0 1px 0 rgba(255,255,255,0.15);
}
.sb-orb-core::after {
    content:''; position:absolute; inset:0; border-radius:12px;
    background: linear-gradient(135deg, rgba(255,255,255,0.14) 0%, transparent 55%);
}
.sb-dot {
    position:absolute; border-radius:50%;
    width:5px; height:5px; top:50%; left:50%; margin:-2.5px 0 0 -2.5px;
}
.sb-dot-1{ background:#5B8FF9; animation:orbitA 3s linear infinite; }
.sb-dot-2{ background:#F97B8B; animation:orbitB 4s linear infinite; }
.sb-dot-3{ background:#5BF9C4; animation:orbitC 2.6s linear infinite; }

.sb-brand {
    font-size: 1.25rem; font-weight: 800; letter-spacing: -0.02em;
    background: linear-gradient(90deg, #DDE6FF 0%, #5B8FF9 40%, #DDE6FF 100%);
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: shimmer 4s linear infinite;
    margin-bottom: 3px;
}
.sb-tagline {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem; color: #2E3D5C;
    letter-spacing: 0.14em; text-transform: uppercase;
}

.sb-section {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem; font-weight: 500;
    color: #2E3D5C; letter-spacing: 0.22em; text-transform: uppercase;
    padding: 0 20px; margin: 18px 0 8px;
}

.agent-row {
    display: flex; align-items: center; gap: 11px;
    margin: 0 12px 5px; padding: 9px 10px;
    border-radius: 10px; transition: all 0.18s; cursor: default;
}
.agent-row:hover { transform: translateX(3px); }
.agent-badge {
    width: 28px; height: 28px; border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; flex-shrink: 0;
}
.agent-name-text { font-size: 0.8rem; font-weight: 600; color: #DDE6FF; margin-bottom: 2px; }
.agent-sub-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
}

.sb-divider {
    height: 1px; background: rgba(255,255,255,0.05);
    margin: 18px 20px;
}
</style>

<div class="sb-wrap">
  <div class="sb-top">
    <div class="sb-orb-wrap">
      <div class="sb-orb-core">⚡</div>
      <div class="sb-dot sb-dot-1"></div>
      <div class="sb-dot sb-dot-2"></div>
      <div class="sb-dot sb-dot-3"></div>
    </div>
    <div class="sb-brand">Cortex</div>
    <div class="sb-tagline">Intelligence · Debate · Clarity</div>
  </div>

  <div class="sb-section">Agents Online</div>

  <div class="agent-row" style="background:rgba(91,143,249,0.07);border:1px solid rgba(91,143,249,0.18);">
    <div class="agent-badge" style="background:rgba(91,143,249,0.15);border:1px solid rgba(91,143,249,0.25);">🏛️</div>
    <div>
      <div class="agent-name-text">The Architect</div>
      <div class="agent-sub-text" style="color:#5B8FF9;">Logic · Structure</div>
    </div>
  </div>
  <div class="agent-row" style="background:rgba(249,123,139,0.07);border:1px solid rgba(249,123,139,0.18);">
    <div class="agent-badge" style="background:rgba(249,123,139,0.15);border:1px solid rgba(249,123,139,0.25);">💗</div>
    <div>
      <div class="agent-name-text">The Soul</div>
      <div class="agent-sub-text" style="color:#F97B8B;">Empathy · Culture</div>
    </div>
  </div>
  <div class="agent-row" style="background:rgba(91,249,196,0.07);border:1px solid rgba(91,249,196,0.18);">
    <div class="agent-badge" style="background:rgba(91,249,196,0.15);border:1px solid rgba(91,249,196,0.25);">🛡️</div>
    <div>
      <div class="agent-name-text">The Filter</div>
      <div class="agent-sub-text" style="color:#5BF9C4;">Risk · Dissent</div>
    </div>
  </div>

  <div class="sb-divider"></div>
  <div class="sb-section">How It Works</div>

  <div style="padding: 0 20px; margin-bottom: 16px;">
    <div style="display:flex;gap:10px;margin-bottom:10px;align-items:flex-start;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#5B8FF9;margin-top:1px;flex-shrink:0;">01</div>
      <div style="font-size:0.75rem;color:#6A7A9B;line-height:1.5;">Ask any question or describe a decision</div>
    </div>
    <div style="display:flex;gap:10px;margin-bottom:10px;align-items:flex-start;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#F97B8B;margin-top:1px;flex-shrink:0;">02</div>
      <div style="font-size:0.75rem;color:#6A7A9B;line-height:1.5;">3 agents analyse from different lenses</div>
    </div>
    <div style="display:flex;gap:10px;margin-bottom:10px;align-items:flex-start;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#5BF9C4;margin-top:1px;flex-shrink:0;">03</div>
      <div style="font-size:0.75rem;color:#6A7A9B;line-height:1.5;">They debate — agreeing, pushing back, refining</div>
    </div>
    <div style="display:flex;gap:10px;align-items:flex-start;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#F9D45B;margin-top:1px;flex-shrink:0;">04</div>
      <div style="font-size:0.75rem;color:#6A7A9B;line-height:1.5;">One clear verdict delivered to you</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    if st.button("＋  New Session", key="new_chat_btn"):
        _new_chat()
        st.rerun()

    st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;
     color:#2E3D5C;letter-spacing:0.22em;text-transform:uppercase;
     padding:0 20px;margin:16px 0 8px;">
  Sessions
</div>
""", unsafe_allow_html=True)

    for cid in st.session_state.chat_order:
        chat = st.session_state.chats[cid]
        is_active = cid == st.session_state.active_chat
        label = ("▶  " if is_active else "·  ") + chat["name"]
        if st.button(label, key=f"nav_{cid}"):
            st.session_state.active_chat = cid
            st.rerun()


# ─── MAIN LAYOUT ──────────────────────────────────────────────────────────────
active = st.session_state.chats[st.session_state.active_chat]

# Top nav bar
st.markdown(f"""
<style>
@keyframes blink {{
  0%,100%{{ opacity:1; }} 50%{{ opacity:0.3; }}
}}
.topbar {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 36px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    background: rgba(9,13,24,0.95);
    backdrop-filter: blur(12px);
    position: sticky; top: 0; z-index: 100;
}}
.topbar-left {{
    display: flex; align-items: center; gap: 16px;
}}
.topbar-logo {{
    font-family: 'Outfit', sans-serif;
    font-size: 1.1rem; font-weight: 800; letter-spacing: -0.02em;
    background: linear-gradient(90deg, #DDE6FF, #5B8FF9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.topbar-sep {{
    width: 1px; height: 20px; background: rgba(255,255,255,0.08);
}}
.topbar-session {{
    font-size: 0.82rem; font-weight: 500; color: #6A7A9B;
}}
.topbar-right {{
    display: flex; align-items: center; gap: 20px;
}}
.status-pill {{
    display: flex; align-items: center; gap: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; color: #5BF9C4; letter-spacing: 0.08em;
}}
.status-dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: #5BF9C4;
    animation: blink 2s ease-in-out infinite;
    box-shadow: 0 0 8px #5BF9C4;
}}
.topbar-stat {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; color: #2E3D5C;
}}
.topbar-stat span {{ color: #6A7A9B; }}
</style>
<div class="topbar">
  <div class="topbar-left">
    <div class="topbar-logo">⚡ Cortex</div>
    <div class="topbar-sep"></div>
    <div class="topbar-session">{active['name']}</div>
  </div>
  <div class="topbar-right">
    <div class="topbar-stat">exchanges <span>{len(active['messages'])//2}</span></div>
    <div class="topbar-stat">agents <span>3</span></div>
    <div class="status-pill">
      <div class="status-dot"></div>
      3 agents online
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── MAIN CONTENT AREA ────────────────────────────────────────────────────────
st.markdown("""
<style>
.main-wrap {
    display: grid;
    grid-template-columns: 1fr 420px;
    gap: 0;
    height: calc(100vh - 60px);
    overflow: hidden;
}
.center-stage {
    padding: 32px 36px;
    overflow-y: auto;
    border-right: 1px solid rgba(255,255,255,0.05);
}
.chat-panel {
    padding: 24px 24px 16px;
    display: flex; flex-direction: column;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

col_stage, col_chat = st.columns([1.6, 1], gap="small")

# ══════════════════════════════════════════════════════════════════════════════
# CENTER STAGE — debate arena
# ══════════════════════════════════════════════════════════════════════════════
with col_stage:
    st.markdown("""
<style>
@keyframes fadeUp    { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
@keyframes pulseGlow { 0%,100%{opacity:.5;transform:scale(1)} 50%{opacity:1;transform:scale(1.04)} }
@keyframes scanline  { from{transform:translateY(-100%)} to{transform:translateY(100vh)} }
@keyframes ringPulse { 0%{opacity:.7;transform:scale(.9)} 100%{opacity:0;transform:scale(1.6)} }
@keyframes typing    { from{width:0} to{width:100%} }
@keyframes cursorBlink { 0%,100%{opacity:1} 50%{opacity:0} }
@keyframes floatCard {
    0%,100%{ transform:perspective(800px) rotateX(1deg) rotateY(0deg) translateY(0); }
    33%    { transform:perspective(800px) rotateX(-1deg) rotateY(2deg) translateY(-4px); }
    66%    { transform:perspective(800px) rotateX(2deg) rotateY(-1.5deg) translateY(-2px); }
}
@keyframes nodePulse {
    0%,100%{ transform:scale(1); filter:drop-shadow(0 0 6px currentColor); }
    50%    { transform:scale(1.08); filter:drop-shadow(0 0 14px currentColor); }
}
@keyframes lineFlow {
    0%{ stroke-dashoffset:60 }
    100%{ stroke-dashoffset:0 }
}
@keyframes debateSlide {
    from{ opacity:0; transform:translateX(-12px); }
    to  { opacity:1; transform:translateX(0); }
}

/* ── Empty state: neural arena ── */
.arena-wrap {
    position: relative; text-align: center;
    padding: 48px 24px 36px;
    animation: fadeUp 0.6s ease;
}
.arena-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; letter-spacing: 0.25em; text-transform: uppercase;
    color: #2E3D5C; margin-bottom: 10px;
}
.arena-title {
    font-size: 2.8rem; font-weight: 800; letter-spacing: -0.04em; line-height: 1;
    color: #DDE6FF; margin-bottom: 8px;
}
.arena-title .g {
    background: linear-gradient(90deg, #5B8FF9 0%, #8AB5FF 40%, #5BF9C4 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.arena-sub {
    font-size: 0.9rem; color: #6A7A9B; line-height: 1.65;
    max-width: 480px; margin: 0 auto 36px;
}

/* SVG neural graph */
.neural-svg-wrap {
    position: relative; display: inline-block;
    width: 400px; height: 260px; margin: 0 auto 36px;
}

/* Prompt chips */
.prompt-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 8px; max-width: 520px; margin: 0 auto;
}
.prompt-chip {
    background: rgba(13,18,32,0.9);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 13px 16px;
    text-align: left; cursor: pointer;
    transition: all 0.2s;
    font-size: 0.78rem; color: #6A7A9B; line-height: 1.4;
}
.prompt-chip:hover {
    border-color: rgba(91,143,249,0.35);
    color: #DDE6FF;
    background: rgba(91,143,249,0.06);
    transform: translateY(-2px);
}
.prompt-chip-icon {
    font-size: 1rem; margin-bottom: 6px; display: block;
}

/* ── Result cards ── */
.result-section { margin-bottom: 28px; animation: fadeUp 0.5s ease; }

.result-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 18px; padding-bottom: 14px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.result-header-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; letter-spacing: 0.2em; text-transform: uppercase;
    color: #2E3D5C;
}
.result-header-q {
    font-size: 1.05rem; font-weight: 600; color: #DDE6FF;
    margin-bottom: 4px; line-height: 1.35;
}
.result-q-wrap { margin-bottom: 28px; }

.agent-view-card {
    border-radius: 14px; padding: 20px 22px;
    margin-bottom: 12px;
    transition: transform 0.2s;
    transform-style: preserve-3d;
    animation: floatCard 8s ease-in-out infinite;
}
.agent-view-card:nth-child(2) { animation-delay: 2.5s; }
.agent-view-card:nth-child(3) { animation-delay: 5s; }
.agent-view-card:hover {
    animation: none;
    transform: perspective(700px) rotateX(2deg) rotateY(4deg) translateY(-3px) !important;
}
.agent-view-top {
    display: flex; align-items: center; gap: 10px; margin-bottom: 12px;
}
.agent-view-icon {
    width: 32px; height: 32px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center; font-size: 15px;
    flex-shrink: 0;
}
.agent-view-name {
    font-size: 0.88rem; font-weight: 700; margin-bottom: 2px;
}
.agent-view-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; opacity: 0.6;
}
.agent-view-text {
    font-size: 0.86rem; color: #DDE6FF; line-height: 1.7;
}

/* Debate arena */
.debate-arena {
    background: rgba(9,13,24,0.8);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px; padding: 28px 28px 24px;
    margin-bottom: 20px; position: relative; overflow: hidden;
}
.debate-arena::before {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background: linear-gradient(90deg, transparent, rgba(91,143,249,0.5), rgba(91,249,196,0.3), transparent);
}
.debate-arena-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem; letter-spacing: 0.24em; text-transform: uppercase;
    color: #2E3D5C; margin-bottom: 18px;
    display: flex; align-items: center; gap: 8px;
}
.debate-arena-label::before {
    content:''; display:inline-block; width:6px; height:6px; border-radius:50%;
    background: #5BF9C4; box-shadow: 0 0 8px #5BF9C4;
    animation: blink 2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

.debate-line {
    display: flex; gap: 12px; margin-bottom: 14px;
    animation: debateSlide 0.4s ease;
}
.debate-line:nth-child(2){ animation-delay:.1s; }
.debate-line:nth-child(3){ animation-delay:.2s; }
.debate-line:nth-child(4){ animation-delay:.3s; }
.debate-speaker-badge {
    flex-shrink: 0; padding: 3px 9px; border-radius: 99px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem; font-weight: 500;
    align-self: flex-start; margin-top: 2px; white-space: nowrap;
}
.debate-line-text {
    font-size: 0.84rem; color: #8A9ABB; line-height: 1.65;
}

/* Final verdict */
.verdict-card {
    border-radius: 16px; padding: 26px 28px;
    position: relative; overflow: hidden;
    background: linear-gradient(135deg, #0A1428 0%, #0E1C38 100%);
    border: 1px solid rgba(249,212,91,0.2);
}
.verdict-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg, #F9D45B, #F9A85B, #F97B8B);
}
.verdict-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem; letter-spacing: 0.22em; text-transform: uppercase;
    color: #F9D45B; margin-bottom: 12px;
    display: flex; align-items: center; gap: 8px;
}
.verdict-label::before {
    content: '🎯';
}
.verdict-text {
    font-size: 0.95rem; font-weight: 500; color: #DDE6FF; line-height: 1.72;
}
</style>
""", unsafe_allow_html=True)

    results = active.get("results", [])

    if not results:
        # ── EMPTY STATE: Neural arena ─────────────────────────────────────
        st.markdown("""
<div class="arena-wrap">
  <div class="arena-eyebrow">Multi-Agent Reasoning System</div>
  <div class="arena-title">Where <span class="g">intelligence</span><br>debates itself</div>
  <p class="arena-sub">
    Three minds. One question. No filter. Cortex puts your ideas through
    a rigorous debate between logic, empathy, and scepticism — then delivers
    a clear, battle-tested verdict.
  </p>

  <!-- Animated Neural Graph -->
  <div class="neural-svg-wrap">
    <svg viewBox="0 0 400 260" fill="none" xmlns="http://www.w3.org/2000/svg"
         style="width:100%;height:100%;">
      <defs>
        <filter id="gBlue"><feGaussianBlur stdDeviation="5" result="b"/>
          <feComposite in="b" in2="SourceGraphic" operator="over"/></filter>
        <filter id="gPink"><feGaussianBlur stdDeviation="4" result="b"/>
          <feComposite in="b" in2="SourceGraphic" operator="over"/></filter>
        <filter id="gTeal"><feGaussianBlur stdDeviation="4" result="b"/>
          <feComposite in="b" in2="SourceGraphic" operator="over"/></filter>
      </defs>

      <!-- Connection lines -->
      <path d="M200 80 L120 190" stroke="rgba(91,143,249,0.25)" stroke-width="1.5"
            stroke-dasharray="5 4">
        <animate attributeName="stroke-dashoffset" from="36" to="0" dur="2s" repeatCount="indefinite"/>
      </path>
      <path d="M200 80 L280 190" stroke="rgba(249,123,139,0.25)" stroke-width="1.5"
            stroke-dasharray="5 4">
        <animate attributeName="stroke-dashoffset" from="36" to="0" dur="2.4s" repeatCount="indefinite"/>
      </path>
      <path d="M120 190 L280 190" stroke="rgba(91,249,196,0.2)" stroke-width="1.5"
            stroke-dasharray="4 5">
        <animate attributeName="stroke-dashoffset" from="0" to="36" dur="3s" repeatCount="indefinite"/>
      </path>

      <!-- Glow backing -->
      <circle cx="200" cy="80"  r="22" fill="rgba(91,143,249,0.10)" filter="url(#gBlue)"/>
      <circle cx="120" cy="190" r="18" fill="rgba(249,123,139,0.10)" filter="url(#gPink)"/>
      <circle cx="280" cy="190" r="18" fill="rgba(91,249,196,0.10)"  filter="url(#gTeal)"/>

      <!-- Pulse rings -->
      <circle cx="200" cy="80" r="28" stroke="rgba(91,143,249,0.3)" stroke-width="1" fill="none">
        <animate attributeName="r" from="24" to="44" dur="2.5s" repeatCount="indefinite"/>
        <animate attributeName="opacity" from="0.6" to="0" dur="2.5s" repeatCount="indefinite"/>
      </circle>
      <circle cx="120" cy="190" r="22" stroke="rgba(249,123,139,0.3)" stroke-width="1" fill="none">
        <animate attributeName="r" from="20" to="36" dur="3s" begin="0.8s" repeatCount="indefinite"/>
        <animate attributeName="opacity" from="0.5" to="0" dur="3s" begin="0.8s" repeatCount="indefinite"/>
      </circle>
      <circle cx="280" cy="190" r="22" stroke="rgba(91,249,196,0.3)" stroke-width="1" fill="none">
        <animate attributeName="r" from="20" to="36" dur="2.8s" begin="1.4s" repeatCount="indefinite"/>
        <animate attributeName="opacity" from="0.5" to="0" dur="2.8s" begin="1.4s" repeatCount="indefinite"/>
      </circle>

      <!-- Node cores -->
      <circle cx="200" cy="80"  r="22" fill="#0D1828" stroke="rgba(91,143,249,0.6)"  stroke-width="1.5"/>
      <circle cx="120" cy="190" r="18" fill="#0D1828" stroke="rgba(249,123,139,0.6)" stroke-width="1.5"/>
      <circle cx="280" cy="190" r="18" fill="#0D1828" stroke="rgba(91,249,196,0.6)"  stroke-width="1.5"/>

      <!-- Node icons -->
      <text x="200" y="85" text-anchor="middle" dominant-baseline="middle"
            font-size="16" style="font-family:sans-serif;">🏛️</text>
      <text x="120" y="195" text-anchor="middle" dominant-baseline="middle"
            font-size="14" style="font-family:sans-serif;">💗</text>
      <text x="280" y="195" text-anchor="middle" dominant-baseline="middle"
            font-size="14" style="font-family:sans-serif;">🛡️</text>

      <!-- Travel dots -->
      <circle r="4" fill="#5B8FF9" filter="url(#gBlue)">
        <animateMotion dur="2.2s" repeatCount="indefinite" path="M200,80 L120,190"/>
      </circle>
      <circle r="4" fill="#F97B8B" filter="url(#gPink)">
        <animateMotion dur="2.8s" repeatCount="indefinite" begin="0.5s" path="M200,80 L280,190"/>
      </circle>
      <circle r="3.5" fill="#5BF9C4" filter="url(#gTeal)">
        <animateMotion dur="3.2s" repeatCount="indefinite" begin="1s" path="M120,190 L280,190"/>
      </circle>

      <!-- Labels -->
      <text x="200" y="50" text-anchor="middle" fill="rgba(91,143,249,0.7)"
            font-size="9" font-family="JetBrains Mono, monospace" letter-spacing="2">ARCHITECT</text>
      <text x="80" y="220" text-anchor="middle" fill="rgba(249,123,139,0.7)"
            font-size="9" font-family="JetBrains Mono, monospace" letter-spacing="2">SOUL</text>
      <text x="318" y="220" text-anchor="middle" fill="rgba(91,249,196,0.7)"
            font-size="9" font-family="JetBrains Mono, monospace" letter-spacing="2">FILTER</text>

      <!-- Center spark -->
      <circle cx="200" cy="140" r="5" fill="#F9D45B" opacity="0.6">
        <animate attributeName="r" values="3;7;3" dur="2s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.4;0.9;0.4" dur="2s" repeatCount="indefinite"/>
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
""", unsafe_allow_html=True)

    else:
        # ── RESULTS STATE ─────────────────────────────────────────────────
        for i, result in enumerate(results):
            q = result["question"]
            views = result["views"]
            debate_raw = result["debate"]
            final = result["final"]

            # Question header
            st.markdown(f"""
<div class="result-q-wrap">
  <div class="result-header-label">Question {i+1}</div>
  <div class="result-header-q">{q}</div>
</div>
""", unsafe_allow_html=True)

            # Agent view cards
            agent_colors = {
                "Architect": ("#5B8FF9", "rgba(91,143,249,0.08)", "rgba(91,143,249,0.2)", "🏛️", "Logic · Structure"),
                "Soul":      ("#F97B8B", "rgba(249,123,139,0.08)", "rgba(249,123,139,0.2)", "💗", "Empathy · Culture"),
                "Filter":    ("#5BF9C4", "rgba(91,249,196,0.08)", "rgba(91,249,196,0.2)", "🛡️", "Risk · Dissent"),
            }
            for agent in AGENTS:
                nm = agent["name"]
                c, bg, bd, em, tg = agent_colors[nm]
                txt = views.get(nm, "")
                st.markdown(f"""
<div class="agent-view-card" style="background:{bg};border:1px solid {bd};">
  <div class="agent-view-top">
    <div class="agent-view-icon" style="background:rgba(0,0,0,0.3);border:1px solid {bd};">{em}</div>
    <div>
      <div class="agent-view-name" style="color:{c};">{agent['full']}</div>
      <div class="agent-view-tag" style="color:{c};">{tg}</div>
    </div>
  </div>
  <div class="agent-view-text">{txt}</div>
</div>
""", unsafe_allow_html=True)

            # Debate arena
            lines = [l.strip() for l in debate_raw.split("\n") if l.strip()]
            debate_html = ""
            speaker_cfg = {
                "architect": ("#5B8FF9", "rgba(91,143,249,0.15)"),
                "soul":      ("#F97B8B", "rgba(249,123,139,0.15)"),
                "filter":    ("#5BF9C4", "rgba(91,249,196,0.15)"),
            }
            for line in lines:
                lower = line.lower()
                badge_html = ""
                text = line
                for key, (c, bg) in speaker_cfg.items():
                    if lower.startswith(key + ":"):
                        name = key.capitalize()
                        text = line[len(key)+1:].strip()
                        badge_html = f'<span class="debate-speaker-badge" style="color:{c};background:{bg};border:1px solid {c}33;">{name}</span>'
                        break
                if not badge_html:
                    if ":" in line[:20]:
                        parts = line.split(":", 1)
                        nm = parts[0].strip()
                        text = parts[1].strip()
                        badge_html = f'<span class="debate-speaker-badge" style="color:#6A7A9B;background:rgba(106,122,155,0.1);border:1px solid rgba(106,122,155,0.2);">{nm}</span>'
                    else:
                        badge_html = ""
                debate_html += f"""
<div class="debate-line">
  {badge_html}
  <div class="debate-line-text">{text}</div>
</div>"""

            st.markdown(f"""
<div class="debate-arena">
  <div class="debate-arena-label">Live Debate</div>
  {debate_html}
</div>
""", unsafe_allow_html=True)

            # Verdict
            st.markdown(f"""
<div class="verdict-card">
  <div class="verdict-label">Final Verdict</div>
  <div class="verdict-text">{final}</div>
</div>
""", unsafe_allow_html=True)

            if i < len(results) - 1:
                st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.05);margin:32px 0;'>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# RIGHT PANEL — chat
# ══════════════════════════════════════════════════════════════════════════════
with col_chat:
    st.markdown("""
<style>
.chat-panel-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; letter-spacing: 0.2em; text-transform: uppercase;
    color: #2E3D5C; margin-bottom: 16px;
    display: flex; align-items: center; gap: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 14px;
}
.chat-panel-header::before {
    content: ''; width: 6px; height: 6px; border-radius: 50%;
    background: #5B8FF9; box-shadow: 0 0 8px #5B8FF9;
    display: inline-block;
}
</style>
<div class="chat-panel-header">Neural Chat Interface</div>
""", unsafe_allow_html=True)

    msg_box = st.container(height=520)
    with msg_box:
        if not active["messages"]:
            st.markdown("""
<div style="text-align:center;padding:40px 20px;">
  <div style="font-size:2rem;margin-bottom:12px;opacity:.4;">⚡</div>
  <div style="font-size:0.82rem;color:#2E3D5C;line-height:1.7;">
    Type your question below.<br>
    The agents will debate it and deliver a verdict.
  </div>
</div>
""", unsafe_allow_html=True)
        for msg in active["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Ask Cortex anything…"):
        active["messages"].append({"role": "user", "content": prompt})
        with msg_box:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Thinking state
        with msg_box:
            with st.chat_message("assistant"):
                with st.spinner("Agents are debating…"):
                    result = generate_response(prompt, active["messages"])

                # Format chat response (compact)
                chat_resp = ""
                for agent in AGENTS:
                    nm = agent["name"]
                    chat_resp += f"### {agent['emoji']} {agent['full']}\n{result['views'].get(nm, '')}\n\n"
                chat_resp += f"### 🎯 Verdict\n{result['final']}"
                st.markdown(chat_resp)

        active["messages"].append({"role": "assistant", "content": chat_resp})

        # Store full result for center stage
        if "results" not in active:
            active["results"] = []
        active["results"].append({
            "question": prompt,
            "views":    result["views"],
            "debate":   result["debate"],
            "final":    result["final"],
        })

        st.rerun()