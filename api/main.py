import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.session import Base, engine
from db.setup import setup_qdrant
from routes import api_router
from services import start_scheduler, stop_scheduler

load_dotenv()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning("Could not auto-create tables: %s", e)

    try:
        setup_qdrant()
    except Exception as e:
        logger.warning("Could not setup Qdrant collection: %s", e)

    # Start reminder scheduler on startup (every 5 seconds)
    start_scheduler(interval_seconds=5)
    yield
    # Stop scheduler on shutdown
    stop_scheduler()


app = FastAPI(title="Personal Agent API", lifespan=lifespan)

# Allow CORS for Next.js frontend or other clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register application routes
app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
