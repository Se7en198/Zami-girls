#!/bin/bash
# JOB: Generar 4 rostros latinas exóticas
echo "[$(date)] ▸ Iniciando generación de 4 rostros latinas..."
cd /workspace/Zami-girls
python3 test-latinas.py
echo "[$(date)] ✓ Job completado"
