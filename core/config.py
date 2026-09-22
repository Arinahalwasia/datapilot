import os
import json
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency for env loading
    def load_dotenv(*_args, **_kwargs):  # type: ignore[empty-body]
        """Fallback no-op when python-dotenv is not installed."""


# Load environment variables from .env
load_dotenv()

# Define PROJECT_ROOT early - needed for session paths (resolve to absolute path)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

try:
    models_json = os.environ.get("AI_MODELS_CONFIG", "[]")
    AVAILABLE_MODELS = json.loads(models_json)
    if not AVAILABLE_MODELS:
        raise ValueError("AI_MODELS_CONFIG is empty or not configured in .env file.")
except (json.JSONDecodeError, ValueError) as e:
    print(f"CRITICAL ERROR: Could not parse AI_MODELS_CONFIG from .env file. Details: {e}")
    # Define a fallback model so the app doesn't crash
    AVAILABLE_MODELS = [{
        "name": "Gemma 3",
        "api_url": "http://10.242.139.97:8081/v1",
        "api_key": "dummy-key"
    }]

# DESIRED_MODEL_NAME = "gpt-oss-120b"  # Currently returning 502 Bad Gateway
DESIRED_MODEL_NAME = "Gemma 4"
DEFAULT_MODEL = next((model for model in AVAILABLE_MODELS if model["name"] == DESIRED_MODEL_NAME), AVAILABLE_MODELS[0])
AI_MODEL_NAME = DEFAULT_MODEL["name"]
AI_API_URL = DEFAULT_MODEL["api_url"]
OPENAI_API_KEY = DEFAULT_MODEL["api_key"]

print(f"--- Config: Default AI Model set to: {AI_MODEL_NAME} ({AI_API_URL}) ---")
print(f"--- Config: Found {len(AVAILABLE_MODELS)} available models. ---")

SUMMARY_MODEL_NAME = os.environ.get("SUMMARY_MODEL_NAME", AI_MODEL_NAME)
MAX_API_RETRIES = int(os.getenv("MAX_API_RETRIES", "3"))




