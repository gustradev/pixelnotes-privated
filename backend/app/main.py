"""
Pixel Notes Backend - Main Application
FastAPI application with Redis, JWT auth, and rate limiting
"""
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.redis_client import redis_client
from app.routes import auth, chat, notes


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Pixel Notes Backend...")
    
    # Check Redis connection
    if redis_client.health_check():
        logger.info("Redis connection established")
    else:
        logger.error("Failed to connect to Redis")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Pixel Notes Backend...")


# Create FastAPI application
app = FastAPI(
    title="Pixel Notes API",
    description="Backend API for Pixel Notes application",
    version="0.1.0",
    docs_url=None,  # Disable docs in production
    redoc_url=None,  # Disable redoc in production
    lifespan=lifespan,
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600,
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Content Security Policy
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = datetime.utcnow()
    
    response = await call_next(request)
    
    duration = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    # Sanitize log output (don't log sensitive data)
    logger.info(
        f"{request.method} {request.url.path} - "
        f"{response.status_code} - {duration:.2f}ms"
    )
    
    return response


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(notes.router, prefix="/api")


# ===========================================
# HEALTH CHECK ENDPOINTS
# ===========================================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns status of the application and Redis connection.
    """
    redis_status = "healthy" if redis_client.health_check() else "unhealthy"
    
    return {
        "status": "healthy",
        "redis": redis_status,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - returns simple status"""
    return {"status": "ok", "service": "pixel-notes-api"}


# ===========================================
# ERROR HANDLERS
# ===========================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler - returns generic error"""
    logger.error(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=False,
        access_log=False,
    )
