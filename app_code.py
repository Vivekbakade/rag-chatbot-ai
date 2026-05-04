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

# ── IMPORTS ───────────────────────────────────────────────────────────────────
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS

# ── HELPERS ───────────────────────────────────────────────────────────────────
def set_api_key(key):
    os.environ["GOOGLE_API_KEY"] = key

def get_pdf_text(files):
    pages = []
    for f in files:
        reader = PdfReader(f)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages.append((f.name, i+1, text))
    return pages

def get_docx_text(files):
    pages = []
    for f in files:
        doc = DocxDocument(f)
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        if text.strip():
            pages.append((f.name, 1, text))
    return pages

def get_txt_text(files):
    pages = []
    for f in files:
        text = f.read().decode("utf-8", errors="ignore")
        if text.strip():
            pages.append((f.name, 1, text))
    return pages

def build_chunks(pages):
    splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len)
    chunks, metas = [], []
    for fname, pg, text in pages:
        for chunk in splitter.split_text(text):
            chunks.append(chunk)
            metas.append({"source": fname, "page": pg})
    return chunks, metas

def get_vectorstore(chunks, metas):
    emb = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return FAISS.from_texts(texts=chunks, embedding=emb, metadatas=metas)

def ask_question(vs, question):
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    docs = vs.similarity_search(question, k=4)
    context = "\n\n".join([d.page_content for d in docs])
    seen, citations = set(), []
    for d in docs:
        key = f"{d.metadata.get('source')}-{d.metadata.get('page')}"
        if key not in seen:
            seen.add(key)
            citations.append(f"**{d.metadata.get('source')}** — page {d.metadata.get('page')}")
    prompt = f"""Answer ONLY from the context below. If not found say: "I couldn't find this in the documents."

Context:
{context}

Question: {question}
Answer:"""
    answer = llm.invoke(prompt).content
    if citations:
        answer += "\n\n---\n🔍 **Sources:** " + " · ".join(citations)
    return answer

