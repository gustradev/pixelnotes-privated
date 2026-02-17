# Production Runbook

## 1) Environment Source of Truth
- All runtime secrets/configs must come from `credential.env`.
- Never print sensitive values in logs.
- Rotate leaked or historical secrets before production launch.

## 2) Deploy Commands
### Development
```bash
./scripts/deploy.sh dev
```

### Staging
```bash
./scripts/deploy.sh staging
```

### Production
```bash
./scripts/deploy.sh prod
```

### Monitoring Stack
```bash
docker compose -f docker-compose.yml -f infra/docker-compose.monitoring.yml up -d
```

## 3) Validation Checklist
- `docker compose ps` -> all services healthy.
- Backend health reachable.
- Redis health reachable and TTL policy active.
- Websocket connect with valid JWT succeeds.
- Chat send/get works for authenticated users.
- Flush propagates realtime and clears all clients.
- Face service health + verify endpoint operational.
- CI checks pass (`pytest`, `flutter analyze`).

## 4) Rollback
```bash
./scripts/rollback.sh <image-tag>
```

## 5) Incident Response
1. Rotate JWT/WS/encryption secrets.
2. Rotate user hashes for `user_alpha` and `user_beta`.
3. Purge Redis runtime keys if compromise suspected.
4. Redeploy stack with rotated `credential.env`.
5. Re-validate end-to-end auth, chat, flush, and websocket.

## 6) Release Hygiene
- Tag release semver (`vMAJOR.MINOR.PATCH`).
- Require CI green before merge to main.
- Keep release notes and `progress.log` updated.
