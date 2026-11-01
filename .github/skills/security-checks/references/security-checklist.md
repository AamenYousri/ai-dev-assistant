# Security Review Checklist

Use these criteria when applicable. Record evidence, status, and repeatable fix validation for each check. Mark a check NOT APPLICABLE only with a project-specific reason. Source review cannot verify cloud dashboards, identity-provider settings, DNS, production traffic, or recovery operations.

## Identity and Access

### C01. Authentication
- **What / why:** Protected endpoints and operations require authentication to prevent anonymous access.
- **Inspect / tools:** Trace route registration through middleware/controllers and test unauthenticated requests; Semgrep can flag framework patterns.
- **Evidence / verify:** Record endpoint-to-auth mapping and 401/403 tests; repeat tests after changes.

### C02. API Keys and Secrets
- **What / why:** Credentials must not be exposed in source, history, logs, builds, or client bundles.
- **Inspect / tools:** Gitleaks scans the working tree and, with `--history`, all Git refs; inspect generated JS/maps and configuration.
- **Evidence / verify:** Record only redacted path/rule/commit evidence; revoke and rotate exposed credentials, then rescan current files and history.

### C03. Database Security
- **What / why:** Least-privilege access, tenant/owner checks, and data isolation prevent unauthorized reads and writes.
- **Inspect / tools:** Review SQL grants, ORM/repository predicates, SAP CAP authorization annotations, transactions, and tenant boundaries; Dependency-Check covers known component CVEs, not permissions.
- **Evidence / verify:** Map data operations to authorization predicates and integration tests for cross-user/tenant denial.

### C04. HTTPS and Transport
- **What / why:** TLS protects credentials and data in transit.
- **Inspect / tools:** Search application, proxy, and deployment configuration for HTTP endpoints, insecure TLS settings, and mixed content; verify deployed ingress manually.
- **Evidence / verify:** Cite secure endpoint/config and TLS tests or external configuration evidence; ensure HTTP redirects or is disabled.

### C05. Password Security
- **What / why:** Locally managed passwords require strong salted password hashing and safe handling.
- **Inspect / tools:** Trace password creation, comparison, reset, logs, and storage; check whether an external IdP owns the flow.
- **Evidence / verify:** Identify the actual storage/auth owner; validate approved password-hash settings and ensure plaintext never persists or logs. If entirely delegated, document IdP controls as manual evidence.

### C06. Server-Side Validation and Mass Assignment
- **What / why:** Server-side type, range, schema, and ownership validation prevents invalid or unauthorized state changes.
- **Inspect / tools:** Review API schemas, DTO binding, CAP validation, Spring validation, Angular/Fiori trust boundaries, and writable fields.
- **Evidence / verify:** Record validators and negative tests for malformed, out-of-range, and privileged fields; client-side validation alone is insufficient.

### C07. XSS Protection
- **What / why:** Untrusted output must not execute as script in a user's browser.
- **Inspect / tools:** Trace data into Angular templates, Fiori controls, HTML rendering, URLs, and DOM APIs; Semgrep helps identify unsafe sinks.
- **Evidence / verify:** Cite encoding/sanitization and tests with hostile text; avoid unsafe bypass APIs unless input is reviewed and sanitized.

### C08. Logging and Monitoring
- **What / why:** Security events need useful audit evidence without leaking secrets or sensitive data.
- **Inspect / tools:** Review auth failures, privilege changes, validation failures, sensitive operations, log fields, retention, and alert routing.
- **Evidence / verify:** Cite event tests and redaction checks; verify production monitoring/retention manually.

### C09. Administrative Authorization
- **What / why:** Admin functions require server-enforced role/permission checks, not hidden UI controls.
- **Inspect / tools:** Trace each privileged endpoint/action to role checks and policy definitions; test direct API calls as ordinary users.
- **Evidence / verify:** Map operations to required roles and retain denied/allowed authorization tests.

### C10. SQL Injection
- **What / why:** Untrusted input must not alter query structure.
- **Inspect / tools:** Review query construction, native SQL, stored procedures, CAP query APIs, and ORM escape hatches; use Semgrep rules for relevant languages.
- **Evidence / verify:** Cite parameterized query paths and tests with metacharacters; validate behavior without running destructive payloads.

### C11. Environment Variables and Configuration Secrets
- **What / why:** Runtime secrets must stay server-side and out of source, client bundles, logs, and diagnostics.
- **Inspect / tools:** Review env loading, build-time Angular/Fiori config, CI variables, templates, and Gitleaks results.
- **Evidence / verify:** Cite secret-manager references and bundle checks; rotate exposed credentials and rescan history.

