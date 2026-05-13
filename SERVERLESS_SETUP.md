# Estado de la Migración a RunPod Serverless (12 Mayo 2026)

Este documento resume los avances realizados para mover la infraestructura de "Zami Girls" de un Pod persistente a un esquema **Serverless** (Scale-to-Zero).

## 🚀 Infraestructura Actual

| Componente | Detalle |
|------------|---------|
| **Endpoint ID** | `aqzsu0jydlras1` |
| **Worker Repo** | [Se7en198/comfyui-aion-creador-de-rostros-con-nano-banana-pro](https://github.com/Se7en198/comfyui-aion-creador-de-rostros-con-nano-banana-pro) |
| **GPU Config** | 24 GB (High Supply - AMPERE_24) |
| **Estado** | Build completado, Endpoint activo. |
| **API Key** | `[REDACTED_CHECK_DOTENV]` |

## 🛠️ Cambios Realizados

1. **Migración de Workflow**: Se utilizó `comfy.getrunpod.io` para analizar el workflow `face-generation.json`.
2. **Generación de Worker**: Se creó un repositorio dedicado para el worker serverless que ya incluye los modelos (baked-in) y los custom nodes necesarios.
3. **Despliegue de Endpoint**: Se configuró el endpoint en RunPod apuntando al nuevo repositorio de GitHub.
4. **Actualización de README**: Se eliminó la referencia al daemon de polling (GitHub polling) y se documentó el flujo serverless.

## 📋 Próximos Pasos (Para el siguiente agente)

1. **Integración en el Dashboard** ✅:
   - `src/api/runpod.js` creado para `/run` + polling `/status/{job_id}`.
   - `Phase1Face.jsx` actualizado para usar RunPod Serverless con 4 jobs en paralelo y guardar data URI en Supabase.
2. **Variables de Entorno**:
   - Actualizar el archivo `.env` local con el `VITE_RUNPOD_API_KEY` y `VITE_RUNPOD_ENDPOINT_ID`.
3. **Limpieza**:
   - Una vez confirmada la generación en el dashboard, el pod antiguo `4yjpcxmu17d344` puede ser eliminado definitivamente para ahorrar costos de almacenamiento.

## 💡 Notas Técnicas
- El worker devuelve las imágenes en formato **base64** dentro del objeto `output.images`.
- El Dashboard debe decodificar este base64 para mostrar la imagen (usando `URL.createObjectURL` o similar).
- Tiempo estimado de cold start: 30-60 segundos si el worker no está caliente.
