# Endee AI RAG System: Scientific AI Papers 📚🔍

A practical, high-performance **Semantic Search and Retrieval-Augmented Generation (RAG)** application leveraging the [Endee Vector Database](https://github.com/endee-io/endee). This project demonstrates how to ingest, index, and retrieve dense vector embeddings for natural language search queries against a corpus of leading AI research abstracts.

## 🚀 Project Overview
Traditional keyword search often fails to capture the underlying meaning or intent of a query. In this project, we utilize the modern AI paradigm of semantic vector search. By converting both documents and search queries into high-dimensional numerical vectors (embeddings), we can find conceptually similar texts even if they don't share exact words.

**Core technology stack:**
- **Endee Vector Database:** Selected for its speed, lightweight footprint, and efficient C++ REST API implementation.
- **Hugging Face (`sentence-transformers`):** Used `all-MiniLM-L6-v2` to vectorize queries and documents efficiently into a 384-dimensional space.
- **Streamlit:** Serves the frontend web interface, creating a rapid, reactive UI for querying.
- **Python / FastAPI (via `requests` calls):** Glues the embedding engine and the Endee REST API (`/api/v1/index/create`, `/insert`, `/search`).

## 🏯 System Design

The architecture of this AI/ML system involves three major layers:

1. **Vector Storage Layer (Endee via Docker):**
   - Endee is executed natively within a Docker container to ensure cross-platform compatibility without manual C++ builds. It receives incoming API queries on port `8080`.
   - The data is mounted to a local `./endee-data` volume so your vector index survives container restarts.
   
2. **Ingestion Pipeline (`backend/ingest.py`):**
   - Fetches an in-memory batch of popular AI research paper abstracts (e.g., Attention Is All You Need, BERT, LLaMA 2).
   - Initializes the Hugging Face `all-MiniLM-L6-v2` transformer model.
   - Encodes text into 384D float vectors.
   - Posts the vectors and their stringified JSON metadata to Endee DB via `EndeeClient.insert_vectors()`.
   
3. **Retrieval Application (`frontend/app.py`):**
   - A reactive user interface. When a user queries (e.g., "Natural Language Understanding models"), the string is vectorized through the same `MiniLM` model.
   - Searches Endee DB utilizing the `EndeeClient.search()`, calculating similarities inside Endee's optimized indexes.
   - Top-K results are returned and decoded, revealing paper titles, authors, and abstracts.

## 🛠️ How Endee is Used

Endee is placed perfectly in the center of the retrieval pipeline. This repository natively integrates via its REST API standard:
- **`POST /api/v1/index/create`**: We programmatically create an index (`arxiv_papers`) configured to `dim=384` and `space_type="cosine"`.
- **`POST /api/v1/index/<string>/vector/insert`**: Each embedded paper is bundled together into a standard JSON array and shipped to Endee in batches. Custom parameters like *paper title* are serialized into the Endee `meta` parameter.
- **`POST /api/v1/index/<string>/search`**: Using the incoming query embedding array, we search Endee natively and grab the closest Euclidean/Cosine distances natively parsed as matching papers.

---

## 🏃 Setup and Execution Instructions

### Prerequisites
1. **Docker Desktop** installed and running (for local Endee instantiation).
2. **Python 3.9+** installed.

### Step 1: Start the Endee Vector Database
In your console, run docker compose to spin up the Endee database:
```bash
docker-compose up -d
```
Check if it correctly booted by visiting `http://localhost:8080` or seeing the port bound.

### Step 2: Set up your Python Environment
Open a terminal in the root directory and create a virtual environment:
```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Ingest Data
Before we can search, we must build the index and generate the embeddings.
```bash
python backend/ingest.py
```
*You should see logs indicating successful model load, index creation, and insertion.*

### Step 4: Run the Web UI
Launch the Streamlit web dashboard:
```bash
streamlit run frontend/app.py
```

It will automatically open a browser window displaying the UI. Type in queries to test the Semantic Search engine dynamically! 

---
### Future Improvements
To expand this into a full end-to-end autonomous Agent or Chatbot:
1. Parse User Query -> Retrieve Context from Endee -> Supply Context to Open-Source LLM (e.g., `llama-cpp-python` or `Ollama`) to generate an intelligent natural language response!
