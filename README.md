# LLM Eval Lab

A FastAPI service that demonstrates a small production-ready pattern for serving LLM-based chat with semantic caching, Prometheus metrics, and multi-model routing. This repository includes a simple docker-compose stack (Redis + Prometheus) for local testing and monitoring.

Key features
- FastAPI-based HTTP API exposing:
  - GET /health — basic health check
  - POST /chat — main chat endpoint (request/response validated with Pydantic models)
- Semantic cache using Redis + sentence-transformers embeddings to return previously-generated answers when queries are semantically similar
- Multi-model routing (simple rule-based routing using a query complexity heuristic)
- Streaming response consumption from the LLM client with measurements:
  - Time-to-first-token (TTFT)
  - Tokens-per-second (TPS) estimate
  - Simple cost estimate (placeholder values)
- Prometheus metrics exposed at `/metrics` (via prometheus-fastapi-instrumentator)
- Docker Compose stack for local Redis and Prometheus

Architecture diagram
See architecture.html in the repository root for a visual diagram and component descriptions.

Quickstart (local)
1. Install Python dependencies:
   pip install -r requirements.txt
2. Copy the environment template and set your API key(s):
   cp .env.example .env
   # fill in OPENAI_EDU_API and other variables
3. Start Redis + Prometheus (optional, recommended for monitoring):
   docker compose up
4. Run the FastAPI app:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
5. Access:
   - API: http://localhost:8000
   - Prometheus: http://localhost:9090 (if using docker compose)
   - Metrics endpoint: http://localhost:8000/metrics

Configuration
- .env.example shows the environment variables used. Important ones:
  - OPENAI_EDU_API — API key used by the LLM client
  - REDIS_URL — Redis connection string used by the semantic cache
  - EMBEDDING_MODEL — model name used by sentence-transformers for embeddings

High-level implementation details
- app/main.py
  - FastAPI app and the `/chat` endpoint.
  - Checks the semantic cache first; on hit, returns cached response and updates metrics.
  - On miss, routes the request using the router module, calls the LLM client to generate the answer, stores the response in the semantic cache, and updates metrics.
- app/router.py
  - Simple routing function `choose_model(query: str) -> str` that returns either `gpt-4o` or `gpt-4o-mini` based on a small complexity heuristic.
- app/cache.py
  - Builds query embeddings using SentenceTransformer and stores cached items in Redis with a TTL.
  - Performs a scan over keys with prefix `semantic_cache:` and computes cosine similarity to pick the best match above a threshold (SIMILARITY_THRESHOLD = 0.92).
- app/llm_client.py
  - Wraps the LLM provider (langfuse.openai.OpenAI client in this sample).
  - Streams responses, measures TTFT and TPS, estimates token counts and cost.
- app/metrics.py
  - Prometheus metrics used for monitoring (request counts, latency, TTFT histogram, TPS gauge, cost gauge, error counts).
- app/schemas.py
  - Pydantic request/response models for the API.
- app/utils.py
  - Small helper utilities: text normalization and query complexity detector.

Semantic cache behavior
- When the chat endpoint receives a query:
  - Create a normalized embedding for the incoming query.
  - Iterate cached entries (keys starting with `semantic_cache:`), compute cosine similarity, and pick the best match.
  - If the best match has similarity >= SIMILARITY_THRESHOLD (0.92), the cached response is returned as a cache hit with the previously measured metrics (TTFT, TPS, cost).
  - On cache miss, the request is forwarded to the chosen LLM model, result streamed and measured, then stored in Redis with an embedding and TTL.

Routing
- The routing heuristic classifies queries as "complex" if any complexity keywords are present or the query length exceeds 20 words (see `app/utils.py:is_complex_query`). Complex queries route to `gpt-4o`, simpler ones to `gpt-4o-mini`.

Monitoring and metrics
- All incoming requests increment the REQUEST_COUNT metric with labels for route, cache_hit, and status.
- REQUEST_LATENCY tracks end-to-end latency for request handling.
- TTFT_HISTOGRAM captures first-token latency distribution.
- TPS_GAUGE and COST_GAUGE provide runtime estimates of token throughput and estimated cost.

Repository structure
- app/ — application code (main, cache, client, routing, schemas, metrics, utils)
- docker-compose.yml — recommended local stack (Redis + Prometheus)
- monitoring/ — Prometheus job configuration (if present)
- requirements.txt — Python dependencies
- README.md — this file
- architecture.html — architecture diagram (add this file to repo root)

Notes and next steps
- The cost estimation in app/llm_client.py uses placeholder pricing values; replace with your provider's current pricing for accurate cost reporting.
- The semantic cache currently scans keys in Redis. For larger scale, replace scanning with a vector index (e.g., RedisVector, Milvus, or FAISS) that supports nearest-neighbor search.
- Consider rate-limiting, authentication, and request/response size validation for production readiness.

License
- Add a LICENSE file if you want to specify licensing for this project.
