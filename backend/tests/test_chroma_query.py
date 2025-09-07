"""
Test ChromaDB querying to see if embeddings and search work properly
"""
import chromadb
from pathlib import Path
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_chroma_basic():
    """Test basic ChromaDB functionality without embeddings"""
    print("🧪 Testing basic ChromaDB functionality...\n")
    
    # Get the correct path
    chroma_path = Path(__file__).parent / "backend" / "chroma_db"
    print(f"📍 ChromaDB path: {chroma_path}")
    
    try:
        chroma = chromadb.PersistentClient(path=str(chroma_path))
        
        # List collections
        collections = chroma.list_collections()
        print(f"📊 Found {len(collections)} collections:")
        
        for col in collections:
            print(f"  - {col.name}: {col.count()} documents")
            
            # Get a few sample documents
            sample = col.get(limit=3, include=["documents", "metadatas"])
            print(f"    Sample documents:")
            for i, (doc, meta) in enumerate(zip(sample["documents"], sample["metadatas"])):
                print(f"      [{i+1}] Text: {doc[:100]}...")
                print(f"          Meta: {meta}")
                
        return chroma, collections
        
    except Exception as e:
        print(f"❌ Error connecting to ChromaDB: {e}")
        return None, None

def test_text_search(chroma, collection_name="dishwasher_parts"):
    """Test text-based search (without embeddings)"""
    print(f"\n🔍 Testing text search in {collection_name}...\n")
    
    try:
        col = chroma.get_collection(collection_name)
        
        # Try simple text search queries
        test_queries = [
            "pump",
            "door",
            "seal",
            "motor"
        ]
        
        for query in test_queries:
            print(f"🔎 Searching for: '{query}'")
            
            # Simple text search (no embeddings)
            results = col.query(
                query_texts=[query],
                n_results=3,
                include=["documents", "metadatas", "distances"]
            )
            
            if results["documents"][0]:
                print(f"  ✅ Found {len(results['documents'][0])} results:")
                for i, (doc, meta, dist) in enumerate(zip(
                    results["documents"][0], 
                    results["metadatas"][0], 
                    results["distances"][0]
                )):
                    print(f"    [{i+1}] Distance: {dist:.4f}")
                    print(f"        Text: {doc[:150]}...")
                    print(f"        Part: {meta.get('part_id', 'N/A')}")
            else:
                print("  ❌ No results found")
            print()
            
    except Exception as e:
        print(f"❌ Error with text search: {e}")

def test_embedding_search(chroma, collection_name="dishwasher_parts"):
    """Test embedding-based search"""
    print(f"\n🧠 Testing embedding search in {collection_name}...\n")
    
    try:
        # Check if OpenAI API key is available
        if not os.environ.get("OPENAI_API_KEY"):
            print("❌ No OPENAI_API_KEY found - skipping embedding test")
            return
            
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        col = chroma.get_collection(collection_name)
        
        test_queries = [
            "dishwasher not draining water",
            "door won't close properly",
            "pump making noise",
            "water leak under appliance"
        ]
        
        for query in test_queries:
            print(f"🧠 Embedding search for: '{query}'")
            
            try:
                # Generate embedding
                emb_response = client.embeddings.create(
                    model="text-embedding-3-small", 
                    input=[query]
                )
                query_embedding = emb_response.data[0].embedding
                
                # Search with embedding
                results = col.query(
                    query_embeddings=[query_embedding],
                    n_results=3,
                    include=["documents", "metadatas", "distances"]
                )
                
                if results["documents"][0]:
                    print(f"  ✅ Found {len(results['documents'][0])} results:")
                    for i, (doc, meta, dist) in enumerate(zip(
                        results["documents"][0], 
                        results["metadatas"][0], 
                        results["distances"][0]
                    )):
                        print(f"    [{i+1}] Distance: {dist:.4f}")
                        print(f"        Text: {doc[:150]}...")
                        print(f"        Part: {meta.get('part_id', 'N/A')}")
                else:
                    print("  ❌ No results found")
                    
            except Exception as e:
                print(f"  ❌ Error generating embedding: {e}")
            print()
            
    except Exception as e:
        print(f"❌ Error with embedding search: {e}")

def main():
    print("🚀 ChromaDB Query Test\n")
    
    # Test basic functionality
    chroma, collections = test_chroma_basic()
    
    if not chroma or not collections:
        print("❌ Cannot proceed - ChromaDB connection failed")
        return
    
    # Test text search
    if any(col.name == "dishwasher_parts" for col in collections):
        test_text_search(chroma, "dishwasher_parts")
    
    # Test embedding search
    if any(col.name == "dishwasher_parts" for col in collections):
        test_embedding_search(chroma, "dishwasher_parts")
    
    print("✅ ChromaDB query test complete!")

if __name__ == "__main__":
    main()
