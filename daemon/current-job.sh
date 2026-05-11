#!/bin/bash
# JOB: Generar 4 rostros latinas + pushear imágenes a GitHub
set -e

REPO_DIR="/workspace/Zami-girls"
OUTPUT_DIR="$REPO_DIR/test-output"
IMG_DIR="$REPO_DIR/daemon/output"
PAT=$(cat /workspace/.zami_pat)
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"

echo "[$(date)] ▸ Generando 4 rostros latinas exóticas..."
cd "$REPO_DIR"
python3 test-latinas.py

echo "[$(date)] ▸ Copiando imágenes al repo..."
mkdir -p "$IMG_DIR"
cp "$OUTPUT_DIR"/*.png "$IMG_DIR/" 2>/dev/null || true
ls -lh "$IMG_DIR/"

echo "[$(date)] ▸ Pusheando imágenes a GitHub..."
git config user.email "daemon@zami.local"
git config user.name "Zami Daemon"
git add daemon/output/
git commit -m "images: 4 rostros latinas generados"
git push "$REMOTE" "$BRANCH"

echo "[$(date)] ✓ Imágenes disponibles en GitHub — rama daemon/output/"
