import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Get the correct path to ChromaDB - go up from this file to find backend/chroma_db
current_file = Path(__file__)
# From services/retrievers/qan_retriever/qan_retriever.py -> go up 3 levels to backend/
backend_dir = current_file.parent.parent.parent.parent
chroma_path = backend_dir / "backend" / "chroma_db"

chroma = chromadb.PersistentClient(path=str(chroma_path))

EMBED_MODEL = "text-embedding-3-small"

def embed_query(text: str):
    emb = client.embeddings.create(model=EMBED_MODEL, input=[text]).data[0].embedding
    return emb

def qan_retrieve(query: str, appliance: str | None = None, k: int = 5):
    collections = {
        "dishwasher": "dishwasher_parts",
        "refrigerator": "refrigerator_parts"
    }
    qvec = embed_query(query)

    def _search(col_name):
        col = chroma.get_collection(col_name)
        return col.query(query_embeddings=[qvec], n_results=k, include=["documents", "metadatas", "distances"])

    if appliance and appliance in collections:
        return _search(collections[appliance])
    else:
        # Search across all collections and combine results
        all_results = {"documents": [], "metadatas": [], "ids": [], "distances": []}
        for col_name in collections.values():
            try:
                col_results = _search(col_name)
                if col_results["documents"]:
                    all_results["documents"].extend(col_results["documents"][0])
                    all_results["metadatas"].extend(col_results["metadatas"][0])
                    all_results["ids"].extend(col_results["ids"][0])
                    all_results["distances"].extend(col_results["distances"][0])
            except Exception as e:
                print(f"Warning: Could not search collection {col_name}: {e}")
                continue
        
        # Sort by distance and return top k
        if all_results["distances"]:
            sorted_indices = sorted(range(len(all_results["distances"])), 
                                  key=lambda i: all_results["distances"][i])[:k]
            return {
                "documents": [[all_results["documents"][i] for i in sorted_indices]],
                "metadatas": [[all_results["metadatas"][i] for i in sorted_indices]],
                "ids": [[all_results["ids"][i] for i in sorted_indices]],
                "distances": [[all_results["distances"][i] for i in sorted_indices]]
            }
        else:
            return {"documents": [[]], "metadatas": [[]], "ids": [[]], "distances": [[]]}