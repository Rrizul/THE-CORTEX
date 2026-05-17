import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="Cortex",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL = "llama-3.1-8b-instant"

AGENTS = [
    {
        "icon": "🏛️",
        "name": "The Architect",
        "tagline": "Logic & Structure",
        "color": "#4F8EF7",
        "bg": "rgba(79,142,247,0.08)",
        "border": "rgba(79,142,247,0.25)",
        "persona": "Focus on structural integrity. Map nth-order consequences. Ensure airtight logic and sound systemic reactions.",
    },
    {
        "icon": "💖",
        "name": "The Soul",
        "tagline": "Human & Emotion",
        "color": "#F77F9F",
        "bg": "rgba(247,127,159,0.08)",
        "border": "rgba(247,127,159,0.25)",
        "persona": "Focus on human resonance. Use EQ and theory of mind. Predict social fallout and cultural impact.",
    },
    {
        "icon": "🛡️",
        "name": "The Filter",
        "tagline": "Risk & Critique",
        "color": "#4FD9A0",
        "bg": "rgba(79,217,160,0.08)",
        "border": "rgba(79,217,160,0.25)",
        "persona": "Focus on vulnerability detection. Challenge groupthink. Hunt black swan risks and hidden failure points.",
    },
]

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

:root {
    --bg:        #080C14;
    --surface:   #0F1520;
    --card:      #121A2A;
    --border:    rgba(255,255,255,0.07);
    --border2:   rgba(255,255,255,0.12);
    --text:      #E8EEFF;
    --muted:     #4E5A72;
    --dim:       #2A3348;
    --blue:      #4F8EF7;
    --pink:      #F77F9F;
    --green:     #4FD9A0;
    --yellow:    #F7C94F;
    --font:      'Space Grotesk', sans-serif;
    --mono:      'Space Mono', monospace;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { font-family: var(--font) !important; }

.stButton > button {
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
    font-family: var(--mono) !important;
    font-size: 0.76rem !important;
    padding: 0.45rem 0.9rem !important;
    transition: all 0.2s !important;
    width: 100% !important;
    text-align: left !important;
    letter-spacing: 0.02em !important;
}
.stButton > button:hover {
    border-color: var(--blue) !important;
    color: var(--blue) !important;
    background: rgba(79,142,247,0.08) !important;
    transform: translateX(3px) !important;
}

[data-testid="stChatInputContainer"] {
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 12px !important;
    box-shadow: 0 0 30px rgba(79,142,247,0.06) !important;
}
[data-testid="stChatInputContainer"] textarea {
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 0.95rem !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder { color: var(--muted) !important; }

[data-testid="stChatMessage"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    margin-bottom: 10px !important;
}

[data-testid="stMarkdown"] p { color: var(--text) !important; font-size: 0.9rem !important; line-height: 1.65 !important; }
[data-testid="stMarkdown"] h3 {
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    margin: 20px 0 6px !important;
    padding-bottom: 6px !important;
    border-bottom: 1px solid var(--border) !important;
    font-family: var(--mono) !important;
}

.block-container { padding: 0 2rem 2rem !important; max-width: 100% !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--dim); border-radius: 4px; }
.stSpinner > div { border-top-color: var(--blue) !important; }
</style>
""", unsafe_allow_html=True)


# ── GROQ CLIENT ────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])


def call_llm(prompt: str, tokens: int = 200) -> str:
    try:
        resp = get_client().chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=tokens,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip().replace("**", "")
    except Exception as e:
        return f"Error: {e}"


def get_context(messages):
    lines = []
    for m in messages[-6:]:
        who = "User" if m["role"] == "user" else "Cortex"
        lines.append(f"{who}: {m['content'][:200]}")
    return "\n".join(lines)


def generate_cortex_response(user_input: str, history: list) -> str:
    context = get_context(history)
    views = {}

    for agent in AGENTS:
        prompt = f"""You are {agent['name']}.
{agent['persona']}

Conversation context:
{context}

User says: {user_input}

Give your perspective in 3 concise sentences."""
        if views:
            prompt += f"\n\nOther views so far:\n{views}"
        views[agent["name"]] = call_llm(prompt, 180)

    debate = call_llm(f"""User input: {user_input}

Agent views:
{views}

Write a short internal debate (2-3 exchanges) where they agree, challenge, or refine each other.""", 220)

    final = call_llm(f"""User input: {user_input}

Views:
{views}

Debate:
{debate}

Give a single, practical final conclusion in 2-3 sentences.""", 180)

    parts = []
    for agent in AGENTS:
        parts.append(f"### {agent['icon']} {agent['name']} — {agent['tagline']}\n{views[agent['name']]}")
    parts.append(f"### 🎯 Final Conclusion\n{final}")
    return "\n\n".join(parts)


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
    st.session_state.chats[cid] = {"name": f"Analysis {st.session_state.chat_count}", "messages": []}
    st.session_state.chat_order.insert(0, cid)
    st.session_state.active_chat = cid

init_state()

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <style>
    @keyframes float {
        0%,100% { transform: perspective(300px) translateY(0px) rotateY(0deg); }
        50%      { transform: perspective(300px) translateY(-6px) rotateY(10deg); }
    }
    @keyframes pulse-ring {
        0%   { box-shadow: 0 0 0 0 rgba(79,142,247,0.45); }
        70%  { box-shadow: 0 0 0 14px rgba(79,142,247,0); }
        100% { box-shadow: 0 0 0 0 rgba(79,142,247,0); }
    }
    @keyframes shimmer {
        0%   { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    .sb-logo-wrap {
        padding: 28px 20px 22px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 18px;
    }
    .sb-icon {
        width: 50px; height: 50px;
        background: linear-gradient(135deg, #1A3A8A 0%, #2A5FD4 60%, #4F8EF7 100%);
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 24px; margin-bottom: 14px;
        animation: float 4s ease-in-out infinite, pulse-ring 2.5s ease-out infinite;
        transform-style: preserve-3d;
    }
    .sb-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.3rem; font-weight: 700;
        background: linear-gradient(90deg, #E8EEFF 0%, #4F8EF7 50%, #E8EEFF 100%);
        background-size: 200% auto;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: shimmer 4s linear infinite;
        margin: 0 0 3px; letter-spacing: -0.01em;
    }
    .sb-sub {
        font-family: 'Space Mono', monospace;
        font-size: 0.62rem; color: #4E5A72;
        letter-spacing: 0.12em; text-transform: uppercase; margin: 0;
    }
    .sb-label {
        font-family: 'Space Mono', monospace;
        font-size: 0.6rem; font-weight: 700;
        color: #2A3348; letter-spacing: 0.2em; text-transform: uppercase;
        margin: 20px 0 10px; padding-left: 2px;
    }
    .agent-chip {
        display: flex; align-items: center; gap: 10px;
        padding: 10px 12px; border-radius: 10px; margin-bottom: 6px;
        transition: transform 0.2s;
    }
    .agent-chip:hover { transform: translateX(3px); }
    .agent-chip-icon {
        width: 30px; height: 30px; border-radius: 8px;
        display: flex; align-items: center; justify-content: center; font-size: 14px;
    }
    .agent-chip-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.8rem; font-weight: 600; color: #E8EEFF; margin: 0 0 1px;
    }
    .agent-chip-tag {
        font-family: 'Space Mono', monospace;
        font-size: 0.62rem; margin: 0;
    }
    </style>

    <div class="sb-logo-wrap">
        <div class="sb-icon">⚡</div>
        <p class="sb-title">Cortex</p>
        <p class="sb-sub">Multi-Agent Reasoning</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("＋  New Analysis"):
        _new_chat()
        st.rerun()

    st.markdown('<div class="sb-label">History</div>', unsafe_allow_html=True)
    for cid in st.session_state.chat_order:
        chat = st.session_state.chats[cid]
        marker = "▶  " if cid == st.session_state.active_chat else "   "
        if st.button(f"{marker}{chat['name']}", key=f"nav_{cid}"):
            st.session_state.active_chat = cid
            st.rerun()

    st.markdown('<div class="sb-label" style="margin-top:24px">Active Agents</div>', unsafe_allow_html=True)
    for agent in AGENTS:
        st.markdown(f"""
        <div class="agent-chip" style="background:{agent['bg']};border:1px solid {agent['border']};">
            <div class="agent-chip-icon" style="background:{agent['bg']};border:1px solid {agent['border']};">
                {agent['icon']}
            </div>
            <div>
                <p class="agent-chip-name">{agent['name']}</p>
                <p class="agent-chip-tag" style="color:{agent['color']};">{agent['tagline']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── MAIN ───────────────────────────────────────────────────────────────────────
active = st.session_state.chats[st.session_state.active_chat]

# ── HERO BANNER ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@keyframes orbit  { from{transform:rotate(0deg)   translateX(30px) rotate(0deg)}   to{transform:rotate(360deg)  translateX(30px) rotate(-360deg)}  }
@keyframes orbit2 { from{transform:rotate(120deg) translateX(24px) rotate(-120deg)} to{transform:rotate(480deg) translateX(24px) rotate(-480deg)} }
@keyframes orbit3 { from{transform:rotate(240deg) translateX(19px) rotate(-240deg)} to{transform:rotate(600deg) translateX(19px) rotate(-600deg)} }
@keyframes hero-pulse { 0%,100%{opacity:.4;transform:scale(1)} 50%{opacity:.7;transform:scale(1.08)} }
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }

.hero {
    position: relative; overflow: hidden;
    background: linear-gradient(135deg, #090F20 0%, #0D1830 60%, #090F20 100%);
    border: 1px solid rgba(79,142,247,0.18);
    border-radius: 20px;
    padding: 38px 44px 34px;
    margin-bottom: 26px;
    display: flex; align-items: center; gap: 44px;
    animation: fadeUp 0.5s ease;
}
.hero::before {
    content:''; position:absolute; top:-50%; right:-5%;
    width:380px; height:380px; border-radius:50%;
    background: radial-gradient(ellipse, rgba(79,142,247,0.12) 0%, transparent 70%);
    animation: hero-pulse 5s ease-in-out infinite; pointer-events:none;
}
.hero::after {
    content:''; position:absolute; bottom:-60%; left:5%;
    width:280px; height:280px; border-radius:50%;
    background: radial-gradient(ellipse, rgba(79,217,160,0.06) 0%, transparent 70%);
    animation: hero-pulse 6s ease-in-out infinite reverse; pointer-events:none;
}

.hero-orb {
    position:relative; flex-shrink:0;
    width:88px; height:88px;
    display:flex; align-items:center; justify-content:center;
}
.hero-orb-core {
    width:60px; height:60px;
    background: linear-gradient(135deg, #162A70, #234FBC, #4F8EF7);
    border-radius:18px; font-size:28px;
    display:flex; align-items:center; justify-content:center;
    transform: rotate(-8deg);
    box-shadow: 0 10px 40px rgba(79,142,247,0.40), inset 0 1px 0 rgba(255,255,255,0.18);
    position:relative; z-index:2;
}
.orb-dot {
    position:absolute; border-radius:50%;
    width:8px; height:8px; top:50%; left:50%; margin:-4px 0 0 -4px;
}
.orb-dot-1 { background:#4F8EF7; box-shadow:0 0 8px #4F8EF7; animation: orbit  3.2s linear infinite; }
.orb-dot-2 { background:#F77F9F; box-shadow:0 0 8px #F77F9F; animation: orbit2 4.1s linear infinite; }
.orb-dot-3 { background:#4FD9A0; box-shadow:0 0 8px #4FD9A0; animation: orbit3 2.8s linear infinite; }

.hero-content {}
.hero-eyebrow {
    font-family:'Space Mono',monospace; font-size:0.64rem; font-weight:700;
    letter-spacing:0.2em; text-transform:uppercase;
    color:#2A3348; margin:0 0 10px;
}
.hero-h1 {
    font-family:'Space Grotesk',sans-serif;
    font-size:2rem; font-weight:700; letter-spacing:-0.03em; line-height:1.1;
    color:#E8EEFF; margin:0 0 8px;
}
.hero-h1 .accent {
    background: linear-gradient(90deg, #4F8EF7, #7EC8FF);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.hero-p {
    font-family:'Space Grotesk',sans-serif;
    font-size:0.9rem; color:#4E5A72; line-height:1.65;
    margin:0 0 20px; max-width:520px;
}
.hero-chips { display:flex; gap:8px; flex-wrap:wrap; }
.h-chip {
    font-family:'Space Mono',monospace; font-size:0.65rem;
    padding:4px 11px; border-radius:99px; letter-spacing:0.04em;
}
</style>

<div class="hero">
    <div class="hero-orb">
        <div class="hero-orb-core">⚡</div>
        <div class="orb-dot orb-dot-1"></div>
        <div class="orb-dot orb-dot-2"></div>
        <div class="orb-dot orb-dot-3"></div>
    </div>
    <div class="hero-content">
        <p class="hero-eyebrow">Multi-Agent AI Reasoning System</p>
        <h1 class="hero-h1">Think deeper with <span class="accent">Cortex</span></h1>
        <p class="hero-p">
            Three specialised AI agents debate your question from different angles —
            logical structure, human empathy, and critical risk — then converge on one clear, balanced answer.
        </p>
        <div class="hero-chips">
            <span class="h-chip" style="background:rgba(79,142,247,0.1);color:#4F8EF7;border:1px solid rgba(79,142,247,0.22);">🏛️ Architect</span>
            <span class="h-chip" style="background:rgba(247,127,159,0.1);color:#F77F9F;border:1px solid rgba(247,127,159,0.22);">💖 Soul</span>
            <span class="h-chip" style="background:rgba(79,217,160,0.1);color:#4FD9A0;border:1px solid rgba(79,217,160,0.22);">🛡️ Filter</span>
            <span class="h-chip" style="background:rgba(247,201,79,0.1);color:#F7C94F;border:1px solid rgba(247,201,79,0.22);">🎯 Final Verdict</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── HOW IT WORKS (empty state only) ───────────────────────────────────────────
if not active["messages"]:
    st.markdown("""
    <style>
    @keyframes card-hover-idle {
        0%,100% { transform: perspective(500px) rotateY(0deg) rotateX(0deg) translateY(0); }
        33%     { transform: perspective(500px) rotateY(5deg)  rotateX(2deg) translateY(-3px); }
        66%     { transform: perspective(500px) rotateY(-3deg) rotateX(-2deg) translateY(-5px); }
    }
    .section-label {
        font-family:'Space Mono',monospace; font-size:0.62rem; font-weight:700;
        color:#2A3348; letter-spacing:0.2em; text-transform:uppercase;
        margin:0 0 14px;
    }
    .how-grid {
        display:grid; grid-template-columns:repeat(4,1fr); gap:12px;
        margin-bottom:28px;
    }
    .how-card {
        background:#0F1520; border:1px solid rgba(255,255,255,0.07);
        border-radius:14px; padding:20px 16px; text-align:center;
        transition:border-color .25s, transform .3s;
        transform-style:preserve-3d;
        animation: card-hover-idle 8s ease-in-out infinite;
    }
    .how-card:nth-child(2) { animation-delay: 1s; }
    .how-card:nth-child(3) { animation-delay: 2s; }
    .how-card:nth-child(4) { animation-delay: 3s; }
    .how-card:hover {
        animation: none;
        transform: perspective(500px) rotateY(8deg) rotateX(4deg) translateY(-6px) !important;
        border-color: rgba(79,142,247,0.3) !important;
    }
    .how-num {
        font-family:'Space Mono',monospace; font-size:0.6rem;
        color:#2A3348; margin-bottom:10px; letter-spacing:.1em;
    }
    .how-icon { font-size:1.7rem; margin-bottom:10px; }
    .how-name {
        font-family:'Space Grotesk',sans-serif;
        font-size:0.85rem; font-weight:600; color:#E8EEFF; margin-bottom:5px;
    }
    .how-desc {
        font-family:'Space Grotesk',sans-serif;
        font-size:0.73rem; color:#4E5A72; line-height:1.5;
    }
    .try-row { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:32px; }
    .try-chip {
        font-family:'Space Grotesk',sans-serif; font-size:0.8rem;
        padding:9px 16px; border-radius:9px; cursor:pointer;
        background:#0F1520; border:1px solid rgba(255,255,255,0.08);
        color:#8896B3; transition:all .2s;
    }
    .try-chip:hover {
        border-color:rgba(79,142,247,0.4); color:#4F8EF7;
        background:rgba(79,142,247,0.06);
        transform:translateY(-2px);
    }
    </style>

    <p class="section-label">How it works</p>
    <div class="how-grid">
        <div class="how-card">
            <div class="how-num">step 01</div>
            <div class="how-icon">💬</div>
            <div class="how-name">You ask</div>
            <div class="how-desc">Type any question, dilemma, or topic you want explored</div>
        </div>
        <div class="how-card">
            <div class="how-num">step 02</div>
            <div class="how-icon">🧠</div>
            <div class="how-name">Agents analyse</div>
            <div class="how-desc">Each of the 3 agents responds from its own perspective</div>
        </div>
        <div class="how-card">
            <div class="how-num">step 03</div>
            <div class="how-icon">⚔️</div>
            <div class="how-name">They debate</div>
            <div class="how-desc">Agents challenge and refine each other's views</div>
        </div>
        <div class="how-card">
            <div class="how-num">step 04</div>
            <div class="how-icon">🎯</div>
            <div class="how-name">One verdict</div>
            <div class="how-desc">A clear, balanced conclusion is delivered to you</div>
        </div>
    </div>

    <p class="section-label">Try asking</p>
    <div class="try-row">
        <span class="try-chip">Should I quit my job to start a business?</span>
        <span class="try-chip">Is remote work better than office work?</span>
        <span class="try-chip">How do I handle a difficult coworker?</span>
        <span class="try-chip">What are risks of AI in hiring decisions?</span>
    </div>
    """, unsafe_allow_html=True)

# ── CHAT AREA HEADER ───────────────────────────────────────────────────────────
exchanges = len(active["messages"]) // 2
st.markdown(f"""
<style>
@keyframes ping {{
    0%  {{ box-shadow: 0 0 0 0 rgba(79,217,160,0.5); }}
    70% {{ box-shadow: 0 0 0 9px rgba(79,217,160,0); }}
    100%{{ box-shadow: 0 0 0 0 rgba(79,217,160,0); }}
}}
.chat-header {{
    display:flex; align-items:center; justify-content:space-between;
    margin-bottom:14px; padding-bottom:14px;
    border-bottom:1px solid rgba(255,255,255,0.06);
}}
.chat-title {{
    font-family:'Space Grotesk',sans-serif;
    font-size:1.05rem; font-weight:600; color:#E8EEFF;
    display:flex; align-items:center; gap:10px;
}}
.live-dot {{
    display:inline-block; width:7px; height:7px; border-radius:50%;
    background:#4FD9A0; animation: ping 1.8s ease-out infinite;
}}
.chat-meta {{
    font-family:'Space Mono',monospace; font-size:0.67rem; color:#2A3348;
}}
</style>
<div class="chat-header">
    <div class="chat-title">
        <span class="live-dot"></span>
        {active['name']}
    </div>
    <div class="chat-meta">{exchanges} exchange{"s" if exchanges != 1 else ""}</div>
</div>
""", unsafe_allow_html=True)

# ── MESSAGES ───────────────────────────────────────────────────────────────────
msg_box = st.container(height=420)
with msg_box:
    for msg in active["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ── INPUT ──────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask the Cortex anything — it thinks from every angle…"):
    active["messages"].append({"role": "user", "content": prompt})
    with msg_box:
        with st.chat_message("user"):
            st.markdown(prompt)
    with msg_box:
        with st.chat_message("assistant"):
            with st.spinner("Three agents are reasoning…"):
                response = generate_cortex_response(prompt, active["messages"])
            st.markdown(response)
    active["messages"].append({"role": "assistant", "content": response})
    st.rerun()