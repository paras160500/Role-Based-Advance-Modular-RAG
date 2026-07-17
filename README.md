# 🏥 Healthcare RAG — Role-Based Document Access with AI Chat

<div align="center">

### 🌐 Live Deployment

| Service | URL | Platform |
|---|---|---|
| 🖥️ **Frontend** | [Open Live App ↗](https://role-based-advance-modular-rag-i7u8hnrednrc5pqe8tgqki.streamlit.app/) | Streamlit Cloud |
| 🚀 **Backend API** | [role-based-advance-modular-rag.onrender.com ↗](https://role-based-advance-modular-rag.onrender.com) | Render |

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB_Atlas-47A248?logo=mongodb&logoColor=white)
![Pinecone](https://img.shields.io/badge/Pinecone-000000?logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?logo=render&logoColor=black)

</div>

---

## 🧠 What Is This?

**Healthcare RAG** is a fully deployed **role-based Retrieval-Augmented Generation system** for the medical domain. The core idea is simple but powerful: **a document uploaded for doctors can only be read by doctors. A document uploaded for nurses stays locked to nurses.** Patients only ever see patient-level content. No cross-role data leakage — ever.

The role check doesn't happen at the application layer. It happens inside **Pinecone at query time**, using metadata filters baked into every vector. Even if someone intercepted the query, they'd only get chunks their role is allowed to see.

---

## ✨ Features at a Glance

| | Feature | Detail |
|---|---|---|
| 🔐 | **Signup & Login** | username · password · role — stored in MongoDB with bcrypt hashing |
| 🛡️ | **Role-Based Document Access** | `admin`, `doctor`, `nurse`, `patient`, `other` — each role is a separate document silo |
| 📄 | **Admin-Only PDF Upload** | Only `admin` users can upload PDFs — target role is stamped into every vector's metadata |
| 🔒 | **Query-Time Role Enforcement** | Pinecone metadata filter + server-side role check per retrieved chunk |
| 🤖 | **Context-Grounded AI Answers** | `llama-3.3-70b-versatile` via Groq answers only from role-authorised context |
| 📚 | **Source Citation** | Every answer includes the source document filename(s) |
| 🌐 | **Fully Deployed** | FastAPI on Render · Streamlit on Streamlit Cloud |

---

## 🏗️ System Pipeline

```mermaid
flowchart TD
    S(["👤 User"])

    SIGN["📝 Sign Up"]
    LOG["🔑 Login · bcrypt verify"]

    ADMIN(["🔑 Admin"])
    USER(["🧑 Doctor / Nurse / Patient / Other"])

    PDF["📄 Upload PDF"]
    CHUNK["✂️ Chunk · 500 tokens"]
    EMBED["🔢 Embed · text-embedding-3-small"]
    UPSERT["🌲 Pinecone · role metadata tag"]

    ASK["❓ Ask Question"]
    QEMBED["🔢 Embed Query"]
    SEARCH["🌐 Pinecone · top_k=3"]
    GUARD["🛡️ Role Check per Chunk"]
    LLM["🤖 llama-3.3-70b · Groq"]
    RES["📬 Answer + Sources"]

    S --> SIGN & LOG
    LOG --> ADMIN & USER
    ADMIN --> PDF --> CHUNK --> EMBED --> UPSERT

    USER --> ASK --> QEMBED --> SEARCH --> GUARD
    GUARD -->|"role match ✅"| LLM --> RES
    GUARD -->|"role mismatch ❌"| BLOCK["🚫 Not Authorised"]

    classDef entry   fill:#7c3aed,stroke:#5b21b6,color:#fff
    classDef auth    fill:#f59e0b,stroke:#d97706,color:#fff
    classDef role    fill:#475569,stroke:#334155,color:#fff
    classDef ingest  fill:#10b981,stroke:#059669,color:#fff
    classDef query   fill:#3b82f6,stroke:#2563eb,color:#fff
    classDef guard   fill:#dc2626,stroke:#b91c1c,color:#fff
    classDef llm     fill:#a855f7,stroke:#9333ea,color:#fff

    class S entry
    class SIGN,LOG auth
    class ADMIN,USER role
    class PDF,CHUNK,EMBED,UPSERT ingest
    class ASK,QEMBED,SEARCH query
    class GUARD,BLOCK guard
    class LLM,RES llm
```

---

## 🔐 How Role-Based Access Works

This is the most important feature in the system. Here's exactly how it's enforced at every level:

### 1. Upload — Role is Stamped into Every Vector

When an admin uploads a PDF and selects a target role (e.g. `doctor`), every chunk from that PDF gets the role embedded in its Pinecone metadata:

```python
metadata = [{
    "source":  file.filename,
    "doc_id":  doc_id,
    "role":    role,          # ← "doctor" / "nurse" / "patient" / "other"
    "page":    chunk.metadata.get("page", 0),
    "text":    chunk.page_content
}]
index.upsert(vectors=list(zip(ids, embeddings, metadata)))
```

### 2. Query — Role is Checked Per Retrieved Chunk

When a user asks a question, Pinecone returns the top-3 most semantically similar chunks. But before any chunk reaches the LLM, each chunk's `role` metadata is checked against the user's authenticated role:

```python
for match in results['matches']:
    metadata = match['metadata']
    if metadata.get("role") == role:          # ← user's role must match chunk's role
        filtered_context.append(metadata['text'])
        sources.add(metadata.get("source"))
    else:
        return {"answer": "You are not authorised to ask question"}
```

> **Why this matters:** even if a nurse's query semantically matches a doctor's document (because the topic is similar), the server rejects it at the chunk level before the LLM ever sees it.

### 3. Upload — Admin-Only Endpoint

The upload endpoint checks the authenticated user's role before processing:

```python
@router.post("/upload_docs")
async def upload_docs(user=Depends(authenticate), ...):
    if user['role'] != "admin":
        raise HTTPException(status_code=401, detail="Only admin can upload docs.")
```

---

## 🗂️ Project Structure

```
Role-Based-Advance-Modular-RAG/
│
├── client/
│   ├── main.py               # Streamlit app — auth UI, upload panel, chat interface
│   └── requirements.txt      # streamlit · requests · python-dotenv
│
├── server/
│   ├── main.py               # FastAPI entry — registers routers + /health + /mongo
│   │
│   ├── auth/
│   │   ├── models.py         # Pydantic: SignupRequest (username, password, role)
│   │   ├── hash_utils.py     # bcrypt hash_password() + verify_password()
│   │   └── routes.py         # POST /signup · GET /login · authenticate() dependency
│   │
│   ├── config/
│   │   └── db.py             # MongoDB Atlas client + users_collection
│   │
│   ├── docs/
│   │   ├── vectorstore.py    # load_vectorstore(): PDF → chunk → embed → Pinecone upsert
│   │   └── routes.py         # POST /upload_docs (admin only)
│   │
│   ├── chat/
│   │   ├── chat_query.py     # answer_query(): embed → Pinecone → role guard → Groq → answer
│   │   └── routes.py         # POST /chat
│   │
│   ├── requirements.txt      # all server dependencies
│   └── upload_docs/          # temp PDF storage (DIABETES.pdf, research papers...)
│
├── main.py                   # Root entry point
├── pyproject.toml            # Project metadata
└── requirements.txt          # Root lockfile
```

---

## 👥 Roles Explained

| Role | Can Upload | Can Chat | Sees |
|---|---|---|---|
| `admin` | ✅ Yes | ✅ Yes | Documents tagged for their own queries |
| `doctor` | ❌ No | ✅ Yes | Only documents tagged `doctor` |
| `nurse` | ❌ No | ✅ Yes | Only documents tagged `nurse` |
| `patient` | ❌ No | ✅ Yes | Only documents tagged `patient` |
| `other` | ❌ No | ✅ Yes | Only documents tagged `other` |

> An admin uploads a PDF and **chooses which role can access it** — doctor, nurse, patient, or other. The system tags every chunk with that role. Users of any other role are blocked at query time.

---

## 📦 Installation & Local Setup

### Prerequisites

- Python 3.12+
- [MongoDB Atlas](https://www.mongodb.com/atlas) account (free tier)
- [Pinecone](https://pinecone.io) account (free tier)
- [Groq](https://console.groq.com) API key (free)
- [OpenAI](https://platform.openai.com) API key (for embeddings)

### 1. Clone

```bash
git clone https://github.com/paras160500/Role-Based-Advance-Modular-RAG.git
cd Role-Based-Advance-Modular-RAG
```

### 2. Install

```bash
pip install -r requirements.txt
```

### 3. Backend `.env` — inside `server/`

```env
# MongoDB
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=healthcare_rag

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=healthcare-rag
PINECONE_ENVIRONMENT=us-east-1

# OpenAI (embeddings only)
OPEN_AI_API=your_openai_api_key

# Groq (LLM generation)
GROQ_API_KEY=your_groq_api_key
```

### 4. Frontend `.env` — inside `client/`

```env
API_URL=http://localhost:8000
# or for live backend:
# API_URL=https://role-based-advance-modular-rag.onrender.com
```

---

## ▶️ Running Locally

```bash
# Terminal 1 — FastAPI backend
cd server
uvicorn main:app --reload --port 8000

# Terminal 2 — Streamlit frontend
cd client
streamlit run main.py
```

Open [http://localhost:8501](http://localhost:8501) — or just open the [live app](https://role-based-advance-modular-rag-i7u8hnrednrc5pqe8tgqki.streamlit.app/) directly.

---

## 🌐 API Reference

Base URL: **`https://role-based-advance-modular-rag.onrender.com`**

### Auth

| Method | Endpoint | Body | Returns |
|---|---|---|---|
| `POST` | `/signup` | `{ username, password, role }` | `{ message }` |
| `GET` | `/login` | HTTP Basic Auth header | `{ message, role }` |

### Documents

| Method | Endpoint | Auth | Body | Returns |
|---|---|---|---|---|
| `POST` | `/upload_docs` | Admin only | `file` (PDF) + `role` (form) | `{ message, doc_id, accessible_to }` |

### Chat

| Method | Endpoint | Auth | Body | Returns |
|---|---|---|---|---|
| `POST` | `/chat` | Any logged-in user | `message` (form) | `{ answer, sources }` or `{ answer: "Not authorised" }` |

### Health

| Method | Endpoint | Returns |
|---|---|---|
| `GET` | `/health` | `{ message: "OK" }` |
| `GET` | `/mongo` | `{ status: "connected successfully." }` |

### Quick Test with curl

```bash
# 1 — Sign up as admin
curl -X POST https://role-based-advance-modular-rag.onrender.com/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"secret","role":"admin"}'

# 2 — Login
curl https://role-based-advance-modular-rag.onrender.com/login \
  -u admin1:secret

# 3 — Upload a PDF for doctors
curl -X POST https://role-based-advance-modular-rag.onrender.com/upload_docs \
  -u admin1:secret \
  -F "file=@DIABETES.pdf" \
  -F "role=doctor"

# 4 — Ask as a doctor
curl -X POST https://role-based-advance-modular-rag.onrender.com/chat \
  -u doctor1:doctorpass \
  -F "message=What are the symptoms of Type 2 diabetes?"
```

---

## ☁️ Deployment

### Backend → Render

| Setting | Value |
|---|---|
| **Root Directory** | `server` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

Add all environment variables in the Render **Environment** tab.

### Frontend → Streamlit Cloud

| Setting | Value |
|---|---|
| **Repository** | `paras160500/Role-Based-Advance-Modular-RAG` |
| **Main file path** | `client/main.py` |

Add `API_URL=https://role-based-advance-modular-rag.onrender.com` under **Secrets**.

---

## ⚡ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit |
| **Backend** | FastAPI + Uvicorn |
| **Authentication** | HTTP Basic Auth + bcrypt |
| **User Storage** | MongoDB Atlas (`users` collection) |
| **Vector Store** | Pinecone Serverless — 1536-dim · dotproduct · role-tagged metadata |
| **Embeddings** | OpenAI `text-embedding-3-small` |
| **LLM** | Groq `llama-3.3-70b-versatile` · `temperature=0.1` |
| **PDF Parsing** | LangChain `PyPDFLoader` |
| **Chunking** | `RecursiveCharacterTextSplitter` — 500 tokens · 100 overlap |
| **Batch Upsert** | Pinecone — batches of 20 vectors |
| **Deployment** | Render (backend) · Streamlit Cloud (frontend) |
| **Language** | Python 3.12+ |

---

## 🧠 Key Design Decisions

- **Role enforcement happens server-side, not client-side.** The Streamlit frontend only hides the upload button from non-admins for UX — the real gate is `if user['role'] != "admin": raise HTTPException(401)` on the FastAPI endpoint.
- **Role metadata is baked into every vector at ingest time.** This means even a direct Pinecone query (bypassing the app) would require knowing the role value to filter correctly.
- **Chunk-level role checking, not query-level.** If the top-3 results include even one chunk from a different role, the entire request is rejected — not just that chunk. This is a strict "all or nothing" policy for safety.
- **`asyncio.to_thread()`** wraps all Pinecone and embedding calls so the FastAPI event loop is never blocked by synchronous I/O.
- **Batch upsert (20 vectors at a time)** prevents Pinecone payload-size errors on large PDFs.
- **MongoDB is used only for user accounts.** Chunk text is stored inside Pinecone's vector metadata (`text` field), avoiding a MongoDB round-trip on every query.

---

## 🔮 Future Improvements

- [ ] **JWT tokens** — replace HTTP Basic Auth with time-limited tokens (credentials aren't sent on every request)
- [ ] **Admin dashboard** — view uploaded documents, delete by `doc_id`, see which roles have access
- [ ] **Chat history** — persist per-user conversation history in MongoDB
- [ ] **Multi-file upload** — current UI handles one file per request; backend supports batching
- [ ] **DOCX + TXT support** — extend `load_vectorstore` beyond PDFs
- [ ] **Streaming responses** — token-by-token answer display in the Streamlit chat UI

---

## 👨‍💻 Author

Built and deployed by **[paras160500](https://github.com/paras160500)**

Role-Based Healthcare RAG · FastAPI · Streamlit · MongoDB · Pinecone · Groq · Render