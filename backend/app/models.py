"""
Pixel Notes Backend - Pydantic Models
Request and response models for API endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ===========================================
# AUTH MODELS
# ===========================================




class LoginRequest(BaseModel):
    """Request model for user login"""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Response model for successful login"""
    token: str
    username: str
    expires_in: int  # seconds
    encryption_key: str  # For client-side encryption


class ErrorResponse(BaseModel):
    """Generic error response"""
    error: str
    detail: Optional[str] = None


# ===========================================
# CHAT MODELS
# ===========================================

class SendMessageRequest(BaseModel):
    """Request model for sending a chat message"""
    message: str = Field(..., min_length=1, max_length=10000)


class MessageResponse(BaseModel):
    """Response model for a single message"""
    id: str
    from_user: str = Field(..., alias="from")
    message: str
    timestamp: int
    
    class Config:
        populate_by_name = True


class MessagesResponse(BaseModel):
    """Response model for list of messages"""
    messages: List[MessageResponse]
    count: int


class SendMessageResponse(BaseModel):
    """Response model for sending a message"""
    success: bool
    message_id: str
    timestamp: int


class ClearChatResponse(BaseModel):
    """Response model for clearing chat"""
    success: bool
    cleared_count: int


class FlushChatResponse(BaseModel):
    """Response model for remote flush chat"""
    success: bool
    event_id: str
    cleared_count: int
    timestamp: int


class WebSocketEvent(BaseModel):
    """Model for WebSocket events"""
    type: str  # "event", "flush", "ping", "pong"
    event_id: Optional[str] = None
    nonce: Optional[str] = None
    timestamp: Optional[int] = None
    checksum: Optional[str] = None
    signature: Optional[str] = None
    signal_type: Optional[str] = None
    message_id: Optional[str] = None


# ===========================================
# NOTES MODELS (Surface App)
# ===========================================

class NoteCreateRequest(BaseModel):
    """Request model for creating a note"""
    content: str = Field(..., max_length=50000)
    ttl: Optional[int] = Field(None, description="Optional TTL in seconds")


class NoteResponse(BaseModel):
    """Response model for a single note"""
    id: str
    content: str
    created_at: Optional[datetime] = None


class NotesListResponse(BaseModel):
    """Response model for list of notes"""
    notes: List[str]  # List of note IDs


# ===========================================
# HEALTH MODELS
# ===========================================

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    redis: str
    timestamp: str
