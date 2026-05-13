const RUNPOD_BASE = 'https://api.runpod.ai/v2'

function getOptionalEnv(name) {
  return import.meta.env[name]
}

function getEnv(name) {
  const value = getOptionalEnv(name)
  if (!value) throw new Error(`Missing environment variable: ${name}`)
  return value
}

function getEndpointId() {
  return getEnv('VITE_RUNPOD_ENDPOINT_ID')
}

function hasProxyConfig() {
  return Boolean(getOptionalEnv('VITE_SUPABASE_URL') && getOptionalEnv('VITE_SUPABASE_ANON_KEY'))
}

function getProxyUrl() {
  const base = getEnv('VITE_SUPABASE_URL')
  return `${base}/functions/v1/runpod-proxy`
}

function getProxyHeaders() {
  return {
    'Content-Type': 'application/json',
    apikey: getEnv('VITE_SUPABASE_ANON_KEY'),
    Authorization: `Bearer ${getEnv('VITE_SUPABASE_ANON_KEY')}`,
  }
}

function getDirectHeaders() {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${getEnv('VITE_RUNPOD_API_KEY')}`,
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export function b64ToDataUrl(b64) {
  return `data:image/png;base64,${b64}`
}

async function submitViaProxy(workflow, jobName) {
  const res = await fetch(getProxyUrl(), {
    method: 'POST',
    headers: getProxyHeaders(),
    body: JSON.stringify({ action: 'run', workflow, job_name: jobName }),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(`Proxy /run error ${res.status}: ${JSON.stringify(data)}`)
  return data
}

async function getStatusViaProxy(jobId) {
  const res = await fetch(getProxyUrl(), {
    method: 'POST',
    headers: getProxyHeaders(),
    body: JSON.stringify({ action: 'status', job_id: jobId }),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(`Proxy /status error ${res.status}: ${JSON.stringify(data)}`)
  return data
}

export async function submitRunpodJob(workflow, jobName = 'face_generation') {
  let data
  if (hasProxyConfig()) {
    data = await submitViaProxy(workflow, jobName)
  } else {
    const endpointId = getEndpointId()
    const res = await fetch(`${RUNPOD_BASE}/${endpointId}/run`, {
      method: 'POST',
      headers: getDirectHeaders(),
      body: JSON.stringify({ input: { workflow, job_name: jobName } }),
    })
    if (!res.ok) throw new Error(`RunPod /run error ${res.status}: ${await res.text()}`)
    data = await res.json()
  }

  if (!data?.id) throw new Error('RunPod did not return job id')
  return data
}

export async function getRunpodStatus(jobId) {
  if (hasProxyConfig()) return getStatusViaProxy(jobId)

  const endpointId = getEndpointId()
  const res = await fetch(`${RUNPOD_BASE}/${endpointId}/status/${jobId}`, {
    method: 'GET',
    headers: getDirectHeaders(),
  })
  if (!res.ok) throw new Error(`RunPod /status error ${res.status}: ${await res.text()}`)
  return res.json()
}

export async function waitForRunpodResult(jobId, { timeoutMs = 8 * 60 * 1000, pollMs = 4000, onProgress } = {}) {
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    const statusPayload = await getRunpodStatus(jobId)
    const status = statusPayload?.status
    if (onProgress) onProgress(statusPayload)

    if (status === 'COMPLETED') {
      const images = statusPayload?.output?.images || []
      if (!images.length) throw new Error('RunPod job completed without images')
      return { statusPayload, images }
    }
    if (status === 'FAILED' || status === 'CANCELLED' || status === 'TIMED_OUT') {
      throw new Error(`RunPod job ${jobId} ended with status ${status}`)
    }
    await sleep(pollMs)
  }
  throw new Error(`RunPod job ${jobId} timed out after ${Math.floor(timeoutMs / 1000)} seconds`)
}
