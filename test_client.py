import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from endee_client import EndeeClient

def test():
    client = EndeeClient()
    print("Health:", client.health())
    res = client.search("arxiv_papers", [0.1]*384, k=1)
    print("Search Result Dictionary Keys:", res.keys())
    if "results" in res and len(res["results"]) > 0:
        print("First result score:", res["results"][0].get("score"))
    else:
        print("No results found.")

if __name__ == "__main__":
    test()
