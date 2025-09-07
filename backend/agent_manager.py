"""
Agent Manager - Core orchestrator for the PartSelect Assistant

Follows the flow: Request → Intent Classification → Retriever → Response Generation
"""
from services.intent_service.intent_service import IntentService
from services.external_api.deepseek_client import DeepSeekClient
from services.outofscope_service import OutOfScopeService
from services.retrievers.qan_retriever.qan_retriever import qan_retrieve
from services.retrievers.compatibility_retriever.compatibility_retriever import compatibility_retrieve
from services.retrievers.symptom_retriever.symptom_retriever import symptom_retrieve
from services.retrievers.installation_retriever.installation_retriever import installation_retrieve

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
    
    def handle_chat_request(self, query: str, model: str = "deepseek-chat") -> Dict[str, Any]:
        """
        Main entry point for chat requests. Follows the complete flow from the diagram on the main README.
        
        Args:
            query: User's question/request
            model: The model to use for response generation (deepseek-chat or deepseek-reasoning)
            
        Returns:
            Dict containing response, intent, and any retrieved data
        """
        
        intent = self.intent_service.classify_intent(query)
        
        # handle out of scope immediately using OutOfScopeService
        if intent == "out_of_scope":
            return self.outofscope_service.get_out_of_scope_response()
        
        # route to appropriate retriever based on intent
        retrieved_data = self._route_to_retriever(intent, query)
        
        # generate response using LLM with retrieved data
        response = self._generate_response(intent, query, retrieved_data, model)
        
        return {
            "response": response,
            "intent": intent,
            "retrieved_data": retrieved_data,
            "model": model
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
        
        # route to appropriate retriever based on intent
        if intent == "qna":
            return qan_retrieve(query, appliance=None, k=5)
        elif intent == "compatibility":
            return compatibility_retrieve(query, appliance=None, k=3)
        elif intent == "installation":
            return installation_retrieve(query, appliance=None, k=3)
        elif intent == "troubleshoot":
            return symptom_retrieve(query, appliance=None, k=3)
        else: # this is just for safety, this condition can't happen
            return None
    
    def _generate_response(self, intent: str, query: str, retrieved_data: Any, model: str = "deepseek-chat") -> str:
        """
        Generate response using DeepSeek LLM based on intent, query, and retrieved data.
        
        Args:
            intent: The classified intent
            query: User's original query
            retrieved_data: Data retrieved from the appropriate retriever
            model: The model to use for response generation
            
        Returns:
            Generated response string
        """
        # create system prompt based on intent
        system_prompts = {
            "compatibility": """You are a PartSelect compatibility specialist with access to enhanced compatibility data including direct JSON mappings and semantic search results.

CRITICAL INSTRUCTIONS FOR ENHANCED DATA STRUCTURE:
- The retrieved data contains TWO sources: "direct_lookup" and "semantic_search"
- ALWAYS PRIORITIZE "direct_lookup" results - these are 100% accurate JSON mappings
- Use "semantic_search" only as supplementary information or when direct lookup is empty
- NEVER hallucinate part numbers, prices, or descriptions not in the retrieved data
- Reference the exact confidence levels provided (HIGH, VERY_HIGH)

DIRECT LOOKUP DATA STRUCTURE:
- "part_to_models": Part number → list of compatible models
- "model_to_parts": Model number → list of compatible part numbers  
- "cross_check": Definitive compatibility between specific part + model
- ALWAYS cite these exact part numbers and model numbers from the data

RESPONSE RULES:
- If cross_check exists: Use its YES/NO result with VERY_HIGH confidence
- If direct matches exist: List the exact part numbers or model numbers found
- DO NOT invent prices, descriptions, or specifications
- DO NOT reference part numbers not in the retrieved data
- State when information comes from direct lookup vs semantic search

FORMAT YOUR RESPONSE:
1. Direct compatibility answer (YES/NO/UNCERTAIN) with confidence level
2. Exact part numbers or models from direct_lookup results
3. Cross-check results if available (definitive compatibility)
4. Semantic search supplements only if relevant
5. Honest statement about limitations of available data""",

            "troubleshoot": """You are a PartSelect troubleshooting expert with access to real symptom-to-part solution data.

CRITICAL INSTRUCTIONS:
- ALWAYS reference the specific symptoms, parts, and fix percentages from the retrieved data
- Cite exact part names and part numbers that fix the reported issue
- Include the fix percentage when available (e.g., "fixes 57% of cases")
- Prioritize solutions by their success rates from the data
- Provide part descriptions and installation difficulty when available
- Reference multiple solution options from the retrieved results
- If the symptom isn't clearly covered, suggest related symptoms from the data

FORMAT YOUR RESPONSE:
1. Problem diagnosis based on retrieved symptoms
2. Top solutions ranked by fix percentage
3. Specific part numbers and descriptions
4. Additional troubleshooting steps if needed
5. When to call a professional""",

            "qna": """You are a PartSelect appliance parts expert with access to detailed part specifications and technical data.

CRITICAL INSTRUCTIONS:
- ALWAYS cite specific part numbers, brands, model compatibility, and prices from retrieved data
- Reference exact part descriptions and technical specifications provided
- Include installation difficulty, tools required, and safety warnings when available
- Mention compatible appliance models and brands from the data
- Provide PartSelect part numbers (PS numbers) for ordering
- If multiple similar parts exist, explain the differences using retrieved data
- Always ground your response in the specific retrieved information - don't generalize

FORMAT YOUR RESPONSE:
1. Direct answer using retrieved part data
2. Specific part numbers and compatibility info
3. Technical details and specifications
4. Installation requirements and difficulty
5. Pricing and ordering information when available""",

            "installation": """You are a PartSelect installation expert with access to enhanced installation data including direct manual lookup and semantic search results.

CRITICAL INSTRUCTIONS FOR ENHANCED DATA STRUCTURE:
- The retrieved data contains TWO sources: "direct_lookup" and "semantic_search"
- ALWAYS PRIORITIZE "direct_lookup" results - these are exact installation manuals for specific parts
- Use "semantic_search" only as supplementary information or when direct lookup is empty
- NEVER hallucinate installation steps, tools, or procedures not in the retrieved data
- Reference the exact confidence levels provided (HIGH, VERY_HIGH)

DIRECT LOOKUP DATA STRUCTURE:
- "installation_manual": Part number → exact installation instructions
- ALWAYS cite the specific part numbers and installation text from the data

RESPONSE RULES:
- If direct matches exist: Use the exact installation text and procedures provided
- Include specific tools mentioned in the installation text
- Reference safety warnings and precautions from the data
- DO NOT invent installation steps not in the retrieved data
- State when information comes from direct lookup vs semantic search

FORMAT YOUR RESPONSE:
1. Part identification and confirmation
2. Step-by-step installation instructions from retrieved data
3. Required tools and safety precautions mentioned in data
4. Additional tips or warnings from the installation text
5. Honest statement about limitations if data is incomplete"""
        }
        
        system_prompt = system_prompts.get(intent, "You are a helpful appliance parts assistant.")
        
        # Create user prompt with context - format the retrieved data properly
        context_text = ""
        
        # Handle enhanced data structures (compatibility and installation)
        if retrieved_data and isinstance(retrieved_data, dict):
            if "direct_lookup" in retrieved_data and "semantic_search" in retrieved_data:
                # Enhanced retriever format (compatibility or installation)
                if intent == "compatibility":
                    context_text = "COMPATIBILITY DATA RETRIEVED:\n\n"
                elif intent == "installation":
                    context_text = "INSTALLATION DATA RETRIEVED:\n\n"
                else:
                    context_text = "ENHANCED DATA RETRIEVED:\n\n"
                
                # Add extracted identifiers
                extracted = retrieved_data.get("extracted_identifiers", {})
                if extracted.get("part_numbers") or extracted.get("model_numbers"):
                    context_text += f"EXTRACTED FROM QUERY:\n"
                    context_text += f"- Part Numbers: {extracted.get('part_numbers', [])}\n"
                    context_text += f"- Model Numbers: {extracted.get('model_numbers', [])}\n\n"
                
                # Add direct lookup results (PRIORITY)
                direct = retrieved_data.get("direct_lookup", {})
                if direct.get("direct_matches"):
                    context_text += f"DIRECT LOOKUP RESULTS (Confidence: {direct.get('confidence', 'HIGH')}):\n"
                    for match in direct["direct_matches"]:
                        if match.get("type") == "part_to_models":
                            context_text += f"- Part {match['part_number']} is compatible with {match['count']} models:\n"
                            context_text += f"  Models: {', '.join(match['compatible_models'][:10])}{'...' if match['count'] > 10 else ''}\n"
                        elif match.get("type") == "model_to_parts":
                            context_text += f"- Model {match['model_number']} is compatible with {match['count']} parts:\n"
                            context_text += f"  Parts: {', '.join(match['compatible_parts'])}\n"
                        elif match.get("type") == "cross_check":
                            context_text += f"- CROSS-CHECK RESULTS:\n"
                            for check in match["cross_check_results"]:
                                status = "COMPATIBLE" if check["is_compatible"] else "NOT COMPATIBLE"
                                context_text += f"  {check['part_number']} + {check['model_number']}: {status} (Confidence: {check['confidence']})\n"
                        elif match.get("type") == "installation_manual":
                            context_text += f"- INSTALLATION MANUAL for {match['part_number']}:\n"
                            context_text += f"  Title: {match['title']}\n"
                            context_text += f"  Instructions: {match['installation_text'][:200]}{'...' if len(match['installation_text']) > 200 else ''}\n"
                            context_text += f"  Full Instructions: {match['installation_text']}\n"
                            context_text += f"  URL: {match['url']}\n"
                            context_text += f"  Confidence: {match['confidence']}\n"
                    context_text += "\n"
                
                # Add semantic search as supplementary
                semantic = retrieved_data.get("semantic_search", {})
                if semantic.get("documents") and semantic["documents"][0]:
                    context_text += "SEMANTIC SEARCH SUPPLEMENTS:\n"
                    for i, (doc, meta) in enumerate(zip(semantic["documents"][0][:2], semantic["metadatas"][0][:2]), 1):
                        context_text += f"- Part {meta.get('part_number', 'N/A')}: {meta.get('title', 'N/A')}\n"
                        context_text += f"  Preview: {doc[:100]}...\n"
                    context_text += "\n"
                    
            elif "documents" in retrieved_data:
                # Standard retriever format (QnA, troubleshooting, etc.)
                documents = retrieved_data["documents"][0] if retrieved_data["documents"] else []
                metadatas = retrieved_data["metadatas"][0] if retrieved_data.get("metadatas") else []
                
                context_text = "Here are relevant appliance parts and information:\n\n"
                for i, (doc, meta) in enumerate(zip(documents, metadatas), 1):
                    part_id = meta.get("part_id", meta.get("part_number", "Unknown"))
                    brand = meta.get("brand", "Unknown")
                    title = meta.get("title", "Unknown Part")
                    price = meta.get("price", "N/A")
                    
                    context_text += f"Part {i}: {title} ({brand})\n"
                    context_text += f"Part ID: {part_id} | Price: ${price}\n"
                    context_text += f"Description: {doc}\n\n"
        
        user_prompt = f"""User Question: {query}

{context_text}

Based on the specific parts and information above, please provide a detailed, helpful response that references the actual parts, their part numbers, brands, and prices when relevant. Use the technical details from the part descriptions to give accurate information."""

        try:
            return self.llm_client.chat_with_system(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=model,
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