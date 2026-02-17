"""
Pixel Notes Backend - Authentication Module
Handles JWT token generation, validation, and password hashing
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings


security = HTTPBearer()


class AuthHandler:
    """Handles all authentication operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to compare against
            
        Returns:
            bool: True if password matches
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def create_token(username: str) -> str:
        """
        Create a JWT token for a user.
        
        Args:
            username: User identifier
            
        Returns:
            str: JWT token
        """
        payload = {
            "sub": username,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=settings.jwt_expiry_hours),
            "type": "access",
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Optional[dict]: Decoded payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def validate_entry_password(password: str) -> bool:
        """
        Validate the secret entry password.
        
        Args:
            password: Password to validate
            
        Returns:
            bool: True if valid
        """
        return password == settings.secret_entry_password
    
    @staticmethod
    def validate_user(username: str, password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user credentials against .env stored users.
        
        Args:
            username: Username to validate
            password: Password to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        # Check if user exists
        if username not in settings.secret_users:
            return False, None  # No explicit error for security
        
        # Get stored hash
        stored_hash = settings.secret_users[username]
        
        # Verify password
        if AuthHandler.verify_password(password, stored_hash):
            return True, None
        
        return False, None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = security
) -> str:
    """
    FastAPI dependency to get current authenticated user.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        str: Username
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    payload = AuthHandler.decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    return username


async def get_optional_user(
    request: Request
) -> Optional[str]:
    """
    FastAPI dependency to optionally get current user.
    Returns None if no valid token provided.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Optional[str]: Username or None
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    payload = AuthHandler.decode_token(token)
    
    if payload is None:
        return None
    
    return payload.get("sub")


# Global auth handler instance
auth_handler = AuthHandler()
