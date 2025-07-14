# Data models for chat functionality
from pydantic import BaseModel


class ChatRequest(BaseModel):
    # Request for sending a message to the chatbot
    message: str


class ChatResponse(BaseModel):
    # Response from the chatbot
    response: str


class ChatResetResponse(BaseModel):
    # Response for chat reset confirmation
    message: str
