#!/bin/bash
# JOB: Pushear imágenes existentes a GitHub
REPO_DIR="/workspace/Zami-girls"
OUTPUT_DIR="$REPO_DIR/test-output"
IMG_DIR="$REPO_DIR/daemon/output"
PAT=$(cat /workspace/.zami_pat | tr -d '\n\r')
REMOTE="https://x-access-token:${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"

echo "▸ Imágenes en test-output:"
ls -lh "$OUTPUT_DIR/"*.png 2>/dev/null || echo "  (ninguna encontrada)"

mkdir -p "$IMG_DIR"
COUNT=$(ls "$OUTPUT_DIR"/*.png 2>/dev/null | wc -l)

if [ "$COUNT" -eq 0 ]; then
    echo "✗ No hay imágenes PNG en $OUTPUT_DIR"
    echo "  Contenido del directorio:"
    ls -la "$OUTPUT_DIR/" 2>/dev/null || echo "  Directorio no existe"
    exit 0
fi

cp "$OUTPUT_DIR"/*.png "$IMG_DIR/"
echo "✓ $COUNT imágenes copiadas a daemon/output/"
ls -lh "$IMG_DIR/"

cd "$REPO_DIR"
git add daemon/output/
git diff --cached --quiet && echo "Nada nuevo" && exit 0
git commit -m "images: $COUNT rostros latinas generados"
git push "$REMOTE" HEAD:"$BRANCH"
echo "✓ Imágenes pusheadas a GitHub"
