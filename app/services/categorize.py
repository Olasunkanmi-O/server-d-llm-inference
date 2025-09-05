from llama_cpp import Llama
import json
import re
from app.schemas import TransactionUpdate




llm = Llama(
    model_path="models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=8
)

CONFIDENCE_THRESHOLD = 0.7

def build_categorization_prompt(transactions: list) -> str:
    ids = [str(tx["id"]) for tx in transactions]
    lines = [f"{tx['id']}: {tx['description']} (£{tx['amount']})" for tx in transactions]
    return (
        f"Categorize the following transactions. Only return JSON for these IDs: {', '.join(ids)}.\n"
        "Each object must include: id, category, confidence.\n"
        "Categories must be one of: Grocery, Technology, Entertainment, Other.\n"
        "Confidence must be a float between 0 and 1.\n\n"
        + "\n".join(lines)
    )



def extract_json_objects(text: str) -> list:
    matches = re.findall(r'\{[^{}]+\}', text, re.DOTALL)
    parsed = []

    for m in matches:
        try:
            parsed.append(json.loads(m))
        except json.JSONDecodeError as e:
            print("⚠️ Skipping malformed object:", m)
            print("⚠️ JSON error:", e)

    return parsed

def merge_predictions(original: list, predictions: list) -> list:
    indexed = {tx["id"]: tx for tx in original}
    enriched = []

    for pred in predictions:
        tx_id = pred.get("id")
        base = indexed.get(tx_id)
        if not base:
            print(f"⚠️ No matching original transaction for ID {tx_id}")
            continue

        enriched_tx = {
            "id": tx_id,
            "description": base["description"],
            "amount": base["amount"],
            "date": base.get("date"),
            "category": pred.get("category", base.get("category", "Uncategorized")),
            "confidence": pred.get("confidence", 0.0),
            "needs_review": pred.get("needs_review", True)
        }

        enriched.append(enriched_tx)

    return [TransactionUpdate(**tx).dict() for tx in enriched]



async def categorize_transactions(transactions: list) -> list:
    DEBUG = True  # Toggle this to False in production

    prompt = build_categorization_prompt(transactions)
    response = llm(prompt, max_tokens=512)
    raw_text = response["choices"][0]["text"]

    if DEBUG:
        print("🔍 RAW LLM OUTPUT:\n", raw_text)

    try:
        predictions = json.loads(raw_text)
    except json.JSONDecodeError:
        predictions = extract_json_objects(raw_text)

    if not predictions:
        print("⚠️ No valid predictions returned by LLM.")
        return []

    # ✅ Filter out hallucinated IDs after parsing
    valid_ids = {tx["id"] for tx in transactions}
    predictions = [tx for tx in predictions if int(tx.get("id", -1)) in valid_ids]

    # ✅ Log prediction coverage
    matched_ids = {tx["id"] for tx in predictions}
    coverage = len(matched_ids) / len(transactions)
    if DEBUG:
        print(f"✅ Prediction coverage: {coverage:.2%}")

    # ✅ Process predictions
    low_conf_count = 0
    valid_categories = {"Grocery", "Technology", "Entertainment", "Other"}

    for tx in predictions:
        # Fallback confidence
        conf = tx.get("confidence", 0.0)
        try:
            if isinstance(conf, list):
                conf = conf[0] if conf else 0.0
            conf = float(conf)
        except Exception as e:
            if DEBUG:
                print(f"⚠️ Confidence parse error for tx {tx.get('id')}: {e}")
            conf = 0.0

        tx["confidence"] = conf
        tx["needs_review"] = conf < CONFIDENCE_THRESHOLD
        if tx["needs_review"]:
            low_conf_count += 1

        # Fallback category
        if tx.get("category") not in valid_categories:
            if DEBUG:
                print(f"⚠️ Invalid or missing category for tx {tx.get('id')}, assigning 'Other'")
            tx["category"] = "Other"

    if DEBUG:
        print(f"⚠️ Low-confidence transactions: {low_conf_count}")

    return merge_predictions(transactions, predictions)