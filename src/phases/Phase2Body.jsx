import { Upload, Wand2 } from 'lucide-react'

// Phase 2: Body generation
// Workflow pending — user will share the body generation ComfyUI workflow
export default function Phase2Body({ model, onAdvance }) {
  const hasWorkflow = false // set true when workflow JSON is added

  if (!model.face_image_url) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-500 text-sm">Completa la Fase 1 primero y selecciona un rostro.</p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white mb-1">Fase 2 — Generación de Cuerpo</h2>
        <p className="text-gray-500 text-sm">
          Usará el rostro seleccionado como referencia para generar 4 tipos de cuerpo (voluptuosa, delgada, thick, etc.)
        </p>
      </div>

      {/* Face reference */}
      <div className="card mb-6 flex items-center gap-4">
        <img src={model.face_image_url} alt="Rostro" className="w-16 h-16 rounded-xl object-cover border border-brand-border" />
        <div>
          <p className="text-sm font-medium text-white">Rostro de referencia</p>
          <p className="text-xs text-gray-500">Este rostro se usará para generar el cuerpo completo</p>
        </div>
      </div>

      {hasWorkflow ? (
        <div className="card">
          <p className="text-gray-400 text-sm">Workflow cargado. Listo para generar.</p>
        </div>
      ) : (
        <div className="card border-dashed text-center py-16">
          <Upload size={32} className="text-gray-700 mx-auto mb-3" />
          <p className="text-gray-400 font-medium mb-1">Workflow de cuerpo pendiente</p>
          <p className="text-gray-600 text-sm">
            Comparte el workflow de ComfyUI para generación de cuerpo y lo integro de inmediato.
          </p>
        </div>
      )}
    </div>
  )
}
