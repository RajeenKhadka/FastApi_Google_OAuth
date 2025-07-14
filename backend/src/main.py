# FastAPI app with Google OAuth
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables first
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Import OAuth and Chat routes
from src.auth.oauth import router as oauth_router
from src.chat.routes import router as chat_router

# Create app
app = FastAPI()

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add OAuth and Chat routes
app.include_router(oauth_router)
app.include_router(chat_router)


@app.get("/")
async def home():
    # API info
    return {
        "message": "FastAPI Google OAuth2 API with AI Chat",
        "endpoints": {
            "login": "/login",
            "callback": "/auth/callback",
            "user_info": "/auth/me",
            "logout": "/auth/logout",
            "chat": "/chat",
            "reset_chat": "/chat/reset"
        }
    }


# Start server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)