def summarize_all(vs):
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    docs = vs.similarity_search("summary overview key points conclusions", k=8)
    context = "\n\n".join([d.page_content for d in docs])
    return llm.invoke(f"Write a comprehensive, well-structured summary of this content:\n\n{context}").content

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">◈ AI-POWERED DOCUMENT INTELLIGENCE ◈</div>
    <div class="hero-title">DOCCHAT AI</div>
    <div class="hero-sub">Neural Document Analysis · Powered by Google Gemini</div>
    <div class="hero-links">
        Built by <strong style="color:#C9A84C;font-family:'Orbitron',monospace;">VIVEK BAKADE</strong>
        &nbsp;·&nbsp;<a href="mailto:vivekbakade14@gmail.com">vivekbakade14@gmail.com</a>
        &nbsp;·&nbsp;<a href="https://linkedin.com/in/vivek-bakade-a2726224b" target="_blank">LinkedIn</a>
        &nbsp;·&nbsp;<a href="https://github.com/Vivekbakade" target="_blank">GitHub</a>
    </div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='stitle'>⬡ API Configuration</div>", unsafe_allow_html=True)

    typed_key = st.text_input("key", type="password", placeholder="AIzaSy...", label_visibility="collapsed")
    if typed_key and typed_key.strip().startswith("AIza"):
        st.session_state.api_key = typed_key.strip()

    st.markdown("<div style='font-size:0.7rem;color:rgba(250,247,240,0.35);margin-bottom:10px;'>Never stored. <a href='https://aistudio.google.com' target='_blank' style='color:#C9A84C;'>Get free key →</a></div>", unsafe_allow_html=True)

    if st.session_state.api_key:
        st.markdown("<div class='sok'>◉ SYSTEM ONLINE</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='swarn'>◎ AWAITING API KEY</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='stitle'>⬡ Upload Documents</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.72rem;color:rgba(250,247,240,0.4);margin-bottom:6px;'>PDF · DOCX · TXT</div>", unsafe_allow_html=True)

    pdf_docs  = st.file_uploader("PDF",  accept_multiple_files=True, type=["pdf"],  label_visibility="collapsed")
    docx_docs = st.file_uploader("DOCX", accept_multiple_files=True, type=["docx"], label_visibility="collapsed")
    txt_docs  = st.file_uploader("TXT",  accept_multiple_files=True, type=["txt"],  label_visibility="collapsed")

    if st.button("⚡ PROCESS DOCUMENTS", use_container_width=True):
        if not st.session_state.api_key:
            st.error("⚠️ Enter your Gemini API key first.")
        else:
            total = len(pdf_docs or []) + len(docx_docs or []) + len(txt_docs or [])
            if total == 0:
                st.error("Upload at least one file.")
            else:
                set_api_key(st.session_state.api_key)
                with st.spinner(f"Processing {total} file(s)..."):
                    pages = []
                    if pdf_docs:  pages += get_pdf_text(pdf_docs)
                    if docx_docs: pages += get_docx_text(docx_docs)
                    if txt_docs:  pages += get_txt_text(txt_docs)
                    chunks, metas = build_chunks(pages)
                    st.session_state.vectorstore = get_vectorstore(chunks, metas)
                    st.session_state.chat_history = []
                st.success(f"✓ {len(chunks)} chunks ready!")

    st.markdown("""<div class='ssection'>
        <strong style='color:#C9A84C;'>PROTOCOL:</strong><br>
        01 · Enter Gemini API key<br>
        02 · Upload documents<br>
        03 · Click PROCESS<br>
        04 · Ask questions<br>
        05 · Use Summarize
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='sfooter'>VIVEK BAKADE<br>AI PM PORTFOLIO · 2025</div>", unsafe_allow_html=True)

# ── MAIN ─────────────────────────────────────────────────────────────────────
if not st.session_state.api_key:
    st.markdown("""<div class='api-banner'>
        <strong>◎ SYSTEM AWAITING AUTHORIZATION</strong><br>
        Enter your free Google Gemini API key in the sidebar to activate DocChat AI.<br>
        Get one free (no credit card) at <a href='https://aistudio.google.com' target='_blank'>aistudio.google.com</a>
    </div>""", unsafe_allow_html=True)

for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"<div class='msg-user'><div class='bubble-user'>{msg['content']}</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='msg-bot'><div class='avatar-bot'>⬡</div><div class='bubble-bot'>{msg['content']}</div></div>", unsafe_allow_html=True)

user_question = st.text_input("q", placeholder="⬡  Ask anything about your documents...", label_visibility="collapsed")

col1, col2, _ = st.columns([1.3, 1, 4])
with col1:
    if st.button("◈ SUMMARIZE ALL"):
        if not st.session_state.api_key:
            st.warning("Enter API key first.")
        elif st.session_state.vectorstore:
            set_api_key(st.session_state.api_key)
            with st.spinner("Generating summary..."):
                try:
                    summary = summarize_all(st.session_state.vectorstore)
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        summary = "⚠️ **API Rate Limit Hit** — Please wait 1 minute and try again."
                    else:
                        summary = f"⚠️ **Error:** {str(e)}"
            st.session_state.chat_history.append({"role": "user", "content": "Summarize all documents"})
            st.session_state.chat_history.append({"role": "bot", "content": summary})
            st.rerun()
        else:
            st.warning("Process documents first.")

with col2:
    if st.button("⬡ CLEAR"):
        st.session_state.chat_history = []
        st.session_state.vectorstore = None
        st.rerun()

if user_question:
    if not st.session_state.api_key:
        st.warning("Enter API key in sidebar first.")
    elif st.session_state.vectorstore:
        set_api_key(st.session_state.api_key)
        with st.spinner("Analyzing..."):
            try:
                answer = ask_question(st.session_state.vectorstore, user_question)
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    answer = "⚠️ **API Rate Limit Hit** — Free quota exceeded. Wait 1 minute or use a new API key from [aistudio.google.com](https://aistudio.google.com)"
                else:
                    answer = f"⚠️ **Error:** {str(e)}"
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        st.session_state.chat_history.append({"role": "bot", "content": answer})
        st.rerun()
    else:
        st.warning("Upload and process your documents first.")
