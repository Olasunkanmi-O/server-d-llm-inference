server-d/
├── models/                        # Local GGUF models
│   └── mistral-7b-instruct-v0.1.Q4_K_M.gguf
├── app/
│   ├── main.py                   # FastAPI entrypoint
│   ├── config/                   # Config resolver for dynamic behavior
│   │   └── scenario_config.py
│   ├── db/                       # DB pool and SQL helpers
│   │   └── pool.py
│   ├── routers/                  # API routes
│   │   ├── scenario.py
│   │   ├── categorize.py
│   │   └── feedback.py
│   ├── schemas/                  # Pydantic models
│   │   ├── scenario.py
│   │   ├── categorize.py
│   │   ├── feedback.py
│   │   └── __init__.py
│   ├── services/                 # LLM orchestration and logic
│   │   ├── scenario.py
│   │   ├── categorize.py
│   │   └── feedback.py
│   └── prompts/                  # Prompt templates
│       ├── scenario.txt
│       └── categorize.txt
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (optional)
└── README.md                     # Setup and usage notes


## System Requirements

Before installing Python dependencies, make sure the following system packages are installed:

```bash
sudo apt update
sudo apt install build-essential cmake python3-dev

mistra 7
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf \
     -O /home/ubuntu/server-d-llm-inference/models/mistral-7b-instruct-v0.1.Q4_K_M.gguf