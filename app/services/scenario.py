from llama_cpp import Llama

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
        "- Return your response in JSON format with keys: 'recommendations', 'tax_implications', 'cash_flow_projection'."
    )

async def generate_scenario(full_prompt: str) -> dict:
    response = llm(full_prompt, max_tokens=1024)
    return {
        "response": response["choices"][0]["text"],
        "source_model": SOURCE_MODEL,
        "confidence": None  # Placeholder for future scoring
    }