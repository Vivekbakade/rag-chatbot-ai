import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="DocChat AI — Vivek Bakade",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif !important;
    background-color: #0A0015 !important;
    color: #FAF7F0 !important;
}
.stApp {
    background: radial-gradient(ellipse at top left, #1B0F3A 0%, #0A0015 50%, #000510 100%) !important;
}
.stApp::before {
    content: '';
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(123,47,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(123,47,255,0.04) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: gridMove 20s linear infinite;
    pointer-events: none; z-index: 0;
}
@keyframes gridMove { 0%{transform:translateY(0)} 100%{transform:translateY(50px)} }
@keyframes pulse { 0%,100%{box-shadow:0 0 10px rgba(123,47,255,0.4)} 50%{box-shadow:0 0 25px rgba(123,47,255,0.7),0 0 50px rgba(123,47,255,0.4)} }
@keyframes textGlow { 0%,100%{text-shadow:0 0 10px rgba(201,168,76,0.5)} 50%{text-shadow:0 0 30px rgba(201,168,76,0.9),0 0 60px rgba(201,168,76,0.4)} }
@keyframes fadeInDown { from{opacity:0;transform:translateY(-20px)} to{opacity:1;transform:translateY(0)} }
@keyframes slideR { from{opacity:0;transform:translateX(20px)} to{opacity:1;transform:translateX(0)} }
@keyframes slideL { from{opacity:0;transform:translateX(-20px)} to{opacity:1;transform:translateX(0)} }

.hero { text-align:center; padding:2rem 0 1rem; animation:fadeInDown 0.8s ease; }
.hero-badge {
    display:inline-block; background:rgba(123,47,255,0.15);
    border:1px solid rgba(201,168,76,0.3); border-radius:4px;
    padding:4px 16px; font-size:0.65rem; color:#C9A84C;
    letter-spacing:0.2em; text-transform:uppercase;
    font-family:'Orbitron',monospace; animation:pulse 3s ease infinite; margin-bottom:0.8rem;
}
.hero-title {
    font-family:'Orbitron',monospace; font-size:3rem; font-weight:900;
    background:linear-gradient(135deg,#F0D080 0%,#C9A84C 50%,#7B2FFF 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text; letter-spacing:4px; animation:textGlow 4s ease infinite; margin-bottom:0.3rem;
}
.hero-sub { font-size:0.8rem; color:rgba(250,247,240,0.45); letter-spacing:0.15em; text-transform:uppercase; margin-bottom:0.5rem; }
.hero-links { font-size:0.75rem; color:rgba(250,247,240,0.4); }
.hero-links a { color:#C9A84C !important; text-decoration:none; margin:0 8px; }
.divider { height:1px; background:linear-gradient(90deg,transparent,#7B2FFF,#C9A84C,#7B2FFF,transparent); margin:1.2rem 0 1.5rem; opacity:0.5; }

.api-banner {
    background:rgba(123,47,255,0.08); border:1px solid rgba(201,168,76,0.2);
    border-left:3px solid #C9A84C; border-radius:8px;
    padding:1rem 1.5rem; margin-bottom:1.5rem; font-size:0.85rem; line-height:1.7;
}
.api-banner strong { color:#C9A84C; font-family:'Orbitron',monospace; font-size:0.75rem; }
.api-banner a { color:#C9A84C; }

.msg-user { display:flex; justify-content:flex-end; margin:10px 0; animation:slideR 0.3s ease; }
.msg-bot { display:flex; justify-content:flex-start; align-items:flex-start; gap:10px; margin:10px 0; animation:slideL 0.3s ease; }
.bubble-user {
    background:linear-gradient(135deg,#C9A84C,#8A6020); color:#0A0015;
    padding:12px 18px; border-radius:16px 16px 4px 16px;
    max-width:68%; font-size:0.9rem; font-weight:500;
    box-shadow:0 4px 20px rgba(201,168,76,0.3);
}
.bubble-bot {
    background:rgba(10,0,21,0.85); border:1px solid rgba(123,47,255,0.3);
    border-left:3px solid #7B2FFF; color:#FAF7F0;
    padding:14px 18px; border-radius:4px 16px 16px 16px;
    max-width:72%; font-size:0.9rem; line-height:1.75;
    backdrop-filter:blur(10px); box-shadow:0 4px 20px rgba(0,0,0,0.4);
}
.avatar-bot {
    width:34px; height:34px; background:linear-gradient(135deg,#7B2FFF,#4A1A99);
    border-radius:8px; display:flex; align-items:center; justify-content:center;
    font-size:1rem; flex-shrink:0; box-shadow:0 0 15px rgba(123,47,255,0.4);
    animation:pulse 3s ease infinite;
}

.stTextInput>div>div>input {
    background:rgba(10,0,21,0.7) !important; border:1px solid rgba(123,47,255,0.4) !important;
    border-radius:8px !important; color:#FAF7F0 !important;
    font-family:'Exo 2',sans-serif !important; padding:14px 18px !important;
    font-size:0.95rem !important; transition:all 0.3s !important;
}
.stTextInput>div>div>input:focus { border-color:#C9A84C !important; box-shadow:0 0 0 2px rgba(201,168,76,0.2) !important; }
.stTextInput>div>div>input::placeholder { color:rgba(250,247,240,0.25) !important; }

.stButton>button {
    background:linear-gradient(135deg,#7B2FFF,#4A1A99) !important;
    color:#FAF7F0 !important; border:1px solid rgba(123,47,255,0.5) !important;
    border-radius:8px !important; font-family:'Orbitron',monospace !important;
    font-weight:700 !important; font-size:0.65rem !important;
    letter-spacing:0.1em !important; padding:10px 20px !important;
    transition:all 0.3s !important; box-shadow:0 4px 15px rgba(123,47,255,0.3) !important;
    text-transform:uppercase !important;
}
.stButton>button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 8px 25px rgba(123,47,255,0.5) !important;
    border-color:#C9A84C !important;
}

section[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#0D0020 0%,#0A0015 100%) !important;
    border-right:1px solid rgba(123,47,255,0.25) !important;
}
section[data-testid="stSidebar"] * { color:#FAF7F0 !important; }

.stitle { font-family:'Orbitron',monospace; font-size:0.78rem; color:#C9A84C !important; letter-spacing:0.15em; text-transform:uppercase; margin-bottom:8px; }
.ssection {
    background:rgba(123,47,255,0.06); border:1px solid rgba(123,47,255,0.2);
    border-left:2px solid #7B2FFF; border-radius:6px;
    padding:10px 14px; margin:8px 0; font-size:0.78rem; line-height:1.8;
    color:rgba(250,247,240,0.6) !important;
}
.sfooter {
    text-align:center; font-size:0.65rem; color:rgba(250,247,240,0.3) !important;
    margin-top:1rem; padding-top:1rem; border-top:1px solid rgba(123,47,255,0.2);
    font-family:'Orbitron',monospace; letter-spacing:0.05em;
}
.sok { font-size:0.72rem; color:#4CAF50 !important; font-family:'Orbitron',monospace; letter-spacing:0.08em; }
.swarn { font-size:0.72rem; color:#C9A84C !important; font-family:'Orbitron',monospace; letter-spacing:0.08em; }

#MainMenu,footer,header{visibility:hidden}
.stDeployButton{display:none}
</style>
""", unsafe_allow_html=True)