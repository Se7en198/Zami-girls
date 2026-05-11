import { useState, useEffect } from 'react'
import { Plus, ChevronRight, Calendar, Wand2, Check, Loader2, ImageIcon } from 'lucide-react'
import { supabase } from '../lib/supabase.js'

const DAYS   = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
const RATIOS = ['9:16','1:1','4:5','16:9']
const SLOTS  = [1, 2, 3]

export default function Phase4Content({ model, onAdvance }) {
  const [posts, setPosts]       = useState([])
  const [loading, setLoading]   = useState(true)
  const [week, setWeek]         = useState(1)
  const [editPost, setEditPost] = useState(null)

  useEffect(() => { loadPosts() }, [model.id, week])

  async function loadPosts() {
    setLoading(true)
    const { data } = await supabase
      .from('content_posts')
      .select('*')
      .eq('model_id', model.id)
      .eq('week_number', week)
      .order('day_of_week', { ascending: true })
    setPosts(data || [])
    setLoading(false)
  }

  async function savePost(post) {
    if (post.id) {
      await supabase.from('content_posts').update(post).eq('id', post.id)
    } else {
      await supabase.from('content_posts').insert({ ...post, model_id: model.id, week_number: week })
    }
    setEditPost(null)
    loadPosts()
  }

  async function approvePost(id) {
    await supabase.from('content_posts').update({ status: 'approved' }).eq('id', id)
    loadPosts()
  }

  // Group posts by day
  const byDay = DAYS.reduce((acc, _, i) => {
    acc[i + 1] = posts.filter(p => p.day_of_week === i + 1)
    return acc
  }, {})

  return (
    <div className="max-w-5xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white mb-1">Fase 4 — Calendario de Contenido</h2>
          <p className="text-gray-500 text-sm">Hasta 3 posts por día. Contenido consecuente y narrativa continua.</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Week selector */}
          <div className="flex items-center gap-2 bg-brand-surface border border-brand-border rounded-lg px-3 py-2">
            <Calendar size={14} className="text-gray-500" />
            <span className="text-sm text-white">Semana</span>
            <select
              className="bg-transparent text-brand-pink text-sm font-semibold focus:outline-none"
              value={week}
              onChange={e => setWeek(Number(e.target.value))}
            >
              {[1,2,3,4].map(w => <option key={w} value={w}>{w}</option>)}
            </select>
          </div>
          <button className="btn-primary text-sm" onClick={onAdvance}>
            Fase 5 <ChevronRight size={14} />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-gray-500 text-sm">Cargando calendario...</div>
      ) : (
        <div className="space-y-3">
          {DAYS.map((day, di) => (
            <DayRow
              key={day}
              day={day}
              dayNum={di + 1}
              posts={byDay[di + 1] || []}
              onAdd={() => setEditPost({ day_of_week: di + 1, slot: (byDay[di + 1]?.length || 0) + 1, status: 'pending' })}
              onEdit={post => setEditPost(post)}
              onApprove={approvePost}
            />
          ))}
        </div>
      )}

      {editPost && (
        <PostModal
          post={editPost}
          model={model}
          onSave={savePost}
          onClose={() => setEditPost(null)}
        />
      )}
    </div>
  )
}

function DayRow({ day, dayNum, posts, onAdd, onEdit, onApprove }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold text-white text-sm">{day}</h4>
        {posts.length < 3 && (
          <button onClick={onAdd} className="text-xs text-brand-pink hover:text-pink-400 flex items-center gap-1 transition-colors">
            <Plus size={12} /> Agregar post
          </button>
        )}
      </div>

      {posts.length === 0 ? (
        <p className="text-gray-700 text-xs">Sin contenido planificado.</p>
      ) : (
        <div className="space-y-2">
          {posts.map(post => (
            <PostRow key={post.id} post={post} onEdit={onEdit} onApprove={onApprove} />
          ))}
        </div>
      )}
    </div>
  )
}

