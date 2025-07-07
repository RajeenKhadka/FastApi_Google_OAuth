import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from pathlib import Path
import os

# Load .env from the root project directory before importing anything that uses env vars
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Import the OAuth router after .env is loaded
from .oauth import router as oauth_router

# Create FastAPI app instance
app = FastAPI()
# Include OAuth routes (login, callback) from oauth.py
app.include_router(oauth_router)

# Home page with a link to start Google OAuth login
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h2>Welcome to FastAPI Google OAuth2 Login</h2>
    <a href="/login">Login with Google</a>
    """

# Profile page that displays user info after successful login
@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    user_info = request.query_params
    name = user_info.get("name")
    email = user_info.get("email")
    picture = user_info.get("picture")
    return f"""
    <html>
        <head><title>User Profile</title></head>
        <body style='text-align:center; font-family:sans-serif;'>
            <h1>Welcome, {name}!</h1>
            <img src=\"{picture}\" alt=\"Profile Picture\" width=\"120\"/><br>
            <p>Email: {email}</p>
        </body>
    </html>
    """

# Run the app with Uvicorn if this file is executed directly
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)