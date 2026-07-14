# PrivAI — Privacy-First Personal AI Assistant

<div align="center">

**A fully local, multi-agent AI assistant. No cloud. No API keys. Zero data leakage.**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama%20%7C%20Local-black?logo=ollama)](https://ollama.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Privacy: 100% Local](https://img.shields.io/badge/Privacy-100%25%20Local-brightgreen?logo=shield)](docs/privacy_design.md)

</div>

---

## ✨ What is PrivAI?

**PrivAI** is a production-ready, privacy-preserving AI assistant that runs **entirely on your machine**. It combines a multi-agent backend with a polished Streamlit UI — featuring chat, document Q&A, intelligent summarization, and natural language task management — all powered by local LLMs via [Ollama](https://ollama.com/).

> 🔒 **Your data never leaves your device.** No cloud API keys. No telemetry. No data leakage.

---

## 🖥️ UI Preview

<table>
<tr>
<td><img src="docs/screenshots/chat.png" alt="Chat Interface"/><br><em>Multi-Agent Chat with handoff tracing</em></td>
<td><img src="docs/screenshots/tasks.png" alt="Task Manager"/><br><em>Natural Language Task Manager</em></td>
</tr>
</table>

---

## 🚀 Features

### 🤖 Multi-Agent Chat Routing
Messages are classified by intent and routed to specialist agents. Every response shows:
- 🎯 **Detected intent** — what the system thinks you want
- 🤝 **Agent handoff trace** — which agents were invoked
- 📍 **Handling agent** — who answered

### 📄 Document Summarization
Upload PDFs, DOCX, or TXT files and get structured summaries with:
- **Detail levels:** `concise` · `standard` · `detailed`
- **Output formats:** `plain` · `structured` · `study_guide`
- Chunk-by-chunk LLM processing with merge summary

### ✅ Natural Language Task Management
Create tasks from plain English — no forms needed:
- *"Remind me to submit the project report by Friday at 5pm"*
- Deterministic weekday parsing
- Direct editing, priority and status updates from the UI

### 🔍 Document Q&A (RAG)
Ask questions about your uploaded documents using a full RAG pipeline:
- **Embed** → **Retrieve** → **Rerank** → **Generate**
- Powered by ChromaDB + SentenceTransformers + Phi-3 Mini
- Cross-encoder reranking for high-precision answers

### 🛡️ Privacy by Design
- All services bound to `127.0.0.1` (loopback only)
- ChromaDB telemetry explicitly disabled
- Optional AES-256 file encryption
- Optional Differential Privacy noise on embeddings (ε=1.0)
- [Full privacy design →](docs/privacy_design.md)

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────┐
│          PRESENTATION LAYER              │
│   Streamlit UI — localhost:8501          │
│   Chat  │  Summarizer  │  Tasks  │  RAG  │
└──────────────┬───────────────────────────┘
               │ HTTP (loopback only)
┌──────────────▼───────────────────────────┐
│          APPLICATION LAYER               │
│   FastAPI REST API — localhost:8000      │
│   /chat  /summarize  /tasks  /documents  │
└───┬──────┬─────┬──────┬──────────────────┘
    │      │     │      │
    ▼      ▼     ▼      ▼
 Agents   RAG  Tasks  Memory
  Layer   Eng   Mgr    Layer
    │      │            │
    ▼      ▼            ▼
 Ollama ChromaDB     SQLite
 :11434  (local)    (local)
```

**Agent Pipeline:**
```
User Input
    │
    ▼
Intent Detector (TinyLlama, ~0.5s)
    │
    ├── summarize       → Summarizer Agent
    ├── schedule        → Scheduler Agent
    ├── query_document  → Document QA Agent
    ├── list_tasks      → Task Manager Agent
    ├── delete_task     → Task Manager Agent
    └── general_chat    → General Chat Agent
```

---

## 📁 Project Structure

```
PrivAI-main/
├── 📂 app/                     # FastAPI backend
│   ├── agents/                 # Multi-agent system
│   │   ├── intent_detector.py  # TinyLlama intent classifier
│   │   ├── task_planner.py     # Orchestrator / coordinator
│   │   ├── general_chat_agent.py
│   │   ├── scheduler_agent.py
│   │   ├── task_manager_agent.py
│   │   ├── document_qa_agent.py
│   │   └── summarizer_agent.py
│   ├── models/
│   │   ├── llm_client.py       # Ollama wrapper (Phi-3, TinyLlama)
│   │   └── embedder.py         # SentenceTransformers embeddings
│   ├── memory/
│   │   ├── conversation.py     # SQLite chat history
│   │   └── vector_store.py     # ChromaDB interface
│   ├── tools/
│   │   ├── rag_engine.py       # Embed → Retrieve → Rerank → Generate
│   │   ├── scheduler.py        # NLP → task → SQLite
│   │   └── summarizer.py       # Chunk → summarize → merge
│   ├── storage/                # Database + file manager
│   ├── config.py               # All configuration constants
│   └── main.py                 # FastAPI app + all routes
│
├── 📂 ui/                      # Streamlit frontend
│   ├── pages/
│   │   ├── chat.py             # Multi-agent chat page
│   │   ├── summarizer.py       # Document summarization page
│   │   ├── tasks.py            # Task management page
│   │   └── documents.py        # Document Q&A page
│   ├── components/
│   │   └── sidebar.py          # Navigation sidebar
│   └── app.py                  # Streamlit entry point
│
├── 📂 docs/                    # Design documentation
│   ├── architecture.md         # Full system architecture
│   ├── privacy_design.md       # Privacy guarantees & mechanisms
│   └── screenshots/            # UI screenshots
│
├── 📂 evaluation/              # Evaluation scripts
│   └── eval_script.py
│
├── 📂 tests/                   # Unit tests
│   ├── test_rag.py
│   ├── test_scheduler.py
│   └── test_summarizer.py
│
├── 📂 data/                    # Local data (gitignored)
│   ├── documents/              # Uploaded user files
│   ├── vectorstore/            # ChromaDB embeddings
│   └── assistant.db            # SQLite database
│
├── start_assistant.bat         # One-click Windows startup script
├── start_assistant.sh          # One-click Linux/macOS startup script
├── requirements.txt            # Python dependencies
├── conftest.py                 # Pytest configuration
├── CITATION.cff                # Citation file
├── LICENSE                     # MIT License
└── README.md                   # This file
```

---

## ⚡ Quick Start

### Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11+ | [python.org](https://python.org) |
| Ollama | Latest | [ollama.com](https://ollama.com) |
| Java | — | Not required |

### 1. Clone & Install

```bash
git clone https://github.com/Iswaan/PrivAI.git
cd PrivAI
python -m venv venv
```

**Windows:**
```powershell
venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Linux/macOS:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Pull Local Models

```bash
ollama pull phi3:mini      # Primary reasoning model (~2.3GB)
ollama pull tinyllama      # Fast intent classification (~600MB)
```

### 3. Preload RAG Reranker (one-time)

```powershell
venv\Scripts\python.exe -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"
```

### 4. Start — One Command (Windows)

```powershell
.\start_assistant.bat
```

This starts Ollama, FastAPI backend, and Streamlit UI automatically and opens your browser.

### 4. Start — Manual (any platform)

```bash
# Terminal 1: Backend
uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2: Frontend
streamlit run ui/app.py --server.port 8501
```

### 5. Open

| Service | URL |
|---|---|
| 🖥️ Streamlit UI | http://localhost:8501 |
| 📡 FastAPI Docs | http://localhost:8000/docs |
| 🤖 Ollama | http://localhost:11434 |

---

## 🔌 API Reference

The FastAPI backend exposes a clean REST API. Interactive docs at `http://localhost:8000/docs`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/chat` | Send a message (returns intent + agent trace) |
| `POST` | `/summarize` | Upload + summarize a document |
| `GET` | `/summaries` | List summary history |
| `POST` | `/tasks/create` | Create task from natural language |
| `GET` | `/tasks` | List all tasks |
| `PATCH` | `/tasks/{id}` | Update task fields |
| `DELETE` | `/tasks/{id}` | Delete a task |
| `POST` | `/documents/upload` | Upload + index a document |
| `GET` | `/documents` | List uploaded documents |
| `POST` | `/documents/query` | RAG query against documents |
| `GET` | `/history/{session_id}` | Get chat history for session |
| `DELETE` | `/history/{session_id}` | Clear chat history |

---

## ⚙️ Configuration

Edit `app/config.py` to customise:

```python
# LLM Models (Ollama)
PRIMARY_MODEL = "phi3:mini"           # Main reasoning model
FAST_MODEL    = "tinyllama"           # Intent classification

# RAG Settings
CHUNK_SIZE        = 800               # Characters per chunk
TOP_K_RESULTS     = 4                 # Chunks to retrieve
RERANK_TOP_K      = 3                 # Chunks after reranking

# Privacy (optional)
ENABLE_ENCRYPTION = False             # AES-256 file encryption
ENABLE_DP_NOISE   = False             # Differential privacy noise
DP_EPSILON        = 1.0               # ε privacy budget
```

---

## 🧪 Tests

```bash
pytest tests/ -v
```

| Test File | What it Tests |
|---|---|
| `test_rag.py` | RAG indexing, retrieval, and Q&A pipeline |
| `test_scheduler.py` | Task creation from natural language |
| `test_summarizer.py` | Document summarization pipeline |

---

## 🛡️ Privacy Guarantees

| Mechanism | Status |
|---|---|
| All services on `127.0.0.1` only | ✅ Always active |
| No cloud API calls | ✅ Always active |
| ChromaDB telemetry disabled | ✅ Always active |
| No external logging or analytics | ✅ Always active |
| AES-256 file encryption | ⚙️ Optional (`config.py`) |
| Differential Privacy (ε-DP) embeddings | ⚙️ Optional (`config.py`) |

**To delete all personal data:** `rm -rf data/`

Read the full [Privacy Design Document →](docs/privacy_design.md)

---

## 📚 Documentation

- [System Architecture](docs/architecture.md)
- [Privacy Design](docs/privacy_design.md)
- [API Reference](http://localhost:8000/docs) *(when running)*

---

## 🏛️ Affiliation

**Department of Computer Science and Engineering**  
College of Engineering and Computer Science  
Wright State University  
Fairborn, OH 45435, USA

---

## 📄 License

MIT License — see [LICENSE](LICENSE).

---

## 📚 Citation

```bibtex
@misc{PrivAI2026,
  author    = {Iswaan},
  title     = {PrivAI: Privacy-First Local Multi-Agent AI Assistant},
  year      = {2026},
  publisher = {GitHub},
  url       = {https://github.com/Iswaan/PrivAI}
}
```

---

## 🤝 Acknowledgements

- [Ollama](https://ollama.com/) — local LLM inference
- [Phi-3 Mini](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct) — Microsoft
- [TinyLlama](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0) — fast intent classifier
- [ChromaDB](https://www.trychroma.com/) — local vector database
- [SentenceTransformers](https://www.sbert.net/) — local embeddings
- [FastAPI](https://fastapi.tiangolo.com/) — backend framework
- [Streamlit](https://streamlit.io/) — UI framework
