from llama_cpp import Llama
import json

llm = Llama(model_path="models/mistral-7b-instruct-v0.1.Q4_K_M.gguf", n_ctx=4096, n_threads=8)
CONFIDENCE_THRESHOLD = 0.7

def build_categorization_prompt(transactions: list) -> str:
    lines = [f"{tx['id']}: {tx['description']} (£{tx['amount']})" for tx in transactions]
    return (
        "Categorize the following transactions. Return JSON with fields: id, category, confidence.\n" +
        "\n".join(lines)
    )

async def categorize_transactions(transactions: list) -> list:
    prompt = build_categorization_prompt(transactions)
    response = llm(prompt, max_tokens=512)
    text = response["choices"][0]["text"]
    parsed = json.loads(text)
    for tx in parsed:
        tx["needs_review"] = tx["confidence"] < CONFIDENCE_THRESHOLD
    return parsed