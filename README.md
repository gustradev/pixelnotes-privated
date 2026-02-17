# Pixel Notes

Pixel Notes adalah aplikasi notes dengan mode chat tersembunyi berbasis Flutter + FastAPI + Redis, didesain untuk arsitektur tunnel-only, data ephemeral, dan kontrol keamanan berlapis.

## Status Proyek
- Backend API aktif: auth, notes, chat, flush, websocket, face orchestration.
- Frontend aktif: notes UI, secret entry/login, secret chat, websocket client, biometric service.
- Face GPU service aktif: endpoint health + verify (multi-frame embedding).
- CI aktif: backend tests + flutter analyze.
- Dokumentasi aktif di folder `docs/` dan `documents/`.

## Struktur Repositori
- `frontend/` Flutter Web/Android/iOS client.
- `backend/` FastAPI backend + Redis integration.
- `face-gpu-service/` Python GPU face verification microservice.
- `infra/` Compose overlays + monitoring + tunnel template.
- `tests/` Test suite backend.
- `scripts/` Deploy, rollback, test runner, enrollment hash.
- `docs/` Dokumentasi arsitektur, keamanan, runbook, fase implementasi.
- `documents/` Dokumen perencanaan/detail implementasi.

## Quick Start
1. Lengkapi nilai rahasia di `credential.env`.
2. Jalankan environment:
   - Dev: `./scripts/deploy.sh dev`
   - Staging: `./scripts/deploy.sh staging`
   - Production: `./scripts/deploy.sh prod`
3. Jalankan quality checks:
   - `./scripts/run_tests.sh`

## Dokumen Utama
- `docs/ARCHITECTURE.md`
- `docs/SECURITY.md`
- `docs/PRODUCTION_RUNBOOK.md`
- `docs/IMPLEMENTATION_PHASES.md`
- `FEATURES_IMPLEMENTATION.md`
- `documents/IMPLEMENTATION_PLAN.md`
- `masterplan.txt`
- `progress.log`

## Catatan Keamanan Penting
`credential.env` pernah berisi kredensial sensitif. Lakukan rotasi total credential/token sebelum deployment publik atau produksi real.
