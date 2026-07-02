# Infrastructure Security, Cryptography & Secrets

**Overview:** Application-layer defenses sit on top of an infrastructure layer that has its own attack surface: the network, the containers, the cloud account, the keys. This doc covers the concepts below the code — enough crypto to make correct choices (not to implement primitives — **never implement crypto primitives**), plus the operational security of secrets, containers, and cloud.

---

## 1. Cryptography: The Practical Map

You need to *choose* correctly among four jobs. Each has one or two right answers in 2025+:

| Job | Use | Never |
|---|---|---|
| **Symmetric encryption** (same key both ways) | **AES-256-GCM** or ChaCha20-Poly1305 (both are AEAD: encrypt + integrity together) | AES-ECB (identical blocks → identical ciphertext — the "penguin picture" failure), CBC without a MAC, DES/3DES/RC4 |
| **Asymmetric** (public/private keypair) | RSA-2048+ (OAEP for encryption, PSS for signatures), or elliptic curves: **Ed25519** (signatures), X25519 (key exchange) — smaller, faster | RSA with PKCS#1v1.5 encryption, 1024-bit keys |
| **Hashing** (integrity/fingerprint) | **SHA-256** / SHA-3, BLAKE2/3 | MD5, SHA-1 (collisions are practical) |
| **Password hashing** (deliberately slow) | **Argon2id**, bcrypt, scrypt | Any fast hash, even salted SHA-256 |

Supporting concepts:
- **HMAC** = keyed hash → message authenticity (webhook signatures, JWT HS256). Verify with constant-time comparison.
- **Nonces/IVs must never repeat** under the same key (GCM nonce reuse = catastrophic). Random 96-bit nonces or counters — library defaults handle this; don't get creative.
- **Randomness:** `secrets` module, never `random`, for anything security-relevant (tokens, IDs, nonces).
- **Envelope encryption** (how clouds do encryption at scale): data encrypted with a per-object **data key**; the data key itself encrypted by a master key living in **KMS/HSM** that never leaves the service. You store the encrypted data key next to the data. Enables rotation and audit without re-encrypting everything.
- Python: use `cryptography` (or its `Fernet` recipe for simple symmetric needs). Composing primitives yourself is how vulnerabilities are born.

---

## 2. TLS — What's Actually Happening

TLS gives three things: **confidentiality** (encryption), **integrity** (tamper detection), **authentication** (certificates prove the server is who it claims).

- **Handshake in one breath (TLS 1.3):** client hello (+key share) → server hello, certificate, key share → both derive session keys via ECDHE → symmetric encryption (AES-GCM) for the actual data. Asymmetric crypto only bootstraps the symmetric session.
- **Certificates & the chain of trust:** server cert signed by intermediate CA, signed by root CA in the OS/browser trust store. Validation = signature chain + expiry + hostname match. This is what stops man-in-the-middle.
- **Forward secrecy** (ephemeral ECDHE keys): a future compromise of the server's private key cannot decrypt *recorded past traffic*. Standard in TLS 1.3.
- **Operational reality:** TLS 1.2 minimum (prefer 1.3), certs automated via Let's Encrypt/cert-manager (manual cert renewal is an outage waiting for a calendar), HSTS header, redirect 80→443.
- **mTLS:** *both* sides present certificates — the standard for service-to-service identity (service meshes like Istio/Linkerd automate cert issuance and rotation via SPIFFE identities).
- **Don't disable verification.** Every `verify=False` "temporary fix" is a permanent MITM hole. Fix the CA bundle instead.

---

## 3. Secrets Management

The lifecycle: **generate → store → distribute → use → rotate → revoke.** Most setups only think about "store."

