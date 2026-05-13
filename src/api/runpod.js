const RUNPOD_BASE = 'https://api.runpod.ai/v2'

function getEnv(name) {
  const value = import.meta.env[name]
  if (!value) {
    throw new Error(`Missing environment variable: ${name}`)
  }
  return value
}

function getHeaders() {
  const apiKey = getEnv('VITE_RUNPOD_API_KEY')
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${apiKey}`,
  }
}

function getEndpointId() {
  return getEnv('VITE_RUNPOD_ENDPOINT_ID')
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export function b64ToDataUrl(b64) {
  return `data:image/png;base64,${b64}`
}

export async function submitRunpodJob(workflow, jobName = 'face_generation') {
  const endpointId = getEndpointId()
  const res = await fetch(`${RUNPOD_BASE}/${endpointId}/run`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({
      input: {
        workflow,
        job_name: jobName,
      },
    }),
  })

  if (!res.ok) {
    const body = await res.text()
    throw new Error(`RunPod /run error ${res.status}: ${body}`)
  }

  const data = await res.json()
  if (!data?.id) {
    throw new Error('RunPod did not return job id')
  }
  return data
}

export async function getRunpodStatus(jobId) {
  const endpointId = getEndpointId()
  const res = await fetch(`${RUNPOD_BASE}/${endpointId}/status/${jobId}`, {
    method: 'GET',
    headers: getHeaders(),
  })

  if (!res.ok) {
    const body = await res.text()
    throw new Error(`RunPod /status error ${res.status}: ${body}`)
  }

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
      if (!images.length) {
        throw new Error('RunPod job completed without images')
      }
      return {
        statusPayload,
        images,
      }
    }

    if (status === 'FAILED' || status === 'CANCELLED' || status === 'TIMED_OUT') {
      throw new Error(`RunPod job ${jobId} ended with status ${status}`)
    }

    await sleep(pollMs)
  }

  throw new Error(`RunPod job ${jobId} timed out after ${Math.floor(timeoutMs / 1000)} seconds`)
}
