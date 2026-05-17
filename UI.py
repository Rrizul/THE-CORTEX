import streamlit as st
import streamlit.components.v1 as components

try:
    from cortex import init_state, new_chat, generate_cortex_response, AGENTS
except ImportError:
    AGENTS = []
    pass

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Cortex",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── PREMIUM GLOBAL CSS ─────────────────────────────────────────────────────────
CLEAN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=DM+Mono:wght@400;500&display=swap');

/* ── CSS VARIABLES ── */
:root {
    --bg-void:      #04060E;
    --bg-deep:      #070B18;
    --bg-surface:   #0C1220;
    --bg-glass:     rgba(12, 18, 32, 0.72);
    --bg-glass-2:   rgba(18, 26, 50, 0.55);
    --accent-blue:  #2F6FEB;
    --accent-cyan:  #00C8FF;
    --accent-green: #00E5A0;
    --accent-pulse: #4488FF;
    --border-dim:   rgba(255, 255, 255, 0.06);
    --border-glow:  rgba(47, 111, 235, 0.35);
    --border-bright:rgba(255, 255, 255, 0.14);
    --text-primary: #EDF2FF;
    --text-secondary:#8896B3;
    --text-muted:   #4A5578;
    --font-display: 'Syne', sans-serif;
    --font-body:    'DM Sans', sans-serif;
    --font-mono:    'DM Mono', monospace;
    --shadow-card:  0 24px 64px -12px rgba(0,0,0,0.7), 0 4px 16px rgba(0,0,0,0.4);
    --shadow-glow:  0 0 40px rgba(47,111,235,0.18), 0 0 80px rgba(0,200,255,0.06);
    --r-sm: 10px; --r-md: 14px; --r-lg: 20px; --r-xl: 28px;
}

/* ── GLOBAL RESET ── */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background: var(--bg-void) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}
*, *::before, *::after { box-sizing: border-box; }

/* ── BACKGROUND NEBULA EFFECT ── */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 20% -10%, rgba(30,60,140,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(0,120,180,0.10) 0%, transparent 55%),
        radial-gradient(ellipse 40% 40% at 55% 50%, rgba(10,20,60,0.12) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}
[data-testid="stAppViewContainer"] > * { position: relative; z-index: 1; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080C1A 0%, #060A15 100%) !important;
    border-right: 1px solid var(--border-dim) !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}
[data-testid="stSidebar"] * {
    font-family: var(--font-body) !important;
}

/* ── MAIN CONTENT AREA ── */
.block-container {
    padding: 1.5rem 2rem 3rem !important;
    max-width: 100% !important;
}

/* ── STREAMLIT ELEMENTS RESET ── */
[data-testid="stMarkdown"] p { color: var(--text-primary); }
h1,h2,h3,h4 { font-family: var(--font-display) !important; }
.stButton > button {
    background: rgba(47,111,235,0.12) !important;
    border: 1px solid rgba(47,111,235,0.35) !important;
    color: #7AABFF !important;
    border-radius: var(--r-sm) !important;
    font-family: var(--font-body) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 1.1rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: rgba(47,111,235,0.22) !important;
    border-color: rgba(47,111,235,0.6) !important;
    box-shadow: 0 0 20px rgba(47,111,235,0.2) !important;
    transform: translateY(-1px) !important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInputContainer"] {
    background: rgba(12, 18, 32, 0.85) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: var(--r-md) !important;
    backdrop-filter: blur(16px) !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.06) !important;
}
[data-testid="stChatInputContainer"] textarea {
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    font-size: 0.95rem !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder {
    color: var(--text-muted) !important;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
    background: var(--bg-glass) !important;
    border: 1px solid var(--border-dim) !important;
    border-radius: var(--r-lg) !important;
    backdrop-filter: blur(12px) !important;
    margin-bottom: 0.75rem !important;
}

/* ── DIVIDER ── */
hr { border-color: var(--border-dim) !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.18); }
</style>
"""

# ── SIDEBAR HTML ──────────────────────────────────────────────────────────────
SIDEBAR_HTML = """
<style>
.cx-sidebar {
    padding: 0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}
