from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    query: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    route_used: str
    cache_hit: bool
    ttft_seconds: float
    tps: float
    estimated_cost_usd: float
    error: Optional[str] = None