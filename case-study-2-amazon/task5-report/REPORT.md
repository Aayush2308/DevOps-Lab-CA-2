# Task 5: Reflection Report — Amazon Case Study
## DevOps Lab CA-II | Aayush Joshi | PRN: 23070122008 | SIT Pune

---

## Q2: Amazon — How Amazon Uses DevOps for Release Speed (5 Marks)

### Problem Statement

Amazon deploys to production every **11.7 seconds** on average (2014 re:Invent data —
the number is higher today). A centralized monolith cannot achieve this. Amazon's answer
was to restructure teams and technology simultaneously: "Two-Pizza Teams" own their
services end to end, including deployment. This organizational change enabled their
technical acceleration.

### DevOps Practices Implemented (with Evidence)

#### 1. Two-Pizza Team Architecture (Task 3 + Task 1)

Three completely independent services, each owned by a separate team:

| Team | Service | Port | Independent Deploy |
|---|---|---|---|
| Orders Team | `orders-service` | 8003 | Yes |
| Inventory Team | `inventory-service` | 8004 | Yes |
| Payments Team | `payments-service` | 8005 | Yes |

**Proof of independence**: The `amazon-ci.yml` pipeline uses `fail-fast: false`:
```yaml
strategy:
  matrix:
    service: [orders-service, inventory-service, payments-service]
  fail-fast: false  # payments failing does NOT block orders from deploying
```

If payments-service breaks, orders and inventory still deploy. This is the
Amazon two-pizza principle encoded directly in CI configuration.

#### 2. CI/CD Pipeline — Independent Per-Service Deploy (Task 1)

```
Push → flake8 all 3 → [Test orders] [Test inventory] [Test payments] (parallel)
     → [Build+Scan orders] [Build+Scan inventory] [Build+Scan payments] (parallel)
     → [Deploy orders] [Deploy inventory] [Deploy payments] (independent, fail-fast=false)
```

- **Matrix strategy**: 3 parallel test jobs, 3 parallel build jobs, 3 parallel deploys
- **Deploy frequency**: Each team can deploy multiple times per day without coordination
- **Evidence**: GitHub Actions matrix run at https://github.com/Aayush2308/DevOps-Lab-CA-2/actions

#### 3. Configuration Management — Ansible (Task 2)

The same `app-server` role is applied to multiple teams:

```yaml
# Amazon site.yml — same role, different variables (two-pizza teams using shared infra tooling)
- name: Configure orders team server
  roles:
    - role: app-server
      vars: { app_name: amazon-orders, app_port: 8003 }

- name: Configure inventory team server
  roles:
    - role: app-server
      vars: { app_name: amazon-inventory, app_port: 8004 }
```

This shows standardized infrastructure for independent teams — each team's server
is configured identically, but with team-specific parameters.

**Idempotency**: Run 1 → `changed=10`. Run 2 → `changed=0, ok=10`.

#### 4. Kubernetes — Independent Deployments (Task 3)

Each service has its OWN Kubernetes Deployment object:
- `orders-service-deployment.yaml`
- `inventory-service-deployment.yaml`
- `payments-service-deployment.yaml`

Rolling update for ONLY orders, without touching payments or inventory:
```bash
# Only orders team deploys a new version
kubectl set image deployment/orders-service \
  orders-service=ghcr.io/aayush2308/amazon-orders-service:v2 \
  -n amazon

kubectl rollout status deployment/orders-service -n amazon
# Inventory and payments are UNAFFECTED

# Rollback just orders:
kubectl rollout undo deployment/orders-service -n amazon
```

#### 5. Monitoring — Per-Team Observability (Task 4)

Prometheus scrapes each service independently:
```yaml
scrape_configs:
  - job_name: "orders-service"   targets: ["orders-service:8003"]
  - job_name: "inventory-service" targets: ["inventory-service:8004"]
  - job_name: "payments-service" targets: ["payments-service:8005"]
```

Grafana panels show deployment frequency per service — the DORA metric that
Amazon optimizes for. When orders-service deploys, only its error rate and
latency panels show a spike. The other two remain flat.

---

### Key Learning

Amazon's deployment velocity is not a technology achievement. It is an
**organizational achievement enabled by technology**. Conway's Law states that
systems reflect the communication structure of the organizations that build them.
Amazon reversed this — they changed the org structure (two-pizza teams) to force
their systems to become modular.

The technical artifacts in this repo (separate deployments, `fail-fast: false`,
matrix jobs, independent K8s manifests) are the *expression* of that organizational
decision in code.

> **"You build it, you run it." — Werner Vogels**
> Two-pizza teams own their service through development, deployment, and production.

---

### Metrics Demonstrated

| Metric | Value |
|---|---|
| Services deployed | 3 (orders, inventory, payments) |
| Unit tests | 19 (7+7+5) |
| CI pipeline stages | 4, fully matrix-parallelized |
| Teams blocked by single service failure | 0 (fail-fast=false) |
| Independent K8s deployments | 3 separate Deployment objects |
| Rolling update downtime | 0 seconds (maxUnavailable=0) |
| Ansible idempotency | Run 2: 0 changed, 10 ok |
