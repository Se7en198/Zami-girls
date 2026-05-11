#!/bin/bash
# Zami Girls — One-time setup en el pod
# Corre esto UNA SOLA VEZ en el Web Terminal del pod

set -e
REPO_DIR="/workspace/Zami-girls"
PAT_FILE="/workspace/.zami_pat"
BRANCH="claude/ugc-profile-generator-PxVGb"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ZAMI GIRLS — Instalando daemon          ║"
echo "╚══════════════════════════════════════════╝"

# Pedir PAT si no existe
if [ ! -f "$PAT_FILE" ]; then
    echo ""
    read -rsp "Pega tu GitHub PAT (ghp_...): " PAT
    echo ""
    echo "$PAT" > "$PAT_FILE"
    chmod 600 "$PAT_FILE"
    echo "▸ PAT guardado en $PAT_FILE"
fi

PAT=$(cat "$PAT_FILE")
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"

# Configurar identidad git en el pod
git config --global user.email "zami-daemon@runpod.local"
git config --global user.name "Zami Daemon"
echo "▸ Git identity configurada"

# Clonar o actualizar repo
if [ ! -d "$REPO_DIR/.git" ]; then
    echo "▸ Clonando repo..."
    git clone -b "$BRANCH" "$REMOTE" "$REPO_DIR"
else
    echo "▸ Actualizando repo..."
    cd "$REPO_DIR"
    git fetch "$REMOTE" "$BRANCH"
    git reset --hard FETCH_HEAD
fi

# Matar daemon anterior
if [ -f /tmp/zami-daemon.pid ]; then
    OLD_PID=$(cat /tmp/zami-daemon.pid)
    kill "$OLD_PID" 2>/dev/null && echo "▸ Daemon anterior detenido (PID $OLD_PID)"
fi

# Lanzar daemon
mkdir -p "$REPO_DIR/daemon/done"
nohup bash "$REPO_DIR/daemon/zami-daemon.sh" > /tmp/zami-daemon-boot.log 2>&1 &
DAEMON_PID=$!
echo $DAEMON_PID > /tmp/zami-daemon.pid

echo ""
echo "✓ Daemon corriendo — PID: $DAEMON_PID"
echo "✓ Log de arranque : tail -f /tmp/zami-daemon-boot.log"
echo "✓ Log del daemon  : tail -f $REPO_DIR/daemon/daemon.log"
echo ""
echo "  Claude ya controla el pod. No necesitas hacer nada más."
echo ""
