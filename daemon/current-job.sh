#!/bin/bash
# JOB: Inspeccionar workflows disponibles en ComfyUI + nodo GeminiNanoBanana2
PAT=$(cat /workspace/.zami_pat | tr -d '\n\r ')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"
REPO_DIR="/workspace/Zami-girls"

cd "$REPO_DIR"

echo "=== WORKFLOWS EN /workspace ==="
find /workspace -name "*.json" | grep -i "workflow\|portrait\|aion\|zimage\|turbo\|creador\|rostro" 2>/dev/null | head -20

echo ""
echo "=== CUSTOM NODES INSTALADOS ==="
ls /workspace/runpod-slim/ComfyUI/custom_nodes/ 2>/dev/null | head -30

echo ""
echo "=== BÚSQUEDA GeminiNanoBanana ==="
find /workspace/runpod-slim/ComfyUI/custom_nodes -name "*.py" | xargs grep -l "NanoBanana\|nanobana\|GeminiNana" 2>/dev/null | head -10

echo ""
echo "=== WORKFLOWS EN ComfyUI ==="
ls /workspace/runpod-slim/ComfyUI/user/default/workflows/ 2>/dev/null
ls /workspace/runpod-slim/ComfyUI/workflows/ 2>/dev/null

echo ""
echo "=== NUESTRO WORKFLOW ACTUAL ==="
python3 -c "
import json
try:
    wf = json.load(open('src/workflows/face-generation.json'))
    for k,v in wf.items():
        print(f'  Node {k}: {v.get(\"class_type\",\"?\")} — {v.get(\"_meta\",{}).get(\"title\",\"\")}')
except Exception as e:
    print('Error:', e)
"

# Pushear resultado
git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" 2>/dev/null
git reset --hard refs/remotes/origin/"$BRANCH"
mkdir -p daemon/results
{
    echo "=== WORKFLOWS EN /workspace ==="
    find /workspace -name "*.json" | grep -i "workflow\|portrait\|aion\|zimage\|turbo\|creador\|rostro" 2>/dev/null
    echo ""
    echo "=== CUSTOM NODES ==="
    ls /workspace/runpod-slim/ComfyUI/custom_nodes/ 2>/dev/null
    echo ""
    echo "=== GeminiNanaBanana search ==="
    find /workspace/runpod-slim/ComfyUI/custom_nodes -name "*.py" | xargs grep -l "NanoBanana\|Nano_Banana\|GeminiNana" 2>/dev/null
    echo ""
    echo "=== ComfyUI workflows folder ==="
    find /workspace/runpod-slim/ComfyUI -name "*.json" -path "*/workflows/*" 2>/dev/null | head -20
} > daemon/results/workflow-inspection.txt

git add daemon/results/workflow-inspection.txt
git commit -m "result: workflow inspection + gemini banana search"
git push "$REMOTE" HEAD:"$BRANCH" && echo "✓ Pusheado" || echo "✗ Push falló"
