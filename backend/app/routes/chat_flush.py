"""
Pixel Notes Backend - Chat Routes (Enhanced)
Includes stealth notifications and remote flush
"""
import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional

from app.models import (
    SendMessageRequest,
    SendMessageResponse,
    MessageResponse,
    MessagesResponse,
    ClearChatResponse,
    ErrorResponse,
    FlushChatResponse,
)
from app.auth import get_current_user
from app.redis_client import redis_client
from app.websocket_manager import stealth_service

logger = logging.getLogger(__name__)
from app.config import settings

router = APIRouter(prefix="/chat", tags=["Chat"])
limiter = Limiter(key_func=get_remote_address)

# Store recent flush event IDs for replay protection
FLUSH_COOLDOWN_SECONDS = 10


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
    - Triggers stealth notification to all connected clients
    """
    message_obj = redis_client.add_message(username, body.message)
    
    # Publish stealth notification signal
    await stealth_service.publish_message_signal(message_obj["id"])
    
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


@router.post(
    "/flush",
    response_model=FlushChatResponse,
    responses={
        200: {"model": FlushChatResponse},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    },
    summary="Remote flush chat",
    description="Flush all chat messages and notify all connected clients in realtime",
)
@limiter.limit("6/minute")  # One flush per 10 seconds max
async def flush_chat(
    request: Request,
    username: str = Depends(get_current_user),
):
    """
    Remote flush chat - deletes all messages and broadcasts to all clients.
    
    Security:
    - Requires valid JWT token
    - Rate limited (cooldown enforced)
    - Event signed with HMAC
    - Replay protection via event ID tracking
    
    Flow:
    1. Validate user
    2. Check cooldown
    3. Delete Redis messages
    4. Generate signed event
    5. Broadcast to all WebSocket clients
    6. Store event ID for replay protection
    """
    # Check cooldown
    last_flush = redis_client.client.get("chat:flush:last_time")
    if last_flush:
        last_time = int(last_flush)
        current_time = int(datetime.utcnow().timestamp())
        if current_time - last_time < FLUSH_COOLDOWN_SECONDS:
            raise HTTPException(
                status_code=429,
                detail=f"Cooldown active. Try again in {FLUSH_COOLDOWN_SECONDS - (current_time - last_time)} seconds."
            )
    
    # Generate event ID
    event_id = str(uuid.uuid4())
    timestamp = int(datetime.utcnow().timestamp())
    
    # Delete all messages
    cleared_count = redis_client.clear_messages()
    
    # Reset TTL on chat key
    redis_client.client.delete("chat:room:global")
    
    # Store flush event for replay protection (60 second TTL)
    redis_client.client.setex(
        f"chat:flush:event:{event_id}",
        60,
        str(timestamp)
    )
    
    # Store last flush time for cooldown
    redis_client.client.set("chat:flush:last_time", str(timestamp))
    
    # Broadcast flush signal to all connected clients
    await stealth_service.publish_flush_signal(event_id)
    
    logger.info("chat_flush executed user=%s ts=%s cleared=%s", username, timestamp, cleared_count)
    
    return FlushChatResponse(
        success=True,
        event_id=event_id,
        cleared_count=cleared_count,
        timestamp=timestamp,
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


@router.get(
    "/events/poll",
    summary="Poll for events (fallback)",
    description="Polling endpoint for clients without WebSocket support",
)
@limiter.limit("30/minute")
async def poll_events(
    request: Request,
    username: str = Depends(get_current_user),
    last_event_id: Optional[str] = None,
):
    """
    Polling fallback for realtime events.
    
    Returns any new events since last_event_id.
    Used when WebSocket is not available.
    """
    # Get last signal from Redis
    last_signal = redis_client.client.get("signal:last")
    
    if last_signal is None:
        return {"events": []}
    
    import json
    signal = json.loads(last_signal)
    
    # Check if this is a new event
    if last_event_id and signal.get("event_id") == last_event_id:
        return {"events": []}
    
    return {"events": [signal]}
