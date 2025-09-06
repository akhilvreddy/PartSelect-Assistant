from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from agent_manager import AgentManager
# from vector_manager import VectorManager
from services.health_service.health_service import HealthService
from services.intent_service.intent_service import IntentService
import time

app = FastAPI(title="PartSelect Assistant API", version="1.0.0")

# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    query: str
    model: str = "deepseek"

class QueryRequest(BaseModel):
    query: str

class SearchRequest(BaseModel):
    query: str
    k: int = 5

class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    version: str

class IntentResponse(BaseModel):
    query: str
    intent: str

class SearchResponse(BaseModel):
    query: str
    results: List[Any]

# track uptime
START_TIME = time.time()

# services
health_service = HealthService(START_TIME)
intent_service = IntentService()

# managers
agent_manager = AgentManager()
# vector = VectorManager()

@app.post("/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """
    Main chat endpoint - handles user queries through the complete flow:
    Intent Classification → Retriever → Response Generation
    """
    response = agent_manager.handle_chat_request(request.query)
    return response

@app.get("/health")
async def health() -> HealthResponse:
    """
    Health check endpoint - returns application status and uptime
    """
    health_data = health_service.get_health_status()
    return HealthResponse(**health_data)

@app.post("/intents")
async def intents(request: QueryRequest) -> IntentResponse:
    """
    Intent classification endpoint - classifies user queries into intent categories
    """
    intent = intent_service.classify_intent(request.query)
    return IntentResponse(
        query=request.query,
        intent=intent
    )

@app.post("/search")
async def search(request: SearchRequest) -> SearchResponse:
    results = vector.search(request.query, k=request.k)
    return SearchResponse(
        query=request.query,
        results=results
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)