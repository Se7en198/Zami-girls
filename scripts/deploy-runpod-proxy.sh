#!/usr/bin/env bash
set -euo pipefail

PROJECT_REF="${SUPABASE_PROJECT_REF:-vtyuylgfjvleywupbdzl}"
: "${SUPABASE_ACCESS_TOKEN:?Need SUPABASE_ACCESS_TOKEN}"
: "${RUNPOD_API_KEY:?Need RUNPOD_API_KEY}"
: "${RUNPOD_ENDPOINT_ID:=aqzsu0jydlras1}"

if command -v supabase >/dev/null 2>&1; then
  SUPABASE_CMD=(supabase)
else
  SUPABASE_CMD=(npx -y @supabase/cli@latest)
fi

"${SUPABASE_CMD[@]}" login --token "$SUPABASE_ACCESS_TOKEN"
"${SUPABASE_CMD[@]}" link --project-ref "$PROJECT_REF"
"${SUPABASE_CMD[@]}" functions deploy runpod-proxy --no-verify-jwt
"${SUPABASE_CMD[@]}" secrets set RUNPOD_API_KEY="$RUNPOD_API_KEY" RUNPOD_ENDPOINT_ID="$RUNPOD_ENDPOINT_ID"

echo "runpod-proxy deployed for project $PROJECT_REF"
