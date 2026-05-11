#!/bin/bash
# JOB: Diagnóstico de PAT y push forzado
PAT=$(cat /workspace/.zami_pat | tr -d '\n\r' | tr -d ' ')
PAT_LEN=${#PAT}
PAT_START="${PAT:0:8}"

echo "▸ PAT longitud: $PAT_LEN caracteres"
echo "▸ PAT inicio: ${PAT_START}..."

# Test con curl directamente
echo "▸ Test curl auth:"
HTTP=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: token $PAT" \
    https://api.github.com/user)
echo "  GitHub API responde: $HTTP"

# Push con formato username:token
echo "▸ Intentando push con Se7en198:TOKEN..."
cd /workspace/Zami-girls
git push "https://Se7en198:${PAT}@github.com/Se7en198/Zami-girls.git" \
    HEAD:claude/ugc-profile-generator-PxVGb \
    && echo "✓ Push exitoso" || echo "✗ Push falló"
