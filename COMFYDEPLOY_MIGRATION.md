# Migración de RunPod/ComfyUI a ComfyDeploy

Este documento define un plan operativo y técnico para migrar la generación de imágenes del proyecto **Zami Girls** hacia **ComfyDeploy** sin romper el flujo actual de producto.

> Objetivo: mantener la UX actual (generar 4 rostros, seleccionar uno, guardar en Supabase) cambiando el motor de ejecución a ComfyDeploy de forma robusta, auditable y con rollback.

---

## 1) Alcance y criterios de éxito

### Alcance (Fase 1)
- Migrar la **Fase 1 (rostro)** completa a ComfyDeploy.
- Mantener el flujo de persistencia en `phase_images` y selección en `models.face_image_url`.
- Mantener soporte de ejecución en paralelo (4 jobs).

### Éxito funcional
- El botón "Generar 4 rostros" produce 4 resultados reales.
- Se guardan 4 filas en `phase_images` con estado correcto.
- Se puede seleccionar una imagen y avanzar a Fase 2.
- Error handling visible al usuario (timeout, failed run, rate limit).

### Éxito operativo
- Sin secretos expuestos en el frontend.
- Webhook operativo + fallback polling.
- Logs suficientes para depuración (`run_id`, estado, tiempos).

---

## 2) Arquitectura objetivo

## Flujo recomendado
1. Frontend envía solicitud de generación (4 variantes).
2. API interna/proxy (Supabase Edge Function o backend) llama **ComfyDeploy Queue Run**.
3. ComfyDeploy devuelve `run_id` inmediato.
4. Se persiste `run_id` por variante en DB.
5. ComfyDeploy notifica por webhook cambios de estado.
6. Frontend (o backend) usa polling de respaldo para estado final.
7. Al completar, se transforma output a formato que consume la UI y se guarda en `phase_images`.

### Principios
- **Asíncrono first**: nunca depender de una request larga única.
- **Idempotencia**: no duplicar insert/update por eventos repetidos.
- **Observabilidad**: registrar transición de estados por `run_id`.

---

## 3) Mapeo conceptual RunPod -> ComfyDeploy

| Concepto actual | ComfyDeploy equivalente |
|---|---|
| submit `/run` | queue run (deployment) |
| poll `/status/{id}` | get run `{run_id}` |
| output.images base64 | output de run (normalizar) |
| proxy propio | backend/proxy para token ComfyDeploy |
| `comfyui_prompt_id` | `comfydeploy_run_id` (puede reutilizarse columna existente temporalmente) |

> Recomendación: crear columna nueva `provider_run_id` + `provider` para no acoplarse a nombres históricos.

---

## 4) Preparación de infraestructura

## 4.1 ComfyDeploy
1. Crear cuenta/proyecto en ComfyDeploy.
2. Publicar deployment del workflow de rostro (importar JSON probado de `src/workflows/face-generation.json`).
3. Definir y probar inputs esperados (semilla, rasgos faciales, prompt libre, etc.).
4. Configurar API key para servidor/proxy (no frontend).
5. Configurar webhook endpoint de estado de runs.

## 4.2 Supabase
1. Crear/ajustar Edge Function para proxy de ComfyDeploy (nuevo archivo sugerido: `supabase/functions/comfydeploy-proxy/index.ts`).
2. Guardar secretos:
   - `COMFYDEPLOY_API_KEY`
   - `COMFYDEPLOY_DEPLOYMENT_ID`
   - opcional: `COMFYDEPLOY_WEBHOOK_SECRET`
3. Definir tabla o columnas para tracking de runs:
   - `provider` (runpod/comfydeploy)
   - `provider_run_id`
   - `provider_status`
   - `provider_payload` (jsonb opcional)

---

## 5) Cambios de código en este repo (paso a paso)

## 5.1 Crear cliente ComfyDeploy
- Crear `src/api/comfydeploy.js` con funciones:
  - `queueComfyDeployRun(inputs, jobName)`
  - `getComfyDeployRun(runId)`
  - `waitForComfyDeployResult(runId, opts)`
  - `normalizeComfyDeployOutput(output)`

### Reglas del cliente
- El cliente de frontend **no** debe llevar API key de ComfyDeploy.
- Llamar siempre a proxy interno (Supabase function o backend).
- Manejar errores por categoría: auth, rate limit, timeout, failed.

## 5.2 Actualizar `src/phases/Phase1Face.jsx`
- Sustituir llamadas a RunPod por cliente ComfyDeploy.
- Mantener patrón actual de 4 jobs paralelos.
- Guardar en DB:
  - `provider = 'comfydeploy'`
  - `provider_run_id = run_id`
  - URL final normalizada para `image_url`.

## 5.3 Webhook receptor (servidor)
- Crear endpoint receptor de webhook:
  - valida firma/secret si aplica.
  - upsert de estado por `provider_run_id`.
  - evita duplicados (idempotencia por evento + run_id).

