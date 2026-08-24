# Security Architecture

- Prefer OAuth workload identity or service principals.
- Keep connector permissions read-only.
- Do not store table rows.
- Treat SQL/query text as sensitive.
- Use external secrets and TLS in production.
- Fail closed for protected Tier-0 production workflows when appropriate.
