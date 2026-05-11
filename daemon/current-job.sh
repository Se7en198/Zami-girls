#!/bin/bash
# JOB: Copiar imágenes, commitear y pushear a GitHub
PAT=$(cat /workspace/.zami_pat | tr -d '\n\r ')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"
REPO_DIR="/workspace/Zami-girls"
OUTPUT_DIR="$REPO_DIR/test-output"
IMG_DIR="$REPO_DIR/daemon/output"

cd "$REPO_DIR"

echo "▸ Imágenes en test-output:"
ls "$OUTPUT_DIR"/*.png 2>/dev/null || echo "NINGUNA"

mkdir -p "$IMG_DIR"
cp "$OUTPUT_DIR"/*.png "$IMG_DIR/" 2>/dev/null

echo "▸ Imágenes copiadas:"
ls -lh "$IMG_DIR/"

git add daemon/output/
git diff --cached --quiet && echo "Ya estaban commiteadas" || git commit -m "images: rostros latinas generados"

echo "▸ Pusheando a GitHub..."
git push "$REMOTE" HEAD:"$BRANCH" && echo "✓ LISTO — imágenes en GitHub" || echo "✗ Push falló"
