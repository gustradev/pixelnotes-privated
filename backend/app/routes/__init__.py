"""
Pixel Notes Backend - Routes Package
"""
from app.routes import auth, chat_flush as chat, notes, websocket, face

__all__ = ["auth", "chat", "notes", "websocket", "face"]
