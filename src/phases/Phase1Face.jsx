import { useEffect, useState } from 'react'
import { Wand2, Check, RefreshCw, ChevronRight, Loader2, AlertCircle } from 'lucide-react'
import { supabase } from '../lib/supabase.js'
import { buildFaceWorkflow } from '../api/comfyui.js'
import { submitRunpodJob, waitForRunpodResult, b64ToDataUrl } from '../api/runpod.js'
import baseWorkflow from '../workflows/face-generation.json'

// ─── FACIAL FEATURE OPTIONS ───────────────────────────────────────────────────
const ETHNICITIES  = ['Caucasian','Hispanic','East Asian','South Asian','Black / African','Middle Eastern','Mixed','Southeast Asian']
const SKIN_TONES   = ['very fair','fair','light tan','medium','olive','tan','dark','very dark']
const EYE_COLORS   = ['brown','dark brown','hazel','green','blue','blue-green','gray','amber']
const HAIR_COLORS  = ['jet black','dark brown','brown','chestnut','auburn','dirty blonde','blonde','platinum blonde','red']
const HAIR_LENGTHS = ['buzz cut','pixie cut','ear-length','chin-length','shoulder-length','mid-back','waist-length']
const EXPRESSIONS  = ['neutral','happiness','smiling','soft smile','seductive','fierce','confident','playful']
const PHOTO_TYPES  = ['Studio white background','Outdoor natural light','Indoor lifestyle','Golden hour outdoor']

