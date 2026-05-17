import streamlit as st
from groq import Groq

MODEL = "llama-3.1-8b-instant"
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

AGENTS = [
    {
        "icon": "🏛️",
        "name": "The Architect",
        "persona": "Focus on structural integrity. Map nth-order consequences. Ensure airtight logic and sound systemic reactions."
    },
    {
        "icon": "💖",
        "name": "The Soul",
        "persona": "Focus on human resonance. Use EQ and theory of mind. Predict social fallout and cultural impact."
    },
    {
        "icon": "🛡️",
        "name": "The Filter",
        "persona": "Focus on vulnerability detection. Challenge groupthink. Hunt black swan risks and hidden failure points."
    },
]

def call_llm(prompt, tokens=250):
    try:
        chat = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=tokens,
            temperature=0.7,
        )
        return chat.choices[0].message.content.strip().replace("**", "")
    except Exception as e:
        return f"⚠ Error: {e}"

def init_state():
    if "chats" not in st.session_state:
        st.session_state.chats = {}
        st.session_state.chat_order = []
        st.session_state.chat_count = 0
        new_chat()

def new_chat():
    st.session_state.chat_count += 1
    cid = f"chat_{st.session_state.chat_count}"
    st.session_state.chats[cid] = {
        "name": f"Analysis {st.session_state.chat_count}",
        "messages": []
    }
    st.session_state.chat_order.insert(0, cid)
    st.session_state.active_chat = cid

def get_context(messages):
    lines = []
    for m in messages[-6:]:
        who = "User" if m["role"] == "user" else "Cortex"
        lines.append(f"{who}: {m['content'][:200]}")
    return "\n".join(lines)

def generate_cortex_response(user_input, chat_history):
    context = get_context(chat_history)
    views = {}

    for agent in AGENTS:
        prompt = f"""
You are {agent['name']}.
{agent['persona']}

Conversation Context:
{context}

User Input:
{user_input}

Give your perspective in 3 concise sentences.
"""
        if views:
            prompt += f"\nPrevious Views:\n{views}"

        views[agent["name"]] = call_llm(prompt, 180)

    debate_prompt = f"""
User Input: {user_input}

Views:
{views}

Create a short internal debate where they agree/disagree and adapt.
"""
    debate = call_llm(debate_prompt, 220)

    final_prompt = f"""
User Input: {user_input}

Views:
{views}

Debate:
{debate}

Give final practical conclusion.
"""
    final_answer = call_llm(final_prompt, 200)

    output = []
    for agent in AGENTS:
        output.append(f"### {agent['icon']} {agent['name']}\n{views[agent['name']]}")
    output.append(f"### 🎯 Final Conclusion\n{final_answer}")

    return "\n\n".join(output)