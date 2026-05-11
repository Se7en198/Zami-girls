#!/bin/bash
# Zami Girls — Remote Control Daemon (v2)
REPO_DIR="/workspace/Zami-girls"
JOB_FILE="$REPO_DIR/daemon/current-job.sh"
DONE_DIR="/tmp/zami-done"
LOG="$REPO_DIR/daemon/daemon.log"
INTERVAL=20
BRANCH="claude/ugc-profile-generator-PxVGb"

PAT_FILE="/workspace/.zami_pat"
if [ ! -f "$PAT_FILE" ]; then
    echo "[$(date)] ERROR: No se encontró $PAT_FILE" | tee -a "$LOG"; exit 1
fi
PAT=$(cat "$PAT_FILE" | tr -d '\n\r')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"

# Configurar git globalmente
git config --global user.email "daemon@zami.local"
git config --global user.name "Zami Daemon"

mkdir -p "$DONE_DIR"
echo "[$(date)] Zami Daemon v2 iniciado (PID $$)" | tee -a "$LOG"

while true; do
    cd "$REPO_DIR" || { sleep "$INTERVAL"; continue; }

    # Fetch y actualizar repo
    git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" --quiet 2>>"$LOG"
    git reset --hard refs/remotes/origin/"$BRANCH" --quiet 2>>"$LOG"

    if [ -f "$JOB_FILE" ]; then
        JOB_HASH=$(md5sum "$JOB_FILE" | cut -d' ' -f1)
        DONE_MARKER="$DONE_DIR/$JOB_HASH.done"

        if [ ! -f "$DONE_MARKER" ]; then
            echo "[$(date)] ▸ Job: $JOB_HASH" | tee -a "$LOG"

            # Ejecutar job
            bash "$JOB_FILE" >> "$LOG" 2>&1
            EXIT_CODE=$?
            echo "[$(date)] ✓ Terminado (exit: $EXIT_CODE)" | tee -a "$LOG"
            touch "$DONE_MARKER"

            # Push resultado (log)
            git add daemon/ 2>>"$LOG"
            git diff --cached --quiet || git commit -m "job-done: $JOB_HASH" 2>>"$LOG"
            git push "$REMOTE" HEAD:"$BRANCH" 2>>"$LOG" && \
                echo "[$(date)] ✓ Pusheado a GitHub" | tee -a "$LOG" || \
                echo "[$(date)] ✗ Push falló" | tee -a "$LOG"
        fi
    fi

    sleep "$INTERVAL"
done
