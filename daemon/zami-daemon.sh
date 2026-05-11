#!/bin/bash
# Zami Girls — Remote Control Daemon
REPO_DIR="/workspace/Zami-girls"
JOB_FILE="$REPO_DIR/daemon/current-job.sh"
DONE_DIR="$REPO_DIR/daemon/done"
LOG="$REPO_DIR/daemon/daemon.log"
INTERVAL=20

# PAT guardado en setup
PAT_FILE="/workspace/.zami_pat"
if [ ! -f "$PAT_FILE" ]; then
    echo "[$(date)] ERROR: No se encontró $PAT_FILE. Corre setup.sh primero." | tee -a "$LOG"
    exit 1
fi
PAT=$(cat "$PAT_FILE")
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"

mkdir -p "$DONE_DIR"
echo "[$(date)] Zami Daemon iniciado (PID $$)" | tee -a "$LOG"

while true; do
    cd "$REPO_DIR"
    git fetch "$REMOTE" "$BRANCH" --quiet 2>>"$LOG"
    git reset --hard FETCH_HEAD --quiet 2>>"$LOG"

    if [ -f "$JOB_FILE" ]; then
        JOB_HASH=$(md5sum "$JOB_FILE" | cut -d' ' -f1)
        DONE_MARKER="$DONE_DIR/$JOB_HASH.done"

        if [ ! -f "$DONE_MARKER" ]; then
            echo "[$(date)] ▸ Job detectado: $JOB_HASH" | tee -a "$LOG"
            bash "$JOB_FILE" 2>&1 | tee -a "$LOG" > "$DONE_DIR/$JOB_HASH.output"
            EXIT_CODE=${PIPESTATUS[0]}
            echo "[$(date)] ✓ Job terminado (exit: $EXIT_CODE)" | tee -a "$LOG"
            touch "$DONE_MARKER"

            git add daemon/done/ 2>>"$LOG"
            git commit -m "job-result: $JOB_HASH exit=$EXIT_CODE" 2>>"$LOG"
            git push "$REMOTE" "$BRANCH" 2>>"$LOG"
            echo "[$(date)] ✓ Resultado pusheado" | tee -a "$LOG"
        fi
    fi

    sleep "$INTERVAL"
done
