# Features Implementation Status

## Implemented Features

### 1. Secret Chat Authentication
- Secret entry password endpoint (`/api/auth/entry`).
- Username/password login endpoint (`/api/auth/login`).
- JWT verification endpoint (`/api/auth/verify`).

### 2. Ephemeral Encrypted Chat
- Send encrypted messages (`/api/chat/send`).
- Read messages (`/api/chat/messages`).
- Message TTL enforced in Redis (default 86400).

### 3. Remote Flush (Realtime)
- Flush endpoint (`/api/chat/flush`).
- Signed flush event broadcast over websocket.
- Replay protection key and cooldown control.

### 4. WebSocket Realtime Layer
- Notification and chat websocket routes.
- Heartbeat ping/pong model.
- Event signing support with HMAC.

### 5. Face Verification Integration
- Backend face orchestration endpoint (`/api/face/verify`).
- GPU microservice (`face-gpu-service`) with `/health` and `/verify`.

### 6. Frontend Unlock Layer
- Password fallback path.
- Biometric service integration for supported platforms.
- WebSocket client with reconnect and heartbeat.

## Partially Implemented / Next Hardening Steps
- Full client-side signature verification logic hardening in websocket service.
- Full stealth template rotation service finalization in UI notification layer.
- Expanded integration/e2e tests for multi-client flush + websocket behavior.
- Optional token refresh endpoint and rotation policy.

## Verification Commands
```bash
# backend tests
cd backend && PYTHONPATH=. /home/gustradev/www/pixelnotes/.venv/bin/python -m pytest ../tests/backend -q

# flutter static checks
cd ../frontend && flutter analyze
```
