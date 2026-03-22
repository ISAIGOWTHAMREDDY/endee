import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from endee_client import EndeeClient

app = FastAPI(title="Endee Premium Search API", description="AI Semantic Search Backend")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Model and Endee Vector DB Client globally
print("Loading Embedding Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
client = EndeeClient()
INDEX_NAME = "arxiv_papers"

class SearchRequest(BaseModel):
    query: str
    k: int = 5

@app.get("/api/health")
def health():
    return {
        "status": "online",
        "endee_database_connected": client.health()
    }

@app.post("/api/search")
def search(req: SearchRequest):
    if not req.query or req.query.strip() == "":
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # 1. Embed query
    query_vector = model.encode(req.query).tolist()
    
    # 2. Search Endee Database
    search_results = client.search(INDEX_NAME, query_vector, k=req.k)
    
    return search_results

# Mount static frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
