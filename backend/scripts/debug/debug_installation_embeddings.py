#!/usr/bin/env python3
"""
Debug installation embeddings specifically in ChromaDB
"""

import os
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

def debug_installation_embeddings():
    """Debug installation embeddings in ChromaDB"""
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY not set")
    
    # Connect to ChromaDB
    project_root = Path(__file__).parent.parent.parent
    chroma_path = project_root / "backend" / "chroma_store"
    
    client = chromadb.Client(
        Settings(
            is_persistent=True,
            persist_directory=str(chroma_path),
        )
    )
    
    embed_fn = OpenAIEmbeddingFunction(api_key=openai_key, model_name="text-embedding-3-small")
    collection = client.get_collection(
        name="partselect-docs",
        embedding_function=embed_fn
    )
    
    print("🔍 INSTALLATION EMBEDDINGS DEBUG")
    print("=" * 50)
    
    # Get all installation documents
    try:
        installation_docs = collection.get(
            where={"source": "installation"},
            limit=10  # Get first 10 for analysis
        )
        
        print(f"📊 Found {len(installation_docs['ids'])} installation documents")
        
        # Analyze first few documents
        for i, (doc_id, document, metadata) in enumerate(zip(
            installation_docs['ids'][:5],
            installation_docs['documents'][:5], 
            installation_docs['metadatas'][:5]
        )):
            print(f"\n📄 Installation Doc {i+1}:")
            print(f"   🆔 ID: {doc_id}")
            print(f"   🔧 Part Number: {metadata.get('part_number', 'N/A')}")
            print(f"   📝 Title: {metadata.get('title', 'N/A')}")
            print(f"   📖 Content Length: {len(document)} chars")
            print(f"   📖 Content Preview: {document[:100]}...")
            print(f"   ⚙️  Difficulty: '{metadata.get('difficulty', '')}'")
            print(f"   ⏱️  Time: '{metadata.get('time_required', '')}'")
            print(f"   🛠️  Tools: '{metadata.get('tools', '')}'")
            
        print(f"\n🧪 TESTING SPECIFIC QUERIES:")
        
        # Test 1: Direct part number search
        print(f"\n--- Test 1: Direct part number search ---")
        results1 = collection.query(
            query_texts=["PS11752991"],
            n_results=3,
            where={"source": "installation"}
        )
        
        print(f"Results for 'PS11752991': {len(results1['ids'][0])} found")
        for j, (doc_id, distance) in enumerate(zip(results1['ids'][0], results1['distances'][0])):
            similarity = 1 - distance
            print(f"   {j+1}. {doc_id} (similarity: {similarity:.3f}, distance: {distance:.3f})")
        
        # Test 2: Installation query
        print(f"\n--- Test 2: Installation query ---")
        results2 = collection.query(
            query_texts=["How can I install part number PS11752991?"],
            n_results=3,
            where={"source": "installation"}
        )
        
        print(f"Results for installation query: {len(results2['ids'][0])} found")
        for j, (doc_id, distance) in enumerate(zip(results2['ids'][0], results2['distances'][0])):
            similarity = 1 - distance
            print(f"   {j+1}. {doc_id} (similarity: {similarity:.3f}, distance: {distance:.3f})")
            
        # Test 3: Compare with other sources
        print(f"\n--- Test 3: Compare with compatibility ---")
        results3 = collection.query(
            query_texts=["How can I install part number PS11752991?"],
            n_results=3,
            where={"source": "compatibility"}
        )
        
        print(f"Compatibility results for same query: {len(results3['ids'][0])} found")
        for j, (doc_id, distance) in enumerate(zip(results3['ids'][0], results3['distances'][0])):
            similarity = 1 - distance
            print(f"   {j+1}. {doc_id} (similarity: {similarity:.3f}, distance: {distance:.3f})")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_installation_embeddings()
