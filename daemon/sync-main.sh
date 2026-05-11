#!/bin/bash
# Fusiona el branch de trabajo a main y pushea ambos.
# Se llama automáticamente al final de cada job.
set -euo pipefail

BRANCH="claude/ugc-profile-generator-PxVGb"
PAT=$(cat /workspace/.zami_pat | tr -d '\n\r ')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
REPO_DIR="/workspace/Zami-girls"

cd "$REPO_DIR"

echo "▸ Sincronizando main..."
git fetch "$REMOTE" main:refs/remotes/origin/main 2>/dev/null || true
git checkout main
git pull "$REMOTE" main --no-rebase 2>/dev/null || true
git merge refs/remotes/origin/"$BRANCH" --no-edit -m "sync: auto-merge desde $BRANCH"
git push "$REMOTE" main
git checkout "$BRANCH"
echo "✓ main actualizado"
