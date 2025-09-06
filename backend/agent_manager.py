"""
Agent Manager - Core orchestrator for the PartSelect Assistant

Follows the flow: Request → Intent Classification → Retriever → Response Generation
"""
from services.intent_service.intent_service import IntentService
from services.external_api.deepseek_client import DeepSeekClient
from services.outofscope_service import OutOfScopeService
# from retrievers.compatibility_retriever import CompatibilityRetriever
# from retrievers.part_retriever import PartRetriever
# from retrievers.symptom_retriever import SymptomRetriever
# from retrievers.vector_retriever import VectorRetriever
from typing import Dict, Any


class AgentManager:
    """
    Main orchestrator that handles the complete chat flow:
    1. Classify intent using IntentService
    2. Route to appropriate retriever based on intent
    3. Generate response using DeepSeek LLM
    4. Return structured response
    """
    
    def __init__(self):

        self.intent_service = IntentService()
        self.llm_client = DeepSeekClient()
        self.outofscope_service = OutOfScopeService()
        
        # Retrievers (commented out until implemented)
        # self.compatibility_retriever = CompatibilityRetriever()
        # self.part_retriever = PartRetriever()
        # self.symptom_retriever = SymptomRetriever()
        # self.vector_retriever = VectorRetriever()
    
    def handle_chat_request(self, query: str) -> Dict[str, Any]:
        """
        Main entry point for chat requests. Follows the complete flow from the diagram on the main README.
        
        Args:
            query: User's question/request
            
        Returns:
            Dict containing response, intent, and any retrieved data
        """
        
        intent = self.intent_service.classify_intent(query)
        
        # handle out of scope immediately using OutOfScopeService
        if intent == "out_of_scope":
            return self.outofscope_service.get_out_of_scope_response()
        
        # Step 3: Route to appropriate retriever based on intent
        retrieved_data = self._route_to_retriever(intent, query)
        
        # Step 4: Generate response using LLM with retrieved data
        response = self._generate_response(intent, query, retrieved_data)
        
        return {
            "response": response,
            "intent": intent,
            "retrieved_data": retrieved_data
        }
    
    def _route_to_retriever(self, intent: str, query: str) -> Any:
        """
        Route query to the appropriate retriever based on classified intent.
        
        Args:
            intent: The classified intent
            query: User's query
            
        Returns:
            Retrieved data from the appropriate retriever
        """
        retriever_map = {
            "compatibility": self.compatibility_retriever,
            "installation": self.part_retriever,
            "troubleshoot": self.symptom_retriever,
            "qna": self.vector_retriever
        }
        
        retriever = retriever_map.get(intent)
        if retriever:
            return retriever.retrieve(query)
        else:
            return None
    
    def _generate_response(self, intent: str, query: str, retrieved_data: Any) -> str:
        """
        Generate response using DeepSeek LLM based on intent, query, and retrieved data.
        
        Args:
            intent: The classified intent
            query: User's original query
            retrieved_data: Data retrieved from the appropriate retriever
            
        Returns:
            Generated response string
        """
        # Create system prompt based on intent
        system_prompts = {
            "compatibility": "You are a helpful appliance parts compatibility expert. Help users determine if parts are compatible with their appliances. Be specific and accurate.",
            "installation": "You are a helpful appliance parts installation guide. Provide clear, step-by-step instructions for installing or replacing parts. Focus on safety and accuracy.",
            "troubleshoot": "You are a helpful appliance troubleshooting expert. Help users diagnose and fix problems with their dishwashers and refrigerators. Provide practical solutions.",
            "qna": "You are a helpful appliance parts expert. Answer general questions about how appliance parts work, their specifications, and features. Be informative and accurate."
        }
        
        system_prompt = system_prompts.get(intent, "You are a helpful appliance parts assistant.")
        
        # Create user prompt with context
        user_prompt = f"""User Question: {query}

Retrieved Information: {retrieved_data}

Please provide a helpful, accurate response based on the user's question and the retrieved information. Be concise but thorough."""

        try:
            return self.llm_client.chat_with_system(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=500,
                temperature=0.7
            )
        except Exception as e:
            return f"I apologize, but I encountered an error while generating a response. Please try rephrasing your question. Error: {str(e)}"
    
    def get_intent_only(self, query: str) -> str:
        """
        Get just the intent classification for a query (used by /intents endpoint).
        
        Args:
            query: User's query
            
        Returns:
            Classified intent string
        """
        return self.intent_service.classify_intent(query)