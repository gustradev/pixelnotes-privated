# Pixel Notes Architecture

## High-Level Diagram
```text
[Flutter Web / Android / iOS]
        |
        | HTTPS + WSS (Cloudflare Tunnel)
        v
[Cloudflare Edge / Zero Trust]
        |
        | Private tunnel
        v
[FastAPI Backend] <---------> [Redis]
        |                        |
        | HTTP internal          | TTL chat/events/replay/session
        v                        v
[Face GPU Service]         [Pub/Sub + cache keys]
```

## Data Flow

### 1. Auth Flow
1. User masuk secret entry password (`/api/auth/entry`).
2. User login username/password (`/api/auth/login`).
3. Backend verifikasi bcrypt hash user env (`user_alpha`, `user_beta`).
4. Backend mengembalikan JWT + material encryption key.

### 2. Chat Flow
1. Pesan dienkripsi di client (AES-256-GCM).
2. Client kirim ciphertext ke `/api/chat/send`.
3. Backend simpan ciphertext ke Redis key `chat:room:global`.
4. Backend set/refresh TTL 86400 detik.
5. Backend publish event realtime ke websocket.

### 3. Remote Flush Flow
1. Client kirim `POST /api/chat/flush`.
2. Backend verifikasi JWT + cooldown + rate limit.
3. Backend delete key chat Redis.
4. Backend simpan event replay guard `chat:flush:event:{id}` TTL 60.
5. Backend broadcast signed flush event ke semua websocket client.

### 4. Stealth Notification Flow
1. Backend kirim event netral (tanpa sender/message plaintext).
2. Frontend validasi signature/checksum.
3. Frontend tampilkan template netral lokal (bukan isi chat).

### 5. Face Verification Flow
1. Client capture multi-frame challenge.
2. Backend forward ke face service `/verify`.
3. Face service hitung embedding + similarity.
4. Backend terima verdict verified/unverified.

## Trust Boundaries
- Boundary A: Public internet ↔ Cloudflare edge.
- Boundary B: Cloudflare ↔ backend ingress.
- Boundary C: Backend ↔ Redis internal network.
- Boundary D: Backend ↔ Face service internal network.
- Boundary E: Mobile/web runtime ↔ secure local storage + biometric OS.

## Redis Usage Map
- `chat:room:global`: list pesan terenkripsi, TTL 86400.
- `chat:flush:last_time`: cooldown flush.
- `chat:flush:event:{event_id}`: replay protection, TTL 60.
- `signal:last` dan `signal:last:{id}`: fallback polling cache.

## Encryption Layers
- TLS/WSS in transit via Cloudflare.
- AES-256-GCM message payload di client.
- HMAC-SHA256 pada event websocket.
- JWT signature untuk auth session.