.cx-logo {
    padding: 28px 24px 20px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    display: flex;
    align-items: center;
    gap: 10px;
}
.cx-logo-icon {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, #2F6FEB, #00C8FF);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    box-shadow: 0 4px 16px rgba(47,111,235,0.4);
    flex-shrink: 0;
}
.cx-logo-text {
    font-family: 'Syne', sans-serif;
    font-weight: 700; font-size: 1rem;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: #EDF2FF;
}
.cx-logo-text span { color: rgba(255,255,255,0.4); font-weight: 400; }

.cx-nav { padding: 16px 12px; flex: 1; }
.cx-nav-label {
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: rgba(255,255,255,0.28);
    padding: 0 12px; margin: 16px 0 6px;
}
.cx-nav-item {
    display: flex; align-items: center; gap: 11px;
    padding: 10px 12px; border-radius: 10px;
    cursor: pointer; transition: all 0.18s ease;
    color: rgba(255,255,255,0.45);
    font-size: 0.875rem; font-weight: 500;
    margin-bottom: 2px; text-decoration: none;
    position: relative;
}
.cx-nav-item:hover {
    background: rgba(255,255,255,0.05);
    color: rgba(255,255,255,0.75);
}
.cx-nav-item.active {
    background: rgba(47,111,235,0.14);
    color: #7AABFF;
    border: 1px solid rgba(47,111,235,0.22);
}
.cx-nav-item.active::before {
    content: '';
    position: absolute; left: 0; top: 20%; bottom: 20%;
    width: 2.5px; border-radius: 2px;
    background: linear-gradient(180deg, #2F6FEB, #00C8FF);
}
.cx-nav-icon {
    width: 18px; height: 18px; flex-shrink: 0;
    opacity: 0.7;
}
.cx-nav-item.active .cx-nav-icon { opacity: 1; }

.cx-badge {
    margin-left: auto;
    background: rgba(47,111,235,0.2);
    color: #7AABFF; font-size: 0.65rem; font-weight: 600;
    padding: 2px 7px; border-radius: 99px;
    border: 1px solid rgba(47,111,235,0.3);
}

.cx-status-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #00E5A0; flex-shrink: 0;
    box-shadow: 0 0 8px rgba(0,229,160,0.6);
    animation: pulse-dot 2s ease-in-out infinite;
    margin-left: auto;
}
@keyframes pulse-dot {
    0%,100%{ box-shadow: 0 0 8px rgba(0,229,160,0.6); }
    50%{ box-shadow: 0 0 14px rgba(0,229,160,0.9), 0 0 24px rgba(0,229,160,0.4); }
}

