---
name: zami-portrait-generator
description: "Genera retratos de modelos virtuales Zami Girls usando el nodo AION Portrait Master en ComfyUI (RunPod). Controla 33 parámetros morfológicos para crear identidades latinas únicas y cautivadoras."
---

> **AUTOMATION**: Claude pushes all jobs. User NEVER runs terminal commands after initial setup.
> If generation isn't starting: restart Claude Code session (MCP write token may have expired).

# ZAMI GIRLS — PORTRAIT GENERATOR

## Arquitectura

- **ComfyUI**: `http://127.0.0.1:8188` (local en RunPod, proxy: `https://4yjpcxmu17d344-8188.proxy.runpod.net`)
- **Workflow Fase 1**: `src/workflows/face-generation.json` — AION Portrait Master + z_image_turbo_bf16
- **Workflow Fase 2**: `src/workflows/body-generation.json` — Qwen Image Edit img2img
- **Control remoto**: daemon en pod vía GitHub (`daemon/zami-daemon.sh`)
- **Output Fase 1**: `test-output/` en el pod, pusheado a `daemon/output/` en GitHub

## Motor Fase 1 — Nodos clave

| Nodo | Función |
|------|---------|
| 82 | `AionFluxPrompterNode` — 33 parámetros morfológicos |
| 78 | KSampler — seed principal |
| 14 | KSamplerAdvanced — noise_seed |
| 73 | SeedVarianceEnhancer |
| 6/57 | SaveImage |
| 93 | `GeminiNanoBanana2` — character sheet generator (requiere Gemini API key) |
| 94 | `SaveImage` — guarda el character sheet output |

El workflow `face-generation-nano-banana.json` incluye los nodos 93+94 para generar character sheets de 5 vistas (close portrait + front + right side + left side + back) en formato 16:9.

## Motor Fase 2 — Nodos clave

| Nodo | Función |
|------|---------|
| 41 | LoadImage — imagen de referencia (cara Fase 1) |
| 321 | TextEncodeQwenImageEditPlus — prompt del cuerpo |
| 333 | KSampler — seed |
| 334 | SEXGOD LoRA |

## GeminiNanoBanana2 — Character Sheet

Genera una lámina de 5 vistas del personaje en una sola imagen 16:9.

