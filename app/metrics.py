from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter(
    "llm_requests_total",
    "Total number of LLM requests",
    ["route", "cache_hit", "status"]
)

REQUEST_LATENCY = Histogram(
    "llm_request_latency_seconds",
    "Total request latency in seconds",
    ["route"]
)

TTFT_HISTOGRAM = Histogram(
    "llm_ttft_seconds",
    "Time to first token in seconds",
    ["route"]
)

TPS_GAUGE = Gauge(
    "llm_tokens_per_second",
    "Estimated tokens per second",
    ["route"]
)

COST_GAUGE = Gauge(
    "llm_estimated_cost_usd",
    "Estimated cost per query in USD",
    ["route"]
)

ERROR_COUNT = Counter(
    "llm_errors_total",
    "Total number of LLM errors",
    ["route"]
)