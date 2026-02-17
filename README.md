# Pixel Notes – Secret Chat Mode

## 🚀 Overview
Pixel Notes is a stealth, ephemeral notes and chat application with a hidden, production-grade secret chat mode. Designed for maximum privacy, security, and plausible deniability, it features:
- **Ephemeral messaging** (auto-delete, TTL)
- **Stealth notification system** (no chat indicators)
- **Dual unlock (password + biometric)**
- **Remote flush chat** (secure, real-time wipe)
- **No public IP, no open ports**
- **Client-side encryption (AES-256-GCM)**
- **JWT authentication**
- **Zero plaintext storage**

---

## 🏛️ Architecture Diagram (Text)

```
[Flutter Web/Android] <---wss/http---> [FastAPI Backend] <---redis---> [Redis]
      |  |                                 |  |
      |  |<-- Stealth Notification (wss) --|  |
      |  |                                 |  |
      |  |<-- Remote Flush Event (wss) ----|  |
      |  |                                 |  |
      |  |<-- JWT Auth, Encrypted Payload--|  |
      |  |                                 |  |
      |  |<-- Biometric Unlock (Android) --|  |
      |  |                                 |  |
      |  |<-- Secure Storage (AES) --------|  |
```

---

## 📦 Backend Implementation Structure

```
backend/
  app/
    main.py                # FastAPI app, CORS, security headers
    routes/
      auth.py              # Entry, login, JWT, biometric
      chat.py              # Chat, flush, WebSocket
      notes.py             # Decoy notes
    redis_client.py        # Redis ops, TTL, pub/sub
    encryption.py          # AES-256-GCM, HMAC
    config.py              # Env, settings
    models.py              # Pydantic models
```

---

## 📱 Flutter Implementation Structure

```
frontend/lib/
  services/
    websocket_service.dart   # Realtime, wss, reconnect, heartbeat
    notification_service.dart# Stealth notification logic
    encryption_service.dart  # AES-256-GCM
    biometric_service.dart   # Android biometric
    secure_storage_service.dart # flutter_secure_storage + AES
    flush_service.dart       # Remote flush logic
    auth_service.dart        # JWT, unlock
  controllers/
    unlock_controller.dart   # Dual unlock flow
    chat_controller.dart     # Chat, flush, badge
  pages/
    secret_unlock_page.dart  # Unlock UI
    secret_chat_page.dart    # Chat UI, flush button
  models/
    unlock_state.dart        # Unlock state model
```

---

## 🗄️ Redis Config
- `appendonly no`
- `maxmemory-policy allkeys-lru`
- `TTL per key: 86400s`
- `chat:room:global` (list, TTL)
- `chat:flush:event:{event_id}` (replay protection, TTL 60s)

---

## 🔌 WebSocket Handler Example (Backend)
```python
@app.websocket("/ws/notify")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params["token"]
    user = validate_jwt(token)
    await websocket.accept()
    while True:
        event = await redis_subscribe()
        if event:
            # event = {type, event_id, nonce, checksum, signature}
            await websocket.send_json(event)
```

---

## 🔒 Encryption Implementation Example
- **Client:** AES-256-GCM, key from entry password + salt
- **Backend:** Never sees plaintext, only relays encrypted payload
- **Notification:**
  - Backend publishes `{type, event_id, nonce, checksum, signature}`
  - Signature: HMAC-SHA256(secret, event_id + nonce)
  - Client verifies signature, decrypts signal

---

## 📰 Template System Example (Flutter)
```dart
const newsTemplates = [
  NewsTemplate(
    title: "Market Update: Regional Index Shows Stability",
    body: "Daily performance remains within expected range."
  ),
  NewsTemplate(
    title: "Tech Update: System Maintenance Complete",
    body: "All services are operating normally."
  ),
  // ...more templates
];
// On notification: pick random template, show as notification
```

---

## 🛠️ Phase Breakdown & Checklist

### PHASE 1 – Realtime Infrastructure
- [x] WebSocket endpoint (wss)
- [x] Redis Pub/Sub
- [x] Client listener
- [x] Heartbeat

### PHASE 2 – Encrypted Signal Layer
- [x] AES-256-GCM
- [x] HMAC signature
- [x] Client verification
- [x] Secure key derivation

### PHASE 3 – Stealth Template Engine
- [x] Local template bank
- [x] Randomizer
- [x] Notification logic

### PHASE 4 – Hardening
- [x] Obfuscate client
- [x] Prevent debug leak
- [x] Rate limiting
- [x] Reconnect/idle lock

---

## 🛡️ Attack Vector Analysis
- **Replay Attack:** HMAC signature, event_id replay protection
- **WebSocket Injection:** JWT validated, signature checked
- **Token Theft:** JWT short-lived, never stored plaintext
- **Unauthorized Flush:** Only .env users, HMAC, confirmation
- **Race Condition:** Redis atomic ops, event replay check
- **Partial Wipe:** UI/Redis always in sync, event-driven

---

## ⚡ Performance Considerations
- WebSocket: <1s latency, auto-reconnect, heartbeat
- Redis: Pub/Sub, TTL, LRU
- Notification: Constant payload size, random jitter
- Flush: Real-time, atomic, no recovery

---

## 📢 Stealth Notification System
- No sender/message in notification
- Random news template (local only)
- Badge counter subtle, no chat indicator
- All signals encrypted, signed, and verified

---

## 🔐 Dual Unlock System (Password + Biometric)
- First login: password only
- Optionally enable fingerprint (Android)
- JWT encrypted with AES, stored in flutter_secure_storage
- Biometric unlock only decrypts token
- Expiry enforced, retry/lockout logic
- Device binding: SHA256(device_id + salt)

---

## 🧹 Remote Flush Chat
- Button in chat UI (subtle, confirm)
- Calls `/chat/flush` (JWT, HMAC, replay protection)
- Backend deletes Redis, broadcasts event
- Clients clear local cache, show neutral reset message

---

## 📝 License
MIT License

---

## 👤 Author
[GustraDev](https://github.com/gustradev)

---

## 🌐 Live Demo / Docs
*Private, self-hosted only. No public demo.*

---

## 🛠️ How to Run
1. Copy `.env.example` to `.env` and fill secrets
2. `docker compose up -d`
3. Access frontend via Cloudflare Tunnel
4. Use secret symbol to unlock chat mode

---

## 📣 Contact
For security review or collaboration, contact via GitHub.
