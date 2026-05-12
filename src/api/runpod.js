// RunPod Serverless API client
// Endpoint: https://api.runpod.ai/v2/{ENDPOINT_ID}

const getEndpointId = () => import.meta.env.VITE_RUNPOD_ENDPOINT_ID || 'aqzsu0jydlras1'
const getApiKey     = () => import.meta.env.VITE_RUNPOD_API_KEY

const BASE = 'https://api.runpod.ai/v2'

function headers() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getApiKey()}`,
  }
}

// POST /run — envía el job, devuelve job_id
export async function submitJob(workflow, jobName = 'face') {
  const res = await fetch(`${BASE}/${getEndpointId()}/run`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ input: { workflow, job_name: jobName } }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`RunPod submit error ${res.status}: ${text}`)
  }
  const data = await res.json()
  return data.id
}

// GET /status/{job_id} — consulta el estado del job
export async function getJobStatus(jobId) {
  const res = await fetch(`${BASE}/${getEndpointId()}/status/${jobId}`, {
    headers: headers(),
  })
  if (!res.ok) throw new Error(`RunPod status error ${res.status}`)
  return res.json()
}

// Espera hasta COMPLETED o FAILED (poll cada 4s, timeout ~40 min)
export async function pollJob(jobId, onProgress) {
  const maxTries = 600
  for (let i = 0; i < maxTries; i++) {
    await new Promise(r => setTimeout(r, 4000))
    const data = await getJobStatus(jobId)

    if (onProgress) onProgress(data.status, i)

    if (data.status === 'COMPLETED') return data
    if (data.status === 'FAILED')
      throw new Error(`RunPod job falló: ${JSON.stringify(data.error || data)}`)
    if (data.status === 'CANCELLED' || data.status === 'TIMED_OUT')
      throw new Error(`RunPod job terminó con estado: ${data.status}`)
  }
  throw new Error('Timeout esperando job de RunPod (>40 min)')
}

// Wrapper principal: submit + poll, devuelve array de strings base64
export async function runFaceJob(workflow, jobName = 'face', onProgress) {
  const jobId = await submitJob(workflow, jobName)
  const result = await pollJob(jobId, onProgress)
  const images = result?.output?.images
  if (!images?.length) throw new Error('RunPod no devolvió imágenes en output.images')
  return { jobId, images }
}

// base64 → data URI válida para <img src>
export function b64ToDataUrl(b64, mime = 'image/png') {
  return `data:${mime};base64,${b64}`
}

// ─── VÍA PROXY SUPABASE (para llamadas desde servidor / Claude Code) ──────────
// Necesario porque RunPod bloquea IPs de data centers. Las Edge Functions de
// Supabase salen con IPs residenciales que RunPod acepta.

function proxyUrl() {
  const base = import.meta.env?.VITE_SUPABASE_URL || process.env.SUPABASE_URL || ''
  return `${base}/functions/v1/runpod-proxy`
}

function proxyHeaders() {
  const key = import.meta.env?.VITE_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY || ''
  return { 'Content-Type': 'application/json', 'apikey': key }
}

export async function submitJobViaProxy(workflow, jobName = 'face') {
  const res = await fetch(proxyUrl(), {
    method: 'POST',
    headers: proxyHeaders(),
    body: JSON.stringify({ workflow, jobName }),
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Proxy submit error ${res.status}: ${text}`)
  }
  const data = await res.json()
  if (data.error) throw new Error(`RunPod via proxy: ${data.error}`)
  return data.id
}

export async function pollJobViaProxy(jobId, onProgress) {
  const maxTries = 600
  for (let i = 0; i < maxTries; i++) {
    await new Promise(r => setTimeout(r, 4000))
    const res  = await fetch(`${proxyUrl()}?jobId=${jobId}`, { headers: proxyHeaders() })
    const data = await res.json()

    if (onProgress) onProgress(data.status, i)

    if (data.status === 'COMPLETED') return data
    if (data.status === 'FAILED')
      throw new Error(`RunPod job falló: ${JSON.stringify(data.error || data)}`)
    if (data.status === 'CANCELLED' || data.status === 'TIMED_OUT')
      throw new Error(`RunPod job terminó con estado: ${data.status}`)
  }
  throw new Error('Timeout esperando job de RunPod vía proxy (>40 min)')
}

export async function runFaceJobViaProxy(workflow, jobName = 'face', onProgress) {
  const jobId  = await submitJobViaProxy(workflow, jobName)
  const result = await pollJobViaProxy(jobId, onProgress)
  const images = result?.output?.images
  if (!images?.length) throw new Error('RunPod no devolvió imágenes en output.images')
  return { jobId, images }
}
