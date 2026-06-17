import time
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from app.schemas import ChatRequest, ChatResponse
from app.router import choose_model
from app.cache import semantic_cache_lookup, semantic_cache_store
from app.llm_client import generate_streamed_response
from app.metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    TTFT_HISTOGRAM,
    TPS_GAUGE,
    COST_GAUGE,
    ERROR_COUNT,
)

app = FastAPI(title="Production LLM App - Module 13 Lab 2")

Instrumentator().instrument(app).expose(app)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    route = choose_model(payload.query)
    start_time = time.perf_counter()

    try:
        cache_result = semantic_cache_lookup(payload.query)

        if cache_result["hit"]:
            cached = cache_result["response"]
            REQUEST_COUNT.labels(route=route, cache_hit="true", status="success").inc()
            REQUEST_LATENCY.labels(route=route).observe(time.perf_counter() - start_time)
            TTFT_HISTOGRAM.labels(route=route).observe(cached["ttft_seconds"])
            TPS_GAUGE.labels(route=route).set(cached["tps"])
            COST_GAUGE.labels(route=route).set(cached["estimated_cost_usd"])

            return ChatResponse(
                answer=cached["answer"],
                route_used=route,
                cache_hit=True,
                ttft_seconds=cached["ttft_seconds"],
                tps=cached["tps"],
                estimated_cost_usd=cached["estimated_cost_usd"],
                error=None,
            )

        result = generate_streamed_response(route, payload.query)

        semantic_cache_store(payload.query, result)

        REQUEST_COUNT.labels(route=route, cache_hit="false", status="success").inc()
        REQUEST_LATENCY.labels(route=route).observe(time.perf_counter() - start_time)
        TTFT_HISTOGRAM.labels(route=route).observe(result["ttft_seconds"])
        TPS_GAUGE.labels(route=route).set(result["tps"])
        COST_GAUGE.labels(route=route).set(result["estimated_cost_usd"])

        return ChatResponse(
            answer=result["answer"],
            route_used=route,
            cache_hit=False,
            ttft_seconds=result["ttft_seconds"],
            tps=result["tps"],
            estimated_cost_usd=result["estimated_cost_usd"],
            error=None,
        )

    except Exception as e:
        ERROR_COUNT.labels(route=route).inc()
        REQUEST_COUNT.labels(route=route, cache_hit="false", status="error").inc()
        raise HTTPException(status_code=500, detail=str(e))