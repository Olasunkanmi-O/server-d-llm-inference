from llama_cpp import Llama
import re
import json

llm = Llama(
    model_path="models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=8,
    n_gpu_layers=0
)

SOURCE_MODEL = "Mistral-7B-Q4"

def build_scenario_prompt(user_request: str, recent_summary: str, agg_summary: str, hypothetical_summary: str, summary_text: str) -> str:
    return (
        f"User request: {user_request}\n\n"
        f"Recent transactions (detailed):\n{recent_summary}\n\n"
        f"Older transactions (aggregated by month/category):\n{agg_summary}\n\n"
        f"Hypothetical changes:\n{hypothetical_summary}\n\n"
        f"Summary:\n{summary_text}\n\n"
        "Instructions:\n"
        "- Provide scenario analysis based on actual transactions and hypothetical changes.\n"
        "- Highlight potential tax implications.\n"
        "- Suggest strategies for cash flow, savings, or expense management.\n"
        "- Simulate the impact of any proposed changes the user mentions.\n"
        "- Return your response as a flat JSON object with the following keys:\n"
        "  - recommendations: string\n"
        "  - tax_implications: string\n"
        "  - cash_flow_projection: object with keys:\n"
        "      - initial_impact: float\n"
        "      - estimated_tax_savings: float or null\n"
        "      - net_effect: float or null\n"
        "Do not include nested objects, lists, or additional fields. Do not format as dialogue or markdown."
    )

async def generate_scenario(full_prompt: str) -> dict:
    response = llm(full_prompt, max_tokens=1024)

    def extract_json_block(text: str) -> dict:
        start = text.find('{')
        if start == -1:
            return {}

        brace_count = 0
        for i in range(start, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    try:
                        return json.loads(text[start:i+1])
                    except json.JSONDecodeError as e:
                        print("⚠️ JSON parse error:", e)
                    break
        return {}


    raw_text = response["choices"][0]["text"]
    parsed = extract_json_block(raw_text)

    if not parsed:
        parsed = {
            "recommendations": "Unable to generate scenario.",
            "tax_implications": "Please try again or refine your request.",
            "cash_flow_projection": {
                "initial_impact": -900.0,
                "estimated_tax_savings": None,
                "net_effect": None
            }
        }

    return {
        "response": parsed,
        "source_model": SOURCE_MODEL,
        "confidence": None
    }