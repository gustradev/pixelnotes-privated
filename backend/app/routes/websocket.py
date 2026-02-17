"""
Pixel Notes Backend - WebSocket Routes
Realtime stealth notification endpoints
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional

from app.websocket_manager import ws_manager
from app.auth import AuthHandler

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    WebSocket endpoint for realtime stealth notifications.
    
    Connection flow:
    1. Client connects with JWT token
    2. Server validates token
    3. Server sends heartbeat ping every 30 seconds
    4. Client responds with pong
    5. Server broadcasts stealth signals
    
    Message types:
    - event: New message signal (no content)
    - flush: Chat flush signal
    - ping: Heartbeat request
    - pong: Heartbeat response
    """
    # Validate JWT token
    payload = AuthHandler.decode_token(token)
    
    if payload is None:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    username = payload.get("sub")
    if not username:
        await websocket.close(code=4001, reason="Invalid token payload")
        return
    
    # Accept connection
    connection_id = await ws_manager.connect(websocket, username)
    
    # Start heartbeat task
    heartbeat_task = asyncio.create_task(
        _heartbeat_loop(websocket, connection_id, username)
    )
    
    try:
        # Main message loop
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Handle pong response
                if message.get("type") == "pong":
                    # Client responded to ping, connection alive
                    continue
                
                # Handle client ping
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    continue
                
            except json.JSONDecodeError:
                # Invalid JSON, ignore
                continue
    
    except WebSocketDisconnect:
        pass
    
    finally:
        heartbeat_task.cancel()
        await ws_manager.disconnect(connection_id, username)


async def _heartbeat_loop(websocket: WebSocket, connection_id: str, username: str):
    """
    Send periodic heartbeat pings to keep connection alive.
    
    If client doesn't respond within 60 seconds, connection is closed.
    """
    missed_pongs = 0
    max_missed = 2
    
    while True:
        try:
            await asyncio.sleep(30)  # Ping every 30 seconds
            
            # Send ping
            await websocket.send_json({"type": "ping"})
            
            # Wait briefly for pong (handled in main loop)
            # If too many missed, close connection
            missed_pongs += 1
            if missed_pongs > max_missed:
                await websocket.close(code=4002, reason="Heartbeat timeout")
                break
                
        except Exception:
            break


@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    token: str = Query(...),
):
    """
    WebSocket endpoint for realtime chat updates.
    
    Combines:
    - Message signals
    - Flush signals
    - Typing indicators (optional)
    """
    # Validate JWT token
    payload = AuthHandler.decode_token(token)
    
    if payload is None:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    username = payload.get("sub")
    if not username:
        await websocket.close(code=4001, reason="Invalid token payload")
        return
    
    # Accept connection
    connection_id = await ws_manager.connect(websocket, username)
    
    # Start background tasks
    heartbeat_task = asyncio.create_task(
        _heartbeat_loop(websocket, connection_id, username)
    )
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                if message.get("type") == "pong":
                    continue
                
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    continue
                
                # Handle typing indicator (optional)
                if message.get("type") == "typing":
                    # Broadcast typing status to other user
                    # Don't reveal who is typing
                    await ws_manager.broadcast({
                        "type": "typing",
                        "signal": True,
                    })
                    continue
                
            except json.JSONDecodeError:
                continue
    
    except WebSocketDisconnect:
        pass
    
    finally:
        heartbeat_task.cancel()
        await ws_manager.disconnect(connection_id, username)
