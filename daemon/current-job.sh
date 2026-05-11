#!/bin/bash
# JOB: Generar 3 nuevas latinas top 2025-2026 + pushear a GitHub
PAT=$(cat /workspace/.zami_pat | tr -d '\n\r ')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"
REPO_DIR="/workspace/Zami-girls"
IMG_DIR="$REPO_DIR/daemon/output"

echo "[$(date)] ▸ Generando 3 nuevas latinas..."
cd "$REPO_DIR"
python3 test-nuevas-latinas.py

echo "[$(date)] ▸ Pusheando imágenes a GitHub..."
mkdir -p "$IMG_DIR"
cp test-output/Cubana-*.png "$IMG_DIR/" 2>/dev/null
cp test-output/Mexicana-*.png "$IMG_DIR/" 2>/dev/null
cp test-output/Caribeña-*.png "$IMG_DIR/" 2>/dev/null

git add daemon/output/ PORTRAIT-GENERATOR.md
git diff --cached --quiet || git commit -m "images: 3 nuevas latinas top 2025-2026"
git push "$REMOTE" HEAD:"$BRANCH" && echo "✓ Pusheado" || echo "✗ Push falló"
