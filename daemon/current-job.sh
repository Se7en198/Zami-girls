#!/bin/bash
# JOB: Generar 3 nuevas latinas con 2x2 multi-view grid
PAT=$(cat /workspace/.zami_pat | tr -d '\n\r ')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"
REPO_DIR="/workspace/Zami-girls"

cd "$REPO_DIR"

echo "[$(date)] ▸ Generando 3 latinas con 2x2 multi-view..."
python3 test-nuevas-latinas.py

echo "[$(date)] ▸ Sincronizando con GitHub..."
git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" 2>/dev/null
git reset --hard refs/remotes/origin/"$BRANCH"

mkdir -p daemon/output
cp test-output/Cubana-*.png daemon/output/ 2>/dev/null
cp test-output/Mexicana-*.png daemon/output/ 2>/dev/null
cp "test-output/Caribeña-"*.png daemon/output/ 2>/dev/null

echo "▸ Imágenes copiadas:"
ls -lh daemon/output/*.png 2>/dev/null

git add daemon/output/
git diff --cached --quiet || git commit -m "images: 3 latinas 2x2 multi-view grid"
git push "$REMOTE" HEAD:"$BRANCH" && echo "✓ Pusheado" || echo "✗ Push falló"
