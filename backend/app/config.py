import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./design_concierge.db")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml", "budget_model.joblib")
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
