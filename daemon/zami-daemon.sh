#!/bin/bash
# Zami Girls — Remote Control Daemon (v3)
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

git config --global user.email "daemon@zami.local"
git config --global user.name "Zami Daemon"

mkdir -p "$DONE_DIR"
echo "[$(date)] Zami Daemon v3 iniciado (PID $$)" | tee -a "$LOG"

while true; do
    cd "$REPO_DIR" || { sleep "$INTERVAL"; continue; }

    # Leer PAT fresco cada iteración
    PAT=$(cat "$PAT_FILE" | tr -d '\n\r ')
    REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"

    # SOLO actualizar el job file desde remote — no resetear commits locales
    git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" --quiet 2>>"$LOG"
    git checkout refs/remotes/origin/"$BRANCH" -- daemon/current-job.sh 2>>"$LOG"

    if [ -f "$JOB_FILE" ]; then
        JOB_HASH=$(md5sum "$JOB_FILE" | cut -d' ' -f1)
        DONE_MARKER="$DONE_DIR/$JOB_HASH.done"

        if [ ! -f "$DONE_MARKER" ]; then
            echo "[$(date)] ▸ Job: $JOB_HASH" | tee -a "$LOG"
            bash "$JOB_FILE" >> "$LOG" 2>&1
            EXIT_CODE=$?
            echo "[$(date)] ✓ Terminado (exit: $EXIT_CODE)" | tee -a "$LOG"
            touch "$DONE_MARKER"
        fi
    fi

    sleep "$INTERVAL"
done
