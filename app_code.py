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
