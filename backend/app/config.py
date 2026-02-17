"""
Pixel Notes Backend - Configuration Module
Loads environment variables and provides settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Server Configuration
    frontend_port: int = 58437
    backend_port: int = 58438
    
    # Secret Entry Password
    secret_entry_password: str
    
    # Secret Chat Users (from .env)
    secret_user_1: str
    secret_pass_1: str
    secret_user_2: str
    secret_pass_2: str
    
    # JWT Configuration
    jwt_secret: str
    jwt_expiry_hours: int = 2
    jwt_refresh_expiry_hours: int = 24
    
    # Encryption Key (AES-256-GCM)
    encryption_key: str
    
    # Redis Configuration
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_ttl_seconds: int = 86400
    
    # CORS
    cors_origins: str = "https://note.pixelsolusindo.space"
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # WebSocket Event Signing
    ws_event_secret: str = ""

    # Face Verification Service
    face_service_url: str = "http://face-gpu-service:8091"
    face_similarity_threshold: float = 0.55
    
    model_config = SettingsConfigDict(
        env_file=("credential.env", ".env"),
        case_sensitive=False,
        extra="ignore",
    )
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins as list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def secret_users(self) -> dict[str, str]:
        """Return dict of username -> hashed_password"""
        return {
            self.secret_user_1: self.secret_pass_1,
            self.secret_user_2: self.secret_pass_2,
        }

    @property
    def ws_signing_secret(self) -> str:
        """Return a non-empty secret for WebSocket event signing."""
        return self.ws_event_secret or self.jwt_secret


# Global settings instance
settings = Settings()
