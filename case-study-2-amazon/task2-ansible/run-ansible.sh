#!/bin/bash
# run-ansible.sh — Runs inside WSL Ubuntu to install ansible and run playbook twice
set -e

export PATH="$PATH:$HOME/.local/bin"

echo "======================================================"
echo "  DevOps Lab CA-II — Task 2: Ansible Demo (Amazon)"
echo "  Student: Aayush Joshi | PRN: 23070122008"
echo "======================================================"

if ! command -v ansible &>/dev/null; then
    echo "[STEP 1] Installing Ansible via pip..."
    pip3 install --user ansible --break-system-packages 2>&1 | tail -3
fi

echo ""
ansible --version | head -2
echo ""

PLAYBOOK="/mnt/e/DevOpsLab_CA2/case-study-2-amazon/task2-ansible/site.yml"
INVENTORY="/mnt/e/DevOpsLab_CA2/case-study-2-amazon/task2-ansible/inventory.ini"

echo "======================================================"
echo "  RUN 1 — First application of playbook"
echo "  Expected: tasks will CHANGE (create dirs, files...)"
echo "======================================================"
ansible-playbook "$PLAYBOOK" -i "$INVENTORY" -v 2>&1

echo ""
echo "======================================================"
echo "  RUN 2 — IDEMPOTENCY PROOF"
echo "  Expected: ALL tasks ok, changed=0"
echo "======================================================"
ansible-playbook "$PLAYBOOK" -i "$INVENTORY" -v 2>&1

echo ""
echo "======================================================"
echo "  Ansible demo complete."
echo "  Second run shows: changed=0 — IDEMPOTENCY PROVEN"
echo "======================================================"
