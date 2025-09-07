"""
Test the agent_manager flow to see where the RAG integration is failing
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test if all imports work"""
    print("🔧 Testing imports...\n")
    
    try:
        from agent_manager import AgentManager
        print("✅ AgentManager imported successfully")
    except Exception as e:
        print(f"❌ Failed to import AgentManager: {e}")
        return False
    
    try:
        from services.retrievers.qan_retriever.qan_retriever import qan_retrieve
        print("✅ qan_retrieve imported successfully")
    except Exception as e:
        print(f"❌ Failed to import qan_retrieve: {e}")
        return False
        
    return True

def test_qan_retrieve_directly():
    """Test the QnA retriever function directly"""
    print("\n🧠 Testing qan_retrieve function directly...\n")
    
    try:
        from services.retrievers.qan_retriever.qan_retriever import qan_retrieve
        
        test_query = "dishwasher pump not working"
        print(f"🔎 Query: '{test_query}'")
        
        results = qan_retrieve(test_query, appliance=None, k=3)
        print(f"📊 Results type: {type(results)}")
        print(f"📊 Results keys: {results.keys() if isinstance(results, dict) else 'Not a dict'}")
        
        if isinstance(results, dict) and "documents" in results:
            docs = results["documents"][0] if results["documents"] else []
            print(f"📄 Found {len(docs)} documents:")
            for i, doc in enumerate(docs[:2]):  # Show first 2
                print(f"  [{i+1}] {doc[:150]}...")
        else:
            print(f"⚠️ Unexpected results format: {results}")
            
        return results
        
    except Exception as e:
        print(f"❌ qan_retrieve failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_intent_classification():
    """Test intent classification"""
    print("\n🎯 Testing intent classification...\n")
    
    try:
        from services.intent_service.intent_service import IntentService
        
        intent_service = IntentService()
        test_queries = [
            "How does a dishwasher pump work?",
            "What parts do I need for my refrigerator?",
            "My dishwasher is not draining"
        ]
        
        for query in test_queries:
            intent = intent_service.classify_intent(query)
            print(f"🔎 '{query}' → Intent: '{intent}'")
            
    except Exception as e:
        print(f"❌ Intent classification failed: {e}")
        import traceback
        traceback.print_exc()

def test_agent_manager_flow():
    """Test the full agent manager flow"""
    print("\n🤖 Testing AgentManager flow...\n")
    
    try:
        from agent_manager import AgentManager
        
        agent = AgentManager()
        test_query = "How does a dishwasher pump work?"
        
        print(f"🔎 Query: '{test_query}'")
        
        # Test the full flow
        response = agent.handle_chat_request(test_query, model="deepseek-chat")
        
        print(f"📊 Response type: {type(response)}")
        print(f"📊 Response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
        
        if isinstance(response, dict):
            print(f"🎯 Intent: {response.get('intent', 'N/A')}")
            print(f"🤖 Model: {response.get('model', 'N/A')}")
            print(f"📄 Retrieved data type: {type(response.get('retrieved_data'))}")
            
            retrieved_data = response.get('retrieved_data')
            if retrieved_data:
                print(f"📄 Retrieved data: {str(retrieved_data)[:200]}...")
            else:
                print("⚠️ No retrieved data!")
                
            response_text = response.get('response', 'No response')
            print(f"💬 Response: {response_text[:300]}...")
        
        return response
        
    except Exception as e:
        print(f"❌ AgentManager flow failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_route_to_retriever():
    """Test the _route_to_retriever method specifically"""
    print("\n🛤️ Testing _route_to_retriever method...\n")
    
    try:
        from agent_manager import AgentManager
        
        agent = AgentManager()
        test_query = "How does a dishwasher pump work?"
        
        # Test routing directly
        retrieved_data = agent._route_to_retriever("qna", test_query)
        
        print(f"📊 Retrieved data type: {type(retrieved_data)}")
        if retrieved_data:
            print(f"📄 Retrieved data: {str(retrieved_data)[:200]}...")
        else:
            print("⚠️ No data retrieved from router!")
            
        return retrieved_data
        
    except Exception as e:
        print(f"❌ Route to retriever failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🚀 Agent Manager Debug Test\n")
    
    # Check environment
    print(f"🌍 OPENAI_API_KEY present: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
    print(f"🌍 DEEPSEEK_API_KEY present: {'Yes' if os.getenv('DEEPSEEK_API_KEY') else 'No'}")
    print()
    
    # Test imports
    if not test_imports():
        print("❌ Cannot proceed - import failures")
        return
    
    # Test each component
    test_intent_classification()
    test_qan_retrieve_directly()
    test_route_to_retriever()
    test_agent_manager_flow()
    
    print("\n✅ Agent Manager debug test complete!")

if __name__ == "__main__":
    main()
