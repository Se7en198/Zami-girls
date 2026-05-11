#!/usr/bin/env node
/**
 * Zami Girls — Prueba Fase 1: Generación de Rostros
 * Corre: node test-fase1.js
 * Requiere Node.js 18+
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dir = path.dirname(fileURLToPath(import.meta.url))

// ─── CONFIG ───────────────────────────────────────────────────────────────────
const COMFYUI_URL = 'https://yox2fumbwtg8fb-8188.proxy.runpod.net'
const OUTPUT_DIR  = path.join(__dir, 'test-output')
const WORKFLOW    = JSON.parse(fs.readFileSync(path.join(__dir, 'src/workflows/face-generation.json'), 'utf8'))

// Parámetros del rostro a generar
const PARAMS = {
  ethnicity:   'Hispanic',
  skin_tone:   'medium',
  eye_color:   'brown',
  hair_color:  'dark brown',
  hair_length: 'shoulder-length',
  expression:  'soft smile',
  photo_type:  'Studio white background',
  brief_text:  'beautiful latina woman, elegant, natural',
}

// ─── HELPERS ──────────────────────────────────────────────────────────────────
function randomSeed() {
  return Math.floor(Math.random() * 999999999999999)
}

function buildWorkflow(params, seed) {
  const wf = JSON.parse(JSON.stringify(WORKFLOW))

  // Seeds
  wf['78'].inputs.seed           = seed
  wf['14'].inputs.noise_seed     = randomSeed()
  wf['73'].inputs.seed           = randomSeed()

  // Parámetros faciales en nodo AION (82)
  const allowed = ['brief_text','photo_type','ethnicity','skin_tone','eye_color',
    'hair_color','hair_length','expression','expression_variant']
  for (const k of allowed) {
    if (params[k]) wf['82'].inputs[k] = params[k]
  }

  return wf
}

async function queuePrompt(workflow) {
  const res = await fetch(`${COMFYUI_URL}/prompt`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ prompt: workflow, client_id: crypto.randomUUID() }),
  })
  if (!res.ok) throw new Error(`Queue error: ${res.status} ${await res.text()}`)
  const data = await res.json()
  console.log(`  → Prompt en cola: ${data.prompt_id}`)
  return data.prompt_id
}

async function pollResult(promptId, idx) {
  process.stdout.write(`  [${idx+1}] Generando`)
  for (let i = 0; i < 150; i++) {
    await new Promise(r => setTimeout(r, 2000))
    const res  = await fetch(`${COMFYUI_URL}/history/${promptId}`)
    const data = await res.json()
    if (data[promptId]?.outputs) {
      process.stdout.write(' ✓\n')
      return data[promptId]
    }
    process.stdout.write('.')
  }
  throw new Error('Timeout — ComfyUI tardó más de 5 min')
}

function extractImages(historyEntry) {
  const imgs = []
  for (const out of Object.values(historyEntry.outputs)) {
    if (out.images) imgs.push(...out.images)
  }
  return imgs
}

async function downloadImage(filename, type, subfolder, destPath) {
  const url = `${COMFYUI_URL}/view?filename=${encodeURIComponent(filename)}&type=${type}&subfolder=${encodeURIComponent(subfolder || '')}`
  const res  = await fetch(url)
  if (!res.ok) throw new Error(`Download error: ${res.status}`)
  const buf  = Buffer.from(await res.arrayBuffer())
  fs.writeFileSync(destPath, buf)
}

// ─── MAIN ─────────────────────────────────────────────────────────────────────
async function main() {
  console.log('\n╔══════════════════════════════════════════╗')
  console.log('║  ZAMI GIRLS — Prueba Fase 1: Rostros     ║')
  console.log('╚══════════════════════════════════════════╝\n')

  // Verificar ComfyUI
  console.log('▸ Verificando ComfyUI...')
  try {
    const res = await fetch(`${COMFYUI_URL}/system_stats`)
    if (!res.ok) throw new Error(res.status)
    const stats = await res.json()
    console.log(`  ✓ ComfyUI activo — VRAM: ${Math.round((stats.system?.vram_total||0)/1e9)}GB\n`)
  } catch (e) {
    console.error(`  ✗ No se puede conectar a ComfyUI: ${e.message}`)
    console.error(`  URL: ${COMFYUI_URL}`)
    process.exit(1)
  }

  // Crear carpeta de salida
  fs.mkdirSync(OUTPUT_DIR, { recursive: true })

  // Encolar 4 generaciones
  console.log('▸ Encolando 4 generaciones...')
  const jobs = []
  for (let i = 0; i < 4; i++) {
    const seed     = randomSeed()
    const workflow = buildWorkflow(PARAMS, seed)
    const promptId = await queuePrompt(workflow)
    jobs.push({ promptId, seed, index: i })
    await new Promise(r => setTimeout(r, 400))
  }

  // Esperar resultados
  console.log('\n▸ Esperando resultados (2 min aprox)...')
  const results = []
  for (const job of jobs) {
    try {
      const entry  = await pollResult(job.promptId, job.index)
      const images = extractImages(entry)
      // Tomar la última imagen (upscaled final)
      const img = images[images.length - 1]
      if (img) {
        const dest = path.join(OUTPUT_DIR, `rostro-${job.index + 1}-seed${job.seed}.png`)
        await downloadImage(img.filename, img.type, img.subfolder, dest)
        console.log(`  ✓ Guardada: ${path.relative(__dir, dest)}`)
        results.push({ index: job.index, seed: job.seed, file: dest, url: `${COMFYUI_URL}/view?filename=${encodeURIComponent(img.filename)}&type=${img.type}` })
      }
    } catch (err) {
      console.error(`  ✗ Job ${job.index + 1} falló: ${err.message}`)
    }
  }

  // Resumen
  console.log('\n╔══════════════════════════════════════════╗')
  console.log('║  RESULTADOS                              ║')
  console.log('╚══════════════════════════════════════════╝')
  for (const r of results) {
    console.log(`\n  Rostro ${r.index + 1} (seed: ${r.seed})`)
    console.log(`  Archivo: ${path.relative(__dir, r.file)}`)
    console.log(`  URL:     ${r.url}`)
  }
  console.log(`\n✓ ${results.length}/4 rostros generados en: ${OUTPUT_DIR}\n`)
}

main().catch(e => { console.error('\n✗ Error:', e.message); process.exit(1) })
