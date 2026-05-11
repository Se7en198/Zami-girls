#!/bin/bash
# Zami Girls — One-time pod setup
# Run this ONCE in the RunPod web terminal to start the daemon.
# After this, Claude Code handles everything — no more terminal needed.

set -e
REPO_DIR="/workspace/Zami-girls"
PAT_FILE="/workspace/.zami_pat"
BRANCH="claude/ugc-profile-generator-PxVGb"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ZAMI GIRLS — Pod Setup  (run once)      ║"
echo "╚══════════════════════════════════════════╝"

# ── Check if daemon is already running ──────────────────────────────────────
if [ -f /tmp/zami-daemon.pid ]; then
    EXISTING_PID=$(cat /tmp/zami-daemon.pid)
    if ps -p "$EXISTING_PID" > /dev/null 2>&1; then
        echo ""
        echo "✓ Daemon already running — PID: $EXISTING_PID"
        echo "  Log: tail -f $REPO_DIR/daemon/daemon.log"
        echo ""
        echo "  Send commands via Claude Code — no terminal needed."
        echo ""
        exit 0
    fi
fi

# ── Ask for PAT if not saved ─────────────────────────────────────────────────
if [ ! -f "$PAT_FILE" ]; then
    echo ""
    read -rsp "Paste your GitHub PAT (ghp_... needs repo write scope): " PAT
    echo ""
    echo "$PAT" > "$PAT_FILE"
    chmod 600 "$PAT_FILE"
    echo "▸ PAT saved to $PAT_FILE"
fi

PAT=$(cat "$PAT_FILE")
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"

# ── Configure git identity on pod ────────────────────────────────────────────
git config --global user.email "zami-daemon@runpod.local"
git config --global user.name "Zami Daemon"
echo "▸ Git identity configured"

# ── Clone or update repo ─────────────────────────────────────────────────────
if [ ! -d "$REPO_DIR/.git" ]; then
    echo "▸ Cloning repo..."
    git clone -b "$BRANCH" "$REMOTE" "$REPO_DIR"
else
    echo "▸ Updating repo..."
    cd "$REPO_DIR"
    git fetch "$REMOTE" "$BRANCH"
    git reset --hard FETCH_HEAD
fi

# ── Stop any stale daemon ────────────────────────────────────────────────────
if [ -f /tmp/zami-daemon.pid ]; then
    OLD_PID=$(cat /tmp/zami-daemon.pid)
    kill "$OLD_PID" 2>/dev/null && echo "▸ Stopped previous daemon (PID $OLD_PID)"
fi

# ── Launch daemon ────────────────────────────────────────────────────────────
mkdir -p "$REPO_DIR/daemon/done"
nohup bash "$REPO_DIR/daemon/zami-daemon.sh" > /tmp/zami-daemon-boot.log 2>&1 &
DAEMON_PID=$!
echo $DAEMON_PID > /tmp/zami-daemon.pid

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ✓ Daemon running — PID: $DAEMON_PID"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  ✓ Daemon running. Send commands via Claude Code — no more terminal needed."
echo ""
echo "  Boot log : tail -f /tmp/zami-daemon-boot.log"
echo "  Daemon log: tail -f $REPO_DIR/daemon/daemon.log"
echo ""
