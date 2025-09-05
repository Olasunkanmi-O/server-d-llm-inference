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