#  DocChat AI — RAG-Based Document Q&A Chatbot

> Built by Vivek Bakade | [vivekbakade14@gmail.com] | [LinkedIn](https://linkedin.com/in/vivek-bakade-a2726224b) |

PRD =  https://drive.google.com/file/d/1sPhOV9Bsb3uYXVEqwvO9kxMzsLaeZYCy/view?usp=drive_link
---

##  Product Overview (PM Framing)

**Problem:** Knowledge workers waste 2+ hours/day searching through documents for specific information. PDFs, reports, and manuals are not conversational — they require manual reading.

**Solution:** An AI-powered RAG chatbot that lets users upload any document and ask questions in natural language — getting instant, cited answers.

**Target Users:** Students, researchers, analysts, legal professionals, HR teams — anyone who works with document-heavy workflows.

**Business Value:** Reduces document search time by ~70%. Applicable as internal knowledge base tool for SMEs, reducing support ticket volume.

### Success Metrics
| Metric | Target |
| Query response time | < 5 seconds |
| Answer relevance (user rating) | > 80% helpful |
| Supported file types | PDF, DOCX, TXT |
| Source citation accuracy | 100% (page-level) |

---

##  Features (Beyond Basic Tutorial)

| Feature | Description |
| **Source Citations** | Every answer shows exact filename + page number |
| **Multi-format Support** | PDF, Word (.docx), and Text (.txt) files |
| **Summarize All Docs** | One-click summary of all uploaded documents |
| **Conversation Memory** | Remembers previous questions in session |
| **Multi-file Upload** | Upload and query multiple documents simultaneously |

---

##  Tech Stack

```
Frontend:     Streamlit
LLM:          OpenAI GPT-3.5-turbo
Embeddings:   OpenAI text-embedding-ada-002
Vector Store: FAISS (Facebook AI Similarity Search)
Framework:    LangChain
File Parsing: PyPDF2, python-docx
```

---

##  Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/Vivekbakade/rag-chatbot-ai
cd rag-chatbot-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > .env

# 4. Run
streamlit run app.py
```

##  Product Roadmap

-  PDF support with source citations
-  Word + TXT file support
-  Document summarization
-  Conversation memory
-  Local LLM via Ollama (privacy mode)
-  Export chat history as PDF
-  Table/chart extraction from PDFs
-  Multi-language support

---](https://github.com/Vivekbakade/rag-chatbot-ai)


