# Chat API endpoints
from fastapi import APIRouter, HTTPException
from ..models.chat_models import ChatRequest, ChatResponse, ChatResetResponse
from .chat import chatbot

# Create router for chat endpoints
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    # Send message to chatbot and get response
    try:
        response = chatbot.generate_response(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.post("/chat/reset", response_model=ChatResetResponse)
async def reset_chat():
    # Reset the chat conversation history
    try:
        chatbot.reset_conversation()
        return ChatResetResponse(message="Chat history reset successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset error: {str(e)}")
