# Task 1: CI/CD Pipeline — Amazon

The workflow file lives at the repo root (GitHub Actions requirement):

**File:** [`.github/workflows/amazon-ci.yml`](../../.github/workflows/amazon-ci.yml)

## Pipeline Stages

```mermaid
flowchart LR
    A[Push to main\namazon path] --> B[Lint\nflake8 all 3]
    B --> C{Matrix Test\n3 services}
    C --> D1[Test orders]
    C --> D2[Test inventory]
    C --> D3[Test payments]
    D1 & D2 & D3 --> E{Matrix Build+Scan}
    E --> E1[Build+Scan orders]
    E --> E2[Build+Scan inventory]
    E --> E3[Build+Scan payments]
    E1 & E2 & E3 --> F{Matrix Deploy\nIndependent}
    F --> G1[Deploy orders]
    F --> G2[Deploy inventory]
    F --> G3[Deploy payments]
```

## Key Design: Independent Deploys (Two-Pizza Principle)

The `test`, `build-and-scan`, and `deploy` jobs all use `matrix strategy` with `fail-fast: false`.

This means:
- If payments-service tests fail, orders and inventory **still deploy** independently.
- No team blocks another team's release.
- This directly maps to Amazon's documented two-pizza team principle.

## Evidence

- Screenshot of matrix job run (3 parallel): `evidence/screenshots/amazon-pipeline-matrix.png`
- Screenshot of independent deploy step: `evidence/screenshots/amazon-pipeline-deploy.png`
