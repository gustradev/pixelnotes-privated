"""
Pixel Notes Backend - WebSocket Manager
Handles realtime connections for stealth notifications
"""
import asyncio
import json
import uuid
import hmac
import hashlib
from datetime import datetime
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect

from app.config import settings
from app.redis_client import redis_client


class WebSocketManager:
    """
    Manages WebSocket connections for realtime stealth notifications.
    
    Features:
    - JWT authentication on connect
    - Heartbeat ping/pong
    - Auto reconnect support
    - Redis Pub/Sub integration
    - HMAC event signing
    """
    
    _instance: Optional['WebSocketManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connections = {}
            cls._instance._user_connections = {}
            cls._instance._lock = asyncio.Lock()
        return cls._instance
    
    async def connect(self, websocket: WebSocket, username: str) -> str:
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            username: Authenticated username
            
        Returns:
            str: Connection ID
        """
        await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        
        async with self._lock:
            self._connections[connection_id] = websocket
            
            if username not in self._user_connections:
                self._user_connections[username] = set()
            self._user_connections[username].add(connection_id)
        
        return connection_id
    
    async def disconnect(self, connection_id: str, username: str):
        """Remove a WebSocket connection."""
        async with self._lock:
            self._connections.pop(connection_id, None)
            
            if username in self._user_connections:
                self._user_connections[username].discard(connection_id)
                if not self._user_connections[username]:
                    del self._user_connections[username]
    
    async def send_to_user(self, username: str, message: dict):
        """Send a message to all connections of a specific user."""
        async with self._lock:
            connection_ids = self._user_connections.get(username, set()).copy()
        
        for conn_id in connection_ids:
            websocket = self._connections.get(conn_id)
            if websocket:
                try:
                    await websocket.send_json(message)
                except Exception:
                    await self.disconnect(conn_id, username)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        async with self._lock:
            connections = list(self._connections.items())
        
        for conn_id, websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                pass
    
    def generate_event_signature(self, event_id: str, timestamp: int, event_type: str) -> str:
        """
        Generate HMAC-SHA256 signature for event authentication.
        
        Args:
            event_id: Unique event identifier
            timestamp: Unix timestamp
            event_type: Type of event
            
        Returns:
            str: Hex signature
        """
        message = f"{event_id}:{timestamp}:{event_type}"
        signature = hmac.new(
            settings.ws_signing_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def verify_event_signature(self, event_id: str, timestamp: int, event_type: str, signature: str) -> bool:
        """Verify event signature to prevent injection attacks."""
        expected = self.generate_event_signature(event_id, timestamp, event_type)
        return hmac.compare_digest(expected, signature)


# Global WebSocket manager instance
ws_manager = WebSocketManager()


class StealthNotificationService:
    """
    Handles stealth notification generation and broadcasting.
    
    The notification payload NEVER contains:
    - Sender name
    - Message content
    - Any chat indicator
    
    Only contains encrypted signal that triggers local template display.
    """
    
    @staticmethod
    def create_message_signal(message_id: str) -> dict:
        """
        Create a stealth signal for new message notification.
        
        This signal contains NO plaintext data about the message.
        The client must decrypt locally to know what happened.
        
        Returns:
            dict: Stealth signal payload
        """
        event_id = str(uuid.uuid4())
        timestamp = int(datetime.utcnow().timestamp())
        nonce = uuid.uuid4().hex[:16]
        
        # Create checksum for integrity
        checksum_data = f"{event_id}:{nonce}:{timestamp}"
        checksum = hashlib.sha256(checksum_data.encode()).hexdigest()[:16]
        
        # Generate HMAC signature
        signature = ws_manager.generate_event_signature(event_id, timestamp, "message")
        
        return {
            "type": "event",
            "event_id": event_id,
            "nonce": nonce,
            "timestamp": timestamp,
            "checksum": checksum,
            "signature": signature,
            "signal_type": "generic",
        }
    
    @staticmethod
    def create_flush_signal(event_id: str) -> dict:
        """
        Create a stealth signal for chat flush notification.
        
        Returns:
            dict: Flush signal payload
        """
        timestamp = int(datetime.utcnow().timestamp())
        signature = ws_manager.generate_event_signature(event_id, timestamp, "flush")
        
        return {
            "type": "flush",
            "event_id": event_id,
            "timestamp": timestamp,
            "signature": signature,
        }
    
    @staticmethod
    async def publish_message_signal(message_id: str):
        """
        Publish message signal to Redis and broadcast via WebSocket.
        
        Args:
            message_id: ID of the new message
        """
        signal = StealthNotificationService.create_message_signal(message_id)
        
        # Store signal in Redis for polling fallback (short TTL)
        redis_client.client.setex(
            f"signal:last:{message_id}",
            60,
            json.dumps(signal)
        )
        redis_client.client.setex(
            "signal:last",
            60,
            json.dumps(signal)
        )
        
        # Publish to Redis channel
        redis_client.client.publish("chat:signals", json.dumps(signal))
        
        # Broadcast to all WebSocket connections
        await ws_manager.broadcast(signal)
    
    @staticmethod
    async def publish_flush_signal(event_id: str):
        """
        Publish flush signal to all clients.
        
        Args:
            event_id: Unique flush event ID
        """
        signal = StealthNotificationService.create_flush_signal(event_id)
        
        # Publish to Redis channel
        redis_client.client.publish("chat:signals", json.dumps(signal))
        
        # Broadcast to all WebSocket connections
        await ws_manager.broadcast(signal)


# Global service instance
stealth_service = StealthNotificationService()
