"""
Test the enhanced compatibility retriever with various query types
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from services.retrievers.compatibility_retriever.compatibility_retriever import compatibility_retrieve

def test_enhanced_compatibility():
    """Test various compatibility query patterns"""
    
    print("🧪 TESTING ENHANCED COMPATIBILITY RETRIEVER")
    print("=" * 60)
    
    test_queries = [
        {
            "name": "Part-to-Model Query",
            "query": "Is PS10065979 compatible with my appliance?",
            "expected": "Should find models via direct JSON lookup"
        },
        {
            "name": "Model-to-Parts Query", 
            "query": "What parts fit my 66512762K314 dishwasher?",
            "expected": "Should find parts via direct JSON lookup"
        },
        {
            "name": "Cross-Check Query",
            "query": "Is PS10065979 compatible with 66512762K314?",
            "expected": "Should cross-check compatibility with VERY_HIGH confidence"
        },
        {
            "name": "Natural Language Query",
            "query": "Does part PS11752991 work with my WDT780SAEM1 model?", 
            "expected": "Should extract both identifiers and cross-check"
        },
        {
            "name": "Fuzzy Query (Semantic Fallback)",
            "query": "What Whirlpool dishwasher door seals are available?",
            "expected": "Should use semantic search since no specific identifiers"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n🧪 TEST {i}: {test['name']}")
        print(f"📝 Query: {test['query']}")
        print(f"🎯 Expected: {test['expected']}")
        print("-" * 40)
        
        try:
            results = compatibility_retrieve(test['query'])
            
            # Show extracted identifiers
            extracted = results.get("extracted_identifiers", {})
            print(f"🔍 Extracted Parts: {extracted.get('part_numbers', [])}")
            print(f"🔍 Extracted Models: {extracted.get('model_numbers', [])}")
            
            # Show strategy used
            strategies = results.get("strategy_used", [])
            print(f"📊 Strategy Used: {', '.join(strategies) if strategies else 'None'}")
            
            # Show direct lookup results
            direct = results.get("direct_lookup", {})
            if direct.get("direct_matches"):
                print(f"✅ Direct Matches Found: {len(direct['direct_matches'])}")
                for match in direct["direct_matches"]:
                    match_type = match.get("type")
                    if match_type == "part_to_models":
                        print(f"   📦 {match['part_number']} → {match['count']} models")
                        print(f"   🏷️  Models: {match['compatible_models'][:5]}...")  # Show first 5
                    elif match_type == "model_to_parts":
                        print(f"   🔧 {match['model_number']} → {match['count']} parts")
                        print(f"   📦 Parts: {match['compatible_parts']}")
                    elif match_type == "cross_check":
                        for check in match["cross_check_results"]:
                            compatibility = "✅ COMPATIBLE" if check["is_compatible"] else "❌ NOT COMPATIBLE"
                            print(f"   🔄 {check['part_number']} + {check['model_number']}: {compatibility}")
                            print(f"   🎯 Confidence: {check['confidence']}")
            else:
                print("❌ No direct matches found")
            
            # Show semantic search results
            semantic = results.get("semantic_search", {})
            if semantic.get("documents") and semantic["documents"][0]:
                print(f"🧠 Semantic Results: {len(semantic['documents'][0])}")
                for j, (doc, metadata, distance) in enumerate(zip(
                    semantic["documents"][0][:2],  # Show first 2
                    semantic["metadatas"][0][:2],
                    semantic["distances"][0][:2]
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
    test_enhanced_compatibility()
