#!/bin/bash
# JOB: Diagnóstico + AION photo_types + reinicio si necesario
AION_CONFIGS="/workspace/runpod-slim/ComfyUI/custom_nodes/ComfyUI_AION/configs"
PAT=$(cat /workspace/.zami_pat | tr -d '\n\r ')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"
REPO_DIR="/workspace/Zami-girls"

echo "=== DAEMON VIVO === $(date)"
echo ""
echo "=== PHOTO TYPES ==="
cat "$AION_CONFIGS/photo_types.json" 2>/dev/null \
    || find /workspace -name "photo_types*" 2>/dev/null | head -5

echo ""
echo "=== TODOS LOS CONFIGS ==="
ls "$AION_CONFIGS/" 2>/dev/null

echo ""
echo "=== CONTENIDO ==="
for f in "$AION_CONFIGS"/*.json; do
    echo "--- $(basename $f) ---"
    cat "$f"
    echo ""
done

# Pushear resultado al repo para que Claude lo vea
cd "$REPO_DIR"
mkdir -p daemon/logs
echo "$(date)" > daemon/logs/last-alive.txt
cat "$AION_CONFIGS"/*.json 2>/dev/null > daemon/logs/aion-configs.txt || echo "no configs" > daemon/logs/aion-configs.txt
git add daemon/logs/
git diff --cached --quiet || git commit -m "log: daemon alive + aion configs"
git push "$REMOTE" HEAD:"$BRANCH" && echo "✓ Pusheado" || echo "✗ Push falló"
