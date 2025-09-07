#!/usr/bin/env python3
"""
Debug script to check installation data embedding issues
"""

import os
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_installation_data():
    """Debug the installation data specifically"""
    
    # Setup ChromaDB client
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise SystemExit("OPENAI_API_KEY not set")
    
    # Connect to existing ChromaDB
    client = chromadb.Client(
        Settings(
            is_persistent=True,
            persist_directory="chroma_store",
        )
    )
    
    embed_fn = OpenAIEmbeddingFunction(api_key=openai_key, model_name="text-embedding-3-small")
    
    # Get the collection
    collection = client.get_collection(
        name="partselect-docs",
        embedding_function=embed_fn
    )
    
    print(f"📊 Total documents: {collection.count()}")
    
    # Get all installation documents
    try:
        installation_results = collection.get(
            where={"source": "installation"},
            limit=5  # Just get first 5 for debugging
        )
        
        print(f"\n🔧 Installation documents found: {len(installation_results['ids'])}")
        
        for i, (doc_id, document, metadata) in enumerate(zip(
            installation_results['ids'],
            installation_results['documents'], 
            installation_results['metadatas']
        )):
            print(f"\n📄 Installation Doc {i+1}:")
            print(f"   🆔 ID: {doc_id}")
            print(f"   🔧 Part Number: {metadata.get('part_number', 'N/A')}")
            print(f"   📝 Title: {metadata.get('title', 'N/A')}")
            print(f"   📖 Content Length: {len(document)} chars")
            print(f"   📖 Content Preview: {document[:100]}...")
            
        # Now test the specific query
        print(f"\n🧪 Testing specific query for PS11752991...")
        
        # Direct search for the part number
        results = collection.query(
            query_texts=["PS11752991"],
            n_results=3,
            where={"source": "installation"}
        )
        
        print(f"✅ Found {len(results['ids'][0])} results for 'PS11752991'")
        
        for j, (doc_id, document, metadata, distance) in enumerate(zip(
            results['ids'][0],
            results['documents'][0], 
            results['metadatas'][0],
            results['distances'][0]
        )):
            print(f"\n   📄 Result {j+1} (distance: {distance:.3f}, similarity: {1-distance:.3f})")
            print(f"   🆔 ID: {doc_id}")
            print(f"   🔧 Part Number: {metadata.get('part_number', 'N/A')}")
            print(f"   📖 Content: {document[:200]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_installation_data()
