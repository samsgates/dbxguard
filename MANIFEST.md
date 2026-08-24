# Source Manifest

The archive includes:

- `apps/api`: FastAPI control plane and persistence.
- `apps/cli`: DBXGuard command-line application.
- `apps/web`: Next.js operator console.
- `packages/core`: graph, analyzer, risk, cost, drift, security, inventory, configuration and reports.
- `packages/parsers`: SQL, Databricks Bundle and Terraform change parsing.
- `packages/connectors`: read-only Databricks SDK adapter and system-table queries.
- `packages/policy`: deterministic YAML policy engine.
- `integrations`: GitHub check/comment and ServiceNow client primitives.
- `policies`: production and FinOps policy examples.
- `examples/demo`: runnable blast-radius demo.
- `tests`: core, parser, enterprise engine and API tests.
- `.github/workflows`: CI and DBXGuard pull-request workflows.
- `deploy/helm`: Kubernetes/Helm deployment chart.
- `Dockerfile` and `docker-compose.yml`: containerized deployment.
- `docs`: architecture and security guidance.
