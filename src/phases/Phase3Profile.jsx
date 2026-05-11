import { useState } from 'react'
import { Sparkles, Save, Check } from 'lucide-react'
import { supabase } from '../lib/supabase.js'

// Full AI Persona Template fields
const SECTIONS = [
  {
    title: 'Alias',
    fields: [
      { key: 'stage_name',     label: 'Nombre artístico',     type: 'text' },
      { key: 'real_name',      label: 'Nombre real (fans)',   type: 'text' },
      { key: 'handle',         label: 'Username / @handle',   type: 'text' },
      { key: 'nickname',       label: 'Apodos',               type: 'text' },
      { key: 'age',            label: 'Edad',                 type: 'number' },
      { key: 'birthday',       label: 'Cumpleaños',           type: 'text' },
      { key: 'zodiac',         label: 'Signo zodiacal',       type: 'text' },
    ],
  },
  {
    title: 'Medidas & Apariencia',
    fields: [
      { key: 'height',         label: 'Altura',               type: 'text' },
      { key: 'weight',         label: 'Peso',                 type: 'text' },
      { key: 'cup_size',       label: 'Talla de copa',        type: 'text' },
      { key: 'measurements',   label: 'Medidas (B-C-H)',      type: 'text' },
      { key: 'shoe_size',      label: 'Talla zapatos',        type: 'text' },
      { key: 'hair',           label: 'Cabello (color/estilo)',type: 'text' },
      { key: 'eyes',           label: 'Color de ojos',        type: 'text' },
      { key: 'skin_tone',      label: 'Tono de piel',         type: 'text' },
      { key: 'features',       label: 'Rasgos distintos',     type: 'text' },
    ],
  },
  {
    title: 'Origen & Ubicación',
    fields: [
      { key: 'ethnicity',      label: 'Etnia',                type: 'text' },
      { key: 'hometown',       label: 'Ciudad natal (fans)',  type: 'text' },
      { key: 'location',       label: 'Ubicación actual',     type: 'text' },
      { key: 'known_from',     label: 'De dónde la conocen',  type: 'textarea' },
    ],
  },
  {
    title: 'Estilo de Vida',
    fields: [
      { key: 'pets',           label: 'Mascotas',             type: 'text' },
      { key: 'day_job',        label: 'Trabajo de día',       type: 'text' },
      { key: 'family',         label: 'Contexto familiar',    type: 'textarea' },
    ],
  },
  {
    title: 'Favoritos',
    fields: [
      { key: 'fav_food',       label: 'Comida favorita',      type: 'text' },
      { key: 'fav_restaurant', label: 'Restaurante favorito', type: 'text' },
      { key: 'fav_drink',      label: 'Bebida favorita',      type: 'text' },
      { key: 'cheat_meal',     label: 'Comida trampa',        type: 'text' },
    ],
  },
  {
    title: 'Vibe Musical',
    fields: [
      { key: 'music_genres',   label: 'Géneros musicales',    type: 'text' },
      { key: 'top_artists',    label: 'Artistas favoritos',   type: 'text' },
      { key: 'mood_song',      label: 'Canción de estado',    type: 'text' },
    ],
  },
  {
    title: 'Hobbies & Hábitos',
    fields: [
      { key: 'hobbies',        label: 'Hobbies (3–5)',        type: 'textarea' },
      { key: 'secret_talent',  label: 'Talento secreto',      type: 'text' },
    ],
  },
  {
    title: 'Huella Digital',
    fields: [
      { key: 'emojis',         label: 'Emojis más usados',    type: 'text' },
      { key: 'phrases',        label: 'Frases / jerga',       type: 'textarea' },
      { key: 'typing_style',   label: 'Estilo de escritura',  type: 'text' },
    ],
  },
  {
    title: 'Personalidad & Nicho',
    fields: [
      { key: 'content_niche',  label: 'Nicho de contenido',   type: 'text' },
      { key: 'rep_style',      label: 'Estilo de representación', type: 'text' },
      { key: 'themes',         label: 'Temas recurrentes',    type: 'text' },
      { key: 'fan_traits',     label: 'Rasgos favoritos de fans', type: 'textarea' },
      { key: 'three_words',    label: '3 palabras que la definen', type: 'text' },
      { key: 'flirt_level',    label: 'Nivel de coqueteo',    type: 'text' },
      { key: 'archetype',      label: 'Arquetipo (ej: femme fatale)', type: 'text' },
      { key: 'fantasy',        label: 'Fantasía principal que encarna', type: 'textarea' },
    ],
  },
]

export default function Phase3Profile({ model, onAdvance }) {
  const [profile, setProfile] = useState({})
  const [saving, setSaving]   = useState(false)
  const [saved, setSaved]     = useState(false)
  const [loaded, setLoaded]   = useState(false)

  // Load existing profile
  useState(() => {
    loadProfile()
  })

  async function loadProfile() {
    if (loaded) return
    setLoaded(true)
    const { data } = await supabase
      .from('model_profiles')
      .select('content')
      .eq('model_id', model.id)
      .single()
    if (data?.content) setProfile(data.content)
  }

  function set(key, val) {
    setProfile(p => ({ ...p, [key]: val }))
    setSaved(false)
  }

  async function handleSave() {
    setSaving(true)
    await supabase
      .from('model_profiles')
      .upsert({ model_id: model.id, content: profile, updated_at: new Date().toISOString() },
               { onConflict: 'model_id' })
    setSaving(false)
    setSaved(true)
  }

  return (
    <div className="max-w-3xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white mb-1">Fase 3 — Perfil del Personaje</h2>
          <p className="text-gray-500 text-sm">Perfil psicológico completo de <strong className="text-white">{model.name}</strong></p>
        </div>
        <div className="flex gap-3">
          <button className="btn-secondary text-sm" onClick={handleSave} disabled={saving}>
            {saved ? <><Check size={14} />Guardado</> : <><Save size={14} />{saving ? 'Guardando...' : 'Guardar'}</>}
          </button>
          <button className="btn-primary text-sm" onClick={onAdvance}>
            <Sparkles size={14} />
            Fase 4
          </button>
        </div>
      </div>

      {/* Reference images */}
      <div className="flex gap-3 mb-6">
        {model.face_image_url && (
          <img src={model.face_image_url} alt="Rostro" className="w-16 h-16 rounded-xl object-cover border border-brand-border" />
        )}
        {model.body_image_url && (
          <img src={model.body_image_url} alt="Cuerpo" className="w-16 h-16 rounded-xl object-cover border border-brand-border" />
        )}
      </div>

      <div className="space-y-6">
        {SECTIONS.map(section => (
          <div key={section.title} className="card">
            <h3 className="font-semibold text-white text-sm mb-4 border-b border-brand-border pb-3">{section.title}</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {section.fields.map(f => (
                <div key={f.key} className={f.type === 'textarea' ? 'sm:col-span-2' : ''}>
                  <label className="label">{f.label}</label>
                  {f.type === 'textarea' ? (
                    <textarea
                      className="input resize-none text-sm"
                      rows={3}
                      value={profile[f.key] || ''}
                      onChange={e => set(f.key, e.target.value)}
                    />
                  ) : (
                    <input
                      type={f.type}
                      className="input text-sm"
                      value={profile[f.key] || ''}
                      onChange={e => set(f.key, e.target.value)}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
