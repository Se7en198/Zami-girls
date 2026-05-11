#!/bin/bash
# JOB: Leer photo_type options del config AION
AION_CONFIGS="/workspace/runpod-slim/ComfyUI/custom_nodes/ComfyUI_AION/configs"

echo "▸ photo_types disponibles:"
cat "$AION_CONFIGS/photo_types.json" 2>/dev/null || echo "No encontrado como photo_types.json"

echo ""
echo "▸ Todos los configs disponibles:"
ls "$AION_CONFIGS/"

echo ""
echo "▸ Contenido completo de cada config:"
for f in "$AION_CONFIGS"/*.json; do
    echo "=== $(basename $f) ==="
    cat "$f"
    echo ""
done