### C12. Rate Limiting and Abuse Controls
- **What / why:** Authentication, expensive operations, and public APIs need controls against brute force and resource abuse.
- **Inspect / tools:** Review gateway and application limits, per-account/IP keys, retry behavior, quotas, and CAP/Spring endpoint policies.
- **Evidence / verify:** Record configured limits and repeatable throttling tests; verify provider-side limits manually.

### C13. CORS
- **What / why:** Cross-origin access should be limited to required trusted origins and methods.
- **Inspect / tools:** Inspect Spring/CAP/gateway CORS configuration and environment overrides; test preflight and credentialed requests.
- **Evidence / verify:** List allowed origins/methods/headers and tests rejecting unapproved origins; wildcard plus credentials is not acceptable.

### C14. Browser Security Headers
- **What / why:** CSP, frame, MIME-sniffing, referrer, and other relevant headers reduce browser attack impact.
- **Inspect / tools:** Review app and reverse-proxy policy; inspect deployed responses manually.
- **Evidence / verify:** Cite header config and response tests; test CSP in report-only mode before enforcing where appropriate.

## Sessions and Application Security

### C15. Session Security
- **What / why:** Session identifiers and cookies need secure transport, HttpOnly/SameSite controls, expiry, rotation, and invalidation.
- **Inspect / tools:** Review framework/session/IdP settings and cookie creation; validate deployed cookies manually.
- **Evidence / verify:** Capture redacted cookie attributes and tests for expiry, logout, and privilege-change rotation.

### C16. CSRF Protection
- **What / why:** Browser-authenticated state changes must reject forged cross-site requests.
- **Inspect / tools:** Review Spring/CAP security middleware, SameSite strategy, tokens, and state-changing routes.
- **Evidence / verify:** Cite token/cookie design and negative cross-origin request tests; document when non-cookie bearer auth makes a route inapplicable.

### C17. Password Reset
- **What / why:** Reset flows must use unpredictable, single-use, short-lived tokens and avoid account enumeration.
- **Inspect / tools:** Trace token generation, storage, delivery, rate limits, redemption, and invalidation; mark N/A with evidence if an external IdP owns it.
- **Evidence / verify:** Cite expiry/replay/enum tests and safe token storage; verify IdP settings manually when delegated.

### C18. File Uploads
- **What / why:** Upload validation and storage controls prevent malware, path traversal, parser abuse, and public disclosure.
- **Inspect / tools:** Review file size/type/content checks, generated names, storage location, scanning, serving headers, and permissions.
- **Evidence / verify:** Cite bounded upload tests and storage ACL evidence; test rejected oversized/mismatched files and safe retrieval.

### C19. Payments
- **What / why:** Server-side pricing, signed provider callbacks, replay protection, and idempotency protect financial state.
- **Inspect / tools:** Trace checkout totals, provider APIs, webhook signature verification, retries, and order transitions; mark N/A if no payment flow exists.
- **Evidence / verify:** Cite server-calculated totals and signature/replay/idempotency tests; never use live payment actions for validation.

### C20. Production Configuration
- **What / why:** Debug modes, verbose errors, default credentials, and permissive settings expose internals.
- **Inspect / tools:** Review Spring profiles, CAP config, TypeScript build settings, containers, deployment manifests, and error handlers.
- **Evidence / verify:** Cite production profile assertions and safe error tests; inspect effective deployed configuration manually.

### C21. Vulnerable Dependencies
- **What / why:** Known-vulnerable libraries can expose reachable application paths.
- **Inspect / tools:** Run OWASP Dependency-Check for supported Maven/npm ecosystems and inspect lockfiles, SBOM, and platform alerts.
- **Evidence / verify:** Record package, version, CVE, severity, reachability/context, DB update state, and remediation; rerun after lockfile changes.

### C22. Unused Dependencies
- **What / why:** Unneeded packages increase attack surface and maintenance burden.
- **Inspect / tools:** Compare Maven/npm manifests and lockfiles to imports/build/runtime usage; use package-manager analysis rather than treating absence of imports as proof.
- **Evidence / verify:** Identify demonstrably unused packages and tests/builds after removal; do not remove transitives blindly.

### C23. Exposed Files and Source Maps
- **What / why:** Backups, configuration, database files, source maps, and repository metadata can reveal secrets or internals.
- **Inspect / tools:** Review static hosting/proxy routing and build artifacts; enumerate deployed public paths manually.
- **Evidence / verify:** Cite artifact inventory and access tests; ensure sensitive files are excluded or denied in the deployed environment.

