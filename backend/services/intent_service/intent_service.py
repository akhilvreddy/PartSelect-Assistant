"""
Intent Service - Handles intent classification for user queries
"""
from services.external_api.deepseek_client import DeepSeekClient
from typing import Dict, Any

class IntentService:
    """
    Service for classifying user queries into intent categories.
    """
    
    def __init__(self):
        self.deepseek_client = DeepSeekClient()
        self.valid_intents = ["compatibility", "installation", "qna", "troubleshoot", "out_of_scope"]
    
    def classify_intent(self, query: str) -> str:
        """
        Classify a user query into one of the 5 intent categories.
        
        Args:
            query: The user's query string
            
        Returns:
            str: The classified intent (compatibility, installation, qna, troubleshoot, out_of_scope)
        """
        system_prompt = """You are an intent classifier for an appliance parts assistant called partselect.com. Classify the user query into exactly one of these 5 categories:

1. compatibility - Questions about whether parts work together, fit specific models, or are compatible
2. installation - Questions about how to install, replace, or physically work with parts  
3. qna - General product questions, features, specifications, how things work
4. troubleshoot - Problems, issues, things not working, error diagnosis
5. out_of_scope - Non-appliance related questions or requests outside the system's domain

Examples:
- "Will this pump work with my Whirlpool WDF520PADM?" → compatibility
- "How do I replace the water inlet valve?" → installation  
- "What does the drain pump do?" → qna
- "My dishwasher is not draining properly" → troubleshoot
- "What's the weather like?" → out_of_scope

Respond with ONLY the intent category name. No explanations. You must follow the fact that you are made specifically for answering questions about refridegrators and dishwashwers."""

        try:
            response = self.deepseek_client.chat_with_system(
                system_prompt=system_prompt,
                user_prompt=query,
                model="deepseek-chat",
                max_tokens=10,
                temperature=0.1
            )
            
            intent = response.lower().strip()
            
            if intent in self.valid_intents:
                return intent
            else:
                return "out_of_scope"
                
        except Exception as e:
            print(f"Error in intent classification: {e}")
            return "out_of_scope"