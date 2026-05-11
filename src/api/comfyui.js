// ComfyUI API client
// Base URL is configured via VITE_COMFYUI_URL env var (RunPod proxy URL)

const getBase = () => import.meta.env.VITE_COMFYUI_URL || 'https://yox2fumbwtg8fb-8188.proxy.runpod.net'

function randomSeed() {
  return Math.floor(Math.random() * 999999999999999)
}

// POST /prompt — queue a workflow, returns { prompt_id }
export async function queuePrompt(workflow) {
  const clientId = crypto.randomUUID()
  const res = await fetch(`${getBase()}/prompt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt: workflow, client_id: clientId }),
  })
  if (!res.ok) throw new Error(`ComfyUI queue error: ${res.status}`)
  const data = await res.json()
  return data.prompt_id
}

// GET /history/{id} — returns generation result when complete
export async function getHistory(promptId) {
  const res = await fetch(`${getBase()}/history/${promptId}`)
  if (!res.ok) throw new Error(`ComfyUI history error: ${res.status}`)
  return res.json()
}

// Poll history until outputs appear (max 5 min)
export async function waitForResult(promptId, onProgress) {
  const maxTries = 150
  for (let i = 0; i < maxTries; i++) {
    await new Promise(r => setTimeout(r, 2000))
    const history = await getHistory(promptId)
    const entry = history[promptId]
    if (entry?.outputs) return entry
    if (onProgress) onProgress(i)
  }
  throw new Error('Generación tardó demasiado. Verifica que ComfyUI está activo.')
}

// Build image URL from filename returned by ComfyUI
export function imageUrl(filename, type = 'output', subfolder = '') {
  return `${getBase()}/view?filename=${encodeURIComponent(filename)}&type=${type}&subfolder=${encodeURIComponent(subfolder)}`
}

// Extract output images from a history entry
export function extractImages(historyEntry) {
  const images = []
  if (!historyEntry?.outputs) return images
  for (const nodeOutput of Object.values(historyEntry.outputs)) {
    if (nodeOutput.images) {
      for (const img of nodeOutput.images) {
        images.push({
          filename: img.filename,
          url: imageUrl(img.filename, img.type, img.subfolder),
        })
      }
    }
  }
  return images
}

// ─── FACE GENERATION ─────────────────────────────────────────────────────────

export function buildFaceWorkflow(workflow, params = {}, seed = null) {
  const wf = structuredClone(workflow)
  const mainSeed = seed ?? randomSeed()

  // Randomize sampler seeds for variation
  if (wf['78']) wf['78'].inputs.seed = mainSeed
  if (wf['14']) wf['14'].inputs.noise_seed = randomSeed()
  if (wf['73']) wf['73'].inputs.seed = randomSeed()

  // Apply user-defined facial params to AION node (82)
  if (wf['82'] && params) {
    const allowed = [
      'brief_text', 'photo_type', 'sex', 'ethnicity', 'skin_tone',
      'skin_undertone', 'eye_color', 'eye_shape', 'eye_size', 'eye_tilt',
      'eyebrow_color', 'eyebrow_shape', 'eyebrow_thickness',
      'hair_color', 'hair_length', 'hair_structure', 'hair_volume',
      'nose_profile', 'nose_base', 'nose_tip',
      'lips_volume', 'cupid_bow', 'lips_proportion', 'lips_color',
      'forehead', 'cheekbones', 'jawline', 'chin', 'cheeks',
      'expression', 'expression_variant',
    ]
    for (const key of allowed) {
      if (params[key] !== undefined && params[key] !== '') {
        wf['82'].inputs[key] = params[key]
      }
    }
  }

  return { workflow: wf, seed: mainSeed }
}

// Generate N face variations from the same params
export async function generateFaces(baseWorkflow, params, count = 4) {
  const jobs = []
  for (let i = 0; i < count; i++) {
    const { workflow, seed } = buildFaceWorkflow(baseWorkflow, params)
    const promptId = await queuePrompt(workflow)
    jobs.push({ promptId, seed, index: i })
    // Small stagger so ComfyUI doesn't receive all at once
    await new Promise(r => setTimeout(r, 300))
  }
  return jobs
}

// ─── BODY GENERATION ─────────────────────────────────────────────────────────

export function buildBodyWorkflow(workflow, faceImageUrl, params = {}) {
  const wf = structuredClone(workflow)
  if (wf['78']) wf['78'].inputs.seed = randomSeed()
  if (wf['14']) wf['14'].inputs.noise_seed = randomSeed()

  // Inject face reference image — node ID will vary per workflow, use params.faceNodeId
  const faceNodeId = params.faceNodeId || 'face_input'
  if (wf[faceNodeId]) {
    wf[faceNodeId].inputs.image = faceImageUrl
  }
  return wf
}
