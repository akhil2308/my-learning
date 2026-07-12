# Authentication & Authorization

**Overview:** AuthN answers *"who are you?"*; AuthZ answers *"what are you allowed to do?"*. They are separate problems with separate failure modes — and confusing them (or implementing only the first) is the root of the most common API vulnerabilities.

---

## 1. Password Handling (the table stakes)

- **Never store plaintext or fast hashes** (MD5/SHA-256 are *designed* to be fast — exactly wrong for passwords). Use a slow, salted, memory-hard KDF:
  - **Argon2id** (current best), **bcrypt** (fine, battle-tested), **scrypt**
  - Python: `passlib` with `argon2` / `bcrypt` context
- **Salting is automatic** in these algorithms — its job is making rainbow tables useless and identical passwords hash differently.
- **Policy that actually helps:** length (12+) over complexity rules, check against breached-password lists (haveibeenpwned k-anonymity API), rate limit login attempts, no "security questions."
- **Timing-safe comparison** for any secret check (`secrets.compare_digest`) — string `==` leaks length/prefix info via timing.

---

## 2. Session-Based Auth (cookies)

The classic model: server stores session state, client holds an opaque session ID in a cookie.

```
Login → server creates session in Redis → Set-Cookie: session_id=<random>
Request → cookie sent automatically → server looks up session → identity
```

