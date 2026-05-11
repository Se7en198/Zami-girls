#!/bin/bash
# JOB: Pushear imágenes ya generadas a GitHub
REPO_DIR="/workspace/Zami-girls"
OUTPUT_DIR="$REPO_DIR/test-output"
IMG_DIR="$REPO_DIR/daemon/output"
PAT=$(cat /workspace/.zami_pat)
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"

echo "[$(date)] ▸ Archivos en test-output:"
ls -lh "$OUTPUT_DIR/" 2>/dev/null || echo "Directorio vacío o no existe"

mkdir -p "$IMG_DIR"
cp "$OUTPUT_DIR"/*.png "$IMG_DIR/" 2>/dev/null && echo "✓ Imágenes copiadas" || echo "✗ No se encontraron PNGs en $OUTPUT_DIR"

ls -lh "$IMG_DIR/"

cd "$REPO_DIR"
git config user.email "daemon@zami.local"
git config user.name "Zami Daemon"
git add daemon/output/
git commit -m "images: subir rostros generados" || echo "Nada nuevo para commitear"
git push "$REMOTE" "$BRANCH"
echo "[$(date)] ✓ Listo"
