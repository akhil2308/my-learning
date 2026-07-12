# Web & API Attacks and Defenses (OWASP-Oriented)

**Overview:** The attacks in this doc account for the overwhelming majority of real-world breaches. For each: how it works, what it looks like, and the defense. The mental model throughout: **all input is hostile until proven otherwise, and trust boundaries are where you must re-verify everything.**

---

## 1. Injection Attacks

### SQL Injection
User input concatenated into a query becomes part of the query.

```python
# VULNERABLE — input becomes SQL
query = f"SELECT * FROM users WHERE email = '{email}'"
# email = "' OR '1'='1' --"  → returns all users

# SAFE — parameterized: input can only ever be data
result = await session.execute(
    text("SELECT * FROM users WHERE email = :email"), {"email": email}
)
# ORMs (SQLAlchemy) parameterize by default — the danger returns the moment
# you build raw SQL strings, including f-string ORDER BY / table names.
```
- Column/table names can't be parameterized → validate against an **allowlist** (`if sort_col not in {"created_at", "name"}: raise`).
- Same family: **NoSQL injection** (Mongo operators like `{"$gt": ""}` in JSON input — enforce types with Pydantic), **command injection** (never `os.system(f"convert {filename}")` — use `subprocess.run([...], shell=False)` with list args), **LDAP/XPath injection**.

### Cross-Site Scripting (XSS)
Attacker's JavaScript executes in *another user's* browser because you rendered their input as HTML.
- **Stored** (payload saved in DB, hits everyone who views), **Reflected** (payload in URL, hits whoever clicks the link), **DOM-based** (client-side JS inserts input via `innerHTML`).
- **Impact:** session/token theft, actions as the victim, keylogging.
- **Defenses (layered):**
  1. **Output encoding** by context — modern template engines (Jinja2 autoescape) and frameworks (React) do this by default; the bugs live in `| safe`, `dangerouslySetInnerHTML`, `innerHTML`
  2. **Content-Security-Policy** header — even if injection lands, inline/foreign scripts won't run
  3. **HttpOnly cookies** — stolen DOM ≠ stolen session
  4. Sanitize rich-text HTML with an allowlist library (bleach/DOMPurify), never regex

### Server-Side Request Forgery (SSRF)
Your server fetches a user-supplied URL → attacker makes *your server* request internal targets: `http://169.254.169.254/` (cloud metadata → credentials!), `http://localhost:6379` (Redis), internal admin panels.
- **Defenses:** allowlist of permitted domains; resolve DNS and **reject private/link-local IP ranges** (and re-check after redirects — redirect-to-internal is the classic bypass); network-level egress rules; IMDSv2 on AWS.

### Insecure Deserialization
`pickle.loads(user_data)` = remote code execution, full stop. Never unpickle untrusted input; use JSON + schema validation. Same for `yaml.load` (use `safe_load`).

---

## 2. Cross-Site Request Forgery (CSRF)

Browsers attach cookies automatically — so `evil.com` can make the victim's browser POST to `yourbank.com/transfer`, and the request arrives *with the victim's valid session cookie*.

- **Only applies to cookie/session auth.** Header-borne tokens (`Authorization: Bearer ...`) aren't attached automatically → JWT-in-header APIs are inherently CSRF-immune (their trade: JS-readable storage → XSS-stealable — pick your poison consciously).
- **Defenses:**
  1. **SameSite=Lax/Strict cookies** — the modern first line; Lax blocks cross-site POSTs
  2. **CSRF tokens** — random per-session token embedded in forms/headers, verified server-side; attacker can't read it (same-origin policy)
  3. State-changing operations **never on GET**
  4. Verify `Origin`/`Referer` headers as backup

---

## 3. Broken Access Control (OWASP #1)

