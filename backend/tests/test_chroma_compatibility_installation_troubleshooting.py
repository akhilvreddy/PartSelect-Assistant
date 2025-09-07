#!/usr/bin/env python3
"""
Test script to verify ChromaDB ingestion and search functionality
Tests compatibility, installation, and troubleshooting queries
"""

import os
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_chroma_queries():
    """Test the ChromaDB with sample queries for each data source"""
    
    # Setup ChromaDB client
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise SystemExit("OPENAI_API_KEY not set")
    
    print(f"🔑 OpenAI API Key found: {'YES' if openai_key else 'NO'}")
    
    # Connect to existing ChromaDB (use backend/chroma_store)
    client = chromadb.Client(
        Settings(
            is_persistent=True,
            persist_directory="backend/chroma_store",
        )
    )
    
    embed_fn = OpenAIEmbeddingFunction(api_key=openai_key, model_name="text-embedding-3-small")
    
    # Get the collection
    collection = client.get_collection(
        name="partselect-docs",
        embedding_function=embed_fn
    )
    
    print(f"📊 Collection info: {collection.count()} documents loaded")
    print("=" * 60)
    
    # Test queries
    test_cases = [
        {
            "category": "COMPATIBILITY",
            "query": "Is this part (PS10065979) compatible with my WDT780SAEM1 model?",
            "filter": {"source": "compatibility"},
            "description": "Testing compatibility search for dishwasher model WDT780SAEM1"
        },
        {
            "category": "TROUBLESHOOTING", 
            "query": "The ice maker on my Whirlpool fridge is not working. How can I fix it?",
            "filter": {"source": "troubleshooting"},
            "description": "Testing troubleshooting search for ice maker issues"
        },
        {
            "category": "INSTALLATION",
            "query": "How can I install part number PS11752991?",
            "filter": {"source": "installation"},
            "description": "Testing installation instructions for specific part number"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: {test_case['category']}")
        print(f"📝 Query: {test_case['query']}")
        print(f"🎯 Description: {test_case['description']}")
        print(f"🔍 Filter: {test_case['filter']}")
        
        try:
            # Query with metadata filter
            results = collection.query(
                query_texts=[test_case['query']],
                n_results=3,
                where=test_case['filter']
            )
            
            print(f"✅ Found {len(results['ids'][0])} results")
            
            # Display results
            for j, (doc_id, document, metadata, distance) in enumerate(zip(
                results['ids'][0],
                results['documents'][0], 
                results['metadatas'][0],
                results['distances'][0]
            )):
                print(f"\n   📄 Result {j+1} (similarity: {1-distance:.3f})")
                print(f"   🆔 ID: {doc_id}")
                print(f"   🏷️  Source: {metadata.get('source', 'N/A')}")
                print(f"   🔧 Appliance: {metadata.get('appliance', 'N/A')}")
                
                # Source-specific metadata
                if metadata.get('source') == 'compatibility':
                    print(f"   🎯 Models: {metadata.get('models', 'N/A')[:100]}...")
                    print(f"   🏢 Brands: {metadata.get('brands', 'N/A')}")
                elif metadata.get('source') == 'troubleshooting':
                    print(f"   🚨 Symptom: {metadata.get('symptom', 'N/A')}")
                    print(f"   🔧 Common Parts: {metadata.get('common_parts', 'N/A')}")
                elif metadata.get('source') == 'installation':
                    print(f"   ⚡ Difficulty: {metadata.get('difficulty', 'N/A')}")
                    print(f"   ⏱️  Time Required: {metadata.get('time_required', 'N/A')}")
                    print(f"   🛠️  Tools: {metadata.get('tools', 'N/A')}")
                
                print(f"   📖 Content: {document[:200]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 60)
    
    # General stats
    print(f"\n📈 COLLECTION STATS:")
    try:
        # Count by source
        for source in ['compatibility', 'installation', 'troubleshooting']:
            count = collection.count(where={"source": source})
            print(f"   {source.capitalize()}: {count} documents")
    except Exception as e:
        print(f"   Error getting stats: {e}")

if __name__ == "__main__":
    test_chroma_queries()
