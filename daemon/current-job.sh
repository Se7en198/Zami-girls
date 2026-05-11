#!/bin/bash
# JOB: Leer configs AION — push garantizado (reset a origin primero)
AION_CONFIGS="/workspace/runpod-slim/ComfyUI/custom_nodes/ComfyUI_AION/configs"
PAT=$(cat /workspace/.zami_pat | tr -d '\n\r ')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"
REPO_DIR="/workspace/Zami-girls"

cd "$REPO_DIR"

# 1. Recoger configs AION ANTES de tocar git
mkdir -p /tmp/zami-results
echo "$(date)" > /tmp/zami-results/last-alive.txt
echo "=== AION CONFIGS ===" > /tmp/zami-results/aion-configs.txt
for f in "$AION_CONFIGS"/*.json; do
    echo "--- $(basename $f) ---" >> /tmp/zami-results/aion-configs.txt
    cat "$f" >> /tmp/zami-results/aion-configs.txt
    echo "" >> /tmp/zami-results/aion-configs.txt
done
echo "✓ Configs leídos: $(wc -l < /tmp/zami-results/aion-configs.txt) líneas"

# 2. Sincronizar con remote (fast-forward garantizado)
git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" 2>/dev/null
git reset --hard refs/remotes/origin/"$BRANCH"

# 3. Copiar resultados y pushear
mkdir -p daemon/results
cp /tmp/zami-results/*.txt daemon/results/
git add daemon/results/
git commit -m "result: aion configs $(date +%H:%M)"
git push "$REMOTE" HEAD:"$BRANCH" && echo "✓ Pusheado a GitHub" || echo "✗ Push falló"
