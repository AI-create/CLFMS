# CLFMS Quick Security Audit Report

Date: 2026-04-29
Scope: Quick application and deployment review (code + runtime configuration)
Auditor: GitHub Copilot (GPT-5.3-Codex)

## Executive Summary

This quick audit found no immediate evidence of active compromise, but several security hardening gaps remain. The most important issues are missing rate-limiting on auth/OTP endpoints, production startup seeding of a default admin account, and weak/overly permissive response security policy settings.

Overall risk posture: Medium to High (due to auth abuse potential and configuration hardening gaps).

## Method

- Reviewed backend auth/security code and middleware.
- Reviewed deployment configuration and runtime environment behavior.
- Validated SMTP delivery path and recent operational issues during troubleshooting.

## Findings

### 1) Missing rate limiting on auth and OTP endpoints

Severity: High

Evidence:

- Public endpoints in [app/modules/auth/routes.py](app/modules/auth/routes.py):
  - POST /auth/login
  - POST /auth/signup
  - POST /auth/verify-otp
  - POST /auth/resend-otp
- No request throttling middleware or per-identifier/IP limits observed.

Risk:

- Brute force against passwords/OTP.
- OTP spam and abuse.
- Account lockout/resource exhaustion risk.

Recommendation:

- Add per-IP and per-email limits with sliding windows.
- Add exponential backoff for repeated failed OTP attempts.
- Introduce account lockout thresholds and audit logging for abuse.

---

### 2) Default admin seeding runs in production startup

Severity: High

Evidence:

- [app/main.py](app/main.py): `ensure_default_admin(db)` called in lifespan startup.
- [app/modules/auth/services.py](app/modules/auth/services.py): `ensure_default_admin` creates admin if missing using env credentials.

Risk:

- If admin user is deleted/missing, an admin account is recreated automatically.
- Security depends heavily on env credential quality.

Recommendation:

- Disable default admin seeding in production.
- Gate seeding behind explicit `SEED_DEFAULT_ADMIN=false/true` env flag (default false in prod).
- Use one-time migration/bootstrap command for initial admin setup.

---

### 3) OTP stored in plaintext in database

Severity: Medium

Evidence:

- [app/modules/auth/services.py](app/modules/auth/services.py): stores `otp_code` directly on user record.

Risk:

- DB read access exposes active OTP values.

Recommendation:

- Store only hashed OTP (HMAC/SHA-256 with server-side secret + salt/nonce).
- Compare hash on verification.
- Keep short expiry and one-time invalidation (already present).

---

### 4) Response security headers can be tightened

Severity: Medium

Evidence:

- [app/middleware/security_headers.py](app/middleware/security_headers.py):
  - CSP includes `'unsafe-inline'` for scripts and styles.
  - No `Strict-Transport-Security` (HSTS) header.

Risk:

- Expanded XSS surface due to inline allowances.
- Missing HSTS weakens HTTPS enforcement at browser level.

Recommendation:

- Remove `'unsafe-inline'` where feasible.
- Add nonce/hash-based CSP for inline assets if needed.
- Add HSTS header in Nginx (`max-age>=31536000; includeSubDomains; preload` once ready).

---

### 5) CORS includes localhost origins regardless of environment

Severity: Medium

Evidence:

- [app/main.py](app/main.py): default origins include localhost/127.0.0.1 values when `cors_origins` not set.

Risk:

- Broader-than-needed trust policy in production if env var omitted.

Recommendation:

- Require explicit `CORS_ORIGINS` in production.
- Fail startup in production if CORS origins are not explicitly configured.

---

### 6) Container runtime hardening gaps

Severity: Medium

Evidence:

- [Dockerfile](Dockerfile): no non-root `USER` declared.
- [docker-compose.prod.yml](docker-compose.prod.yml): no read-only root filesystem, capability drops, or `no-new-privileges`.

Risk:

- Greater blast radius if app is compromised.

Recommendation:

- Run app as non-root user.
- Add runtime hardening options:
  - `read_only: true` (with writable mounts where necessary)
  - `cap_drop: ["ALL"]`
  - `security_opt: ["no-new-privileges:true"]`

---

### 7) JWT session lifetime may be long for high-risk roles

Severity: Low/Medium

Evidence:

- [app/core/config.py](app/core/config.py): `jwt_expire_minutes` default `480` (8 hours).

Risk:

- Longer token validity increases impact of token theft.

Recommendation:

- Reduce default access token TTL (e.g., 15-60 minutes).
- Add refresh-token rotation and revocation strategy.

---

### 8) Operational logging growth previously caused 100% disk usage

Severity: Medium (Availability)

Evidence:

- Prior runtime state: oversized Docker JSON logs consumed disk and impacted service behavior.

Risk:

- Service degradation/healthcheck failure and partial content delivery.

Recommendation:

- Enable Docker log rotation (`max-size`, `max-file`) globally or per service.
- Add disk monitoring and alerts.

## Positive Controls Observed

- Password hashing uses bcrypt and verification path is in place.
- JWT contains `iat` and `exp` claims.
- OTP expiry enforced (10 minutes).
- OTP verification required for login (`is_verified` gate).
- Security headers middleware exists.
- Secrets minimum strength check for `SECRET_KEY` in non-debug mode.

## Priority Action Plan (Recommended)

1. Implement rate limiting + OTP/login abuse protection (High).
2. Disable default admin seeding in production (High).
3. Tighten CSP and add HSTS at Nginx layer (Medium).
4. Hash OTP at rest (Medium).
5. Enforce explicit production CORS config (Medium).
6. Add container/runtime hardening (Medium).
7. Implement log rotation and disk alerts (Medium).

## Notes

- This is a quick audit, not a full penetration test.
- No SAST/DAST/dependency scanner execution was included in this pass.
