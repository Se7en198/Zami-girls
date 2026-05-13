#!/usr/bin/env bash
set -euo pipefail

PROJECT_REF="${SUPABASE_PROJECT_REF:-vtyuylgfjvleywupbdzl}"
: "${SUPABASE_ACCESS_TOKEN:?Need SUPABASE_ACCESS_TOKEN}"
: "${RUNPOD_API_KEY:?Need RUNPOD_API_KEY}"
: "${RUNPOD_ENDPOINT_ID:=aqzsu0jydlras1}"

if ! command -v supabase >/dev/null 2>&1; then
  npm i -g supabase
fi

supabase login --token "$SUPABASE_ACCESS_TOKEN"
supabase link --project-ref "$PROJECT_REF"
supabase functions deploy runpod-proxy --no-verify-jwt
supabase secrets set RUNPOD_API_KEY="$RUNPOD_API_KEY" RUNPOD_ENDPOINT_ID="$RUNPOD_ENDPOINT_ID"

echo "runpod-proxy deployed for project $PROJECT_REF"
