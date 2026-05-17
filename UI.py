import streamlit as st
from groq import Groq

# ── CONFIG ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Cortex",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL = "llama-3.1-8b-instant"

# ── AGENTS ─────────────────────────────────────────────────────────────────────
AGENTS = [
    {
        "icon": "🏛️",
        "name": "The Architect",
        "color": "#4F8EF7",
        "persona": "Focus on structural integrity. Map nth-order consequences. Ensure airtight logic and sound systemic reactions.",
    },
    {
        "icon": "💖",
        "name": "The Soul",
        "color": "#F77F7F",
        "persona": "Focus on human resonance. Use EQ and theory of mind. Predict social fallout and cultural impact.",
    },
    {
        "icon": "🛡️",
        "name": "The Filter",
        "color": "#7FF7A0",
        "persona": "Focus on vulnerability detection. Challenge groupthink. Hunt black swan risks and hidden failure points.",
    },
]

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:       #0D0F14;
    --surface:  #161920;
    --border:   #252830;
    --text:     #E2E6F0;
    --muted:    #5A6070;
    --blue:     #4F8EF7;
    --red:      #F77F7F;
    --green:    #7FF7A0;
    --yellow:   #F7D77F;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { font-family: 'IBM Plex Sans', sans-serif !important; }

/* Buttons */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--muted) !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    padding: 0.4rem 0.9rem !important;
    transition: all 0.15s !important;
    width: 100% !important;
    text-align: left !important;
}
.stButton > button:hover {
    border-color: var(--blue) !important;
    color: var(--blue) !important;
    background: rgba(79,142,247,0.06) !important;
}

