import base64
import importlib
import logging
import math
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


class VerifyRequest(BaseModel):
    frames_base64: List[str] = Field(..., min_length=3, max_length=12)
    enrolled_embedding: List[float] = Field(..., min_length=128, max_length=1024)
    threshold: float = Field(0.55, ge=0.2, le=0.95)


class VerifyResponse(BaseModel):
    verified: bool
    score: float
    frame_count: int


class FaceEngine:
    def __init__(self) -> None:
        try:
            insightface_app = importlib.import_module("insightface.app")
            face_analysis_cls = getattr(insightface_app, "FaceAnalysis")
            self._app = face_analysis_cls(name="buffalo_l", providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
            self._app.prepare(ctx_id=0, det_size=(640, 640))
            self._ready = True
        except Exception as exc:
            logger.exception("Face engine initialization failed")
            self._app = None
            self._ready = False
            self._init_error = str(exc)

    @property
    def ready(self) -> bool:
        return self._ready

    def embedding_from_frame(self, frame_b64: str) -> List[float]:
        if not self._app:
            raise RuntimeError("Face engine not initialized")

        np = importlib.import_module("numpy")
        cv2 = importlib.import_module("cv2")

        decoded = base64.b64decode(frame_b64)
        np_bytes = np.frombuffer(decoded, dtype=np.uint8)
        image = cv2.imdecode(np_bytes, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Invalid image frame")

        faces = self._app.get(image)
        if not faces:
            raise ValueError("No face detected")

        emb = faces[0].embedding
        if emb is None:
            raise ValueError("No embedding generated")
        return [float(value) for value in emb]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    a_norm = math.sqrt(sum(x * x for x in a))
    b_norm = math.sqrt(sum(y * y for y in b))
    if a_norm == 0 or b_norm == 0:
        return 0.0
    return float(dot / (a_norm * b_norm))


app = FastAPI(title="Pixel Notes Face GPU Service", version="1.0.0")
engine = FaceEngine()


@app.get("/health")
async def health() -> dict:
    if engine.ready:
        return {"status": "healthy", "model": "loaded"}
    return {"status": "degraded", "model": "unavailable"}


@app.post("/verify", response_model=VerifyResponse)
async def verify_face(body: VerifyRequest) -> VerifyResponse:
    if not engine.ready:
        raise HTTPException(status_code=503, detail="Face engine unavailable")

    enrolled = [float(value) for value in body.enrolled_embedding]

    scores: List[float] = []
    for frame in body.frames_base64:
        try:
            emb = engine.embedding_from_frame(frame)
            scores.append(cosine_similarity(emb, enrolled))
        except ValueError:
            continue

    if not scores:
        return VerifyResponse(verified=False, score=0.0, frame_count=0)

    avg_score = float(sum(scores) / len(scores))
    verified = avg_score >= body.threshold and len(scores) >= 3
    return VerifyResponse(verified=verified, score=avg_score, frame_count=len(scores))
