import streamlit as st
import sys
import os
import json
from sentence_transformers import SentenceTransformer

# Setup import path for backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from endee_client import EndeeClient

INDEX_NAME = "arxiv_papers"

st.set_page_config(page_title="Endee Semantic Search", layout="centered", page_icon="🔍")

st.title("📚 Endee Semantic Search & RAG Demo")
st.markdown("Search through a curated dataset of AI research papers using the high-performance **Endee Vector Database**.")

@st.cache_resource
def load_embedder():
    # Cache the embedding model so it doesn't reload on every UI interaction
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_resource
def get_endee_client():
    return EndeeClient()

client = get_endee_client()
embedder = load_embedder()

# Connection check
if not client.health():
    st.error("⚠️ **Cannot connect to Endee Vector Database!**\n\nPlease ensure you have started the Endee server via `docker-compose up -d`.")
    st.stop()

query = st.text_input("Ask a question or search for a topic (e.g., 'deep learning architectures')", "")
top_k = st.slider("Number of results to retrieve", min_value=1, max_value=5, value=3)

if st.button("Search") and query.strip():
    with st.spinner("Embedding query and searching Endee..."):
        # 1. Embed user query
        query_vector = embedder.encode(query).tolist()
        
        # 2. Query Endee
        search_results = client.search(INDEX_NAME, query_vector, k=top_k)
        
        # 3. Display Results
        if "results" in search_results and len(search_results["results"]) > 0:
            st.success(f"Found {len(search_results['results'])} relevant documents!")
            
            for rank, result in enumerate(search_results["results"], 1):
                # Endee search result has format like:
                # { "id": "doc_1", "score": 0.85, "meta": "{...}" }
                raw_meta = result.get("meta", "{}")
                try:
                    meta = json.loads(raw_meta)
                except:
                    meta = {"title": "Unknown", "authors": "Unknown", "abstract": "No abstract available."}
                
                score = result.get("score", 0.0)
                
                with st.expander(f"{rank}. {meta.get('title', 'Unknown Paper')} (Score: {score:.4f})", expanded=True):
                    st.markdown(f"**Authors:** {meta.get('authors', 'N/A')}")
                    st.markdown(f"**Abstract:** {meta.get('abstract', 'N/A')}")
        else:
            st.warning("No results found. Have you run the ingestion script (`python backend/ingest.py`) yet?")

st.markdown("---")
st.markdown("Built with [Endee](https://github.com/endee-io/endee) • High-Performance Vector Database")
