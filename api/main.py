from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from agent import process_message, IncomingMessage
from processors import preprocess_message
from services.reminder_scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start reminder scheduler on startup (every 5 seconds)
    start_scheduler(interval_seconds=5)
    yield
    # Stop scheduler on shutdown
    stop_scheduler()


app = FastAPI(lifespan=lifespan)


class ChatRequest(BaseModel):
    message: IncomingMessage


@app.post("/chat")
async def chat(request: ChatRequest):

    preprocess_response = preprocess_message(request.message)
    print("\n\npreprocess response", preprocess_response)
    response = process_message(preprocess_response)

    return {
        "response": response
    }