.cx-footer {
    padding: 16px 12px;
    border-top: 1px solid rgba(255,255,255,0.05);
}
.cx-footer-user {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 12px; border-radius: 10px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    cursor: pointer; transition: background 0.18s;
}
.cx-footer-user:hover { background: rgba(255,255,255,0.06); }
.cx-avatar {
    width: 32px; height: 32px; border-radius: 8px;
    background: linear-gradient(135deg, #1A3A8A, #2F6FEB);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 700; color: #fff;
    letter-spacing: 0.04em;
}
.cx-user-info { flex: 1; min-width: 0; }
.cx-user-name { font-size: 0.8rem; font-weight: 600; color: rgba(255,255,255,0.8); }
.cx-user-role { font-size: 0.7rem; color: rgba(255,255,255,0.35); }

/* SVG icons inline */
svg.icon { width: 18px; height: 18px; fill: none; stroke: currentColor; stroke-width: 1.6; stroke-linecap: round; stroke-linejoin: round; }
</style>

<div class="cx-sidebar">
  <div class="cx-logo">
    <div class="cx-logo-icon">⚡</div>
    <div class="cx-logo-text">The Cortex <span>/ v2</span></div>
  </div>

  <nav class="cx-nav">
    <div class="cx-nav-label">Workspace</div>

    <a class="cx-nav-item active" href="#">
      <svg class="icon" viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
      Active Tasks
      <span class="cx-badge">3</span>
    </a>
    <a class="cx-nav-item" href="#">
      <svg class="icon" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
      Task History
    </a>
    <a class="cx-nav-item" href="#">
      <svg class="icon" viewBox="0 0 24 24"><path d="M12 20V10M18 20V4M6 20v-4"/></svg>
      System Stats
      <div class="cx-status-dot"></div>
    </a>

    <div class="cx-nav-label">Intelligence</div>
    <a class="cx-nav-item" href="#">
      <svg class="icon" viewBox="0 0 24 24"><circle cx="12" cy="8" r="5"/><path d="M3 21v-1a9 9 0 0118 0v1"/></svg>
      Agents
    </a>
    <a class="cx-nav-item" href="#">
      <svg class="icon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
      Explore
    </a>

    <div class="cx-nav-label">Config</div>
    <a class="cx-nav-item" href="#">
      <svg class="icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 010 14.14M4.93 4.93a10 10 0 000 14.14"/></svg>
      Settings
    </a>
  </nav>

  <div class="cx-footer">
    <div class="cx-footer-user">
      <div class="cx-avatar">CX</div>
      <div class="cx-user-info">
        <div class="cx-user-name">Cortex Admin</div>
        <div class="cx-user-role">Neural Workspace</div>
      </div>
      <svg class="icon" viewBox="0 0 24 24" style="width:14px;height:14px;color:rgba(255,255,255,0.3)"><path d="M9 18l6-6-6-6"/></svg>
    </div>
  </div>
</div>
"""

# ── HEADER HTML ───────────────────────────────────────────────────────────────
HEADER_HTML = """
<style>
.cx-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 32px; gap: 16px;
}
.cx-breadcrumb {
    display: flex; align-items: center; gap: 8px;
    font-size: 0.8rem; color: rgba(255,255,255,0.3);
    font-family: 'DM Sans', sans-serif;
}
.cx-breadcrumb span { color: rgba(255,255,255,0.6); }
.cx-breadcrumb .sep { opacity: 0.4; }

.cx-header-query {
    flex: 1; max-width: 480px;
    background: rgba(12,18,32,0.8);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 12px;
    padding: 11px 16px;
    display: flex; align-items: center; gap: 10px;
    backdrop-filter: blur(12px);
    cursor: text;
    transition: border-color 0.2s;
}
.cx-header-query:hover { border-color: rgba(255,255,255,0.16); }
.cx-query-label {
    font-size: 0.7rem; color: rgba(255,255,255,0.28);
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.04em; line-height: 1;
}
.cx-query-text {
    font-size: 0.9rem; color: rgba(255,255,255,0.75);
    font-family: 'DM Sans', sans-serif; font-weight: 400;
}
.cx-header-actions { display: flex; gap: 8px; align-items: center; }
.cx-icon-btn {
    width: 36px; height: 36px; border-radius: 9px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; transition: all 0.18s;
    color: rgba(255,255,255,0.4);
}
.cx-icon-btn:hover {
    background: rgba(255,255,255,0.08);
    color: rgba(255,255,255,0.7);
}
.cx-icon-btn svg { width: 16px; height: 16px; fill: none; stroke: currentColor; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }
</style>

<div class="cx-header">
  <div class="cx-breadcrumb">
    Home <span class="sep">›</span> <span>Active Tasks</span>
  </div>
  <div class="cx-header-query">
    <div>
      <div class="cx-query-label">Ask me anything...</div>
      <div class="cx-query-text">Analyze market trends for Q3</div>
    </div>
  </div>
  <div class="cx-header-actions">
    <div class="cx-icon-btn">
      <svg viewBox="0 0 24 24"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0"/></svg>
    </div>
    <div class="cx-icon-btn">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 010 14.14M4.93 4.93a10 10 0 000 14.14"/></svg>
    </div>
  </div>
