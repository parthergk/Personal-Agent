import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("API_KEY")

if not QDRANT_URL:
    raise RuntimeError("Qdrant configuration is missing.")

if not QDRANT_API_KEY:
    raise RuntimeError("Qdrant credentials are missing.")


qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    cloud_inference=True
)
