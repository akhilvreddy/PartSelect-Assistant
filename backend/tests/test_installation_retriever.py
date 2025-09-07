"""
Test the enhanced installation retriever with direct manual lookup
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from services.retrievers.installation_retriever.installation_retriever import installation_retrieve

def test_installation_retriever():
    """Test installation retriever with various queries"""
    
    print("🔧 TESTING ENHANCED INSTALLATION RETRIEVER")
    print("=" * 60)
    
    test_queries = [
        {
            "name": "Direct Part Number Query",
            "query": "How can I install part number PS11752991?",
            "expected": "Should find installation manual via direct lookup"
        },
        {
            "name": "Another Part Number",
            "query": "Installation instructions for PS10065979",
            "expected": "Should find dishwasher rack adjuster instructions"
        },
        {
            "name": "Natural Language Query",
            "query": "How do I install a refrigerator door cam PS11752991?",
            "expected": "Should extract part number and find manual"
        },
        {
            "name": "Generic Installation Query",
            "query": "How to install dishwasher upper rack adjuster?",
            "expected": "Should use semantic search since no specific part number"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n🧪 TEST {i}: {test['name']}")
        print(f"📝 Query: {test['query']}")
        print(f"🎯 Expected: {test['expected']}")
        print("-" * 40)
        
        try:
            results = installation_retrieve(test['query'])
            
            # Show extracted identifiers
            extracted = results.get("extracted_identifiers", {})
            print(f"🔍 Extracted Parts: {extracted.get('part_numbers', [])}")
            
            # Show strategy used
            strategies = results.get("strategy_used", [])
            print(f"📊 Strategy Used: {', '.join(strategies) if strategies else 'None'}")
            
            # Show direct lookup results
            direct = results.get("direct_lookup", {})
            if direct.get("direct_matches"):
                print(f"✅ Direct Manual Found: {len(direct['direct_matches'])}")
                for match in direct["direct_matches"]:
                    if match.get("type") == "installation_manual":
                        print(f"   📦 Part: {match['part_number']}")
                        print(f"   📝 Title: {match['title']}")
                        print(f"   📖 Instructions: {len(match['installation_text'])} chars")
                        print(f"   🎯 Confidence: {match['confidence']}")
                        print(f"   📄 Preview: {match['installation_text'][:150]}...")
            else:
                print("❌ No direct manual found")
            
            # Show semantic search results
            semantic = results.get("semantic_search", {})
            if semantic.get("documents") and semantic["documents"][0]:
                print(f"🧠 Semantic Results: {len(semantic['documents'][0])}")
                for j, (doc, metadata, distance) in enumerate(zip(
                    semantic["documents"][0][:1],  # Show first 1
                    semantic["metadatas"][0][:1],
                    semantic["distances"][0][:1]
                )):
                    similarity = 1 - distance
                    print(f"   📄 Result {j+1} (similarity: {similarity:.3f})")
                    print(f"   🆔 ID: {metadata.get('part_number', 'N/A')}")
                    print(f"   📖 Preview: {doc[:100]}...")
            else:
                print("❌ No semantic results found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("=" * 60)

if __name__ == "__main__":
    test_installation_retriever()