// ─── COMPONENT ────────────────────────────────────────────────────────────────
export default function Phase1Face({ model, onAdvance, onRefresh }) {
  const [faces, setFaces]           = useState([])    // { id, url, seed, status, promptId }
  const [selected, setSelected]     = useState(null)
  const [generating, setGenerating] = useState(false)
  const [error, setError]           = useState(null)
  const [params, setParams]         = useState({
    photo_type:  'Studio white background',
    ethnicity:   'Hispanic',
    skin_tone:   'medium',
    eye_color:   'brown',
    hair_color:  'dark brown',
    hair_length: 'shoulder-length',
    expression:  'soft smile',
    brief_text:  '',
  })

  // Load existing generated faces from DB
  useEffect(() => {
    loadFaces()
  }, [model.id])

  async function loadFaces() {
    const { data } = await supabase
      .from('phase_images')
      .select('*')
      .eq('model_id', model.id)
      .eq('phase', 1)
      .order('created_at', { ascending: true })

    if (data?.length) {
      setFaces(data.map(r => ({
        id: r.id,
        url: r.image_url,
        seed: r.seed,
        promptId: r.comfyui_prompt_id,
        status: 'done',
        selected: r.is_selected,
      })))
      const sel = data.find(r => r.is_selected)
      if (sel) setSelected(sel.id)
    }
  }

  function set(key, val) {
    setParams(p => ({ ...p, [key]: val }))
  }

  // ── Generate 4 faces ─────────────────────────────────────────────────────
  async function handleGenerate() {
    setGenerating(true)
    setError(null)
    setFaces([])
    setSelected(null)

    // Clear previous DB rows for this model/phase
    await supabase.from('phase_images').delete().eq('model_id', model.id).eq('phase', 1)

    try {
      const jobs = Array.from({ length: 4 }).map((_, i) => {
        const { workflow, seed } = buildFaceWorkflow(baseWorkflow, params)
        return { workflow, seed, index: i }
      })

      setFaces(jobs.map(j => ({ id: `pending-${j.index}`, promptId: null, seed: j.seed, status: 'pending', url: null })))

      await Promise.all(jobs.map(async (job) => {
        try {
          const submit = await submitRunpodJob(job.workflow, `face_${job.index + 1}`)
          const jobId = submit.id

          setFaces(prev => prev.map(f =>
            f.seed === job.seed ? { ...f, promptId: jobId, id: jobId } : f
          ))

          const { images } = await waitForRunpodResult(jobId, {
            onProgress: () => {
              setFaces(prev => prev.map(f =>
                (f.promptId === jobId || f.seed === job.seed) ? { ...f, status: 'generating' } : f
              ))
            },
          })

          const dataUrl = b64ToDataUrl(images[0])

          const { data: saved } = await supabase
            .from('phase_images')
            .insert({
              model_id: model.id,
              phase: 1,
              comfyui_prompt_id: jobId,
              filename: `${jobId}.png`,
              image_url: dataUrl,
              seed: job.seed,
              is_selected: false,
            })
            .select()
            .single()

          setFaces(prev => prev.map(f =>
            (f.promptId === jobId || f.seed === job.seed)
              ? { ...f, id: saved?.id || jobId, promptId: jobId, url: dataUrl, status: 'done' }
              : f
          ))
        } catch (err) {
          setFaces(prev => prev.map(f =>
            f.seed === job.seed ? { ...f, status: 'error' } : f
          ))
        }
      }))
    } catch (err) {
      setError(err.message)
    } finally {
      setGenerating(false)
    }
  }

  // ── Select a face ─────────────────────────────────────────────────────────
  async function handleSelect(face) {
    if (face.status !== 'done') return
    setSelected(face.id)

    // Mark selected in DB
    await supabase.from('phase_images').update({ is_selected: false }).eq('model_id', model.id).eq('phase', 1)
    await supabase.from('phase_images').update({ is_selected: true }).eq('id', face.id)

    // Save face url to model
    await supabase.from('models').update({ face_image_url: face.url }).eq('id', model.id)
    await onRefresh()
  }

  // ── Advance to Phase 2 ───────────────────────────────────────────────────
  async function handleAdvance() {
    await onAdvance()
  }

  const allDone = faces.length === 4 && faces.every(f => f.status === 'done' || f.status === 'error')

  return (
    <div className="max-w-4xl">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white mb-1">Fase 1 — Generación de Rostro</h2>
        <p className="text-gray-500 text-sm">Configura las características faciales y genera 4 variaciones para elegir.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-6">
        {/* ── Left: Params form ─────────────────────────────────────────── */}
        <div className="card space-y-4 self-start">
          <h3 className="font-semibold text-white text-sm">Características del Rostro</h3>

          <FormField label="Foto de referencia">
            <select className="select text-sm" value={params.photo_type} onChange={e => set('photo_type', e.target.value)}>
              {PHOTO_TYPES.map(v => <option key={v}>{v}</option>)}
            </select>
          </FormField>

          <FormField label="Descripción libre (opcional)">
            <textarea
              className="input text-sm resize-none"
              rows={2}
              placeholder="Ej: modelo latina, sensual, ojos expresivos..."
              value={params.brief_text}
              onChange={e => set('brief_text', e.target.value)}
            />
          </FormField>

          <FormField label="Etnia">
            <select className="select text-sm" value={params.ethnicity} onChange={e => set('ethnicity', e.target.value)}>
              {ETHNICITIES.map(v => <option key={v}>{v}</option>)}
            </select>
          </FormField>

          <FormField label="Tono de piel">
            <select className="select text-sm" value={params.skin_tone} onChange={e => set('skin_tone', e.target.value)}>
              {SKIN_TONES.map(v => <option key={v}>{v}</option>)}
            </select>
          </FormField>

          <div className="grid grid-cols-2 gap-3">
            <FormField label="Color de ojos">
              <select className="select text-sm" value={params.eye_color} onChange={e => set('eye_color', e.target.value)}>
                {EYE_COLORS.map(v => <option key={v}>{v}</option>)}
              </select>
            </FormField>
            <FormField label="Color de cabello">
              <select className="select text-sm" value={params.hair_color} onChange={e => set('hair_color', e.target.value)}>
                {HAIR_COLORS.map(v => <option key={v}>{v}</option>)}
              </select>
            </FormField>
          </div>

          <FormField label="Largo del cabello">
            <select className="select text-sm" value={params.hair_length} onChange={e => set('hair_length', e.target.value)}>
              {HAIR_LENGTHS.map(v => <option key={v}>{v}</option>)}
            </select>
          </FormField>

          <FormField label="Expresión">
            <select className="select text-sm" value={params.expression} onChange={e => set('expression', e.target.value)}>
              {EXPRESSIONS.map(v => <option key={v}>{v}</option>)}
            </select>
          </FormField>

          <button
            className="btn-primary w-full justify-center text-sm"
            onClick={handleGenerate}
            disabled={generating}
          >
            {generating
              ? <><Loader2 size={15} className="animate-spin" />Generando...</>
              : <><Wand2 size={15} />Generar 4 rostros</>
            }
          </button>

          {allDone && faces.some(f => f.status === 'done') && (
            <button
              className="btn-secondary w-full justify-center text-sm"
              onClick={handleGenerate}
              disabled={generating}
            >
              <RefreshCw size={14} />
              Regenerar
            </button>
          )}
        </div>

        {/* ── Right: Generated faces grid ───────────────────────────────── */}
        <div>
          {error && (
            <div className="flex items-start gap-3 bg-red-500/10 border border-red-500/30 rounded-xl p-4 mb-4 text-sm text-red-400">
              <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-semibold mb-0.5">Error de conexión con ComfyUI</p>
                <p className="text-red-400/70">{error}</p>
              </div>
            </div>
          )}

          {faces.length === 0 && !generating && (
            <div className="grid grid-cols-2 gap-3">
              {[1,2,3,4].map(i => (
                <div key={i} className="aspect-square rounded-xl bg-brand-surface border border-brand-border border-dashed flex items-center justify-center text-gray-700 text-xs">
                  Rostro {i}
                </div>
              ))}
            </div>
          )}

          {faces.length > 0 && (
            <>
              <div className="grid grid-cols-2 gap-3">
                {faces.map((face, i) => (
                  <FaceCard
                    key={face.id || i}
                    face={face}
                    index={i}
                    isSelected={selected === face.id}
                    onSelect={() => handleSelect(face)}
                  />
                ))}
              </div>

              {selected && (
                <div className="mt-5 flex items-center justify-between bg-green-500/10 border border-green-500/30 rounded-xl p-4">
                  <div className="flex items-center gap-2 text-green-400 text-sm font-medium">
                    <Check size={16} />
                    Rostro seleccionado. Lista para la Fase 2.
                  </div>
                  <button className="btn-primary text-sm py-2 px-4" onClick={handleAdvance}>
                    Fase 2 — Cuerpo
                    <ChevronRight size={14} />
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

// ── FaceCard ──────────────────────────────────────────────────────────────────
function FaceCard({ face, index, isSelected, onSelect }) {
  return (
    <button
      onClick={onSelect}
      disabled={face.status !== 'done'}
      className={`relative aspect-square rounded-xl overflow-hidden border-2 transition-all group ${
        isSelected
          ? 'border-brand-pink shadow-lg shadow-brand-pink/20'
          : face.status === 'done'
            ? 'border-brand-border hover:border-brand-pink/50 cursor-pointer'
            : 'border-brand-border cursor-not-allowed'
      }`}
    >
      {/* Image */}
      {face.url && (
        <img src={face.url} alt={`Rostro ${index + 1}`} className="w-full h-full object-cover" />
      )}

      {/* Loading overlay */}
      {(face.status === 'pending' || face.status === 'generating') && (
        <div className="absolute inset-0 bg-brand-surface flex flex-col items-center justify-center gap-2">
          <Loader2 size={24} className="animate-spin text-brand-pink" />
          <span className="text-gray-500 text-xs">
            {face.status === 'pending' ? 'En cola...' : 'Generando...'}
          </span>
        </div>
      )}

      {/* Error overlay */}
      {face.status === 'error' && (
        <div className="absolute inset-0 bg-brand-surface flex flex-col items-center justify-center gap-2">
          <AlertCircle size={24} className="text-red-400" />
          <span className="text-red-400/70 text-xs">Error</span>
        </div>
      )}

      {/* Selected badge */}
      {isSelected && (
        <div className="absolute top-2 right-2 w-6 h-6 rounded-full bg-brand-pink flex items-center justify-center">
          <Check size={12} className="text-white" />
        </div>
      )}

      {/* Index label */}
      <div className="absolute bottom-2 left-2 bg-black/60 text-white text-xs px-2 py-0.5 rounded-full">
        {index + 1}
      </div>

      {/* Select hover */}
      {face.status === 'done' && !isSelected && (
        <div className="absolute inset-0 bg-brand-pink/0 group-hover:bg-brand-pink/10 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
          <span className="bg-brand-pink text-white text-xs font-semibold px-3 py-1.5 rounded-full">
            Seleccionar
          </span>
        </div>
      )}
    </button>
  )
}

function FormField({ label, children }) {
  return (
    <div>
      <label className="label">{label}</label>
      {children}
    </div>
  )
}
