import os
import json
import re
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Load environment variables
load_dotenv()

class InstallationRetriever:
    """Enhanced installation retriever using JSON manual + ChromaDB semantic search"""
    
    def __init__(self):
        """Initialize the retriever with installation manual and ChromaDB connection"""
        self.current_file = Path(__file__)
        # From services/retrievers/installation_retriever/installation_retriever.py -> go up 5 levels to project root
        self.project_root = self.current_file.parent.parent.parent.parent.parent
        
        # Load installation manual
        self.installation_manual = self._load_installation_manual()
        
        # Setup ChromaDB
        self._setup_chromadb()
    
    def _load_installation_manual(self) -> Dict[str, Dict[str, Any]]:
        """Load installation manual JSON file"""
        try:
            manual_path = self.project_root / "backend" / "data" / "maps" / "installation_manual.json"
            with open(manual_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load installation_manual.json: {e}")
            return {}
    
    def _setup_chromadb(self):
        """Setup ChromaDB connection"""
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError("OPENAI_API_KEY not set")
            
            chroma_path = self.project_root / "backend" / "chroma_store"
            
            self.client = chromadb.Client(
                Settings(
                    is_persistent=True,
                    persist_directory=str(chroma_path),
                )
            )
            
            self.embed_fn = OpenAIEmbeddingFunction(api_key=openai_key, model_name="text-embedding-3-small")
            self.collection = self.client.get_collection(
                name="partselect-docs",
                embedding_function=self.embed_fn
            )
        except Exception as e:
            print(f"Warning: ChromaDB setup failed: {e}")
            self.collection = None
    
    def _extract_part_numbers(self, query: str) -> List[str]:
        """Extract part numbers from query (PS followed by digits)"""
        part_numbers = re.findall(r'PS\d+', query.upper())
        # Remove duplicates while preserving order
        return list(dict.fromkeys(part_numbers))
    
    def _direct_lookup(self, part_numbers: List[str]) -> Dict[str, Any]:
        """Perform direct installation manual lookup"""
        results = {
            "direct_matches": [],
            "confidence": "HIGH",
            "lookup_type": "installation_manual"
        }
        
        for part_num in part_numbers:
            if part_num in self.installation_manual:
                manual_entry = self.installation_manual[part_num]
                results["direct_matches"].append({
                    "type": "installation_manual",
                    "part_number": part_num,
                    "title": manual_entry["title"],
                    "installation_text": manual_entry["installation_text"],
                    "url": manual_entry["url"],
                    "confidence": "VERY_HIGH"
                })
        
        return results
    
    def _semantic_search(self, query: str, appliance: Optional[str] = None, k: int = 3) -> Dict[str, Any]:
        """Perform ChromaDB semantic search as fallback"""
        if not self.collection:
            return {"documents": [[]], "metadatas": [[]], "ids": [[]], "distances": [[]]}
        
        # Build filter for installation source
        where_filter = {"source": "installation"}
        if appliance:
            where_filter["appliance"] = appliance
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            return results
        except Exception as e:
            print(f"Error in installation semantic search: {e}")
            return {"documents": [[]], "metadatas": [[]], "ids": [[]], "distances": [[]]}
    
    def retrieve(self, query: str, appliance: Optional[str] = None, k: int = 3) -> Dict[str, Any]:
        """
        Main retrieval method combining direct manual lookup + semantic search
        
        Args:
            query: User's installation question
            appliance: Optional appliance filter (dishwasher, refrigerator)
            k: Number of results to return for semantic search
        
        Returns:
            Combined results from direct lookup and semantic search
        """
        # Extract part numbers from query
        part_numbers = self._extract_part_numbers(query)
        
        # Perform direct lookup
        direct_results = self._direct_lookup(part_numbers)
        
        # Perform semantic search
        semantic_results = self._semantic_search(query, appliance, k)
        
        # Combine results
        combined_results = {
            "query": query,
            "extracted_identifiers": {
                "part_numbers": part_numbers
            },
            "direct_lookup": direct_results,
            "semantic_search": semantic_results,
            "strategy_used": []
        }
        
        # Determine primary strategy
        if direct_results["direct_matches"]:
            combined_results["strategy_used"].append("direct_lookup")
        if semantic_results["documents"][0]:  # Has semantic results
            combined_results["strategy_used"].append("semantic_search")
        
        return combined_results

# Create global instance
_retriever_instance = None

def installation_retrieve(query: str, appliance: str | None = None, k: int = 3):
    """
    Global function interface for installation retrieval (maintains backward compatibility)
    
    Args:
        query: User's installation question
        appliance: Optional appliance filter (dishwasher, refrigerator)
        k: Number of results to return (default 3)
    
    Returns:
        Enhanced installation results with direct lookup + semantic search
    """
    global _retriever_instance
    
    # Initialize retriever instance once
    if _retriever_instance is None:
        _retriever_instance = InstallationRetriever()
    
    return _retriever_instance.retrieve(query, appliance, k)