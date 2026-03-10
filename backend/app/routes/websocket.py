"""
Pixel Notes Backend - WebSocket Routes
Realtime stealth notification endpoints
"""
import asyncio
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict

from app.websocket_manager import ws_manager
from app.auth import AuthHandler

router = APIRouter(tags=["WebSocket"])
_call_rooms: Dict[str, Dict[str, WebSocket]] = {}
_call_conn_meta: Dict[str, tuple[str, str]] = {}
_call_lock = asyncio.Lock()


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


@router.websocket("/ws/call")
async def websocket_call_signaling(
    websocket: WebSocket,
    token: str = Query(...),
    room: str = Query("global"),
):
    """
    WebRTC signaling WebSocket endpoint.

    Message format from client:
    {
      "type": "call-invite|offer|answer|ice-candidate|call-end|call-decline|call-busy|ping",
      "data": { ... }
    }

    Server relays signaling packets to other peers in the same room.
    """
    payload = AuthHandler.decode_token(token)
    if payload is None:
        await websocket.close(code=4001, reason="Invalid token")
        return

    username = payload.get("sub")
    if not username:
        await websocket.close(code=4001, reason="Invalid token payload")
        return

    await websocket.accept()
    conn_id = str(uuid.uuid4())

    async with _call_lock:
        if room not in _call_rooms:
            _call_rooms[room] = {}
        _call_rooms[room][conn_id] = websocket
        _call_conn_meta[conn_id] = (room, username)

    await _call_broadcast(
        room,
        {
            "type": "participant-joined",
            "from": username,
            "room": room,
            "timestamp": int(datetime.utcnow().timestamp()),
            "data": {},
        },
        exclude_conn=conn_id,
    )

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = message.get("type")
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            envelope = {
                "type": msg_type,
                "from": username,
                "room": room,
                "timestamp": int(datetime.utcnow().timestamp()),
                "data": message.get("data", {}),
            }

            await _call_broadcast(room, envelope, exclude_conn=conn_id)

    except WebSocketDisconnect:
        pass
    finally:
        await _remove_call_connection(conn_id)


async def _call_broadcast(room: str, payload: dict, exclude_conn: str | None = None):
    async with _call_lock:
        connections = list(_call_rooms.get(room, {}).items())

    stale_conn_ids = []
    for conn_id, ws in connections:
        if exclude_conn and conn_id == exclude_conn:
            continue
        try:
            await ws.send_json(payload)
        except Exception:
            stale_conn_ids.append(conn_id)

    for stale in stale_conn_ids:
        await _remove_call_connection(stale)


async def _remove_call_connection(conn_id: str):
    room = None
    username = None

    async with _call_lock:
        meta = _call_conn_meta.pop(conn_id, None)
        if meta:
            room, username = meta
            room_map = _call_rooms.get(room, {})
            room_map.pop(conn_id, None)
            if not room_map and room in _call_rooms:
                del _call_rooms[room]

    if room and username:
        await _call_broadcast(
            room,
            {
                "type": "participant-left",
                "from": username,
                "room": room,
                "timestamp": int(datetime.utcnow().timestamp()),
                "data": {},
            },
            exclude_conn=conn_id,
        )