/* Chat input */
[data-testid="stChatInputContainer"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
[data-testid="stChatInputContainer"] textarea {
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder {
    color: var(--muted) !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
}

/* Markdown text */
[data-testid="stMarkdown"] p,
[data-testid="stMarkdown"] li,
[data-testid="stMarkdown"] h3 {
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
[data-testid="stMarkdown"] h3 {
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    margin-bottom: 4px !important;
    margin-top: 16px !important;
    border-bottom: 1px solid var(--border) !important;
    padding-bottom: 6px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

/* Block container */
.block-container { padding: 1.5rem 2rem 2rem !important; max-width: 100% !important; }

/* Spinner */
.stSpinner > div { border-top-color: var(--blue) !important; }

/* Selectbox */
[data-testid="stSelectbox"] { color: var(--text) !important; }
div[data-baseweb="select"] > div { background: var(--surface) !important; border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ── HELPERS ────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])


def call_llm(prompt: str, tokens: int = 200) -> str:
    try:
        client = get_client()
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=tokens,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip().replace("**", "")
    except Exception as e:
        return f"⚠ Error: {e}"


def get_context(messages: list) -> str:
    lines = []
    for m in messages[-6:]:
        who = "User" if m["role"] == "user" else "Cortex"
        lines.append(f"{who}: {m['content'][:200]}")
    return "\n".join(lines)


def generate_cortex_response(user_input: str, chat_history: list) -> str:
    context = get_context(chat_history)
    views = {}

    # Each agent gives its perspective
    for agent in AGENTS:
        prompt = f"""You are {agent['name']}.
{agent['persona']}

Conversation so far:
{context}

User says: {user_input}

Give your perspective in 3 concise sentences."""
        if views:
            prompt += f"\n\nOther views so far:\n{views}"
        views[agent["name"]] = call_llm(prompt, 180)

    # Internal debate
    debate = call_llm(f"""User input: {user_input}

Agent views:
{views}

Write a short internal debate (2–3 exchanges) where these agents agree, challenge, or refine each other's views.""", 220)

    # Final answer
    final = call_llm(f"""User input: {user_input}

Agent views:
{views}

Debate summary:
{debate}

Give a single, practical final conclusion in 2–3 sentences.""", 180)

    parts = []
    for agent in AGENTS:
        parts.append(f"### {agent['icon']} {agent['name']}\n{views[agent['name']]}")
    parts.append(f"### 🎯 Final Conclusion\n{final}")
    return "\n\n".join(parts)


# ── STATE ──────────────────────────────────────────────────────────────────────
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
        "name": f"Analysis {st.session_state.chat_count}",
        "messages": [],
    }
    st.session_state.chat_order.insert(0, cid)
    st.session_state.active_chat = cid


# ── APP ────────────────────────────────────────────────────────────────────────
init_state()

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="padding: 8px 0 20px; border-bottom: 1px solid #252830; margin-bottom: 16px;">
        <div style="font-family:'IBM Plex Mono',monospace; font-size:1.1rem; font-weight:500; color:#E2E6F0; letter-spacing:0.05em;">
            ⚡ cortex
        </div>
        <div style="font-size:0.72rem; color:#5A6070; margin-top:4px; font-family:'IBM Plex Mono',monospace;">
            multi-agent reasoning
        </div>
    </div>
    """, unsafe_allow_html=True)

    # New chat button
    if st.button("＋  New Analysis"):
        _new_chat()
        st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Chat history
    st.markdown("""
    <div style="font-size:0.68rem; font-family:'IBM Plex Mono',monospace;
         color:#5A6070; letter-spacing:0.1em; text-transform:uppercase;
         margin-bottom:8px;">
        History
    </div>
    """, unsafe_allow_html=True)

    for cid in st.session_state.chat_order:
        chat = st.session_state.chats[cid]
        is_active = cid == st.session_state.active_chat
        label = ("▶  " if is_active else "   ") + chat["name"]
        if st.button(label, key=f"nav_{cid}"):
            st.session_state.active_chat = cid
            st.rerun()

    # Agent info
    st.markdown("""
    <div style="height:1px; background:#252830; margin:20px 0 16px;"></div>
    <div style="font-size:0.68rem; font-family:'IBM Plex Mono',monospace;
         color:#5A6070; letter-spacing:0.1em; text-transform:uppercase;
         margin-bottom:10px;">
        Agents
    </div>
    """, unsafe_allow_html=True)

    for agent in AGENTS:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;
             padding:8px 10px; border-radius:6px; background:#161920;
             border:1px solid #252830;">
            <span style="font-size:1rem;">{agent['icon']}</span>
            <div>
                <div style="font-size:0.78rem; font-weight:500; color:#E2E6F0;
                     font-family:'IBM Plex Sans',sans-serif;">{agent['name']}</div>
                <div style="font-size:0.68rem; color:#5A6070;
                     font-family:'IBM Plex Sans',sans-serif; line-height:1.4;
                     margin-top:2px;">{agent['persona'][:60]}…</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── MAIN ───────────────────────────────────────────────────────────────────────
active = st.session_state.chats[st.session_state.active_chat]

# Header
st.markdown(f"""
<div style="display:flex; align-items:baseline; gap:12px; margin-bottom:24px;
     padding-bottom:16px; border-bottom:1px solid #252830;">
    <span style="font-family:'IBM Plex Mono',monospace; font-size:1.2rem;
          font-weight:500; color:#E2E6F0;">⚡ {active['name']}</span>
    <span style="font-size:0.75rem; color:#5A6070;
          font-family:'IBM Plex Mono',monospace;">3 agents active</span>
</div>
""", unsafe_allow_html=True)

# Welcome message if empty
if not active["messages"]:
    st.markdown("""
    <div style="text-align:center; padding:48px 24px;">
        <div style="font-size:2rem; margin-bottom:12px;">⚡</div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:0.9rem;
             color:#E2E6F0; margin-bottom:8px;">Cortex is ready.</div>
        <div style="font-size:0.82rem; color:#5A6070; max-width:360px; margin:0 auto;
             line-height:1.6;">
            Ask anything. Three agents — The Architect, The Soul, and The Filter —
            will each analyse your input, debate, and converge on a final answer.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Messages
msg_box = st.container(height=460)
with msg_box:
    for msg in active["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Ask the Cortex anything…"):
    active["messages"].append({"role": "user", "content": prompt})

    with msg_box:
        with st.chat_message("user"):
            st.markdown(prompt)

    with msg_box:
        with st.chat_message("assistant"):
            with st.spinner("Agents reasoning…"):
                response = generate_cortex_response(prompt, active["messages"])
            st.markdown(response)

    active["messages"].append({"role": "assistant", "content": response})
    st.rerun()