"""
Out of Scope Service - Handles responses for queries outside the system's domain
"""
from typing import Dict, Any


class OutOfScopeService:
    """
    Service for handling out of scope queries with consistent messaging.
    """
    
    def __init__(self):
        self.partselect_message = "Sorry, I am a bot only for helping on partselect.com specifically with dishwasher and refrigerator parts. I can help you with compatibility, installation, troubleshooting, or general questions about dishwashers and refridgerators on this page."
    
    def get_out_of_scope_response(self) -> Dict[str, Any]:
        """
        Get the standard out of scope response.
        
        Returns:
            Dict containing the out of scope response structure
        """
        
        return {
            "response": self.partselect_message,
            "intent": "out_of_scope",
            "retrieved_data": None
        }