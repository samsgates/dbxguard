# DBXGuard

**Pre-flight checks for Databricks. Know the blast radius before you deploy.**

DBXGuard is an open-source change-intelligence and deployment-safety platform for Databricks. It analyzes repository changes, maps them to a workspace dependency graph, calculates data, reliability, security, AI/ML and cost impact, evaluates policy-as-code, and returns an auditable `ALLOW`, `WARN`, `REQUIRE_APPROVAL`, or `BLOCK` decision.

## What is implemented

- FastAPI control plane with health, analysis and workspace endpoints.
- Typer CLI with demo, analyze, diff, policy test and API client commands.
- SQL parser based on sqlglot.
- Databricks Bundle YAML parser and Databricks Terraform parser.
- Deterministic change model and schema-safety rules.
- Dependency graph with downstream blast-radius traversal.
- Multi-dimensional risk scoring with confidence calculation.
- YAML policy-as-code engine.
- Databricks SDK connector with capability discovery and read-only inventory helpers.
- GitHub Action workflow example.
- Next.js operator console.
- Docker Compose, backend Dockerfile and Helm chart.
- Unit and API tests plus a no-account-required demo fixture.

## Architecture

```text
Git PR / local diff
        |
        v
 Change parsers ---- Databricks inventory
        |                   |
        +------> Change + workspace graph
                           |
                           v
                  Blast-radius engine
                           |
            +--------------+--------------+
            |              |              |
          Data          Security         Cost/AI
            +--------------+--------------+
                           |
                       Risk Engine
                           |
                      Policy Engine
                           |
             ALLOW / WARN / APPROVAL / BLOCK
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
dbxguard demo
uvicorn dbxguard_api.main:app --reload --port 8080
```

Run tests:

```bash
pytest -q
```

## Web console

```bash
cd apps/web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8080 npm run dev
```

## Docker

```bash
docker compose up --build
```

The API runs on `http://localhost:8080`, the web console on `http://localhost:3000`.

## Databricks authentication

DBXGuard uses `databricks-sdk` standard authentication. Prefer OAuth workload identity or a service principal in production.

```bash
export DATABRICKS_HOST="https://your-workspace"
export DATABRICKS_CLIENT_ID="..."
export DATABRICKS_CLIENT_SECRET="..."
dbxguard workspace-test
```

DBXGuard is read-only by default. It inventories resources and evidence. Production write/remediation automation is intentionally excluded from the default execution path.

## Policy as code

```yaml
apiVersion: dbxguard.io/v1
kind: Policy
metadata:
  name: block-destructive-production-schema-change
spec:
  match:
    environment: production
  rules:
    - condition:
        operation: DROP_COLUMN
      action: BLOCK
```

Validate policies:

```bash
dbxguard policy-test policies
```

## Production notes

For production, use PostgreSQL, TLS termination, OIDC/SAML at the ingress or enterprise auth adapter, a secrets manager, Kubernetes network policies and external Redis/workflow execution. The analysis path remains deterministic and evidence backed.

## License

Apache-2.0.
