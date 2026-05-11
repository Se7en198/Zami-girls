#!/bin/bash
# Zami Girls — Push a new job to the daemon from the pod
# Usage: bash /workspace/Zami-girls/daemon/push-job.sh [job_file]
#
# If job_file is provided it replaces daemon/current-job.sh before pushing.
# If omitted, the existing daemon/current-job.sh is committed and pushed as-is.

set -e

REPO_DIR="/workspace/Zami-girls"
PAT_FILE="/workspace/.zami_pat"
JOB_TARGET="$REPO_DIR/daemon/current-job.sh"
JOB_SOURCE="${1:-}"

# ── Sanity checks ───────────────────────────────────────────────────────────
if [ ! -f "$PAT_FILE" ]; then
    echo "ERROR: PAT no encontrado en $PAT_FILE"
    echo "       Corre daemon/setup.sh primero."
    exit 1
fi

if [ ! -d "$REPO_DIR/.git" ]; then
    echo "ERROR: Repo no encontrado en $REPO_DIR"
    echo "       Corre daemon/setup.sh primero."
    exit 1
fi

PAT=$(cat "$PAT_FILE")
BRANCH=$(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD)
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"

# ── Copiar job si se pasó uno ───────────────────────────────────────────────
if [ -n "$JOB_SOURCE" ]; then
    if [ ! -f "$JOB_SOURCE" ]; then
        echo "ERROR: Job file no encontrado: $JOB_SOURCE"
        exit 1
    fi
    cp "$JOB_SOURCE" "$JOB_TARGET"
    chmod +x "$JOB_TARGET"
    echo "▸ Job copiado: $JOB_SOURCE → $JOB_TARGET"
else
    echo "▸ Usando job actual: $JOB_TARGET"
fi

if [ ! -f "$JOB_TARGET" ]; then
    echo "ERROR: $JOB_TARGET no existe. Pasa un job_file como argumento."
    exit 1
fi

# ── Fetch + rebase para evitar conflictos ──────────────────────────────────
echo "▸ Sincronizando con GitHub ($BRANCH)..."
git -C "$REPO_DIR" fetch "$REMOTE" "$BRANCH" 2>/dev/null
git -C "$REPO_DIR" rebase FETCH_HEAD 2>/dev/null || true

# ── Commit y push ───────────────────────────────────────────────────────────
git -C "$REPO_DIR" add "$JOB_TARGET"

if git -C "$REPO_DIR" diff --cached --quiet; then
    echo "▸ No hay cambios en current-job.sh — forzando commit vacío para despertar al daemon..."
    git -C "$REPO_DIR" commit --allow-empty -m "chore: trigger daemon job [$(date -u '+%Y-%m-%dT%H:%M:%SZ')]"
else
    git -C "$REPO_DIR" commit -m "job: update current-job.sh [$(date -u '+%Y-%m-%dT%H:%M:%SZ')]"
fi

echo "▸ Pusheando a GitHub..."
git -C "$REPO_DIR" push "$REMOTE" HEAD:"$BRANCH"

echo ""
echo "✓ Job enviado al daemon en la rama $BRANCH"
echo "  El daemon lo ejecutará en el próximo poll (≤ 30 s)."
echo "  Logs: tail -f $REPO_DIR/daemon/daemon.log"
echo ""
