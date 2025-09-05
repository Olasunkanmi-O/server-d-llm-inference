from llama_cpp import Llama
import json
import re

llm = Llama(
    model_path="models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=8
)

CONFIDENCE_THRESHOLD = 0.7

def build_categorization_prompt(transactions: list) -> str:
    lines = [f"{tx['id']}: {tx['description']} (£{tx['amount']})" for tx in transactions]
    return (
        "Categorize the following transactions. Return JSON with fields: id, category, confidence.\n"
        + "\n".join(lines)
    )

def extract_json_objects(text: str) -> list:
    matches = re.findall(r'\{.*?\}', text, re.DOTALL)
    return [json.loads(m) for m in matches]

def merge_predictions(original: list, predictions: list) -> list:
    indexed = {tx["id"]: tx for tx in original}
    enriched = []

    for pred in predictions:
        tx_id = pred["id"]
        base = indexed.get(tx_id, {})
        enriched_tx = {
            **base,
            **pred
        }
        enriched.append(enriched_tx)

    return enriched

async def categorize_transactions(transactions: list) -> list:
    prompt = build_categorization_prompt(transactions)
    response = llm(prompt, max_tokens=512)
    raw_text = response["choices"][0]["text"]

    try:
        predictions = json.loads(raw_text)
    except json.JSONDecodeError:
        predictions = extract_json_objects(raw_text)

    for tx in predictions:
        conf = tx.get("confidence")
        if isinstance(conf, list):
            conf = conf[0] if conf else 0.0
        tx["needs_review"] = float(conf) < CONFIDENCE_THRESHOLD
        print("TX CONFIDENCE:", conf, type(conf))

    return merge_predictions(transactions, predictions)