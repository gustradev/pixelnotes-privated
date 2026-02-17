# Security Documentation

## Implemented Controls
- Secrets loaded from `credential.env` for runtime deployment.
- JWT validation + expiration checks.
- HMAC-signed websocket events.
- Redis replay protection keys for flush events.
- Rate limiting on auth/chat/flush endpoints.
- Security headers in backend middleware.
- Redis TTL enforcement for ephemeral chat data.
- No plaintext chat content persisted by backend.

## Authentication & Access
- Secret entry password gate.
- Two static secret users from environment: `user_alpha`, `user_beta`.
- Password hash verification with bcrypt.
- JWT required for chat, flush, verify endpoints, and websocket connect.

## Realtime Security
- Websocket heartbeat ping/pong.
- Event signature verification model.
- Flush cooldown + replay TTL guard.
- Polling fallback for degraded websocket conditions.

## Mobile / Client Security
- Biometric service integration (platform-supported).
- Secure storage integration for secret session/token path.
- Password fallback mandatory when biometric unavailable/failed.

## Face Service Security
- Multi-frame verification request.
- In-memory frame processing (no image persistence).
- Threshold-based similarity decision.
- Dedicated internal service path via backend orchestration.

## Operational Security Checklist
- Rotate `JWT_SECRET`, `WS_EVENT_SECRET`, `ENCRYPTION_KEY` before go-live.
- Restrict `CORS_ORIGINS` to exact trusted domains.
- Enforce Cloudflare Zero Trust policy at edge.
- Use production compose hardening profile (`no-new-privileges`).
- Keep dependency and image versions pinned and updated.

## Residual Risks
- Compromised client device can still expose decrypted runtime state.
- Biometric trust is bounded by OS/device trust model.
- Face verification quality depends on camera/lighting and anti-spoof sophistication.
- Browser runtime cannot guarantee hardware-backed key storage on all platforms.
