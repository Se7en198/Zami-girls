#!/bin/bash
# JOB: Generar 3 nuevas latinas — Cubana + Mexicana + Caribeña
# Triggered: 2026-05-11
set -euo pipefail

PAT=$(cat /workspace/.zami_pat | tr -d '\n\r ')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"
REPO_DIR="/workspace/Zami-girls"

cd "$REPO_DIR"

git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" 2>/dev/null
git reset --hard refs/remotes/origin/"$BRANCH"

echo "=== Generando 3 nuevas latinas ==="
mkdir -p daemon/output test-output
python3 test-nuevas-latinas.py

cp test-output/*.png daemon/output/ 2>/dev/null || true
git add daemon/output/
git commit -m "output: 3 latinas Cubana+Mexicana+Caribena $(date +%Y%m%d-%H%M)" 2>/dev/null || true
git push "$REMOTE" HEAD:"$BRANCH" && echo "=== OK imagenes pusheadas ===" || echo "=== WARN: push falló, intentando de nuevo ===" && git push "$REMOTE" HEAD:"$BRANCH"

echo "=== Job completado ==="