- **Never in git.** Not in code, not in `docker-compose.yml`, not in `.env` committed "just for dev." A secret that touched git history is compromised — rotate it (history rewrites are cosmetics; assume it's scraped). Pre-commit scanners: gitleaks, trufflehog.
- **The hierarchy (climb as you grow):**
  1. `.env` files, gitignored — local dev only
  2. Platform env vars (K8s Secrets, ECS task secrets) — fine; note K8s Secrets are base64, *not* encrypted, unless you enable encryption-at-rest + RBAC-restrict access
  3. **Secrets manager** (Vault, AWS Secrets Manager, GCP Secret Manager) — encrypted, audited, access-controlled, rotatable; synced into K8s via external-secrets-operator
  4. **Dynamic secrets** (Vault's killer feature): short-lived DB credentials minted per-service on demand — a leaked credential expires in minutes
- **Rotation must be a non-event:** support two valid keys simultaneously (old + new) so rotation needs no downtime. If rotating a secret is scary, that's the finding.
- **Workload identity > static keys:** in cloud, prefer IAM roles bound to the workload (IRSA on EKS, workload identity on GKE) over long-lived access keys in env vars. The credential *is* the identity; nothing to leak.
- **Scrub secrets from logs, error reporters, and tracebacks** — Sentry/OTel scrubbing rules configured, not assumed.

---

## 4. Network Security Architecture

- **Segmentation:** public subnet holds only the load balancer/ingress; app and data tiers in private subnets with no inbound internet route. DB security group admits only the app security group — not `0.0.0.0/0`, not even "the VPC CIDR."
- **Egress control** is underrated: restrict what your services can call *out* to. It's the difference between "attacker got RCE" and "attacker got RCE and exfiltrated the DB to their server."
- **Zero trust mindset:** the perimeter is not the security boundary. Every service authenticates every caller (mTLS/tokens), every request is authorized — "inside the VPC" grants nothing. This is what limits blast radius after the inevitable first compromise (lateral movement is how one popped box becomes a total breach).
- **Bastion/SSM:** no SSH ports open to the internet; access via AWS SSM Session Manager or a bastion with MFA, all sessions logged.
- **DDoS layers:** CDN/edge absorption (CloudFront/Cloudflare), AWS Shield/WAF for L7 patterns, then your own rate limiting. You handle L7 abuse; the platform handles volumetric.
- **WAF:** managed rulesets (SQLi/XSS patterns) as a cheap outer filter — a supplement to, never a substitute for, correct code.

---

## 5. Container & Kubernetes Security

- **Image hygiene:** minimal base (slim/distroless), multi-stage builds (build tools don't ship), pin by digest for critical images, scan in CI (Trivy/Grype), rebuild regularly — patches only apply to *rebuilt* images.
- **Run as non-root** (`USER app` in Dockerfile) + `readOnlyRootFilesystem: true` + drop capabilities:
  ```yaml
  securityContext:
    runAsNonRoot: true
    allowPrivilegeEscalation: false
    capabilities: { drop: ["ALL"] }
  ```
- **No secrets in images or build args** — they persist in layers. Runtime injection only.
- **K8s specifics:** RBAC least-privilege for service accounts (and `automountServiceAccountToken: false` unless needed), NetworkPolicies (default-deny between namespaces, allow explicitly), Pod Security Standards (restricted profile), resource limits (a compromised pod shouldn't be able to starve the node).
- **Registry trust:** pull from your own registry; image signing (cosign) if supply chain matters to you.

---

## 6. Cloud Account Security (IAM)

- **Least privilege as a practice:** start from zero, add permissions as errors demand — not from `AdministratorAccess` minus vibes. Scope to specific resources/ARNs, not `Resource: "*"`.
- **Roles over users:** humans assume roles via SSO with MFA; workloads get roles via workload identity. Long-lived access keys are the thing that leaks.
- **Root account:** MFA'd, credentials locked away, never used for daily work, alerts on any use.
- **Audit everything:** CloudTrail on, logs shipped to a separate locked-down account (attackers delete logs first), alerts on IAM changes, new access keys, disabled logging.
- **The metadata service** (169.254.169.254) is why SSRF is a cloud-account-takeover primitive — enforce IMDSv2 (session-token required) on all EC2/EKS nodes.
- **Multi-account strategy:** prod/staging/dev in separate accounts — the blast radius boundary that actually holds.

---

## 7. Data Protection & Compliance Basics

- **Encryption at rest:** enable everywhere it's a checkbox (RDS, S3, EBS — KMS-backed). It protects against stolen disks/snapshots, *not* against a compromised app with DB credentials — app-layer (field-level) encryption for the crown jewels (govt IDs, tokens) covers that.
- **Data classification:** know which tables/fields hold PII/financial/regulated data — you can't protect what you haven't inventoried.
- **Minimization & retention:** don't collect what you don't need; delete on schedule; support erasure requests (GDPR / India's **DPDP Act**). "Keep everything forever" is a liability, not an asset.
- **Backups are data too:** encrypted, access-controlled, and included in erasure planning.

---

## 8. Detection & Response (assume breach)

- **You can't detect what you don't log:** authentication events, authorization failures, admin actions, IAM changes — retained, tamper-resistant, time-synced.
- **Alert on behavior, not just errors:** login from new geography, spike in 403s (someone probing BOLA), off-hours admin activity, egress volume anomalies.
- **Incident response plan before the incident:** who's on point, how to rotate all credentials fast (you scripted that, right?), how to preserve evidence, who communicates what. The middle of a breach is the worst time to design the process.
- **Practice:** tabletop exercises; try leaking a canary token and see if anything notices.

---

## Checklist
- [ ] AEAD ciphers only (AES-GCM/ChaCha20-Poly1305); `secrets` module for randomness; no hand-rolled crypto
- [ ] TLS 1.2+ everywhere, certs auto-renewed, HSTS; no `verify=False` anywhere in the codebase
- [ ] Secrets: gitleaks in pre-commit/CI, secrets manager (not raw env) for prod, rotation is a non-event, workload identity over static keys
- [ ] Network: private subnets for app+data, security groups reference groups not CIDRs, egress restricted, no public SSH
- [ ] Containers: non-root, read-only fs, dropped caps, scanned images, no secrets in layers
- [ ] K8s: RBAC least-privilege, NetworkPolicies default-deny, restricted PSS
- [ ] Cloud: MFA + SSO for humans, no long-lived keys, IMDSv2 enforced, CloudTrail to a separate account
- [ ] Data: encryption at rest on, PII inventoried, retention + DPDP/GDPR erasure supported
- [ ] Detection: auth/authz/admin events logged and alerted; IR plan written and rehearsed