</div>
"""

# ── 3D NODE GRAPH HTML ────────────────────────────────────────────────────────
NODES_HTML = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700&family=DM+Sans:wght@400;500&display=swap');

.cx-graph-wrapper {
    position: relative;
    background: rgba(8, 12, 26, 0.6);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 36px 28px 28px;
    backdrop-filter: blur(20px);
    box-shadow:
        0 32px 80px -16px rgba(0,0,0,0.7),
        inset 0 1px 0 rgba(255,255,255,0.07),
        0 0 0 1px rgba(0,0,0,0.3);
    overflow: hidden;
    margin-bottom: 24px;
}
.cx-graph-wrapper::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(47,111,235,0.4), rgba(0,200,255,0.3), transparent);
}
.cx-graph-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700; font-size: 0.7rem; letter-spacing: 0.15em;
    text-transform: uppercase; color: rgba(255,255,255,0.3);
    margin-bottom: 28px;
    display: flex; align-items: center; gap: 8px;
}
.cx-graph-title::before {
    content: ''; display: inline-block;
    width: 6px; height: 6px; border-radius: 50%;
    background: #00E5A0;
    box-shadow: 0 0 8px #00E5A0;
    animation: blink 2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* Node Container */
.cx-node-stage {
    position: relative;
    height: 340px;
    perspective: 900px;
}

/* SVG Connections */
.cx-connections {
    position: absolute; top: 0; left: 0;
    width: 100%; height: 100%; pointer-events: none; z-index: 0;
    overflow: visible;
}
.conn-line {
    fill: none;
    stroke: rgba(47,111,235,0.22);
    stroke-width: 1.5;
    stroke-dasharray: 6 4;
    animation: flow 2.5s linear infinite;
}
.conn-line-bright {
    fill: none;
    stroke: rgba(47,111,235,0.5);
    stroke-width: 1.5;
    animation: flow 2s linear infinite;
}
@keyframes flow { to { stroke-dashoffset: -40; } }
.conn-dot {
    fill: #4488FF;
    filter: drop-shadow(0 0 4px #4488FF);
    animation: orbit 3s ease-in-out infinite;
}
@keyframes orbit { 0%,100%{opacity:1} 50%{opacity:0.5} }

/* Glow pulse rings */
.pulse-ring {
    position: absolute;
    border-radius: 50%;
    border: 1px solid rgba(47,111,235,0.35);
    animation: ring-expand 2.5s ease-out infinite;
    pointer-events: none;
}
@keyframes ring-expand {
    0%   { transform: scale(0.85); opacity: 0.7; }
    100% { transform: scale(1.6);  opacity: 0; }
}

/* ── NODES ── */
.cx-node {
    position: absolute;
    border-radius: 16px;
    padding: 18px 20px 16px;
    backdrop-filter: blur(18px);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    cursor: pointer;
    z-index: 2;
    transform-style: preserve-3d;
}
.cx-node:hover {
    transform: translateY(-5px) scale(1.02);
    z-index: 10;
}

/* Active — Blue gradient hero node */
.cx-node-primary {
    width: 200px;
    top: 20px; left: 50%; transform: translateX(-50%);
    background: linear-gradient(145deg, #1A3F9E 0%, #1E3A90 40%, #152D78 100%);
    border: 1px solid rgba(80,140,255,0.45);
    box-shadow:
        0 20px 60px -10px rgba(18,50,140,0.7),
        0 0 0 1px rgba(80,140,255,0.2),
        inset 0 1px 0 rgba(255,255,255,0.12),
        0 0 40px rgba(47,111,235,0.2);
}
.cx-node-primary:hover {
    transform: translateX(-50%) translateY(-5px) scale(1.02);
    box-shadow:
        0 28px 70px -10px rgba(18,50,140,0.8),
        0 0 0 1px rgba(80,140,255,0.35),
        inset 0 1px 0 rgba(255,255,255,0.15),
        0 0 60px rgba(47,111,235,0.3);
}

/* Dark glass secondary nodes */
.cx-node-secondary {
    width: 188px;
    background: rgba(10, 15, 30, 0.85);
    border: 1px solid rgba(255,255,255,0.09);
    box-shadow:
        0 16px 48px -8px rgba(0,0,0,0.6),
        inset 0 1px 0 rgba(255,255,255,0.06);
}
.cx-node-secondary:hover {
    border-color: rgba(47,111,235,0.3);
    box-shadow:
        0 22px 56px -8px rgba(0,0,0,0.7),
        0 0 20px rgba(47,111,235,0.12),
        inset 0 1px 0 rgba(255,255,255,0.08);
}

.cx-node-left  { bottom: 40px; left: 8%; }
.cx-node-right { bottom: 40px; right: 8%; }

/* Node internals */
.cx-node-icon {
    width: 34px; height: 34px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; margin-bottom: 12px;
    position: relative; flex-shrink: 0;
}
.icon-primary {
    background: rgba(255,255,255,0.15);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.2), 0 4px 12px rgba(0,0,0,0.3);
}
.icon-secondary {
    background: rgba(47,111,235,0.12);
    border: 1px solid rgba(47,111,235,0.2);
}
.cx-node-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700; font-size: 0.95rem;
    color: #EDF2FF; margin-bottom: 4px; line-height: 1.2;
}
.cx-node-desc {
    font-size: 0.74rem; font-weight: 400;
    color: rgba(255,255,255,0.42); line-height: 1.45;
    margin-bottom: 12px;
}
.cx-node-status {
    display: inline-flex; align-items: center; gap: 5px;
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.04em;
}
.cx-node-status::before {
    content: ''; display: inline-block;
    width: 5px; height: 5px; border-radius: 50%;
}
.status-active { color: #00E5A0; }
.status-active::before { background: #00E5A0; box-shadow: 0 0 6px #00E5A0; }
.status-paused { color: #8896B3; }
.status-paused::before { background: #4A5578; }

/* 3D shine overlay on hover */
.cx-node::after {
    content: '';
    position: absolute; inset: 0;
    border-radius: inherit;
    background: linear-gradient(135deg, rgba(255,255,255,0.07) 0%, transparent 60%);
    pointer-events: none;
}

/* Agent stats row in primary node */
.cx-node-stats {
    display: flex; gap: 12px; margin-top: 12px; padding-top: 12px;
    border-top: 1px solid rgba(255,255,255,0.1);
}
.cx-stat-item { flex: 1; }
.cx-stat-val { font-family: 'DM Mono', monospace; font-size: 0.8rem; font-weight: 500; color: #7AABFF; }
.cx-stat-lbl { font-size: 0.65rem; color: rgba(255,255,255,0.3); margin-top: 1px; }
</style>

<div class="cx-graph-wrapper">
  <div class="cx-graph-title">Agent Network — Live</div>

  <div class="cx-node-stage">

    <!-- SVG Connections -->
    <svg class="cx-connections" viewBox="0 0 700 340" preserveAspectRatio="none">
      <defs>
        <filter id="glow-f">
          <feGaussianBlur in="SourceGraphic" stdDeviation="2" result="blur"/>
          <feComposite in="blur" in2="SourceGraphic" operator="over"/>
        </filter>
        <marker id="dot-mark" viewBox="0 0 6 6" refX="3" refY="3" markerWidth="4" markerHeight="4">
          <circle cx="3" cy="3" r="3" fill="#4488FF" filter="url(#glow-f)"/>
        </marker>
      </defs>

      <!-- Left connection: Primary → Memory -->
      <path class="conn-line" stroke-dasharray="6 4" d="M 350 140 C 350 220, 200 220, 200 270"/>
      <!-- Glowing overlay line -->
      <path fill="none" stroke="rgba(68,136,255,0.12)" stroke-width="6"
            d="M 350 140 C 350 220, 200 220, 200 270" filter="url(#glow-f)"/>

      <!-- Right connection: Primary → Synthesize -->
      <path class="conn-line" stroke-dasharray="6 4" d="M 350 140 C 350 220, 510 220, 510 270"/>
      <path fill="none" stroke="rgba(68,136,255,0.12)" stroke-width="6"
            d="M 350 140 C 350 220, 510 220, 510 270" filter="url(#glow-f)"/>

      <!-- Memory → Synthesize horizontal -->
      <path class="conn-line" style="animation-duration:3.5s" stroke-dasharray="4 6"
            d="M 295 300 C 340 300, 370 300, 420 300"/>

      <!-- Animated travel dots -->
      <circle r="4" fill="#4488FF" filter="url(#glow-f)">
        <animateMotion dur="2.5s" repeatCount="indefinite" path="M 350 140 C 350 220, 200 220, 200 270"/>
      </circle>
      <circle r="4" fill="#00C8FF" filter="url(#glow-f)">
        <animateMotion dur="2s" repeatCount="indefinite" begin="0.7s"
          path="M 350 140 C 350 220, 510 220, 510 270"/>
      </circle>
      <circle r="3" fill="#7AABFF" filter="url(#glow-f)">
        <animateMotion dur="3s" repeatCount="indefinite" begin="1.2s"
          path="M 295 300 C 340 300, 370 300, 420 300"/>
      </circle>
    </svg>

    <!-- PRIMARY NODE: Reason -->
    <div class="cx-node cx-node-primary">
      <!-- Pulse ring -->
      <div class="pulse-ring" style="width:180%;height:180%;top:-40%;left:-40%;animation-delay:0s;"></div>
      <div class="pulse-ring" style="width:180%;height:180%;top:-40%;left:-40%;animation-delay:1.25s;"></div>

      <div style="display:flex;align-items:flex-start;gap:12px;">
        <div class="cx-node-icon icon-primary">🌀</div>
        <div style="flex:1;min-width:0;">
          <div class="cx-node-title">Reason</div>
          <div class="cx-node-desc">Logical deductions &amp; evaluations</div>
          <div class="cx-node-status status-active">Active</div>
        </div>
      </div>
      <div class="cx-node-stats">
        <div class="cx-stat-item">
          <div class="cx-stat-val">94%</div>
          <div class="cx-stat-lbl">Confidence</div>
        </div>
        <div class="cx-stat-item">
          <div class="cx-stat-val">2.1s</div>
          <div class="cx-stat-lbl">Avg latency</div>
        </div>
        <div class="cx-stat-item">
          <div class="cx-stat-val">47</div>
          <div class="cx-stat-lbl">Steps done</div>
        </div>
      </div>
    </div>

    <!-- MEMORY NODE -->
    <div class="cx-node cx-node-secondary cx-node-left">
      <div style="display:flex;align-items:flex-start;gap:11px;">
        <div class="cx-node-icon icon-secondary" style="font-family:'Syne',sans-serif;font-weight:800;font-size:14px;color:#7AABFF;">M</div>
        <div style="flex:1;min-width:0;">
          <div class="cx-node-title">Memory</div>
          <div class="cx-node-desc">Knowledge base &amp; historical data</div>
          <div class="cx-node-status status-active">Active</div>
        </div>
      </div>
    </div>

    <!-- SYNTHESIZE NODE -->
    <div class="cx-node cx-node-secondary cx-node-right">
      <div style="display:flex;align-items:flex-start;gap:11px;">
        <div class="cx-node-icon icon-secondary">🌊</div>
        <div style="flex:1;min-width:0;">
          <div class="cx-node-title">Synthesize</div>
          <div class="cx-node-desc">Summary &amp; insight generation</div>
          <div class="cx-node-status status-paused">Paused</div>
        </div>
      </div>
    </div>

  </div>
</div>
"""

