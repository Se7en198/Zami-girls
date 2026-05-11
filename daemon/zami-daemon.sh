#!/bin/bash
# Zami Girls — Remote Control Daemon (v4)
# Trigger sources (checked every loop, local takes priority):
#   1. LOCAL:  /workspace/zami-next-job.sh  (FileBrowser / JupyterLab drop)
#   2. GITHUB: daemon/current-job.sh        (MCP / Claude push)
REPO_DIR="/workspace/Zami-girls"
JOB_FILE="$REPO_DIR/daemon/current-job.sh"
LOCAL_TRIGGER="/workspace/zami-next-job.sh"
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
echo "[$(date)] Zami Daemon v4 iniciado (PID $$)" | tee -a "$LOG"
echo "[$(date)] Trigger local: $LOCAL_TRIGGER" | tee -a "$LOG"

# ──────────────────────────────────────────────────────────────────────────────
# run_job <file> <source_label>
#   Executes <file> if its hash hasn't been seen before, then marks it done.
#   For the local trigger, the file is deleted afterwards.
# ──────────────────────────────────────────────────────────────────────────────
run_job() {
    local job_file="$1"
    local source="$2"
    local job_hash
    job_hash=$(md5sum "$job_file" | cut -d' ' -f1)
    local done_marker="$DONE_DIR/$job_hash.done"

    if [ ! -f "$done_marker" ]; then
        echo "[$(date)] ▸ Job [$source]: $job_hash" | tee -a "$LOG"
        bash "$job_file" >> "$LOG" 2>&1
        local exit_code=$?
        echo "[$(date)] ✓ Terminado [$source] (exit: $exit_code)" | tee -a "$LOG"
        touch "$done_marker"
        return 0   # job was run
    fi
    return 1       # already done, skipped
}

while true; do
    cd "$REPO_DIR" || { sleep "$INTERVAL"; continue; }

    # Leer PAT fresco cada iteración
    PAT=$(cat "$PAT_FILE" | tr -d '\n\r ')
    REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"

    # ── TRIGGER 1: LOCAL FILE (priority) ─────────────────────────────────────
    if [ -f "$LOCAL_TRIGGER" ]; then
        echo "[$(date)] Trigger local detectado: $LOCAL_TRIGGER" | tee -a "$LOG"
        run_job "$LOCAL_TRIGGER" "local"
        # Always remove the trigger file so it won't re-fire after a daemon restart
        rm -f "$LOCAL_TRIGGER"
        echo "[$(date)] Trigger local eliminado" | tee -a "$LOG"
        # Skip GitHub check this cycle — job already ran
        sleep "$INTERVAL"
        continue
    fi

    # ── TRIGGER 2: GITHUB (fallback) ─────────────────────────────────────────
    git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" --quiet 2>>"$LOG"
    git checkout refs/remotes/origin/"$BRANCH" -- daemon/current-job.sh 2>>"$LOG"

    if [ -f "$JOB_FILE" ]; then
        run_job "$JOB_FILE" "github"
    fi

    sleep "$INTERVAL"
done
