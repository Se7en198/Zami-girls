#!/usr/bin/env python3
"""Lee los configs del nodo AION para ver las opciones disponibles"""
import json, os
from pathlib import Path

# Rutas posibles del nodo AION en RunPod
PATHS = [
    "/workspace/runpod-slim/ComfyUI/custom_nodes/ComfyUI_AION/configs",
    "/workspace/ComfyUI/custom_nodes/ComfyUI_AION/configs",
    "/workspace/runpod-slim/ComfyUI/custom_nodes/AION/configs",
]

for base in PATHS:
    p = Path(base)
    if p.exists():
        print(f"\n✓ Encontrado: {base}\n")
        for f in sorted(p.glob("*.json")):
            print(f"── {f.name}")
            try:
                data = json.loads(f.read_text())
                for key, val in data.items():
                    if isinstance(val, list):
                        print(f"   {key}: {val}")
                    else:
                        print(f"   {key}: {val}")
            except:
                print("   (error leyendo)")
            print()
        break
else:
    print("No encontrado. Buscando en todo /workspace...")
    result = os.popen("find /workspace -name '*.json' -path '*/AION/configs/*' 2>/dev/null").read()
    print(result or "No encontrado")
    result2 = os.popen("find /workspace -name 'ComfyUI_AION' -type d 2>/dev/null").read()
    print("Directorio AION:", result2 or "No encontrado")
