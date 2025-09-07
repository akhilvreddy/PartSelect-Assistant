from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from agent_manager import AgentManager
from services.health_service.health_service import HealthService
from services.intent_service.intent_service import IntentService
import time

app = FastAPI(title="PartSelect Assistant API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"], # allow all HTTP methods
    allow_headers=["*"], # allow all headers
)

# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    query: str
    model: str = "deepseek-chat"

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

# uptime tracking for health API
START_TIME = time.time()

# services
health_service = HealthService(START_TIME)
intent_service = IntentService()

# manager instance
agent_manager = AgentManager()

@app.post("/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """
    Main chat endpoint - handles user queries through the complete flow:
    Intent Classification → Retriever → Response Generation
    """
    response = agent_manager.handle_chat_request(request.query, request.model)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)