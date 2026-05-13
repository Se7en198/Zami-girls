#!/usr/bin/env bash
set -euo pipefail

PROJECT_REF="${SUPABASE_PROJECT_REF:-vtyuylgfjvleywupbdzl}"
: "${SUPABASE_ACCESS_TOKEN:?Need SUPABASE_ACCESS_TOKEN}"
: "${RUNPOD_API_KEY:?Need RUNPOD_API_KEY}"
: "${RUNPOD_ENDPOINT_ID:=aqzsu0jydlras1}"

API="https://api.supabase.com/v1/projects/${PROJECT_REF}"

# 1) Deploy function source using Management API
curl -sS -X POST "${API}/functions/deploy?slug=runpod-proxy" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  -F 'metadata={"entrypoint_path":"index.ts","verify_jwt":false};type=application/json' \
  -F "file=@supabase/functions/runpod-proxy/index.ts;type=application/typescript" \
  -o /tmp/runpod_proxy_deploy.json

# 2) Set secrets required by the function
curl -sS -X POST "${API}/secrets" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "[{\"name\":\"RUNPOD_API_KEY\",\"value\":\"${RUNPOD_API_KEY}\"},{\"name\":\"RUNPOD_ENDPOINT_ID\",\"value\":\"${RUNPOD_ENDPOINT_ID}\"}]" \
  -o /tmp/runpod_proxy_secrets.json

# 3) Print compact results
python3 - <<'PY'
import json
for path in ['/tmp/runpod_proxy_deploy.json','/tmp/runpod_proxy_secrets.json']:
    print(f'--- {path} ---')
    try:
        with open(path,'r',encoding='utf-8') as f:
            data=json.load(f)
        print(json.dumps(data, indent=2)[:4000])
    except Exception as e:
        print('Could not parse JSON:', e)
PY