function PostRow({ post, onEdit, onApprove }) {
  const statusColor = {
    pending:    'text-gray-500 bg-gray-500/10',
    approved:   'text-green-400 bg-green-400/10',
    generating: 'text-yellow-400 bg-yellow-400/10',
    done:       'text-blue-400 bg-blue-400/10',
    published:  'text-purple-400 bg-purple-400/10',
  }

  return (
    <div className="flex items-start gap-3 p-3 bg-brand-dark rounded-lg border border-brand-border">
      {post.image_url ? (
        <img src={post.image_url} alt="" className="w-10 h-10 rounded-lg object-cover flex-shrink-0" />
      ) : (
        <div className="w-10 h-10 rounded-lg bg-brand-muted flex items-center justify-center flex-shrink-0">
          <ImageIcon size={14} className="text-gray-600" />
        </div>
      )}

      <div className="flex-1 min-w-0">
        <p className="text-white text-xs font-medium truncate">{post.caption || '(sin caption)'}</p>
        <p className="text-gray-600 text-xs truncate mt-0.5">{post.description || post.image_prompt || ''}</p>
        <div className="flex items-center gap-2 mt-1.5">
          <span className="text-xs text-gray-600">{post.aspect_ratio || '9:16'}</span>
          <span className={`text-xs px-1.5 py-0.5 rounded ${statusColor[post.status] || statusColor.pending}`}>
            {post.status}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-1.5 flex-shrink-0">
        <button onClick={() => onEdit(post)} className="text-gray-600 hover:text-white text-xs transition-colors px-2 py-1 rounded hover:bg-brand-muted">
          Editar
        </button>
        {post.status === 'pending' && (
          <button onClick={() => onApprove(post.id)} className="text-green-400 hover:text-green-300 text-xs transition-colors px-2 py-1 rounded hover:bg-green-400/10">
            Aprobar
          </button>
        )}
      </div>
    </div>
  )
}

function PostModal({ post, model, onSave, onClose }) {
  const [form, setForm] = useState({
    caption: '', image_prompt: '', description: '', aspect_ratio: '9:16', ...post
  })

  function set(k, v) { setForm(f => ({ ...f, [k]: v })) }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-brand-surface border border-brand-border rounded-2xl w-full max-w-lg p-6">
        <h3 className="font-bold text-white mb-5">
          {post.id ? 'Editar post' : `Nuevo post — ${['','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo'][post.day_of_week]}`}
        </h3>

        <div className="space-y-4">
          <div>
            <label className="label">Caption</label>
            <textarea className="input resize-none text-sm" rows={3} value={form.caption} onChange={e => set('caption', e.target.value)} placeholder="Caption para Instagram..." />
          </div>
          <div>
            <label className="label">Descripción (qué hace la modelo)</label>
            <input className="input text-sm" value={form.description} onChange={e => set('description', e.target.value)} placeholder="Ej: La modelo está en la playa al atardecer..." />
          </div>
          <div>
            <label className="label">Prompt imagen (técnico)</label>
            <textarea className="input resize-none text-sm" rows={3} value={form.image_prompt} onChange={e => set('image_prompt', e.target.value)} placeholder="Hyperrealistic photo, beautiful woman, beach sunset..." />
          </div>
          <div>
            <label className="label">Aspect Ratio</label>
            <div className="flex gap-2">
              {RATIOS.map(r => (
                <button key={r} type="button" onClick={() => set('aspect_ratio', r)}
                  className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-all ${form.aspect_ratio === r ? 'border-brand-pink bg-brand-pink/10 text-brand-pink' : 'border-brand-border text-gray-500 hover:border-brand-muted'}`}>
                  {r}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button className="btn-secondary flex-1 justify-center text-sm" onClick={onClose}>Cancelar</button>
          <button className="btn-primary flex-1 justify-center text-sm" onClick={() => onSave(form)}>
            <Check size={14} /> Guardar
          </button>
        </div>
      </div>
    </div>
  )
}