### C24. Git History Secrets
- **What / why:** Removed credentials remain accessible in commits, branches, and tags.
- **Inspect / tools:** Run Gitleaks with `--history` to scan all refs; review Git refs and provider mirrors.
- **Evidence / verify:** Report only redacted commit/path/rule; rotate credentials first, then follow approved history-removal and mirror cleanup procedures and rescan.

### C25. Compromised Credentials and Rotation
- **What / why:** A detected credential must be treated as compromised, not merely deleted.
- **Inspect / tools:** Identify credential owner, scope, consumers, and audit trail without printing the value.
- **Evidence / verify:** Record revocation/rotation evidence and dependent-service validation; coordinate owner/provider action manually.

### C26. Full Application and Business-Logic Review
- **What / why:** Cross-component flows can bypass controls even when individual endpoints look safe.
- **Inspect / tools:** Trace trust boundaries, APIs, workflows, async jobs, integration events, tenant ownership, and business invariants.
- **Evidence / verify:** Document reviewed flows and abuse cases, with source references and targeted tests; state scope limitations.

### C27. Security Validation and Retest
- **What / why:** Repeatable tests prove fixes and detect regressions; a scanner run alone is not full validation.
- **Inspect / tools:** Re-run relevant scanners, unit/integration/security tests, and CI checks after approved fixes.
- **Evidence / verify:** Record exact commands, versions, exit status, reports, and resolved/unresolved findings; failed or skipped checks remain incomplete.

## Bonus Checks

### B1. AI Security
- **What / why:** Prompt injection, unsafe tool execution, cross-user context, secret leakage, abuse/cost, and untrusted model output can cross application trust boundaries.
- **Inspect / tools:** Trace prompts/retrieval, tool authorization, tenant scoping, output rendering, budgets, audit logs, and secret filters; test with benign adversarial fixtures.
- **Evidence / verify:** Cite isolation and allowlist controls plus tests for injection, tool denial, leakage, and quotas; do not send private prompts to external analyzers.

### B2. SSRF Protection
- **What / why:** User-controlled fetches can reach internal services or cloud metadata.
- **Inspect / tools:** Find URL fetchers, webhooks, importers, image proxies; inspect scheme/host/IP validation, DNS resolution, redirects, and egress policy.
- **Evidence / verify:** Cite allowlist/resolution controls and tests rejecting loopback/private/link-local/metadata addresses and redirect bypasses; do not probe live networks.

### B3. Backup and Recovery
- **What / why:** Protected, retained backups and tested restoration are needed for resilience and incident recovery.
- **Inspect / tools:** Review backup code/configuration and retention/encryption policy; verify provider dashboards and restore exercises manually.
- **Evidence / verify:** Record policy/config evidence and dated restore-test evidence; source-only inspection cannot establish recoverability.

### B4. Account Security
- **What / why:** MFA, least-privilege accounts, access reviews, integrations, and credentials reduce compromise impact.
- **Inspect / tools:** Inspect role/config declarations and integration secrets; verify IdP, cloud, Bitbucket, and SaaS account controls manually.
- **Evidence / verify:** Record account owner, MFA/access-review evidence, integration scopes, and credential rotation status without secret values.

### B5. Spending Limits and Abuse
- **What / why:** Usage limits and budgets reduce denial-of-wallet and runaway service costs.
- **Inspect / tools:** Identify metered APIs, AI calls, jobs, retries, and resource-heavy operations; inspect quotas and billing dashboards manually.
- **Evidence / verify:** Cite app throttles and test behavior plus provider budget/alert configuration; source cannot prove billing settings.

### B6. Privacy and Data Minimization
- **What / why:** Collect and retain only necessary personal/sensitive data and limit sharing/exposure.
- **Inspect / tools:** Map data fields, flows, logs, storage, analytics, retention, and third-party transfers; compare to stated purpose and policy.
- **Evidence / verify:** Record data inventory, minimization/retention controls, and deletion/access tests; verify contractual/legal decisions with owners.

### B7. Email Security
- **What / why:** SPF, DKIM, and DMARC help prevent spoofing; email content and links must not expose sensitive data or unsafe destinations.
- **Inspect / tools:** Review mail templates/link generation and delivery settings; inspect DNS and provider dashboards manually.
- **Evidence / verify:** Cite redacted template tests and observed DNS/provider records; source cannot prove DNS publication or alignment.
