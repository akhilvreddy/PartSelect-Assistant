import os
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

def symptom_retrieve(query: str, appliance: str | None = None, k: int = 3):
    """
    Retrieve troubleshooting information from ChromaDB.
    
    Args:
        query: User's troubleshooting question or symptom description
        appliance: Optional appliance filter (dishwasher, refrigerator)
        k: Number of results to return (default 3)
    
    Returns:
        ChromaDB query results with troubleshooting documents
    """
    
    # Setup ChromaDB client
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY not set")
    
    # Get the correct path to ChromaDB - go up from this file to find backend/chroma_store
    current_file = Path(__file__)
    # From services/retrievers/symptom_retriever/symptom_retriever.py -> go up 4 levels to project root
    project_root = current_file.parent.parent.parent.parent.parent
    chroma_path = project_root / "backend" / "chroma_store"
    
    # Connect to ChromaDB
    client = chromadb.Client(
        Settings(
            is_persistent=True,
            persist_directory=str(chroma_path),
        )
    )
    
    embed_fn = OpenAIEmbeddingFunction(api_key=openai_key, model_name="text-embedding-3-small")
    
    # Get the collection
    collection = client.get_collection(
        name="partselect-docs",
        embedding_function=embed_fn
    )
    
    # Build filter for troubleshooting source
    where_filter = {"source": "troubleshooting"}
    
    # Add appliance filter if specified
    if appliance:
        where_filter["appliance"] = appliance
    
    try:
        # Query ChromaDB
        results = collection.query(
            query_texts=[query],
            n_results=k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        return results
        
    except Exception as e:
        print(f"Error in symptom_retrieve: {e}")
        return {"documents": [[]], "metadatas": [[]], "ids": [[]], "distances": [[]]}
