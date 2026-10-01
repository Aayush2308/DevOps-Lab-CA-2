# Evidence — Amazon Case Study

Real command outputs from Tasks 1-5. Nothing fabricated.

## Screenshot Checklist

| Filename | What to capture | When |
|---|---|---|
| `screenshots/amazon-pipeline-matrix.png` | GitHub Actions matrix jobs (3 parallel test jobs) | After first push triggers CI |
| `screenshots/amazon-pipeline-deploy.png` | Deploy stage — 3 independent deploy jobs running | Same run |
| `screenshots/amazon-k8s-pods.png` | `kubectl get pods -n amazon` showing all 3 services Running | After `kubectl apply` |
| `screenshots/amazon-rollout.png` | `kubectl rollout status` for orders-service | After rolling update |
| `screenshots/amazon-rollback.png` | `kubectl rollout undo` + pod status | After rollback |
| `screenshots/amazon-independent-deploy.png` | Only orders-service deployment changing, others unchanged | Independent deploy demo |
| `screenshots/amazon-grafana-services.png` | Grafana dashboard — all 3 services healthy | After monitoring setup |
| `screenshots/amazon-grafana-deploy-freq.png` | Deployment frequency panel | While pipeline is running |
| `screenshots/amazon-ansible-run1.png` | First Ansible run output | Batch 4 |
| `screenshots/amazon-ansible-run2.png` | Second run (0 changed — idempotency) | Batch 4 |

## Command Output Files

- `ansible-run-1.txt` — first Ansible run
- `ansible-run-2.txt` — second run (idempotency)
- `kubectl-rollout.txt` — rolling update + rollback
