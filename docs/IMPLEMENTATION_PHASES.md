# Implementation Phases

## Phase 1 — Core Backend + Redis + Minimal Frontend
- Objective: baseline app flow notes/chat online.
- Artifacts: API auth/chat/notes routes, Redis client, Flutter providers/pages.
- Security: base CORS + headers + endpoint rate limiting.
- Tests: backend core auth/token tests.
- Acceptance: basic notes/chat flow available.

## Phase 2 — Auth System (Password + Biometric + JWT)
- Objective: dual unlock with secure session model.
- Artifacts: password gate/login, biometric service, secure token handling path.
- Security: bcrypt hash validation, JWT expiry, failed-attempt lockout logic.
- Tests: JWT issue/verify + invalid token rejection.
- Acceptance: password and biometric fallback behavior valid.

## Phase 3 — GPU Face Microservice + Enrollment CLI
- Objective: face verification capability for high assurance unlock.
- Artifacts: `face-gpu-service`, `/api/face/verify` orchestration, enrollment hash script.
- Security: no image persistence, threshold policy, internal service path.
- Tests: face service health and verify contract tests.
- Acceptance: backend receives stable verified/unverified response.

## Phase 4 — Realtime WebSocket + Flush System
- Objective: low-latency event delivery and synchronized wipe.
- Artifacts: websocket manager/routes, flush endpoint, replay key storage.
- Security: JWT connect validation, signed events, cooldown and rate limit.
- Tests: websocket signature verification, flush replay/cooldown checks.
- Acceptance: realtime flush works cross-client.

## Phase 5 — Stealth Notification Engine
- Objective: hidden notification semantics without metadata leak.
- Artifacts: neutral event payload strategy and client-side template rendering flow.
- Security: no sender/content metadata in event payload.
- Tests: payload format and signature integrity checks.
- Acceptance: receiver gets neutral signal only.

## Phase 6 — Hardening + Anti-Abuse
- Objective: strengthen reliability and abuse resistance.
- Artifacts: security headers, stricter logging, no plaintext persistence.
- Security: replay guard, brute-force control, cooldown.
- Tests: negative-path and abuse tests.
- Acceptance: controlled failure behavior under attack attempts.

## Phase 7 — CI/CD + Automation Gates
- Objective: automated quality enforcement.
- Artifacts: GitHub Actions workflow, test/dev requirements.
- Security: ephemeral CI secrets and non-production test credentials.
- Tests: pytest + flutter analyze pipeline.
- Acceptance: merge gate requires CI green.

## Phase 8 — Monitoring + Telemetry
- Objective: observability and operational health.
- Artifacts: compose monitoring overlay, Prometheus/Grafana bootstrap config.
- Security: sanitized logs without secret exposure.
- Tests: monitoring services boot + scrape health.
- Acceptance: operational metrics and health visibility available.

## Phase 9 — Deployment Profiles + Tunnel
- Objective: environment-specific deployment discipline.
- Artifacts: dev/staging/prod compose overlays + cloudflare tunnel template.
- Security: tunnel-only ingress and production hardening profile.
- Tests: compose-up validation per profile.
- Acceptance: reproducible environment deployments.

## Phase 10 — Final Validation
- Objective: production readiness confirmation.
- Artifacts: runbook, architecture/security docs, progress log.
- Security: residual risk and secret rotation documented.
- Tests: full regression run + smoke validation.
- Acceptance: deployable, testable, and auditable release baseline.