## 5.4 Polling fallback
- Si webhook tarda o falla, `waitForComfyDeployResult` consulta estado cada N segundos.
- Timeout configurable (ej. 8–10 min para cold starts/picos).

## 5.5 Feature flag de migración
- Añadir `VITE_IMAGE_PROVIDER=runpod|comfydeploy`.
- Permitir rollback instantáneo sin revertir código.

---

## 6) Modelo de datos recomendado

Agregar migración SQL (ejemplo):

```sql
alter table phase_images
  add column if not exists provider text,
  add column if not exists provider_run_id text,
  add column if not exists provider_status text,
  add column if not exists provider_payload jsonb;

create index if not exists idx_phase_images_provider_run_id
  on phase_images(provider_run_id);
```

Opcional: tabla separada `generation_runs` para historial completo.

---

## 7) Seguridad

- Nunca exponer `COMFYDEPLOY_API_KEY` en frontend.
- Usar solo secreto de servidor/proxy.
- Limitar CORS en proxy según dominios reales de dashboard.
- Registrar errores sin filtrar secretos.
- Si hay webhook secret, validarlo siempre antes de procesar eventos.

---

## 8) Estrategia de pruebas (obligatoria)

## 8.1 Smoke tests
1. Queue run simple y obtener `run_id`.
2. Consultar estado hasta `COMPLETED`.
3. Verificar que output se persiste en `phase_images`.

## 8.2 E2E de producto
1. Generar 4 rostros desde dashboard.
2. Confirmar 4 tarjetas finalizadas.
3. Seleccionar una imagen y confirmar persistencia en `models.face_image_url`.

## 8.3 Casos de falla
- API key inválida.
- Rate limit.
- Timeout de run.
- Webhook no disponible (debe funcionar polling fallback).

## 8.4 Criterio de aprobación
- 10 ejecuciones consecutivas sin error crítico.
- Tiempo medio dentro del umbral esperado para UX.

---

## 9) Plan de rollout

### Fase A (shadow mode)
- Ejecutar ComfyDeploy en paralelo (sin mostrar al usuario), solo para comparar outputs/latencia.

### Fase B (canary)
- 10–20% del tráfico a ComfyDeploy vía feature flag.

### Fase C (full)
- 100% ComfyDeploy, mantener RunPod como fallback temporal 1–2 semanas.

### Fase D (decomisión)
- Eliminar rutas y secretos RunPod cuando métricas sean estables.

---

## 10) Plan de rollback

- Si hay degradación:
  1. cambiar `VITE_IMAGE_PROVIDER=runpod`,
  2. redeploy frontend,
  3. mantener procesamiento de runs en curso hasta cierre.

- No borrar datos de `provider_run_id`; sirven para auditoría postmortem.

---

## 11) Lista de tareas ejecutables para una IA/agente

1. Crear `src/api/comfydeploy.js` con queue/get/poll/normalize.
2. Crear `supabase/functions/comfydeploy-proxy/index.ts`.
3. Crear receptor de webhook (si es función separada).
4. Añadir migración SQL para columnas `provider_*`.
5. Actualizar `src/phases/Phase1Face.jsx` con feature flag.
6. Añadir script de smoke test `test-comfydeploy-latina.py`.
7. Documentar `.env` nuevos en `SERVERLESS_SETUP.md` y `CONTEXT.md`.
8. Ejecutar build + smoke tests + reporte final.

---

## 12) Variables de entorno sugeridas

```env
# Selector de proveedor
VITE_IMAGE_PROVIDER=comfydeploy

# Supabase frontend
VITE_SUPABASE_URL=...
VITE_SUPABASE_ANON_KEY=...

# ComfyDeploy (SOLO servidor/proxy)
COMFYDEPLOY_API_KEY=...
COMFYDEPLOY_DEPLOYMENT_ID=...
COMFYDEPLOY_WEBHOOK_SECRET=... # opcional
```

---

## 13) Riesgos y mitigaciones

- **Riesgo:** diferencias de output vs RunPod.
  - Mitigación: shadow mode + comparación cuantitativa/cualitativa.

- **Riesgo:** rate limits.
  - Mitigación: backoff exponencial + cola interna + canary.

- **Riesgo:** webhook caído.
  - Mitigación: polling fallback e idempotencia.

- **Riesgo:** lock-in proveedor.
  - Mitigación: capa `provider client` + feature flag.

---

## 14) Definición de “migración completa y funcional”

La migración se considera completa cuando:
1. Fase 1 opera en ComfyDeploy al 100% del tráfico.
2. Webhook + polling fallback activos.
3. Sin secretos en frontend.
4. Métricas estables por 7 días.
5. Rollback probado y documentado.

---

## 15) Notas para próximos agentes

- Este documento es la guía principal de ejecución.
- Si hay discrepancias entre código y docs, priorizar:
  1) seguridad de secretos,
  2) estabilidad de runs,
  3) trazabilidad de estados.
- Mantener cambios incrementales y con feature flag para evitar downtime.
