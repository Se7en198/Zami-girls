// deno-lint-ignore-file no-explicit-any
import { serve } from 'https://deno.land/std@0.224.0/http/server.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
}

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  })
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  if (req.method !== 'POST') {
    return json({ error: 'Method not allowed' }, 405)
  }

  const RUNPOD_API_KEY = Deno.env.get('RUNPOD_API_KEY')
  const RUNPOD_ENDPOINT_ID = Deno.env.get('RUNPOD_ENDPOINT_ID')

  if (!RUNPOD_API_KEY || !RUNPOD_ENDPOINT_ID) {
    return json({ error: 'Missing RUNPOD_API_KEY or RUNPOD_ENDPOINT_ID secret' }, 500)
  }

  try {
    const body = await req.json()
    const action = body?.action

    if (action === 'run') {
      const workflow = body?.workflow
      const jobName = body?.job_name ?? 'face_generation'
      if (!workflow) return json({ error: 'workflow is required for action=run' }, 400)

      const runResp = await fetch(`https://api.runpod.ai/v2/${RUNPOD_ENDPOINT_ID}/run`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${RUNPOD_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: { workflow, job_name: jobName } }),
      })

      const payload = await runResp.json().catch(() => ({}))
      return json(payload, runResp.status)
    }

    if (action === 'status') {
      const jobId = body?.job_id
      if (!jobId) return json({ error: 'job_id is required for action=status' }, 400)

      const statusResp = await fetch(`https://api.runpod.ai/v2/${RUNPOD_ENDPOINT_ID}/status/${jobId}`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${RUNPOD_API_KEY}`,
          'Content-Type': 'application/json',
        },
      })

      const payload = await statusResp.json().catch(() => ({}))
      return json(payload, statusResp.status)
    }

    return json({ error: "Unsupported action. Use 'run' or 'status'" }, 400)
  } catch (error: any) {
    return json({ error: error?.message ?? 'Unknown proxy error' }, 500)
  }
})
