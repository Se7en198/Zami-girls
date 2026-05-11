#!/bin/bash
# JOB: Leer todos los configs AION y pushear resultado
AION_CONFIGS="/workspace/runpod-slim/ComfyUI/custom_nodes/ComfyUI_AION/configs"
PAT=$(cat /workspace/.zami_pat | tr -d '\n\r ')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"
REPO_DIR="/workspace/Zami-girls"

cd "$REPO_DIR"

# Guardar configs en daemon/results/ (no ignorado)
mkdir -p daemon/results
echo "$(date)" > daemon/results/last-alive.txt

echo "=== CONFIGS AION ===" > daemon/results/aion-configs.txt
for f in "$AION_CONFIGS"/*.json; do
    echo "--- $(basename $f) ---" >> daemon/results/aion-configs.txt
    cat "$f" >> daemon/results/aion-configs.txt
    echo "" >> daemon/results/aion-configs.txt
done

echo "✓ Configs guardados en daemon/results/aion-configs.txt"

# Fetch + rebase + push
git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" 2>/dev/null
git add daemon/results/
git diff --cached --quiet || git commit -m "result: aion configs completos"
git rebase refs/remotes/origin/"$BRANCH" 2>/dev/null || git reset --soft refs/remotes/origin/"$BRANCH"
git add daemon/results/
git diff --cached --quiet || git commit -m "result: aion configs completos"
git push "$REMOTE" HEAD:"$BRANCH" && echo "✓ Pusheado" || echo "✗ Push falló"
