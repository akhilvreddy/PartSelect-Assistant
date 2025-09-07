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

class CompatibilityRetriever:
    """Enhanced compatibility retriever using JSON mappings + ChromaDB semantic search"""
    
    def __init__(self):
        """Initialize the retriever with JSON mappings and ChromaDB connection"""
        self.current_file = Path(__file__)
        # From services/retrievers/compatibility_retriever/compatibility_retriever.py -> go up 4 levels to project root
        self.project_root = self.current_file.parent.parent.parent.parent.parent
        
        # Load JSON mappings
        self.parts_to_models = self._load_json_mapping("backend/data/maps/parts_to_models.json")
        self.model_to_parts = self._load_json_mapping("backend/data/maps/model_to_parts.json")
        
        # Setup ChromaDB
        self._setup_chromadb()
    
    def _load_json_mapping(self, relative_path: str) -> Dict[str, List[str]]:
        """Load JSON mapping file"""
        try:
            file_path = self.project_root / relative_path
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load {relative_path}: {e}")
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
    
    def _extract_identifiers(self, query: str) -> Tuple[List[str], List[str]]:
        """Extract part numbers and model numbers from query"""
        # Part numbers: PS followed by digits
        part_numbers = re.findall(r'PS\d+', query.upper())
        
        # Model numbers: Various patterns (letters + digits + optional letters/digits)
        # Common patterns: WDT780SAEM1, KDTM354DSS5, 66512762K314, etc.
        model_patterns = [
            r'\b[A-Z]{2,4}\d{3,4}[A-Z]{2,4}\d{0,2}\b',  # WDT780SAEM1, KDTM354DSS5
            r'\b\d{8}[A-Z]\d{3}\b',                      # 66512762K314
            r'\b\d{5}[A-Z]\d{3}\b',                      # 13263K112
            r'\b\d{4}[A-Z]\d{3}\b',                      # 2213N414
        ]
        
        model_numbers = []
        for pattern in model_patterns:
            model_numbers.extend(re.findall(pattern, query.upper()))
        
        # Remove duplicates while preserving order
        part_numbers = list(dict.fromkeys(part_numbers))
        model_numbers = list(dict.fromkeys(model_numbers))
        
        return part_numbers, model_numbers
    
    def _direct_lookup(self, part_numbers: List[str], model_numbers: List[str]) -> Dict[str, Any]:
        """Perform direct JSON mapping lookup"""
        results = {
            "direct_matches": [],
            "confidence": "HIGH",
            "lookup_type": []
        }
        
        # Part → Models lookup
        for part_num in part_numbers:
            if part_num in self.parts_to_models:
                compatible_models = self.parts_to_models[part_num]
                results["direct_matches"].append({
                    "type": "part_to_models",
                    "part_number": part_num,
                    "compatible_models": compatible_models,
                    "count": len(compatible_models)
                })
                results["lookup_type"].append("part_to_models")
        
        # Model → Parts lookup  
        for model_num in model_numbers:
            if model_num in self.model_to_parts:
                compatible_parts = self.model_to_parts[model_num]
                results["direct_matches"].append({
                    "type": "model_to_parts",
                    "model_number": model_num,
                    "compatible_parts": compatible_parts,
                    "count": len(compatible_parts)
                })
                results["lookup_type"].append("model_to_parts")
        
        # Cross-check: Part + Model compatibility
        if part_numbers and model_numbers:
            cross_check_results = []
            for part_num in part_numbers:
                for model_num in model_numbers:
                    if part_num in self.parts_to_models:
                        is_compatible = model_num in self.parts_to_models[part_num]
                        cross_check_results.append({
                            "part_number": part_num,
                            "model_number": model_num,
                            "is_compatible": is_compatible,
                            "confidence": "VERY_HIGH"
                        })
            
            if cross_check_results:
                results["direct_matches"].append({
                    "type": "cross_check",
                    "cross_check_results": cross_check_results
                })
                results["lookup_type"].append("cross_check")
        
        return results
    
    def _semantic_search(self, query: str, appliance: Optional[str] = None, k: int = 3) -> Dict[str, Any]:
        """Perform ChromaDB semantic search as fallback"""
        if not self.collection:
            return {"documents": [[]], "metadatas": [[]], "ids": [[]], "distances": [[]]}
        
        # Build filter for compatibility source
        where_filter = {"source": "compatibility"}
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
            print(f"Error in semantic search: {e}")
            return {"documents": [[]], "metadatas": [[]], "ids": [[]], "distances": [[]]}
    
    def retrieve(self, query: str, appliance: Optional[str] = None, k: int = 3) -> Dict[str, Any]:
        """
        Main retrieval method combining direct lookup + semantic search
        
        Args:
            query: User's compatibility question
            appliance: Optional appliance filter (dishwasher, refrigerator)
            k: Number of results to return for semantic search
        
        Returns:
            Combined results from direct lookup and semantic search
        """
        # Extract part numbers and model numbers from query
        part_numbers, model_numbers = self._extract_identifiers(query)
        
        # Perform direct lookup
        direct_results = self._direct_lookup(part_numbers, model_numbers)
        
        # Perform semantic search
        semantic_results = self._semantic_search(query, appliance, k)
        
        # Combine results
        combined_results = {
            "query": query,
            "extracted_identifiers": {
                "part_numbers": part_numbers,
                "model_numbers": model_numbers
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

def compatibility_retrieve(query: str, appliance: str | None = None, k: int = 3):
    """
    Global function interface for compatibility retrieval (maintains backward compatibility)
    
    Args:
        query: User's compatibility question
        appliance: Optional appliance filter (dishwasher, refrigerator)
        k: Number of results to return (default 3)
    
    Returns:
        Enhanced compatibility results with direct lookup + semantic search
    """
    global _retriever_instance
    
    # Initialize retriever instance once
    if _retriever_instance is None:
        _retriever_instance = CompatibilityRetriever()
    
    return _retriever_instance.retrieve(query, appliance, k)
