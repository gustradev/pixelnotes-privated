"""
Pixel Notes Backend - Encryption Module
Handles AES-256-GCM encryption/decryption for messages
"""
import os
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from typing import Tuple, Optional
import base64

from app.config import settings


class EncryptionService:
    """
    AES-256-GCM encryption service for client-server communication.
    
    The encryption key is derived from the environment variable.
    Messages are encrypted client-side and stored encrypted in Redis.
    """
    
    # AES-GCM nonce size (12 bytes is recommended)
    NONCE_SIZE = 12
    
    # AES-256 key size in bytes
    KEY_SIZE = 32
    
    def __init__(self):
        """Initialize encryption service with key from settings"""
        self._key = self._derive_key(settings.encryption_key)
        self._aesgcm = AESGCM(self._key)
    
    def _derive_key(self, base_key: str) -> bytes:
        """
        Derive a 256-bit key from the base key.
        
        Args:
            base_key: Base key string from environment
            
        Returns:
            bytes: 32-byte key for AES-256
        """
        # Use SHA-256 to derive a fixed-size key
        # In production, consider using PBKDF2 or HKDF
        derived = hashlib.sha256(
            (base_key + "pixelnotes_salt_v1").encode('utf-8')
        ).digest()
        return derived
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            str: Base64 encoded ciphertext (nonce + ciphertext)
        """
        # Generate random nonce
        nonce = os.urandom(self.NONCE_SIZE)
        
        # Encrypt
        ciphertext = self._aesgcm.encrypt(
            nonce,
            plaintext.encode('utf-8'),
            None  # No additional authenticated data
        )
        
        # Combine nonce + ciphertext and encode as base64
        combined = nonce + ciphertext
        return base64.b64encode(combined).decode('utf-8')
    
    def decrypt(self, encrypted: str) -> Optional[str]:
        """
        Decrypt an encrypted string.
        
        Args:
            encrypted: Base64 encoded ciphertext (nonce + ciphertext)
            
        Returns:
            Optional[str]: Decrypted plaintext or None if decryption fails
        """
        try:
            # Decode base64
            combined = base64.b64decode(encrypted)
            
            # Extract nonce and ciphertext
            nonce = combined[:self.NONCE_SIZE]
            ciphertext = combined[self.NONCE_SIZE:]
            
            # Decrypt
            plaintext = self._aesgcm.decrypt(
                nonce,
                ciphertext,
                None
            )
            
            return plaintext.decode('utf-8')
        except Exception:
            return None
    
    def get_key_for_client(self) -> str:
        """
        Get the encryption key for client-side encryption.
        This should only be sent to authenticated users.
        
        Returns:
            str: Base64 encoded key
        """
        return base64.b64encode(self._key).decode('utf-8')


# Global encryption service instance
encryption_service = EncryptionService()
