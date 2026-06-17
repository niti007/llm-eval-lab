from app.utils import is_complex_query

def choose_model(query: str) -> str:
    if is_complex_query(query):
        return "gpt-4o"
    return "gpt-4o-mini"