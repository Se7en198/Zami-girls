#!/bin/bash
# Job: Fase 1 — Latina Lightskin (1 modelo)
# Nariz prominente · Ojos azul profundo · Cabello muy crespo · Lightskin
PAT=$(cat /workspace/.zami_pat | tr -d '\n\r ')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"
cd /workspace/Zami-girls
git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" 2>/dev/null
git reset --hard refs/remotes/origin/"$BRANCH"
mkdir -p daemon/output test-output
python3 test-modelo-latina.py
