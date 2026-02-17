"""
Pixel Notes Backend - Chat Routes
Handles secret chat message operations
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List

from app.models import (
    SendMessageRequest,
    SendMessageResponse,
    MessageResponse,
    MessagesResponse,
    ClearChatResponse,
    ErrorResponse,
)
from app.auth import get_current_user
from app.redis_client import redis_client

router = APIRouter(prefix="/chat", tags=["Chat"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/messages",
    response_model=MessagesResponse,
    responses={
        200: {"model": MessagesResponse},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
    summary="Get all chat messages",
    description="Retrieve all messages from the global chat room",
)
@limiter.limit("60/minute")
async def get_messages(
    request: Request,
    username: str = Depends(get_current_user),
    count: int = 100,
):
    """
    Get all messages from the global chat room.
    
    - Requires valid JWT token
    - Messages are returned oldest first
    - Default limit is 100 messages
    """
    messages = redis_client.get_messages(count)
    
    message_responses = [
        MessageResponse(
            id=msg["id"],
            from_user=msg["from"],
            message=msg["message"],
            timestamp=msg["timestamp"],
        )
        for msg in messages
    ]
    
    return MessagesResponse(
        messages=message_responses,
        count=len(message_responses),
    )


@router.post(
    "/send",
    response_model=SendMessageResponse,
    responses={
        200: {"model": SendMessageResponse},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
    summary="Send a chat message",
    description="Send an encrypted message to the global chat room",
)
@limiter.limit("30/minute")
async def send_message(
    request: Request,
    body: SendMessageRequest,
    username: str = Depends(get_current_user),
):
    """
    Send a message to the global chat room.
    
    - Requires valid JWT token
    - Message should be encrypted client-side
    - Messages auto-expire after TTL (24 hours)
    """
    message_obj = redis_client.add_message(username, body.message)
    
    return SendMessageResponse(
        success=True,
        message_id=message_obj["id"],
        timestamp=message_obj["timestamp"],
    )


@router.delete(
    "/clear",
    response_model=ClearChatResponse,
    responses={
        200: {"model": ClearChatResponse},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
    summary="Clear all chat messages",
    description="Clear all messages from the global chat room (admin only)",
)
@limiter.limit("5/minute")
async def clear_chat(
    request: Request,
    username: str = Depends(get_current_user),
):
    """
    Clear all messages from the global chat room.
    
    - Requires valid JWT token
    - Rate limited to 5 requests per minute
    """
    cleared_count = redis_client.clear_messages()
    
    return ClearChatResponse(
        success=True,
        cleared_count=cleared_count,
    )


@router.get(
    "/count",
    summary="Get message count",
    description="Get the number of messages in the chat room",
)
@limiter.limit("60/minute")
async def get_message_count(
    request: Request,
    username: str = Depends(get_current_user),
):
    """
    Get the number of messages in the chat room.
    
    - Requires valid JWT token
    """
    count = redis_client.get_message_count()
    return {"count": count}
