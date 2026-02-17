"""
Pixel Notes Backend - Redis Client Module
Handles all Redis operations for ephemeral message storage
"""
import redis
import json
import uuid
from typing import Optional, List
from datetime import datetime

from app.config import settings


class RedisClient:
    """Redis client for ephemeral message storage"""
    
    _instance: Optional['RedisClient'] = None
    
    def __new__(cls) -> 'RedisClient':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
        return cls._instance
    
    @property
    def client(self) -> redis.Redis:
        """Get or create Redis client"""
        if self._client is None:
            self._client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
        return self._client
    
    def health_check(self) -> bool:
        """Check Redis connection health"""
        try:
            return self.client.ping()
        except redis.RedisError:
            return False
    
    # ===========================================
    # CHAT MESSAGE OPERATIONS
    # ===========================================
    
    def add_message(self, username: str, message: str) -> dict:
        """
        Add a message to the global chat room.
        Message is stored with TTL.
        
        Args:
            username: Sender username
            message: Encrypted message content
            
        Returns:
            dict: Message object with id and timestamp
        """
        message_obj = {
            "id": str(uuid.uuid4()),
            "from": username,
            "message": message,
            "timestamp": int(datetime.utcnow().timestamp()),
        }
        
        # Add to list
        self.client.lpush("chat:room:global", json.dumps(message_obj))
        
        # Set/refresh TTL on the key
        self.client.expire("chat:room:global", settings.redis_ttl_seconds)
        
        return message_obj
    
    def get_messages(self, count: int = 100) -> List[dict]:
        """
        Get messages from the global chat room.
        
        Args:
            count: Maximum number of messages to retrieve
            
        Returns:
            List[dict]: List of message objects (oldest first)
        """
        messages = self.client.lrange("chat:room:global", 0, count - 1)
        
        # Parse and reverse (oldest first)
        parsed = [json.loads(msg) for msg in messages]
        return list(reversed(parsed))
    
    def clear_messages(self) -> int:
        """
        Clear all messages from the global chat room.
        
        Returns:
            int: Number of messages cleared
        """
        count = self.client.llen("chat:room:global")
        self.client.delete("chat:room:global")
        return count
    
    def get_message_count(self) -> int:
        """Get the number of messages in the chat room"""
        return self.client.llen("chat:room:global")
    
    # ===========================================
    # NOTES OPERATIONS (Surface App)
    # ===========================================
    
    def save_note(self, note_id: str, content: str, ttl: Optional[int] = None) -> bool:
        """
        Save a note with optional TTL.
        
        Args:
            note_id: Unique note identifier
            content: Note content
            ttl: Optional TTL in seconds
            
        Returns:
            bool: Success status
        """
        key = f"note:{note_id}"
        self.client.set(key, content)
        if ttl:
            self.client.expire(key, ttl)
        return True
    
    def get_note(self, note_id: str) -> Optional[str]:
        """Get a note by ID"""
        key = f"note:{note_id}"
        return self.client.get(key)
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note by ID"""
        key = f"note:{note_id}"
        return bool(self.client.delete(key))
    
    def list_notes(self) -> List[str]:
        """List all note IDs"""
        return self.client.keys("note:*")
    
    # ===========================================
    # RATE LIMITING
    # ===========================================
    
    def increment_rate_limit(self, key: str, window_seconds: int) -> int:
        """
        Increment rate limit counter for a key.
        
        Args:
            key: Rate limit key (e.g., IP address)
            window_seconds: Time window in seconds
            
        Returns:
            int: Current count
        """
        rl_key = f"ratelimit:{key}"
        count = self.client.incr(rl_key)
        
        if count == 1:
            self.client.expire(rl_key, window_seconds)
        
        return count
    
    def get_rate_limit(self, key: str) -> int:
        """Get current rate limit count for a key"""
        rl_key = f"ratelimit:{key}"
        count = self.client.get(rl_key)
        return int(count) if count else 0


# Global Redis client instance
redis_client = RedisClient()
