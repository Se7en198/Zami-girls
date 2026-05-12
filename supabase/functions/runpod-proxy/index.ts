/**
 * runpod-proxy — Supabase Edge Function
 *
 * Actúa de proxy entre Claude Code / scripts de servidor y RunPod API.
 * Necesario porque RunPod bloquea IPs de data centers (403 "Host not in allowlist").
 * Las Edge Functions de Supabase salen con IPs no bloqueadas.
 *
 * POST { workflow, jobName }   → submite job, devuelve { id, status }
 * GET  ?jobId=xxx              → consulta status, devuelve { status, output? }
 */

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...CORS, 'Content-Type': 'application/json' },
  })
}

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS })

  const RUNPOD_KEY = Deno.env.get('RUNPOD_API_KEY')
  const ENDPOINT   = Deno.env.get('RUNPOD_ENDPOINT_ID')

  if (!RUNPOD_KEY || !ENDPOINT) {
    return json({ error: 'Faltan secrets: RUNPOD_API_KEY y/o RUNPOD_ENDPOINT_ID' }, 500)
  }

  const BASE = `https://api.runpod.ai/v2/${ENDPOINT}`
  const auth = { 'Authorization': `Bearer ${RUNPOD_KEY}`, 'Content-Type': 'application/json' }

  try {
    const url   = new URL(req.url)
    const jobId = url.searchParams.get('jobId')

    if (jobId) {
      // ── Poll status ──────────────────────────────────────────────────────
      const r    = await fetch(`${BASE}/status/${jobId}`, { headers: auth })
      const data = await r.json()
      return json(data, r.status)
    }

    // ── Submit new job ───────────────────────────────────────────────────
    if (req.method !== 'POST') return json({ error: 'Use POST para enviar jobs' }, 405)

    const { workflow, jobName = 'face' } = await req.json()
    if (!workflow) return json({ error: "'workflow' es requerido" }, 400)

    const r = await fetch(`${BASE}/run`, {
      method:  'POST',
      headers: auth,
      body:    JSON.stringify({ input: { workflow, job_name: jobName } }),
    })
    const data = await r.json()
    return json(data, r.status)

  } catch (err) {
    return json({ error: String(err) }, 500)
  }
})