- **Requiere**: Gemini API key (gratis en [aistudio.google.com](https://aistudio.google.com))
- **Modelo**: "Nano Banana 2 (Gemini 3.1 Flash Image)"
- **Motor**: Gemini 3.1 Flash Image
- **Vistas**: close portrait + front + right side + left side + back
- **Aspect ratio**: 16:9 — **Resolución**: 1K
- **Workflow**: `src/workflows/face-generation-nano-banana.json`
- **Configuración**: set `gemini_api_key` en el nodo 82 (`AionFluxPrompterNode`)

## Fase 2 — Body Generation

Toma un rostro seleccionado de Fase 1 y genera el cuerpo completo vía img2img.

- **Workflow**: `src/workflows/body-generation.json`
- **Model**: `qwen_image_edit_2511_bf16.safetensors` (Qwen Image Edit)
- **CLIP**: `qwen_2.5_vl_7b_fp8_scaled.safetensors`
- **VAE**: `qwen_image_vae.safetensors`
- **Nodos clave**:
  - `41` — `LoadImage`: carga la cara de referencia (output de Fase 1)
  - `321` — `TextEncodeQwenImageEditPlus`: prompt positivo del cuerpo
  - `333` — `KSampler`: seed de generación
- **Script**: `test-fase2.py <comfyui_filename>`

## Los 33 Parámetros AION (con opciones válidas)

### Demographics
- `sex`: female
- `ethnicity`: Latin American | Mestizo | Caribbean | Afro-Caribbean | South American
- `photo_type`: Studio white background | Studio black background | Natural light portrait | Fashion editorial

### Eye System
- `eye_shape`: almond-shaped | round | upturned | hooded | monolid
- `eye_size`: large | medium | small | very large
- `eye_tilt`: slight upward tilt | neutral tilt | moderate upward tilt | downward tilt
- `eye_color`: dark brown | brown | amber | hazel | green | light brown
- `eyebrow_thickness`: thick | medium thickness | dense and full | thin
- `eyebrow_shape`: high arch | soft arch | straight | angled | rounded
- `eyebrow_color`: dark brown | medium brown | black | light brown

### Nose
- `nose_profile`: slightly convex | high bridge | broad bridge | button nose profile | straight
- `nose_base`: medium base | wide base | narrow base | compact nostrils
- `nose_tip`: rounded tip | broad tip | upturned tip | refined tip | pointed tip

### Lips
- `lips_volume`: very full lips | full lips | naturally plump | medium volume
- `cupid_bow`: pronounced cupid's bow | heart-shaped cupid's bow | rounded cupid's bow | sharply defined bow
- `lips_proportion`: fuller lower lip | balanced upper and lower | slightly fuller lower
- `lips_color`: coral toned | rosy pink | brownish pink | deep rose | nude pink | berry

### Facial Structure
- `forehead`: average proportion | low forehead | narrow forehead | wide forehead
- `cheekbones`: high cheekbones | prominent cheekbones | wide-set cheekbones | angular cheekbones
- `jawline`: soft jawline | defined jawline | rounded jawline | tapered jawline | sharp jawline
- `chin`: rounded chin | soft chin | pointed chin | square chin
- `cheeks`: apple cheeks | full cheeks | soft rounded cheeks | lean cheeks
- `submental`: tight submental area | soft submental area | defined under-chin
- `face_neck_transition`: smooth transition | defined angle | elongated neck line

### Hair
- `hair_structure`: wavy | straight | loosely wavy | curly | coily
- `hair_length`: long | very long | shoulder length | mid-back length | short
- `hair_volume`: high volume | thick and dense | very voluminous | medium volume
- `hair_color`: dark brown | jet black | medium brown | dark auburn | golden brown | black

### Skin
- `skin_tone`: light | medium | medium-tan | olive | deep tan | tan
- `skin_undertone`: warm undertone | golden undertone | olive undertone | neutral undertone
- `skin_texture`: smooth natural grain | natural skin grain | soft velvety texture
- `skin_micro_texture`: visible fine pores | natural pore variation | subtle pore detail | realistic micro detail
- `skin_imperfections`: none visible | light freckles | subtle freckles | light acne marks
- `skin_reflection`: natural dewy glow | matte natural finish | satin finish

### Skin Defects (ninguno para modelos)
- `wrinkles`: none
- `scars`: none
- `deformations`: none
- `tone_loss`: none
- `skin_marks`: none
- `vitiligo`: none
- `under_eye`: none

### Expression
- `expression`: happiness | neutral | slight smile | surprise
- `expression_variant`: radiant joy | Duchenne smile | warm smile | determined | confident | smirk | serene

## Inspiración — Top Latinas 2025-2026

Basado en TC Candler, Ranker, FictionHorizon, PinkVilla rankings:

| Inspiración | Nacionalidad | Rasgos Clave |
|-------------|-------------|--------------|
| Ana de Armas | Cubana | piel olive cálida, ojos almendra oscuros, pómulos altos, labios llenos, cabello oscuro ondulado |
| Eiza González | Mexicana | piel medium-tan, ojos grandes oscuros, mandíbula angular, estructura ósea fuerte |
| Salma Hayek | Mexicana | piel olive profunda, ojos expresivos oscuros, cabello rizado oscuro, labios muy llenos |
| Adria Arjona | Puertorriqueña-Guatemalteca | piel medium-tan, ojos grandes deep-set, huesos definidos, cabello negro liso |
| Camila Mendes | Brasileña-Americana | piel golden-tan, ojos almendra, mandíbula definida, labios llenos |
| Jennifer Lopez | Puertorriqueña | piel medium-warm, ojos hazel/castaños, mandíbula fuerte, labios llenos |

## Output esperado

Cada modelo genera:
- **Fase 1**: 4 rostros con variación de seed (frontal, studio white background)
- **Fase 2**: 4 variaciones de cuerpo usando el rostro seleccionado como referencia
- **Multi-ángulo** (en desarrollo): frente + perfil + nuca + 3/4 manteniendo consistencia de identidad

## Reglas de calidad

Antes de avanzar a Fase 2:
- Una sola persona, cara limpia y visible
- Realismo fotográfico, no beauty-CGI
- Sin watermarks, texto ni collage
- Rasgos coherentes con el perfil étnico diseñado
- Expresión natural y cautivadora
- Piel con textura realista (no plástica)

## Scripts

| Script | Descripción |
|--------|-------------|
| `test-latinas.py` | Genera perfiles latinos con parámetros AION completos |
| `test-nuevas-latinas.py` | 3 nuevos perfiles latinas (Cubana, Mexicana, Caribeña) |
| `test-fase2.py <comfyui_filename>` | Body generation desde la cara seleccionada |
| `daemon/zami-daemon.sh` | Daemon de control remoto vía GitHub |
| `daemon/setup.sh` | Setup ONE-TIME en el pod (lanza el daemon) |
| `daemon/push-job.sh <job_file>` | Pushea un nuevo job al daemon desde el pod |