# ── REASONING TRACE HTML ──────────────────────────────────────────────────────
TRACE_HTML = """
<style>
.cx-trace-wrapper {
    background: rgba(8, 12, 26, 0.55);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 28px;
    backdrop-filter: blur(20px);
    box-shadow: 0 24px 60px -12px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06);
    position: relative; overflow: hidden;
}
.cx-trace-wrapper::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,200,255,0.3), rgba(47,111,235,0.4), transparent);
}
.cx-trace-header {
    display: flex; justify-content: space-between; align-items: flex-end;
    margin-bottom: 24px;
}
.cx-trace-heading {
    font-family: 'Syne', sans-serif;
    font-weight: 700; font-size: 1.05rem; color: #EDF2FF;
    margin: 0 0 3px;
}
.cx-trace-subtext {
    font-size: 0.78rem; color: rgba(255,255,255,0.3); margin: 0;
}
.cx-trace-actions { display: flex; gap: 8px; }
.cx-btn {
    display: inline-flex; align-items: center; gap: 6px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.78rem; font-weight: 500;
    padding: 7px 14px; border-radius: 8px; cursor: pointer;
    transition: all 0.18s; border: 1px solid transparent;
}
.cx-btn-ghost {
    color: rgba(255,255,255,0.45);
    background: rgba(255,255,255,0.04);
    border-color: rgba(255,255,255,0.08);
}
.cx-btn-ghost:hover { background: rgba(255,255,255,0.07); color: rgba(255,255,255,0.7); }
.cx-btn-primary {
    color: #7AABFF;
    background: rgba(47,111,235,0.14);
    border-color: rgba(47,111,235,0.3);
}
.cx-btn-primary:hover { background: rgba(47,111,235,0.22); box-shadow: 0 0 16px rgba(47,111,235,0.2); }

/* Timeline */
.cx-timeline {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 0; position: relative;
}
.cx-timeline::before {
    content: '';
    position: absolute; top: 18px; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg,
        rgba(47,111,235,0.6),
        rgba(47,111,235,0.35),
        rgba(47,111,235,0.2),
        rgba(255,255,255,0.06));
    z-index: 0;
}
.cx-step {
    position: relative; padding: 0 16px 0 0;
    z-index: 1;
}
.cx-step-dot-wrap {
    position: relative; margin-bottom: 14px;
}
.cx-step-dot {
    width: 13px; height: 13px; border-radius: 50%;
    position: relative; z-index: 2;
    border: 2px solid;
}
.cx-step-dot-active {
    background: #2F6FEB; border-color: #7AABFF;
    box-shadow: 0 0 14px rgba(47,111,235,0.7), 0 0 28px rgba(47,111,235,0.3);
}
.cx-step-dot-done {
    background: #0C1220; border-color: rgba(47,111,235,0.5);
}
.cx-step-dot-done::after {
    content: ''; position: absolute; top: 50%; left: 50%;
    transform: translate(-50%,-50%);
    width: 5px; height: 5px; border-radius: 50%;
    background: rgba(47,111,235,0.6);
}
.cx-step-dot-pending {
    background: #0C1220; border-color: rgba(255,255,255,0.12);
}
.cx-step-time {
    font-family: 'DM Mono', monospace;
    font-size: 0.67rem; color: rgba(255,255,255,0.3);
    margin-bottom: 5px; letter-spacing: 0.04em;
}
.cx-step-name {
    font-weight: 600; font-size: 0.82rem; color: rgba(255,255,255,0.85);
    margin-bottom: 4px; line-height: 1.3;
}
.cx-step-detail {
    font-size: 0.72rem; color: rgba(255,255,255,0.35);
    line-height: 1.45;
}
.cx-step:last-child { padding-right: 0; }
</style>

<div class="cx-trace-wrapper">
  <div class="cx-trace-header">
    <div>
      <h3 class="cx-trace-heading">Reasoning Trace</h3>
      <p class="cx-trace-subtext">Cognitive steps taken to reach conclusion</p>
    </div>
    <div class="cx-trace-actions">
      <div class="cx-btn cx-btn-ghost">
        <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.7" viewBox="0 0 24 24"><path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8M16 6l-4-4-4 4M12 2v13"/></svg>
        Share
      </div>
      <div class="cx-btn cx-btn-primary">
        Pause
        <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.7" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>
      </div>
    </div>
  </div>

  <div class="cx-timeline">
    <div class="cx-step">
      <div class="cx-step-dot-wrap">
        <div class="cx-step-dot cx-step-dot-done"></div>
      </div>
      <div class="cx-step-time">10:21 AM</div>
      <div class="cx-step-name">Initial Hypothesis Formation</div>
      <div class="cx-step-detail">Based on recent financial metrics and industry analysis patterns</div>
    </div>
    <div class="cx-step">
      <div class="cx-step-dot-wrap">
        <div class="cx-step-dot cx-step-dot-done"></div>
      </div>
      <div class="cx-step-time">10:22 AM</div>
      <div class="cx-step-name">Data Collection &amp; Validation</div>
      <div class="cx-step-detail">Checked recent news sources and APIs for updates</div>
    </div>
    <div class="cx-step">
      <div class="cx-step-dot-wrap">
        <div class="cx-step-dot cx-step-dot-active"></div>
      </div>
      <div class="cx-step-time">10:22 AM</div>
      <div class="cx-step-name">Pattern Recognition</div>
      <div class="cx-step-detail">Identified recurring patterns in financial indicators</div>
    </div>
    <div class="cx-step">
      <div class="cx-step-dot-wrap">
        <div class="cx-step-dot cx-step-dot-pending"></div>
      </div>
      <div class="cx-step-time">10:22 AM</div>
      <div class="cx-step-name">Final Conclusion</div>
      <div class="cx-step-detail">Determine final Q3 market trend summary</div>
    </div>
  </div>
</div>
"""


