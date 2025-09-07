#!/usr/bin/env python3
"""
List all collections in ChromaDB to debug the collection name issue
"""

import os
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def list_collections():
    """List all collections in ChromaDB"""
    
    # Connect to existing ChromaDB
    client = chromadb.Client(
        Settings(
            is_persistent=True,
            persist_directory="chroma_store",
        )
    )
    
    print("📊 Listing all collections in ChromaDB:")
    
    try:
        collections = client.list_collections()
        print(f"Found {len(collections)} collections:")
        
        for collection in collections:
            print(f"  - Name: {collection.name}")
            print(f"    Count: {collection.count()}")
            print(f"    Metadata: {collection.metadata}")
            print()
            
        if not collections:
            print("❌ No collections found!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_collections()
