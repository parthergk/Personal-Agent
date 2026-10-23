# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from pydantic import BaseModel
from agent import process_message

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat(request: ChatRequest):

    response = process_message(
        request.message
    )

    return {
        "response": response
    }


class SendOtpRequest(BaseModel):
    phone: str


@app.post("/send-otp")
async def send_otp(request: SendOtpRequest):
    return {
        "success": True,
        "message": "Verification code sent successfully",
        "dummy_code": "123456",
        "phone": request.phone
    }
