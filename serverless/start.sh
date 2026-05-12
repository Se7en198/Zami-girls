#!/bin/bash
set -e

# El volumen se monta en /runpod-volume
# ComfyUI busca modelos en /comfyui/models
# Enlazamos los modelos del volumen a ComfyUI

VOLUME_DIR="/runpod-volume"
COMFYUI_MODELS="/comfyui/models"
COMFYUI_NODES="/comfyui/custom_nodes"

if [ -d "${VOLUME_DIR}/models" ]; then
    echo "=== Enlazando modelos del Network Volume ==="
    mkdir -p "${COMFYUI_MODELS}"

    for subdir in "${VOLUME_DIR}/models"/*/; do
        [ -d "$subdir" ] || continue
        name=$(basename "$subdir")
        mkdir -p "${COMFYUI_MODELS}/${name}"

        find "$subdir" -maxdepth 1 -type f | while read -r f; do
            fname=$(basename "$f")
            target="${COMFYUI_MODELS}/${name}/${fname}"
            [ -e "$target" ] || ln -sf "$f" "$target"
        done
        echo "  ✓ $name"
    done
fi

if [ -d "${VOLUME_DIR}/custom_nodes" ]; then
    echo "=== Enlazando custom nodes ==="
    mkdir -p "${COMFYUI_NODES}"

    for node in "${VOLUME_DIR}/custom_nodes"/*/; do
        [ -d "$node" ] || continue
        name=$(basename "$node")
        target="${COMFYUI_NODES}/${name}"
        [ -e "$target" ] || ln -sf "$node" "$target"
        echo "  ✓ $name"
    done
fi

# También enlaza workflows si existen en el volumen
if [ -d "${VOLUME_DIR}/workflows" ]; then
    echo "=== Enlazando workflows ==="
    mkdir -p /comfyui/user/default/workflows
    for wf in "${VOLUME_DIR}/workflows"/*.json; do
        [ -f "$wf" ] || continue
        ln -sf "$wf" "/comfyui/user/default/workflows/$(basename $wf)"
        echo "  ✓ $(basename $wf)"
    done
fi

echo "=== Listo. Iniciando worker ==="
exec python3 /handler.py
