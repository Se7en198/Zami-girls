import { useState, useEffect } from 'react'
import { Upload, BarChart2, TrendingUp, TrendingDown, Minus, FileText } from 'lucide-react'
import { supabase } from '../lib/supabase.js'

export default function Phase6KPI({ model }) {
  const [reports, setReports] = useState([])
  const [uploading, setUploading] = useState(false)
  const [rawData, setRawData] = useState('')
  const [analysis, setAnalysis] = useState(null)

  useEffect(() => { loadReports() }, [model.id])

  async function loadReports() {
    const { data } = await supabase
      .from('kpi_reports')
      .select('*')
      .eq('model_id', model.id)
      .order('created_at', { ascending: false })
    setReports(data || [])
  }

  async function handleCSV(e) {
    const file = e.target.files[0]
    if (!file) return
    setUploading(true)
    const text = await file.text()
    setRawData(text)
    setUploading(false)
  }

  async function analyzeData() {
    if (!rawData.trim()) return
    // Save raw report to DB; analysis will be added when Claude API is available
    const { data } = await supabase
      .from('kpi_reports')
      .insert({
        model_id: model.id,
        report_date: new Date().toISOString().split('T')[0],
        analysis: { raw_csv: rawData, status: 'pending' },
      })
      .select()
      .single()

    if (data) {
      setAnalysis({ status: 'pending', message: 'Datos guardados. El análisis automático estará disponible cuando se configure la API de Claude.' })
      loadReports()
    }
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white mb-1">Fase 6 — Análisis de KPIs</h2>
        <p className="text-gray-500 text-sm">
          Sube los datos de Meta Business Suite para analizar el rendimiento de <strong className="text-white">{model.name}</strong>.
        </p>
      </div>

      {/* Upload area */}
      <div className="card mb-6">
        <h3 className="font-semibold text-white text-sm mb-4">Subir datos de Meta</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* CSV */}
          <label className="border-2 border-dashed border-brand-border rounded-xl p-6 flex flex-col items-center gap-3 cursor-pointer hover:border-brand-pink/50 transition-colors group">
            <input type="file" className="hidden" accept=".csv" onChange={handleCSV} />
            <div className="w-10 h-10 rounded-xl bg-brand-dark flex items-center justify-center group-hover:bg-brand-pink/10 transition-colors">
              <BarChart2 size={20} className="text-gray-600 group-hover:text-brand-pink transition-colors" />
            </div>
            <div className="text-center">
              <p className="text-white text-sm font-medium">CSV de Meta Business Suite</p>
              <p className="text-gray-600 text-xs mt-0.5">Descarga desde Meta → Insights → Exportar</p>
            </div>
          </label>

          {/* Manual / PDF */}
          <label className="border-2 border-dashed border-brand-border rounded-xl p-6 flex flex-col items-center gap-3 cursor-pointer hover:border-brand-pink/50 transition-colors group">
            <div className="w-10 h-10 rounded-xl bg-brand-dark flex items-center justify-center group-hover:bg-brand-pink/10 transition-colors">
              <FileText size={20} className="text-gray-600 group-hover:text-brand-pink transition-colors" />
            </div>
            <div className="text-center">
              <p className="text-white text-sm font-medium">Pegar datos manualmente</p>
              <p className="text-gray-600 text-xs mt-0.5">Copia y pega los números de Meta</p>
            </div>
          </label>
        </div>

        {rawData && (
          <div className="mt-4">
            <label className="label">Vista previa de datos</label>
            <pre className="bg-brand-dark border border-brand-border rounded-lg p-3 text-xs text-gray-400 overflow-x-auto max-h-40">
              {rawData.slice(0, 800)}{rawData.length > 800 ? '\n...' : ''}
            </pre>
            <button className="btn-primary text-sm mt-3" onClick={analyzeData}>
              <BarChart2 size={14} />
              Analizar resultados
            </button>
          </div>
        )}

        {/* Manual textarea */}
        {!rawData && (
          <div className="mt-4">
            <textarea
              className="input resize-none text-sm mt-2"
              rows={5}
              placeholder="Pega aquí métricas manuales: alcance, impresiones, engagement rate, seguidores ganados, mejores posts..."
              value={rawData}
              onChange={e => setRawData(e.target.value)}
            />
            {rawData.trim() && (
              <button className="btn-primary text-sm mt-3" onClick={analyzeData}>
                <BarChart2 size={14} />
                Analizar resultados
              </button>
            )}
          </div>
        )}
      </div>

      {/* Analysis result */}
      {analysis && (
        <div className="card border-brand-pink/20 bg-brand-pink/5">
          <p className="text-brand-pink text-sm">{analysis.message}</p>
        </div>
      )}

      {/* Past reports */}
      {reports.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-white text-sm mb-4">Reportes anteriores</h3>
          <div className="space-y-2">
            {reports.map(r => (
              <div key={r.id} className="flex items-center justify-between p-3 bg-brand-dark rounded-lg border border-brand-border">
                <div>
                  <p className="text-white text-sm font-medium">{r.report_date}</p>
                  <p className="text-gray-600 text-xs mt-0.5">{r.analysis?.status || 'Sin analizar'}</p>
                </div>
                <span className="text-xs text-gray-600">
                  {new Date(r.created_at).toLocaleDateString('es-CO')}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
