#!/bin/bash
# JOB: Push commits pendientes a GitHub
PAT=$(cat /workspace/.zami_pat | tr -d '\n\r')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"

cd /workspace/Zami-girls

echo "▸ Commits pendientes:"
git log --oneline origin/"$BRANCH"..HEAD 2>/dev/null || git log --oneline -3

echo "▸ Pusheando..."
git push "$REMOTE" HEAD:"$BRANCH" && echo "✓ Push exitoso" || echo "✗ Push falló"
