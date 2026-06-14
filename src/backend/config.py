import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Root directory helper
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(root_dir, 'data', 'design_concierge.db')}")
MODEL_PATH = os.path.join(root_dir, "models", "budget_model.joblib")
UPLOAD_DIR = os.path.join(root_dir, "static", "uploads")

# Ensure directories exist
os.makedirs(os.path.join(root_dir, "data"), exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
