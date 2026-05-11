#!/bin/bash
# Job: generate 3 latinas (Cubana + Mexicana + Caribena)
PAT=$(cat /workspace/.zami_pat | tr -d '\n\r ')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"
cd /workspace/Zami-girls
git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" 2>/dev/null
git reset --hard refs/remotes/origin/"$BRANCH"
mkdir -p daemon/output test-output
python3 test-nuevas-latinas.py
cp test-output/*.png daemon/output/ 2>/dev/null || true
git add daemon/output/
git commit -m "output: 3 latinas Cubana+Mexicana+Caribena" 2>/dev/null || true
git push "$REMOTE" HEAD:"$BRANCH" && echo "OK imagenes pusheadas"
