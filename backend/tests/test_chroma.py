"""
Test ChromaDB setup - check what collections exist and their status
"""
import chromadb
import os
from pathlib import Path

def debug_chroma():
    # Try different possible paths
    possible_paths = [
        "chroma_db",           # Relative to backend/
        "backend/chroma_db",   # From project root
        "../chroma_db",        # If running from backend/
        "./chroma_db"          # Current directory
    ]
    
    print("🔍 Debugging ChromaDB setup...\n")
    
    for path in possible_paths:
        print(f"→ Trying path: {path}")
        
        # Check if path exists
        if Path(path).exists():
            print(f"  ✅ Path exists: {Path(path).absolute()}")
        else:
            print(f"  ❌ Path does not exist: {Path(path).absolute()}")
            continue
            
        try:
            # Try to connect
            chroma = chromadb.PersistentClient(path=path)
            print(f"  ✅ Connected to ChromaDB")
            
            # List collections
            collections = chroma.list_collections()
            print(f"  📊 Found {len(collections)} collections:")
            
            for col in collections:
                print(f"    - {col.name}: {col.count()} documents")
                
            if len(collections) == 0:
                print("  ⚠️ No collections found - database is empty")
            
            return chroma, path  # Return successful connection
            
        except Exception as e:
            print(f"  ❌ Error connecting: {e}")
            continue
    
    print("\n❌ Could not connect to ChromaDB with any path")
    return None, None

def check_data_files():
    print("\n🗂️ Checking data files...")
    
    data_files = [
        "data/appliance_parts_dishwasher.csv",
        "data/appliance_parts_refrigerator.csv",
        "../data/appliance_parts_dishwasher.csv",
        "../data/appliance_parts_refrigerator.csv"
    ]
    
    for file_path in data_files:
        if Path(file_path).exists():
            print(f"  ✅ Found: {Path(file_path).absolute()}")
        else:
            print(f"  ❌ Missing: {Path(file_path).absolute()}")

if __name__ == "__main__":
    chroma, working_path = debug_chroma()
    check_data_files()
    
    if chroma is None:
        print("\n💡 Suggestions:")
        print("1. Make sure you've run the ingestion script: python scripts/ingest_parts.py")
        print("2. Check that your CSV files exist in the data/ directory")
        print("3. Verify the ChromaDB path in your code")
    else:
        print(f"\n✅ ChromaDB is working with path: {working_path}")
