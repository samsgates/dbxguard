# DBXGuard Validation

Validation performed in the build environment on 2026-08-24.

## Passed

- Python source compilation: passed.
- Core/API test suite: 9 tests passed.
- Demo analysis: passed and produced a deterministic production BLOCK decision.
- SQL destructive-change parsing: passed.
- Bundle compute-change parsing: passed.
- Terraform compute parsing: passed.
- Blast-radius traversal: passed.
- Policy blocking: passed.
- Cost scaling engine: passed.
- Drift engine: passed.
- Security exposure scoring: passed.
- FastAPI health and SQL analysis endpoints: passed.

## Environment limitation

The execution environment used to assemble this archive did not have outbound PyPI/npm network access. Full dependency installation and the Next.js production build could therefore not be re-downloaded from public registries during packaging. The Python tests were run with compatible libraries already present in the environment. `pyproject.toml` and `apps/web/package.json` contain the project dependencies needed for a normal connected development/build environment.

## Recommended release gates

Before publishing a tagged production release, run the included GitHub Actions CI in a connected environment, build both Docker images, run an integration suite against dedicated Databricks AWS/Azure/GCP test workspaces, scan containers/SBOMs, and sign release artifacts.
