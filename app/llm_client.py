import os
import time
import tiktoken
from langfuse.openai import OpenAI
from app.config import OPENAI_EDU_API

client = OpenAI(api_key=OPENAI_EDU_API)

def estimate_cost(route: str, input_tokens: int, output_tokens: int) -> float:
    # Update these values later if you want exact pricing maintenance.
    # Placeholder estimates for demonstration only.
    pricing = {
        "gpt-4o": {"input": 0.000005, "output": 0.000015},
        "gpt-4o-mini": {"input": 0.00000015, "output": 0.0000006},
    }
    p = pricing.get(route, pricing["gpt-4o-mini"])
    return round((input_tokens * p["input"]) + (output_tokens * p["output"]), 6)

def estimate_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def generate_streamed_response(model_name: str, query: str):
    system_prompt = "You are a concise and reliable production assistant."

    start_time = time.perf_counter()
    first_token_time = None
    full_text = ""

    stream = client.chat.completions.create(
        model=model_name,
        temperature=0.2,
        stream=True,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            if first_token_time is None:
                first_token_time = time.perf_counter()
            token_text = chunk.choices[0].delta.content
            full_text += token_text

    end_time = time.perf_counter()

    ttft = (first_token_time - start_time) if first_token_time else (end_time - start_time)
    generation_time = max(end_time - (first_token_time or start_time), 0.001)

    input_tokens = estimate_tokens(system_prompt + "\n" + query, model_name)
    output_tokens = estimate_tokens(full_text, model_name)
    tps = round(output_tokens / generation_time, 3)
    cost = estimate_cost(model_name, input_tokens, output_tokens)

    return {
        "answer": full_text,
        "ttft_seconds": round(ttft, 3),
        "tps": tps,
        "estimated_cost_usd": cost,
        "input_tokens_est": input_tokens,
        "output_tokens_est": output_tokens,
    }