# Google OAuth for FastAPI
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import RedirectResponse, JSONResponse
import httpx
from urllib.parse import urlencode
import os
import uuid
from typing import Dict
from ..models.models import User, UserResponse

# Router for OAuth endpoints
router = APIRouter()

# Store sessions in memory (use Redis for production)
sessions: Dict[str, User] = {}

# Google OAuth URLs
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def get_oauth_credentials():
    # Get OAuth credentials from environment
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    
    if not all([client_id, client_secret, redirect_uri]):
        raise HTTPException(
            status_code=500, 
            detail="Google OAuth not configured. Check your .env file."
        )
    
    return client_id, client_secret, redirect_uri


@router.get("/login")
def login():
    """Step 1: Redirect user to Google for authentication"""
    client_id, _, redirect_uri = get_oauth_credentials()
    
    # Parameters for Google OAuth
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    
    # Build Google OAuth URL and redirect
    google_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(google_url)


@router.get("/auth/callback")
async def auth_callback(request: Request):
    """Step 2: Handle Google's response and create user session"""
    client_id, client_secret, redirect_uri = get_oauth_credentials()
    
    # Get authorization code from Google
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code received")
    
    try:
        async with httpx.AsyncClient() as client:
            # Exchange code for access token
            token_data = {
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code"
            }
            
            token_response = await client.post(GOOGLE_TOKEN_URL, data=token_data)
            tokens = token_response.json()
            access_token = tokens.get("access_token")
            
            if not access_token:
                raise HTTPException(status_code=400, detail="Failed to get access token")
            
            # Get user info from Google
            headers = {"Authorization": f"Bearer {access_token}"}
            user_response = await client.get(GOOGLE_USER_INFO_URL, headers=headers)
            user_data = user_response.json()
            
            # Create user object
            user = User(
                name=user_data.get("name", ""),
                email=user_data.get("email", ""),
                picture=user_data.get("picture")
            )
            
            # Create session
            session_id = str(uuid.uuid4())
            sessions[session_id] = user
            
            # Redirect to frontend with session cookie
            response = RedirectResponse("http://localhost:5174/")
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,  # Secure: can't be accessed by JavaScript
                max_age=3600,   # 1 hour expiry
                samesite="lax"  # CSRF protection
            )
            return response
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.get("/auth/me", response_model=UserResponse)
def get_current_user(request: Request):
    """Get current logged-in user from session"""
    session_id = request.cookies.get("session_id")
    
    # Check if session exists
    if not session_id or session_id not in sessions:
        return UserResponse(user=None, error="Not logged in")
    
    # Return user data
    user = sessions[session_id]
    return UserResponse(user=user, error=None)


@router.post("/auth/logout")
def logout(request: Request):
    """Logout user and clear session"""
    session_id = request.cookies.get("session_id")
    
    # Remove session if it exists
    if session_id and session_id in sessions:
        del sessions[session_id]
    
    # Clear cookie and return success
    response = JSONResponse({"message": "Logged out successfully"})
    response.delete_cookie("session_id")
    return response
