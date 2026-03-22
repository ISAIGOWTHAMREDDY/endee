import requests
import json
from typing import List, Dict, Any, Optional

class EndeeClient:
    def __init__(self, base_url: str = "http://localhost:8080", auth_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Content-Type": "application/json"}
        if auth_token:
            self.headers["Authorization"] = auth_token

    def health(self) -> bool:
        """Check if Endee server is healthy."""
        try:
            resp = requests.get(f"{self.base_url}/api/v1/health", headers=self.headers, timeout=5)
            return resp.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False

    def create_index(self, index_name: str, dim: int, space_type: str = "cosine") -> bool:
        """Create a new index."""
        url = f"{self.base_url}/api/v1/index/create"
        payload = {
            "index_name": index_name,
            "dim": dim,
            "space_type": space_type
        }
        resp = requests.post(url, headers=self.headers, json=payload)
        # Endee might return 409 if index already exists. Let's return True if 200 or 409 (conflict/exists).
        if resp.status_code in [200, 201]:
            return True
        elif resp.status_code == 409:
            print(f"Index {index_name} might already exist or conflict.")
            return True
        else:
            print(f"Failed to create index: {resp.status_code} - {resp.text}")
            return False

    def insert_vectors(self, index_name: str, vectors: List[Dict[str, Any]]) -> bool:
        """
        Insert vectors into index.
        vectors format:
        [
            {
                "id": "doc_1", 
                "vector": [0.1, 0.2, ...], 
                "meta": '{"title": "Paper 1"}', 
                "filter": '{"year": "2023"}'     # optional
            }
        ]
        """
        url = f"{self.base_url}/api/v1/index/{index_name}/vector/insert"
        resp = requests.post(url, headers=self.headers, json=vectors)
        if resp.status_code == 200:
            return True
        else:
            print(f"Failed to insert vectors: {resp.status_code} - {resp.text}")
            return False

    def search(self, index_name: str, query_vector: List[float], k: int = 5) -> Dict[str, Any]:
        """Search the index for nearest neighbors."""
        url = f"{self.base_url}/api/v1/index/{index_name}/search"
        payload = {
            "vector": query_vector,
            "k": k
        }
        resp = requests.post(url, headers=self.headers, json=payload)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"Failed to search: {resp.status_code} - {resp.text}")
            return {}
