# CONTEXT — Zami Girls: Estado del proyecto para continuar con IA

> **Lee esto primero.** Este documento describe exactamente en qué punto está el proyecto, qué funciona, qué falta, y qué hacer a continuación. Úsalo para ponerte en contexto antes de trabajar con el usuario.

---

## ¿Qué es este proyecto?

**Zami Girls** es un estudio de influencers virtuales latinas generado con IA.  
El flujo tiene 6 fases: Rostro → Cuerpo → Perfil → Contenido → Respuestas → KPIs.

Stack:
- **Frontend**: React + Vite + Tailwind (dashboard en `src/`)
- **Backend IA**: ComfyUI + AION Portrait Master corriendo en RunPod Serverless
- **Base de datos**: Supabase (PostgreSQL)
- **Almacenamiento**: Imágenes como data URIs en Supabase `phase_images`
- **Repo**: https://github.com/Se7en198/Zami-girls

---

## Estado actual por fase

| Fase | Nombre | Estado |
|------|--------|--------|
| 1 | Generación de Rostro | ✅ Código listo, pendiente anon key Supabase en `.env` |
| 2 | Cuerpo | ⏳ UI existe, workflow `body-generation.json` existe, sin integrar a RunPod |
| 3–6 | Perfil, Contenido, Respuestas, KPIs | ⏳ UI placeholder |

---

## Infraestructura RunPod Serverless

### Endpoint activo (Fase 1 — Rostros)
- **Endpoint ID**: `aqzsu0jydlras1`
- **Worker**: `comfyui-aion-creador-de-rostros-con-nano-banana-pro`
- **GPU**: 24 GB AMPERE
- **Workflow**: `src/workflows/face-generation.json`
- **Worker code**: `serverless/handler.py` + `serverless/Dockerfile`

### API RunPod Serverless
```
POST https://api.runpod.ai/v2/aqzsu0jydlras1/run
Authorization: Bearer {VITE_RUNPOD_API_KEY}
Body: { "input": { "workflow": {...}, "job_name": "face_1" } }
→ { "id": "job-xxx", "status": "IN_QUEUE" }

GET https://api.runpod.ai/v2/aqzsu0jydlras1/status/{job_id}
Authorization: Bearer {VITE_RUNPOD_API_KEY}
→ COMPLETED → { "output": { "images": ["base64..."], "count": 1 } }
```

### ⚠️ Problema de IP (resuelto para browser, pendiente para servidor)
RunPod bloquea IPs de data centers con 403. El browser del usuario (IP residencial) puede llamar RunPod directamente. Claude Code (servidor Anthropic) NO puede.

**Solución implementada**: Supabase Edge Function `runpod-proxy` como proxy intermedio.
- Código: `supabase/functions/runpod-proxy/index.ts` ✅ (en repo)
- Deploy en Supabase: ❌ **PENDIENTE**

---

## Archivos clave

| Archivo | Función |
|---------|---------|
| `src/api/runpod.js` | Cliente RunPod: submit, poll, base64→dataURL. Variante vía proxy Supabase. |
| `src/api/comfyui.js` | Cliente legacy ComfyUI. `buildFaceWorkflow()` se reutiliza para construir workflows. |
| `src/phases/Phase1Face.jsx` | UI Fase 1. Llama `runFaceJob()` x4 en paralelo. |
| `src/lib/supabase.js` | Cliente Supabase (usa `VITE_SUPABASE_URL` + `VITE_SUPABASE_ANON_KEY`) |
| `src/workflows/face-generation.json` | Workflow ComfyUI para rostros (nodo 82=AION, 78=seed, 14=noise, 73=variance) |
| `src/workflows/body-generation.json` | Workflow para cuerpo (Fase 2, sin integrar aún) |
| `serverless/handler.py` | Worker RunPod: recibe workflow, ejecuta ComfyUI, devuelve base64 |
| `supabase/functions/runpod-proxy/index.ts` | Edge Function proxy: reenvía calls a RunPod desde IPs no bloqueadas |
| `supabase/schema.sql` | Schema de Supabase |
| `test-serverless.py` | Script Python para testear el endpoint directamente |

