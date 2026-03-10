"""
Pixel Notes Backend - Authentication Routes
Handles secret entry and user login
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models import (
    LoginRequest,
    LoginResponse,
    ErrorResponse,
)
from app.auth import AuthHandler, get_current_user
from app.config import settings
from app.encryption import encryption_service

router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)





@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        200: {"model": LoginResponse},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
    summary="Login with secret user credentials",
    description="Authenticate with one of the two secret users stored in .env",
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: LoginRequest,
):
    """
    Login with secret user credentials.
    
    - Username and password must match .env stored users
    - Passwords are hashed with bcrypt
    - Returns JWT token on success
    - Rate limited to 10 attempts per minute
    """
    is_valid, error = AuthHandler.validate_user(body.username, body.password)
    
    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # Create JWT token
    token = AuthHandler.create_token(body.username)
    
    return LoginResponse(
        token=token,
        username=body.username,
        expires_in=settings.jwt_expiry_hours * 3600,
        encryption_key=encryption_service.get_key_for_client(),
    )


@router.get(
    "/verify",
    summary="Verify JWT token",
    description="Verify if the current JWT token is valid",
)
async def verify_token(username: str = Depends(get_current_user)):
    """
    Verify the current JWT token.
    
    Requires valid Authorization header with Bearer token.
    """
    return {"valid": True, "username": username}
