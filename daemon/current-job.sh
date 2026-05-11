#!/bin/bash
# JOB: Generar 3 nuevas latinas — Cubana + Mexicana + Caribeña
set -euo pipefail

PAT=$(cat /workspace/.zami_pat | tr -d '\n\r ')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"
REPO_DIR="/workspace/Zami-girls"

cd "$REPO_DIR"

# Sync with remote before running so we start from a clean state
git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" 2>/dev/null
git reset --hard refs/remotes/origin/"$BRANCH"

echo "=== Generando 3 nuevas latinas ==="
python3 test-nuevas-latinas.py

# The python script handles its own git push:
#   1. Fetches remote branch
#   2. Resets hard to remote
#   3. Copies test-output/ images to daemon/output/
#   4. git add daemon/output/
#   5. git commit -m "output: 3 nuevas latinas generadas"
#   6. git push

echo "=== Job completado ==="
