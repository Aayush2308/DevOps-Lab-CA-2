# Task 5: Reflection Report — Netflix Case Study
## DevOps Lab CA-II | Aayush Joshi | PRN: 23070122008 | SIT Pune

---

## Q1: Netflix — How Netflix Uses DevOps for Resilience (5 Marks)

### Problem Statement

Netflix streams to 270M+ subscribers across 190+ countries. A monolithic architecture
cannot survive at this scale — a single outage would cascade to every user. Netflix's
engineering approach directly addresses this with microservices, chaos engineering, and
a CI/CD culture where engineers deploy hundreds of times per day.

### DevOps Practices Implemented (with Evidence)

#### 1. Microservices Architecture (Task 3)

Netflix decomposes streaming into independent services. In this implementation:

| Service | Responsibility | Failure behaviour |
|---|---|---|
| `catalog-service` | Movie metadata | Stateless; killed by Chaos Monkey |
| `recommendation-service` | User recommendations | Circuit breaker + static fallback |

When `catalog-service` is unavailable, `recommendation-service` activates its
fallback and returns cached popular titles instead of a 500 error. This is the
Netflix Hystrix pattern recreated in Python.

#### 2. CI/CD Pipeline (Task 1)

The [`.github/workflows/netflix-ci.yml`](../../.github/workflows/netflix-ci.yml) pipeline implements:

```
Push → flake8 lint → pytest tests → Docker build → Trivy CVE scan → Push to GHCR → K8s dry-run deploy
```

- **Mean Time to Deploy**: ~4 minutes from push to image in registry
- **Gate**: No CRITICAL or HIGH CVEs with an available fix pass to production
- **Evidence**: GitHub Actions run at https://github.com/Aayush2308/DevOps-Lab-CA-2/actions

#### 3. Configuration Management — Ansible (Task 2)

Ansible role `app-server` demonstrates infrastructure-as-code:

- **Idempotency proven**: Run 1 → `changed=5`. Run 2 → `changed=0, ok=5`.
- **Template-driven config**: `app.conf.j2` generates environment-specific configs
- **Handler pattern**: The app only "restarts" when config actually changes

#### 4. Kubernetes Orchestration (Task 3)

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0  # zero-downtime rolling update
```

Rolling update command:
```bash
kubectl set image deployment/catalog-service \
  catalog-service=ghcr.io/aayush2308/netflix-catalog-service:v2 \
  -n netflix

kubectl rollout status deployment/catalog-service -n netflix
# Waiting for deployment "catalog-service" rollout to finish: 1 out of 2...
# deployment "catalog-service" successfully rolled out

# Rollback if needed:
kubectl rollout undo deployment/catalog-service -n netflix
```

#### 5. Chaos Engineering (Task 3)

The `chaos-monkey.sh` script simulates Netflix's Chaos Monkey:
1. Kills a random `catalog-service` pod
2. Kubernetes detects the failure via liveness probe failure
3. Schedules a replacement pod within ~15 seconds
4. `recommendation-service` returns fallback during this window
5. After recovery, normal recommendations resume

This demonstrates **design for failure** — Netflix's core engineering principle.

#### 6. Monitoring — Prometheus + Grafana (Task 4)

Metrics captured:
- `http_request_duration_seconds` — latency by endpoint
- `http_requests_total` — request rate by status code
- Grafana panels: Normal state → Chaos spike → Recovery

---

### Key Learning

Netflix's resilience is not achieved by making services more reliable in isolation.
It is achieved by making the **system** tolerate service failures gracefully. The
circuit breaker + fallback pattern means users get a slightly degraded experience
(popular titles instead of personalized ones) rather than an error page.

> **"Everything fails, all the time." — Werner Vogels, CTO Amazon**
> Netflix operationalizes this by building failure into their test strategy.

---

### Metrics Demonstrated

| Metric | Value |
|---|---|
| Services deployed | 2 (catalog, recommendation) |
| Unit tests | 11 (7 catalog + 4 recommendation) |
| CI pipeline stages | 4 (lint → test → build+scan → deploy) |
| Rolling update downtime | 0 seconds (maxUnavailable=0) |
| Chaos recovery time | ~15 seconds (K8s liveness probe cycle) |
| Ansible idempotency | Run 2: 0 changed, 5 ok |
