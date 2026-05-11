#!/bin/bash
# JOB: Fase 2 — Generar 4 cuerpos para rostro-2
REPO_DIR="/workspace/Zami-girls"
TEST_OUTPUT="$REPO_DIR/test-output"
COMFYUI_INPUT="/workspace/runpod-slim/ComfyUI/input"

echo "▸ Archivos en test-output:"
ls -lh "$TEST_OUTPUT"/*.png 2>/dev/null

# Rostro 2 seleccionado por el usuario
FACE_PNG="$TEST_OUTPUT/rostro-2-seed826112501169234.png"

if [ ! -f "$FACE_PNG" ]; then
    echo "✗ No se encontró rostro-2. Buscando alternativas..."
    ls "$TEST_OUTPUT"/*.png 2>/dev/null
    exit 1
fi

echo ""
echo "▸ Copiando rostro-2 al input de ComfyUI..."
mkdir -p "$COMFYUI_INPUT"
cp "$FACE_PNG" "$COMFYUI_INPUT/rostro-2-selected.png"
echo "✓ Copiado como: rostro-2-selected.png"

echo ""
echo "▸ Iniciando Fase 2 — 4 variaciones de cuerpo..."
cd "$REPO_DIR"
python3 test-fase2.py "rostro-2-selected.png"
echo "✓ Fase 2 completada"
