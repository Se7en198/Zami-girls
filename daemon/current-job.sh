#!/bin/bash
# JOB: Leer todos los configs AION y pushear resultado
AION_CONFIGS="/workspace/runpod-slim/ComfyUI/custom_nodes/ComfyUI_AION/configs"
PAT=$(cat /workspace/.zami_pat | tr -d '\n\r ')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"
REPO_DIR="/workspace/Zami-girls"

echo "=== DAEMON VIVO === $(date)"

cd "$REPO_DIR"

# Guardar configs AION
mkdir -p daemon/logs
echo "$(date)" > daemon/logs/last-alive.txt

echo "=== CONFIGS AION ===" > daemon/logs/aion-configs.txt
for f in "$AION_CONFIGS"/*.json; do
    echo "--- $(basename $f) ---" >> daemon/logs/aion-configs.txt
    cat "$f" >> daemon/logs/aion-configs.txt
    echo "" >> daemon/logs/aion-configs.txt
done

echo "✓ Configs guardados"
cat daemon/logs/aion-configs.txt

# Rebase sobre remote antes de pushear
git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" 2>/dev/null
git add daemon/logs/
git diff --cached --quiet || git commit -m "log: aion configs + daemon alive"
git rebase refs/remotes/origin/"$BRANCH" 2>/dev/null || true
git push "$REMOTE" HEAD:"$BRANCH" && echo "✓ Pusheado" || echo "✗ Push falló"
