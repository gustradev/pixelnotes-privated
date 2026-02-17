"""
Pixel Notes Backend - Face Verification Routes
Orchestrates face verification against GPU microservice.
"""
from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/face", tags=["Face"])


class FaceVerifyRequest(BaseModel):
    frames_base64: List[str] = Field(..., min_length=3, max_length=12)
    enrolled_embedding: List[float] = Field(..., min_length=128, max_length=1024)


@router.post("/verify")
async def verify_face(body: FaceVerifyRequest, username: str = Depends(get_current_user)):
    payload = {
        "frames_base64": body.frames_base64,
        "enrolled_embedding": body.enrolled_embedding,
        "threshold": settings.face_similarity_threshold,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{settings.face_service_url}/verify", json=payload)
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="Face service unavailable")

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Face verification failed")

    data = response.json()
    return {
        "verified": bool(data.get("verified", False)),
        "score": float(data.get("score", 0.0)),
        "frame_count": int(data.get("frame_count", 0)),
        "user": username,
    }
