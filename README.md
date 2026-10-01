# DevOps Lab CA-II — Aayush Joshi

[![Netflix CI](https://github.com/Aayush2308/DevOps-Lab-CA-2/actions/workflows/netflix-ci.yml/badge.svg)](https://github.com/Aayush2308/DevOps-Lab-CA-2/actions/workflows/netflix-ci.yml)
[![Amazon CI](https://github.com/Aayush2308/DevOps-Lab-CA-2/actions/workflows/amazon-ci.yml/badge.svg)](https://github.com/Aayush2308/DevOps-Lab-CA-2/actions/workflows/amazon-ci.yml)

## Student Details

| Field | Value |
|---|---|
| **Name** | Aayush Joshi |
| **PRN** | 23070122008 |
| **Batch** | 2023–2027 |
| **Branch** | CSE - A |
| **Institute** | Symbiosis Institute of Technology (SIT), Pune |
| **Assessment** | DevOps Lab — CA-II |

## Case Studies Attempted

| Question | Topic | Marks |
|---|---|---|
| Q1 | Netflix — Resilience via Microservices & Chaos Engineering | 5 |
| Q2 | Amazon — Release Speed via Two-Pizza Teams & Microservices | 5 |

## Repository Navigation

```
DevOps-Lab-CA-2/
├── case-study-1-netflix/     Q1: Netflix (resilience theme)
│   ├── app/                  FastAPI microservices (catalog + recommendation)
│   ├── task1-pipeline/       → .github/workflows/netflix-ci.yml
│   ├── task2-ansible/        Configuration management (Ansible roles)
│   ├── task3-k8s/            Kubernetes manifests + chaos script
│   ├── task4-monitoring/     Prometheus + Grafana (docker-compose)
│   ├── task5-report/         Slides (.pptx) + markdown report
│   └── evidence/             Real command outputs + screenshot guide
│
└── case-study-2-amazon/      Q2: Amazon (release speed theme)
    ├── app/                  FastAPI microservices (orders + inventory + payments)
    ├── task1-pipeline/       → .github/workflows/amazon-ci.yml
    ├── task2-ansible/        Configuration management (Ansible roles)
    ├── task3-k8s/            Kubernetes manifests + independent deploy demo
    ├── task4-monitoring/     Prometheus + Grafana (docker-compose)
    ├── task5-report/         Slides (.pptx) + markdown report
    └── evidence/             Real command outputs + screenshot guide
```

## Marks Mapping

| Task | Marks | Netflix folder | Amazon folder |
|---|---|---|---|
| Task 1: CI/CD Pipeline | 2 | `task1-pipeline/` + `.github/workflows/netflix-ci.yml` | `task1-pipeline/` + `.github/workflows/amazon-ci.yml` |
| Task 2: Config Management | 2 | `task2-ansible/` | `task2-ansible/` |
| Task 3: Containerization & Orchestration | 2 | `task3-k8s/` | `task3-k8s/` |
| Task 4: Monitoring & Logging | 2 | `task4-monitoring/` | `task4-monitoring/` |
| Task 5: Reflection & Report | 2 | `task5-report/` | `task5-report/` |

## Architecture Overview

```
                        ┌─────────────────────────────────────┐
                        │         GitHub Actions CI            │
                        │  lint → test → build → scan → push  │
                        └────────────────┬────────────────────┘
                                         │ ghcr.io images
              ┌──────────────────────────▼──────────────────────────┐
              │                    kind cluster                       │
              │  ┌─────────────┐          ┌──────────────────────┐   │
              │  │   Netflix    │          │       Amazon          │   │
              │  │  catalog-svc │          │  orders-svc           │   │
              │  │  recomm-svc  │          │  inventory-svc        │   │
              │  │  chaos-monkey│          │  payments-svc         │   │
              │  └──────┬──────┘          └──────────┬───────────┘   │
              └─────────┼───────────────────────────┼───────────────┘
                        │                           │
              ┌──────────▼───────────────────────────▼──────────┐
              │          Prometheus + Grafana (docker-compose)    │
              └──────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Clone
git clone https://github.com/Aayush2308/DevOps-Lab-CA-2.git
cd DevOps-Lab-CA-2

# Run Netflix services locally
cd case-study-1-netflix/app/catalog-service
pip install -r requirements.txt
uvicorn main:app --port 8001

# Run Amazon services locally
cd ../../case-study-2-amazon/app/orders-service
pip install -r requirements.txt
uvicorn main:app --port 8003
```

See each case-study README for full instructions.
