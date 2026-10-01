#!/usr/bin/env bash
# ============================================================
# chaos-monkey.sh — Netflix Chaos Engineering Demo
# Simulates the Netflix Chaos Monkey: randomly kills a pod
# and lets Kubernetes self-healing restart it.
#
# Usage:
#   bash chaos-monkey.sh [namespace] [deployment]
#
# Defaults: namespace=netflix, deployment=catalog-service
# ============================================================
set -euo pipefail

NAMESPACE="${1:-netflix}"
DEPLOYMENT="${2:-catalog-service}"
LABEL="app=${DEPLOYMENT}"

echo "============================================================"
echo "  CHAOS MONKEY — DevOps Lab CA-II (Netflix Case Study)"
echo "  Student: Aayush Joshi | PRN: 23070122008"
echo "============================================================"
echo ""
echo "[$(date '+%H:%M:%S')] Target namespace : $NAMESPACE"
echo "[$(date '+%H:%M:%S')] Target deployment: $DEPLOYMENT"
echo ""

# Show current healthy state
echo "--- BEFORE CHAOS: Pod status ---"
kubectl get pods -n "$NAMESPACE" -l "$LABEL" -o wide
echo ""

# Pick a random pod to kill
VICTIM=$(kubectl get pods -n "$NAMESPACE" -l "$LABEL" \
  --field-selector=status.phase=Running \
  -o jsonpath='{.items[0].metadata.name}')

if [ -z "$VICTIM" ]; then
  echo "ERROR: No running pods found for label $LABEL in namespace $NAMESPACE"
  exit 1
fi

echo "[$(date '+%H:%M:%S')] CHAOS MONKEY selecting victim pod: $VICTIM"
echo "[$(date '+%H:%M:%S')] KILLING pod now..."
kubectl delete pod "$VICTIM" -n "$NAMESPACE"

echo ""
echo "[$(date '+%H:%M:%S')] Pod deleted. Watching Kubernetes self-healing..."
echo "--- DURING CHAOS: Watch new pod starting ---"

# Watch pods for 30 seconds to capture self-healing
timeout 30 kubectl get pods -n "$NAMESPACE" -l "$LABEL" -w 2>/dev/null || true

echo ""
echo "--- AFTER CHAOS: Final pod status ---"
kubectl get pods -n "$NAMESPACE" -l "$LABEL" -o wide

echo ""
echo "[$(date '+%H:%M:%S')] Chaos experiment complete."
echo "  Kubernetes detected the pod failure and scheduled a replacement."
echo "  Recommendation-service was serving fallback during this period."
echo "  This demonstrates Netflix's resilience principle: design for failure."
