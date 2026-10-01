#!/usr/bin/env pwsh
# k8s-demo.ps1 — Full Kubernetes Task 3 demonstration
# Run AFTER: images are loaded into kind cluster
# Demonstrates: apply, rolling update, rollback, chaos (netflix), independent deploy (amazon)

param(
    [string]$KindPath = "e:\DevOpsLab_CA2\kind.exe",
    [string]$KubectlCtx = "kind-devops-lab"
)

$env:PATH = "e:\DevOpsLab_CA2;$env:PATH"
$ctx = "--context=$KubectlCtx"

function Banner($msg) {
    Write-Host ""
    Write-Host "============================================================"
    Write-Host "  $msg"
    Write-Host "============================================================"
}

Banner "TASK 3: Kubernetes Orchestration Demo - DevOps Lab CA-II"
Write-Host "  Student: Aayush Joshi | PRN: 23070122008 | SIT Pune"

# -- Step 1: Apply namespaces --------------------------------------------------
Banner "Step 1: Create namespaces"
kubectl $ctx apply -f case-study-1-netflix/task3-k8s/namespace.yaml
kubectl $ctx apply -f case-study-2-amazon/task3-k8s/namespace.yaml
kubectl $ctx get namespaces

# -- Step 2: Apply Netflix manifests ------------------------------------------
Banner "Step 2: Deploy Netflix services (catalog + recommendation)"
kubectl $ctx apply -f case-study-1-netflix/task3-k8s/catalog-deployment.yaml
kubectl $ctx apply -f case-study-1-netflix/task3-k8s/recommendation-deployment.yaml
kubectl $ctx apply -f case-study-1-netflix/task3-k8s/services.yaml

Write-Host "Waiting for Netflix pods to be Running..."
kubectl $ctx rollout status deployment/catalog-service -n netflix --timeout=120s
kubectl $ctx rollout status deployment/recommendation-service -n netflix --timeout=120s
kubectl $ctx get pods -n netflix -o wide

# -- Step 3: Apply Amazon manifests -------------------------------------------
Banner "Step 3: Deploy Amazon services (orders + inventory + payments)"
kubectl $ctx apply -f case-study-2-amazon/task3-k8s/orders-service-deployment.yaml
kubectl $ctx apply -f case-study-2-amazon/task3-k8s/inventory-service-deployment.yaml
kubectl $ctx apply -f case-study-2-amazon/task3-k8s/payments-service-deployment.yaml
kubectl $ctx apply -f case-study-2-amazon/task3-k8s/services.yaml

kubectl $ctx rollout status deployment/orders-service -n amazon --timeout=120s
kubectl $ctx rollout status deployment/inventory-service -n amazon --timeout=120s
kubectl $ctx rollout status deployment/payments-service -n amazon --timeout=120s
kubectl $ctx get pods -n amazon -o wide

# -- Step 4: Rolling Update (Netflix catalog) ----------------------------------
Banner "Step 4: Rolling Update - catalog-service v1 -> v2 (zero downtime)"
kubectl $ctx set image deployment/catalog-service `
    catalog-service=netflix-catalog-service:local `
    -n netflix --record 2>&1

kubectl $ctx rollout status deployment/catalog-service -n netflix --timeout=120s
kubectl $ctx get pods -n netflix

# -- Step 5: Rollback ---------------------------------------------------------
Banner "Step 5: Rollback catalog-service (kubectl rollout undo)"
kubectl $ctx rollout undo deployment/catalog-service -n netflix
kubectl $ctx rollout status deployment/catalog-service -n netflix --timeout=60s
kubectl $ctx rollout history deployment/catalog-service -n netflix
kubectl $ctx get pods -n netflix

# -- Step 6: Chaos Monkey (Netflix) -------------------------------------------
Banner "Step 6: Chaos Monkey - kill a pod, watch K8s self-heal"
$victim = (kubectl $ctx get pods -n netflix -l app=catalog-service -o jsonpath="{.items[0].metadata.name}")
Write-Host "Killing pod: $victim"
kubectl $ctx delete pod $victim -n netflix

Write-Host "Watching self-healing (30s)..."
Start-Sleep 3
kubectl $ctx get pods -n netflix -l app=catalog-service
Start-Sleep 10
kubectl $ctx get pods -n netflix -l app=catalog-service
Start-Sleep 10
kubectl $ctx get pods -n netflix -l app=catalog-service

# -- Step 7: Amazon Independent Deploy Demo ------------------------------------
Banner "Step 7: Amazon Independent Deploy - ONLY orders-service gets new version"
kubectl $ctx set image deployment/orders-service `
    orders-service=amazon-orders-service:local `
    -n amazon --record 2>&1
kubectl $ctx rollout status deployment/orders-service -n amazon --timeout=60s

Write-Host "inventory-service and payments-service are UNCHANGED:"
kubectl $ctx rollout history deployment/inventory-service -n amazon
kubectl $ctx rollout history deployment/payments-service -n amazon
kubectl $ctx get pods -n amazon

Banner "ALL KUBERNETES DEMOS COMPLETE"
kubectl $ctx get pods -n netflix
kubectl $ctx get pods -n amazon
Write-Host "---k8s-demo-done---"
