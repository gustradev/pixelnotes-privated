"""
Pixel Notes Backend - Authentication Routes
Handles secret entry and user login
"""
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models import (
    EntryPasswordRequest,
    EntryPasswordResponse,
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
    "/entry",
    response_model=EntryPasswordResponse,
    responses={
        200: {"model": EntryPasswordResponse},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
    summary="Validate secret entry password",
    description="Validates the secret entry password to access hidden chat mode",
)
@limiter.limit("5/minute")
async def validate_entry_password(
    request: Request,
    body: EntryPasswordRequest,
):
    """
    Validate the secret entry password.
    
    - Returns valid=True if password matches
    - Returns valid=False with no error message if incorrect (security)
    - Rate limited to 5 attempts per minute
    """
    is_valid = AuthHandler.validate_entry_password(body.password)
    
    if is_valid:
        return EntryPasswordResponse(valid=True, message="Access granted")
    
    # No explicit error for security - silent failure
    return EntryPasswordResponse(valid=False)


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
async def verify_token(username: str = get_current_user):
    """
    Verify the current JWT token.
    
    Requires valid Authorization header with Bearer token.
    """
    return {"valid": True, "username": username}
