#!/bin/bash
# JOB: Fase 1 — Latina Lightskin (1 modelo)
# Nariz prominente estilizada · Ojos azul profundo · Cabello muy crespo
# Triggered: 2026-05-11T3 (multi-view)
set -euo pipefail

PAT=$(cat /workspace/.zami_pat | tr -d '\n\r ')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"
REPO_DIR="/workspace/Zami-girls"

cd "$REPO_DIR"
git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" 2>/dev/null
git reset --hard refs/remotes/origin/"$BRANCH"

echo "=== Generando Latina Lightskin — Fase 1 ==="
mkdir -p daemon/output test-output
python3 test-modelo-latina.py

echo "=== Job completado ==="

# Auto-merge a main para que siempre esté actualizado
bash "$REPO_DIR/daemon/sync-main.sh" || echo "⚠ sync-main falló (no crítico)"