- **Cookie flags, all of them:** `HttpOnly` (JS can't read it — kills XSS token theft), `Secure` (HTTPS only), `SameSite=Lax` or `Strict` (CSRF mitigation), scoped `Path`/`Domain`.
- **Session ID:** long, random (`secrets.token_urlsafe(32)`), regenerated on login (prevents session fixation).
- **Pros:** instant revocation (delete from Redis), small cookie, mature model.
- **Cons:** server-side state (Redis lookup per request), CSRF applies (browser sends cookies automatically — see the attacks doc).

---

## 3. Token-Based Auth (JWT)

The server signs a self-contained token; any service holding the public key/secret can verify it **without a DB lookup**.

```
Header (alg) . Payload (claims: sub, exp, iat, aud, iss, roles) . Signature
```

### The rules that keep JWTs safe
1. **Short-lived access tokens** (5–15 min) + **refresh tokens** to get new ones. A stolen access token has a small window.
2. **Validate everything on every request:** signature, `exp`, `iss` (issuer), `aud` (audience — a token minted for service A must not work on service B).
3. **Pin the algorithm** server-side (`algorithms=["RS256"]`). Never trust the `alg` header — the classic `alg: none` and RS256→HS256 confusion attacks come from letting the token choose its own verification.
4. **HS256 vs RS256:** HS256 (shared secret) is fine for a monolith; RS256/EdDSA (private key signs, public key verifies) once multiple services verify tokens — verifiers can't mint tokens.
5. **JWTs are encoded, NOT encrypted.** Anyone can base64-decode the payload. No secrets or PII in claims.
6. **Revocation story:** JWTs are valid until expiry by design. Mitigations: short expiry (primary), a Redis denylist of revoked token IDs (`jti`) checked per request, or versioned tokens (bump `token_version` on the user row to invalidate all).
7. **Refresh token hygiene:** stored `HttpOnly` cookie or secure storage, **rotate on every use**, and detect reuse (a rotated-then-reused refresh token = theft → revoke the whole family).

### Sessions vs JWT — honest comparison
| | Sessions | JWT |
|---|---|---|
| Revocation | instant | hard (needs denylist) |
| Per-request cost | store lookup | signature verify (CPU only) |
| Multi-service | shared session store | verify anywhere ✓ |
| Payload | opaque | claims readable by client |

Rule of thumb: **monolith/first-party web app → sessions are underrated.** Multiple services / mobile clients / third-party API → JWT.

---

## 4. OAuth 2.0 & OpenID Connect (delegated auth)

OAuth2 is about **delegated authorization** ("let app X access my Google Drive"); **OIDC** is a layer on top for **authentication** ("log in with Google" — adds the `id_token`).

### The flow that matters: Authorization Code + PKCE
```
1. App redirects user → auth server (with code_challenge = hash of a random verifier)
2. User logs in & consents at the auth server (app NEVER sees the password)
3. Auth server redirects back with a one-time authorization code
4. App exchanges code + code_verifier → access token (+ id_token, refresh token)
```
- **PKCE** binds steps 1 and 4 so an intercepted code is useless. Originally for mobile apps; now recommended for *all* clients.
- **Deprecated flows you should recognize but never build:** Implicit (token in URL fragment — leaks), Resource Owner Password (app handles the password — defeats the point).
- **Roles vocabulary:** Resource Owner (user), Client (your app), Authorization Server (Google/Auth0/Keycloak), Resource Server (the API).
- **Scopes** limit what the token can do (`drive.readonly`) — request the minimum.
- Validate the `state` parameter (CSRF on the callback) and `nonce` in the id_token (replay).

**Practical advice:** don't build your own identity provider. Use Keycloak (self-hosted), Auth0/Cognito/Firebase Auth (managed), and integrate via OIDC.

---

## 5. Authorization Models (the part everyone under-builds)

Authentication without authorization checks = **BOLA/IDOR**, the #1 API vulnerability (OWASP API Top 10 #1): `GET /orders/12345` returning any order to any logged-in user.

**The iron rule: every request that touches a resource must verify the *authenticated principal* is allowed to touch *that specific resource*.** Object-level, not just endpoint-level.

```python
# WRONG — authenticated ≠ authorized
@app.get("/orders/{order_id}")
async def get_order(order_id: int, user=Depends(current_user)):
    return await db.get(Order, order_id)

# RIGHT — ownership check on the object
    order = await db.get(Order, order_id)
    if order is None or order.user_id != user.id:
        raise HTTPException(404)   # 404, not 403 — don't confirm existence
    return order
```

### Models, in increasing power
- **RBAC (roles):** user → role(s) → permissions. Covers most apps. Keep roles few; check **permissions** in code (`can_delete_invoice`), not role names — roles change, permissions are stable.
- **ABAC (attributes):** rules over attributes of user/resource/context ("managers can approve expenses < ₹50k in their own department"). Flexible; harder to audit.
- **ReBAC (relationships):** authorization from a relationship graph ("editors of the parent folder can edit this doc") — Google Zanzibar model; OpenFGA/SpiceDB are open-source implementations. The right tool once sharing/hierarchies appear.
- **Multi-tenancy:** tenant isolation is authorization's highest-stakes case. Every query filtered by `tenant_id` (enforced centrally — Postgres Row-Level Security is a strong belt-and-suspenders), tenant ID from the *token*, never from the request body.

### Service-to-service authN/Z
Internal calls need identity too: mTLS (SPIFFE/service mesh) or client-credentials OAuth tokens. "It's inside the VPC" is not an auth model — that's how lateral movement works after one box is popped.

---

## 6. Extras That Come Up

- **API keys:** fine for server-to-server with low ceremony — treat like passwords (hash at rest, prefix for identification `sk_live_...`, rotation support, per-key scopes/rate limits).
- **MFA/2FA:** TOTP (authenticator apps) as baseline; SMS is phishable but better than nothing; WebAuthn/passkeys are the gold standard (phishing-resistant).
- **Account flows are attack surface:** password reset (single-use, short-lived, token hashed in DB), email change (confirm both addresses), login notifications, enumeration-safe responses ("if that email exists, we sent a link").
- **Brute-force protection:** per-account and per-IP rate limits, exponential lockout, CAPTCHA at thresholds — and monitor for **credential stuffing** (many accounts, few attempts each — per-account limits won't catch it, per-IP + breach lists will).

---

## Checklist
- [ ] Argon2id/bcrypt for passwords, breached-password check
- [ ] Access tokens ≤ 15 min, refresh rotation with reuse detection
- [ ] JWT: pinned algorithm, aud/iss/exp validated, no PII in claims, revocation story
- [ ] Cookies: HttpOnly + Secure + SameSite
- [ ] Object-level authz check on EVERY resource access (the BOLA rule)
- [ ] Tenant ID from token, enforced in every query
- [ ] OAuth: Authorization Code + PKCE only; state + nonce validated
- [ ] Service-to-service auth exists (mTLS or client credentials)
- [ ] Rate limiting on login/reset endpoints; enumeration-safe messages

## Practice Rep (60 min, pass/fail) — Session 28 [INTERVIEW-CRITICAL]

1. (25 min) **Blind whiteboard: OAuth2 Authorization Code + PKCE** for a SPA + API — every arrow labeled (who redirects whom, where the code_verifier/code_challenge live, what the token endpoint checks), plus where the refresh token is stored and rotated. Photograph it, then diff against this doc's §4 — mark every missing/wrong arrow.
2. (20 min) **Spot-the-bug set** — write the vulnerability + fix for each in ≤2 sentences: (a) JWT validated with `algorithms=["HS256","none"]`; (b) access token in localStorage on an XSS-able page; (c) `GET /api/orders/{id}` checking only "is authenticated"; (d) refresh tokens that never rotate; (e) logout that only deletes the client cookie for a stateless JWT; (f) password reset tokens that don't expire on use.
3. (15 min) Record the 90-second answer to "sessions vs JWT — when each?" including the revocation trade and the hybrid (short JWT + refresh-token rotation with server-side state).

**Pass:** PKCE diagram has ≤2 diffs against the doc; 6/6 bugs named with correct fix class (b = BOLA/IDOR for (c) — object-level check); recording lands the revocation asymmetry.
**Fail:** PKCE drawn without the verifier/challenge pair doing anything, or (c) answered as "add auth middleware" without the ownership check.

## Practice Rep (60 min, pass/fail) — Session 28 [INTERVIEW-CRITICAL]

1. (20 min) **Whiteboard OAuth2 Authorization Code + PKCE blind**, arrows and all: client → /authorize (code_challenge) → user consent → redirect with code → /token (code_verifier) → tokens. Annotate what PKCE defends against (auth-code interception on public clients) and why the verifier can't be faked.
2. (25 min) **Spot-the-bug set** — for each snippet/scenario, name the vuln and the fix in one line:
   a. JWT verified with `algorithms=["HS256","none"]`.
   b. Access token TTL = 30 days, no revocation.
   c. Session ID in URL query string.
   d. `verify=False` / signature not checked, only decoded.
   e. Role claim trusted from a client-sent JWT the server didn't issue.
   f. Password reset token = `md5(email)`.
   g. Refresh token not rotated on use.
3. (15 min) Write the 4-sentence "sessions vs JWT — when each" answer, including the JWT revocation problem and the standard mitigation (short TTL + refresh + denylist).

**Pass:** PKCE flow drawn correctly with the interception threat named; ≥6/7 bugs correctly identified AND fixed; sessions-vs-JWT answer names the revocation gap.
**Fail:** the `alg:none` or unverified-signature bug missed (these are disqualifying in a real interview).