Covered deeply in `authn_authz.md` — the summary: **BOLA/IDOR** (change the ID in the URL, get someone else's data), missing function-level checks (regular user calls `/admin/...` directly because only the UI hid the button), privilege escalation via **mass assignment**:

```python
# VULNERABLE — client sends {"name": "x", "is_admin": true}
user_update = UserModel(**request_json)

# SAFE — explicit input schema containing ONLY client-settable fields
class UserUpdateIn(BaseModel):
    name: str | None = None
    bio: str | None = None
```
Separate input schemas from DB models. Server-controlled fields (`is_admin`, `role`, `balance`, `tenant_id`) never appear in input schemas.

---

## 4. Validation & the Trust Boundary

- **Validate at the boundary, by type and constraint** (Pydantic: types, `max_length`, ranges, enums, regex where truly needed). Reject, don't "clean up."
- **Allowlist > denylist** — enumerating evil always misses variants; defining valid doesn't.
- **Canonicalize before checking:** path traversal (`filename = "../../etc/passwd"`) — resolve the full path and verify it's still inside the allowed directory (`Path(base, name).resolve().is_relative_to(base)`).
- **File uploads:** validate magic bytes not just extension, cap size, randomize stored names, store outside the web root (S3), serve with `Content-Disposition` + correct Content-Type, scan if high-risk.
- **Redirects:** `?next=` parameters validated against an allowlist or relative-only — open redirects are phishing fuel.
- **ReDoS:** catastrophic-backtracking regexes on user input can pin a CPU (`(a+)+$`). Keep regexes simple; timeout or use RE2 for complex ones.

---

## 5. Rate Limiting & Abuse Prevention

Not just for load — it's a security control against brute force, credential stuffing, scraping, and enumeration.

- **Algorithms:** fixed window (simple, bursty at edges), **sliding window** (Redis sorted set — accurate), **token bucket** (allows controlled bursts — usually the right default).
- **Dimensions:** per-IP (crude, shared NATs), per-user/API-key (fair), per-endpoint (login gets 5/min, search gets 100/min).
- Return `429` with `Retry-After`; log and alert on sustained limiting (it's an attack signal).
- **Enumeration defense everywhere:** uniform responses and *uniform timing* for exists/doesn't-exist paths (login, password reset, signup email check).

---

## 6. Security Headers (cheap, do all of them)

```
Strict-Transport-Security: max-age=31536000; includeSubDomains   # force HTTPS
Content-Security-Policy: default-src 'self'                      # XSS blast-radius
X-Content-Type-Options: nosniff                                  # no MIME guessing
X-Frame-Options: DENY  (or CSP frame-ancestors)                  # clickjacking
Referrer-Policy: strict-origin-when-cross-origin
Cache-Control: no-store                                          # on sensitive responses
```

### CORS — commonly misunderstood
CORS *relaxes* the browser's same-origin policy; it protects **users**, not your server (curl ignores it entirely).
- Reflecting the request's `Origin` back while `credentials: true` = disabled CORS with extra steps. Maintain an explicit allowlist.
- `Access-Control-Allow-Origin: *` is fine for genuinely public, credential-less APIs — and only those.

---

## 7. Information Leakage

- **Errors:** generic message + `trace_id` to the client; stack trace, query, and internals to your logs only. Debug mode off in prod (FastAPI: no `debug=True`, custom exception handlers).
- **Don't confirm existence** of resources the caller can't access → `404`, not `403`.
- Strip `Server`/`X-Powered-By` headers; keep `/docs`, `/metrics`, `/debug` off the public internet (auth or network-gate them).
- **Verbose 500s from dependencies** (DB errors bubbling to responses) leak schema — catch at the boundary.

---

## 8. Dependency & Supply Chain Security

Most real compromises arrive through a dependency, not your code.
- **Scan continuously:** `pip-audit` / Dependabot / Renovate + Trivy (containers) in CI, not just at setup.
- **Lock files always** (`uv.lock`/`poetry.lock`) — reproducible builds, no surprise transitive bumps.
- **Typosquatting:** `python-dateutil` vs `python3-dateutil` — verify names, prefer well-known packages, consider an internal proxy (Artifactory) for prod builds.
- Pin base images by digest for critical services; rebuild regularly to pick up OS patches (an unrebuilt image ages like milk).

---

## Attack → Defense Quick Table

| Attack | One-line defense |
|---|---|
| SQL injection | Parameterized queries; allowlist for identifiers |
| XSS | Auto-escaping templates + CSP + HttpOnly |
| CSRF | SameSite cookies + CSRF tokens (cookie auth only) |
| BOLA/IDOR | Object-level ownership check, every access |
| Mass assignment | Explicit input schemas |
| SSRF | URL allowlist + block private IPs post-DNS |
| Path traversal | Resolve + verify path stays in base dir |
| Deserialization RCE | Never pickle/`yaml.load` untrusted input |
| Brute force / stuffing | Rate limits + lockouts + breach lists |
| Open redirect | Allowlist `next=` targets |
| Supply chain | Lock files + continuous scanning |

## Practice Rep (60 min, pass/fail) — Session 29 [INTERVIEW-CRITICAL]

**Fix five seeded vulns in one FastAPI file.** Create `vuln_app.py` containing these five endpoints, then fix each and prove the exploit dead:

1. Raw-SQL search: `f"SELECT * FROM users WHERE name LIKE '%{q}%'"` → exploit with `' OR '1'='1`, fix with parameterization, re-run exploit.
2. IDOR: `GET /invoices/{id}` with no ownership check → demonstrate cross-user read with two test users, fix with owner filter in the query itself.
3. Mass assignment: `User(**payload)` accepting `is_admin`
## Practice Rep (60 min, pass/fail) — Session 29 [INTERVIEW-CRITICAL]

**Fix five seeded vulns in a real FastAPI file.** Create `vuln_app.py` with these planted (or use any you've seen): (1) raw SQL f-string in a query; (2) mass-assignment (`User(**request_body)` letting `is_admin` through); (3) IDOR — `GET /orders/{id}` with no ownership check; (4) SSRF — a `fetch_url` endpoint taking arbitrary URLs; (5) missing rate limit on `/login` enabling credential stuffing.

For each: write the exploit (the curl that abuses it) as a comment, then the fix, then a one-line assertion-style test that fails on the vuln and passes on the fix.

**Pass:** all 5 exploits written as working curls, all 5 fixed, all 5 mini-tests present and passing against the fixed version; the IDOR fix is an ownership check (not just auth), the SSRF fix is an allowlist (not a blocklist).
**Fail:** any fix that's cosmetic (e.g., SSRF "fixed" by blocking `localhost` string — trivially bypassed), or mass-assignment "fixed" without an explicit field allowlist / response model.