# ── MAIN APP ──────────────────────────────────────────────────────────────────
def main():
    # Inject global CSS
    st.markdown(CLEAN_CSS, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        components.html(SIDEBAR_HTML, height=560, scrolling=False)

    # Main content
    components.html(HEADER_HTML, height=80, scrolling=False)

    # Two-column layout: graph (left wide) + chat (right)
    col_graph, col_chat = st.columns([1.15, 1], gap="large")

    with col_graph:
        components.html(NODES_HTML, height=460, scrolling=False)
        components.html(TRACE_HTML, height=280, scrolling=False)

    with col_chat:
        # ── Chat Section ───────────────────────────────────────────────────
        st.markdown("""
        <div style="
            background: rgba(8,12,26,0.55);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 20px;
            padding: 20px 20px 12px;
            backdrop-filter: blur(20px);
            box-shadow: 0 24px 60px -12px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06);
            position: relative; overflow: hidden;
            height: 460px;
        ">
          <div style="position:absolute;top:0;left:0;right:0;height:1px;
              background:linear-gradient(90deg,transparent,rgba(47,111,235,0.35),transparent);">
          </div>
          <div style="
              font-family:'Syne',sans-serif;font-weight:700;font-size:0.7rem;
              letter-spacing:0.14em;text-transform:uppercase;
              color:rgba(255,255,255,0.28);margin-bottom:16px;
              display:flex;align-items:center;gap:8px;
          ">
            <span style="display:inline-block;width:6px;height:6px;border-radius:50%;
                background:#2F6FEB;box-shadow:0 0 8px #2F6FEB;"></span>
            Neural Chat Interface
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Initialize session state
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "**The Cortex is online.** How can I assist your analysis today? I'm currently processing market trend data for Q3."
                }
            ]

        # Display messages
        msg_container = st.container(height=320)
        with msg_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Chat input
        if prompt := st.chat_input("Send a message to The Cortex..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with msg_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

            try:
                response = generate_cortex_response(prompt)
            except Exception:
                response = f"Processing your request: *{prompt}* — Neural reasoning engaged."

            st.session_state.messages.append({"role": "assistant", "content": response})
            with msg_container:
                with st.chat_message("assistant"):
                    st.markdown(response)


if __name__ == "__main__":
    main()