---

## Variables de entorno necesarias (`.env` local — nunca commitear)

```env
# RunPod (ya configurado en .env local)
VITE_RUNPOD_API_KEY=<ver con el usuario — está en su .env local>
VITE_RUNPOD_ENDPOINT_ID=aqzsu0jydlras1

# Supabase — PENDIENTE añadir al .env local
VITE_SUPABASE_URL=https://vtyuylgfjvleywupbdzl.supabase.co
VITE_SUPABASE_ANON_KEY=<obtener de: Supabase Dashboard → Settings → API → "anon public">
```

---

## Supabase

- **Project URL**: `https://vtyuylgfjvleywupbdzl.supabase.co`
- **Project Ref**: `vtyuylgfjvleywupbdzl`
- Tabla principal: `phase_images` (ver `supabase/schema.sql`)
- Las imágenes se guardan como data URIs en `phase_images.image_url`

---

## Lo que falta hacer (en orden de prioridad)

### 1. INMEDIATO — Añadir anon key de Supabase al `.env` local
El usuario debe añadir al archivo `.env` en la raíz del proyecto:
```
VITE_SUPABASE_URL=https://vtyuylgfjvleywupbdzl.supabase.co
VITE_SUPABASE_ANON_KEY=<copiar de Supabase Dashboard → Settings → API → "anon public">
```
Con esto el dashboard funciona al 100% desde el browser.

**Dónde ir**: https://supabase.com/dashboard/project/vtyuylgfjvleywupbdzl/settings/api

### 2. Deploy Supabase Edge Function (una sola vez)
El proxy `runpod-proxy` ya tiene su código en el repo. Falta desplegarlo:
```bash
supabase login
supabase link --project-ref vtyuylgfjvleywupbdzl
supabase functions deploy runpod-proxy --no-verify-jwt
supabase secrets set RUNPOD_API_KEY=<la api key de runpod>
supabase secrets set RUNPOD_ENDPOINT_ID=aqzsu0jydlras1
```
Esto activa la automatización desde el servidor (Claude Code → Supabase → RunPod).

### 3. Integrar Fase 2 (Cuerpo) a RunPod Serverless
- Workflow: `src/workflows/body-generation.json`
- UI: `src/phases/Phase2Body.jsx`
- Mismo patrón que Fase 1: `runFaceJob()` → `b64ToDataUrl()` → guardar en Supabase

### 4. Fases 3–6
- Definir qué genera cada fase
- Implementar siguiendo el mismo patrón de Fase 1

---

## Flujo de datos — Fase 1 (implementado)

```
Usuario → "Generar 4 rostros"
  → Phase1Face.jsx
    → buildFaceWorkflow(baseWorkflow, params) → workflow JSON con seeds aleatorios
    → [×4 en paralelo] runFaceJob(workflow, jobName)
      → POST api.runpod.ai/v2/aqzsu0jydlras1/run → job_id
      → poll /status/{job_id} cada 4s
      → COMPLETED → output.images[0] (base64)
    → b64ToDataUrl(base64) → "data:image/png;base64,..."
    → supabase.phase_images.insert({ image_url: dataUrl, ... })
    → Mostrar en FaceCard
```

---

## Rama de trabajo activa

- **Branch**: `claude/plan-runpod-deployment-UjZRF`
- **PR**: https://github.com/Se7en198/Zami-girls/pull/1
- Hacer merge a `main` cuando todo esté probado y funcionando

---

## Cómo pedirle a la IA que continúe

Empieza la conversación así:

> "Lee el archivo CONTEXT.md en el repositorio https://github.com/Se7en198/Zami-girls y continúa desde donde está el proyecto. El usuario no sabe de código — tú tomas el control y haces todo."

La IA debe leer este archivo, entender el estado, y continuar sin que tengas que explicar nada.
