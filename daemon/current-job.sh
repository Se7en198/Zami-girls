#!/bin/bash
# JOB: Corregir PAT duplicado y hacer push
PAT_FILE="/workspace/.zami_pat"

# El PAT tiene 80 chars (duplicado), debe ser 40 — tomar solo la primera mitad
CURRENT_LEN=$(cat "$PAT_FILE" | tr -d '\n\r' | wc -c)
echo "▸ Longitud actual del PAT: $CURRENT_LEN"

if [ "$CURRENT_LEN" -gt 40 ]; then
    head -c 40 "$PAT_FILE" > /tmp/pat_fix
    echo "" >> /tmp/pat_fix
    mv /tmp/pat_fix "$PAT_FILE"
    chmod 600 "$PAT_FILE"
    echo "✓ PAT corregido a 40 caracteres"
fi

PAT=$(cat "$PAT_FILE" | tr -d '\n\r')
echo "▸ Nueva longitud: ${#PAT}"

# Test
HTTP=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: token $PAT" \
    https://api.github.com/user)
echo "▸ GitHub API: $HTTP"

# Push
cd /workspace/Zami-girls
git push "https://${PAT}@github.com/Se7en198/Zami-girls.git" \
    HEAD:claude/ugc-profile-generator-PxVGb \
    && echo "✓ Push exitoso — imágenes en GitHub" \
    || echo "✗ Push falló"
