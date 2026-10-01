# Task 1: CI/CD Pipeline — Netflix

The workflow file lives at the repo root (GitHub Actions requirement):

**File:** [`.github/workflows/netflix-ci.yml`](../../.github/workflows/netflix-ci.yml)

## Pipeline Stages

```mermaid
flowchart LR
    A[Push to main\nnetflix path] --> B[Lint\nflake8]
    B --> C[Unit Tests\npytest]
    C --> D[Build Docker\nImages]
    D --> E[Trivy Scan\nCRITICAL+HIGH]
    E --> F[Push to\nghcr.io]
    F --> G[Deploy\ndry-run kubectl]
```

## What Each Stage Does

| Stage | Tool | Fail condition |
|---|---|---|
| Lint | flake8 (max 120 chars) | Any PEP8 violation |
| Test | pytest | Any test failure |
| Build | docker buildx | Build error |
| Scan | Trivy | Any CRITICAL or HIGH CVE (unfixed) |
| Push | ghcr.io | Auth failure |
| Deploy | kubectl dry-run | Invalid manifest syntax |

## Evidence

- Screenshot of green pipeline run: `evidence/screenshots/netflix-pipeline-green.png`
- Screenshot of Trivy scan output: `evidence/screenshots/netflix-trivy-scan.png`

> **To trigger:** Push any change to `case-study-1-netflix/` on main branch.
> Go to: https://github.com/Aayush2308/DevOps-Lab-CA-2/actions
