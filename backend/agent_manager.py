from retrievers.part_retriever import PartRetriever
from retrievers.symptom_retriever import SymptomRetriever
from retrievers.compatibility_retriever import CompatibilityRetriever
from services.deepseek_client import DeepSeekClient

class AgentManager:
    def __init__(self):
        self.deepseek = DeepSeekClient()
        self.part = PartRetriever()
        self.symptom = SymptomRetriever()
        self.compat = CompatibilityRetriever()

    def handle_query(self, query, model="deepseek"):
        """
        Main entry point for handling user queries.
        Routes query based on detected intent.
        """
        intent = self.deepseek.detect_intent(query)

        if intent == "installation":
            return self.part.retrieve(query)

        elif intent == "troubleshooting":
            return self.symptom.retrieve(query)

        elif intent == "compatibility":
            return self.compat.retrieve(query)

        elif intent == "questionanswer":
            return self.compat.retrieve(query)

        elif intent == "out_of_scope":
            return {
                "response": (
                    "I can only help with **dishwasher and refrigerator parts** right now. "
                    "Please try asking about installation, compatibility, or troubleshooting."
                ),
                "intent": intent
            }

        else:
            # fallback safety net
            return {
                "response": "Sorry, I couldn’t classify your question. Try rephrasing it.",
                "intent": "unknown"
            }