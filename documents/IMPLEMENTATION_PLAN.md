# Implementation Plan (Consolidated)

## Objective
Menyediakan baseline production-ready untuk Pixel Notes dengan fokus keamanan, realtime reliability, dan deployability.

## Workstream
1. Backend API hardening (auth/chat/flush/websocket/face orchestration).
2. Frontend unlock + websocket client stability.
3. GPU face service integration.
4. Deployment profile + monitoring + CI.
5. Documentation and runbook completion.

## Deliverables
- Auth + chat + flush + websocket API tersedia.
- Redis TTL + replay protection aktif.
- Face verify microservice terintegrasi.
- CI pipeline aktif (`pytest` + `flutter analyze`).
- Dokumen architecture/security/runbook/fases lengkap.
- `progress.log` tersedia untuk audit progres.

## Definition of Done
- Build + test command berjalan konsisten.
- Dokumentasi mencerminkan state kode aktual.
- Secrets tidak hardcoded dan diambil dari `credential.env`.
- Deployment dev/staging/prod dapat direproduksi via script.
