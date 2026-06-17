# LLM Eval Lab

A FastAPI service for LLM inference with semantic caching, Prometheus metrics, and multi-model routing. Includes a docker-compose stack with Redis and Prometheus for local monitoring.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your API keys
docker compose up
```

The API will be available at `http://localhost:8000`. Prometheus metrics are exposed at `/metrics` and scraped by Prometheus at `http://localhost:9090`.
