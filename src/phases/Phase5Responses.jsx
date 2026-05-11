import { useState, useEffect } from 'react'
import { Plus, Trash2, Save, Check, ChevronRight, MessageCircle } from 'lucide-react'
import { supabase } from '../lib/supabase.js'

const EXAMPLE_COMMENTS = [
  'OMG you are so beautiful! 😍',
  'Where did you get that outfit?',
  'Can we collab?',
  'You\'re fake / AI',
  'Love your energy!',
  'What\'s your workout routine?',
  'Will you post more content like this?',
  'I\'ve been following you since day 1 ❤️',
  'Where are you from?',
  'You remind me of [celebrity name]',
]

export default function Phase5Responses({ model, onAdvance }) {
  const [responses, setResponses] = useState([])
  const [saving, setSaving]       = useState(false)
  const [saved, setSaved]         = useState(false)

  useEffect(() => { loadResponses() }, [model.id])

  async function loadResponses() {
    const { data } = await supabase
      .from('community_responses')
      .select('*')
      .eq('model_id', model.id)
      .order('created_at')
    setResponses(data?.length ? data : EXAMPLE_COMMENTS.slice(0, 5).map((c, i) => ({
      id: `temp-${i}`,
      comment_example: c,
      response_example: '',
    })))
  }

  function addRow() {
    setResponses(r => [...r, { id: `new-${Date.now()}`, comment_example: '', response_example: '' }])
  }

  function update(id, key, val) {
    setResponses(r => r.map(x => x.id === id ? { ...x, [key]: val } : x))
    setSaved(false)
  }

  function remove(id) {
    setResponses(r => r.filter(x => x.id !== id))
  }

  async function handleSave() {
    setSaving(true)
    // Delete all and re-insert
    await supabase.from('community_responses').delete().eq('model_id', model.id)
    const rows = responses
      .filter(r => r.comment_example.trim() && r.response_example.trim())
      .map(r => ({ model_id: model.id, comment_example: r.comment_example, response_example: r.response_example }))
    if (rows.length) await supabase.from('community_responses').insert(rows)
    setSaving(false)
    setSaved(true)
  }

  return (
    <div className="max-w-3xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white mb-1">Fase 5 — Respuestas a Comunidad</h2>
          <p className="text-gray-500 text-sm">
            10 ejemplos de cómo respondería <strong className="text-white">{model.name}</strong> a sus seguidores. Siempre en personaje.
          </p>
        </div>
        <div className="flex gap-3">
          <button className="btn-secondary text-sm" onClick={handleSave} disabled={saving}>
            {saved ? <><Check size={14} />Guardado</> : <><Save size={14} />{saving ? 'Guardando...' : 'Guardar'}</>}
          </button>
          <button className="btn-primary text-sm" onClick={onAdvance}>
            Fase 6 <ChevronRight size={14} />
          </button>
        </div>
      </div>

      <div className="card mb-4 flex items-start gap-3">
        <MessageCircle size={16} className="text-brand-pink mt-0.5 flex-shrink-0" />
        <p className="text-gray-400 text-sm">
          Cada respuesta debe reflejar el tono, personalidad y nicho de <strong className="text-white">{model.name}</strong>.
          Nicho: <span className="text-brand-pink">{model.niche}</span>. Nunca salir del personaje.
        </p>
      </div>

      <div className="space-y-3">
        {/* Header */}
        <div className="grid grid-cols-2 gap-3 px-1">
          <span className="text-xs text-gray-600 font-medium uppercase tracking-wider">Comentario del seguidor</span>
          <span className="text-xs text-gray-600 font-medium uppercase tracking-wider">Respuesta de {model.name}</span>
        </div>

        {responses.map((r, i) => (
          <div key={r.id} className="grid grid-cols-2 gap-3 items-start">
            <div className="relative">
              <span className="absolute left-3 top-2.5 text-xs text-gray-700 font-bold">{i + 1}.</span>
              <textarea
                className="input pl-7 resize-none text-sm"
                rows={2}
                placeholder="Comentario ejemplo..."
                value={r.comment_example}
                onChange={e => update(r.id, 'comment_example', e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <textarea
                className="input flex-1 resize-none text-sm"
                rows={2}
                placeholder={`Cómo respondería ${model.name}...`}
                value={r.response_example}
                onChange={e => update(r.id, 'response_example', e.target.value)}
              />
              <button
                onClick={() => remove(r.id)}
                className="text-gray-700 hover:text-red-400 transition-colors mt-2 flex-shrink-0"
              >
                <Trash2 size={14} />
              </button>
            </div>
          </div>
        ))}
      </div>

      {responses.length < 10 && (
        <button onClick={addRow} className="btn-secondary mt-4 text-sm">
          <Plus size={14} />
          Agregar ejemplo ({responses.length}/10)
        </button>
      )}
    </div>
  )
}
