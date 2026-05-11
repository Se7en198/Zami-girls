#!/usr/bin/env python3
"""
Zami Girls — 3 Nuevas Latinas Top-Ranked 2025-2026
Inspiradas en: Ana de Armas (Cuba), Eiza González (México), Adria Arjona / JLo (Caribe)
Corre: python3 test-nuevas-latinas.py
"""

import json, random, time, urllib.request, urllib.parse, uuid
from pathlib import Path

COMFYUI_URL = "http://127.0.0.1:8188"
OUTPUT_DIR  = Path(__file__).parent / "test-output"
WORKFLOW    = json.loads((Path(__file__).parent / "src/workflows/face-generation.json").read_text())

# ─── 3 PERFILES — TOP LATINAS 2025-2026 ──────────────────────────────────────

PERFILES = [
    {
        # INSPIRACIÓN: Ana de Armas
        # Rasgos: piel olive-light cálida, ojos almendra oscuros, pómulos altos,
        # labios llenos con cupid's bow definido, cabello oscuro ondulado, sonrisa cálida
        "nombre": "La Cubana",
        "brief_text": "striking cuban beauty, effortless warm charm, natural actress magnetism",
        "photo_type": "Studio white background",
        "sex": "female",
        "ethnicity": "Latin American",
        "eye_shape": "almond-shaped",
        "eye_size": "large",
        "eye_tilt": "slight upward tilt",
        "eye_color": "dark brown",
        "eyebrow_thickness": "medium thickness",
        "eyebrow_shape": "high arch",
        "eyebrow_color": "dark brown",
        "nose_profile": "slightly convex",
        "nose_base": "narrow base",
        "nose_tip": "rounded tip",
        "lips_volume": "full lips",
        "cupid_bow": "pronounced cupid's bow",
        "lips_proportion": "fuller lower lip",
        "lips_color": "rosy pink",
        "forehead": "average proportion",
        "cheekbones": "high cheekbones",
        "jawline": "soft jawline",
        "chin": "rounded chin",
        "cheeks": "apple cheeks",
        "submental": "tight submental area",
        "face_neck_transition": "smooth transition",
        "hair_structure": "wavy",
        "hair_length": "long",
        "hair_volume": "high volume",
        "hair_color": "dark brown",
        "skin_tone": "light",
        "skin_undertone": "warm undertone",
        "skin_texture": "smooth natural grain",
        "skin_micro_texture": "visible fine pores",
        "skin_imperfections": "none visible",
        "skin_reflection": "natural dewy glow",
        "wrinkles": "none",
        "scars": "none",
        "deformations": "none",
        "tone_loss": "none",
        "skin_marks": "none",
        "vitiligo": "none",
        "under_eye": "none",
        "expression": "happiness",
        "expression_variant": "warm smile",
    },
    {
        # INSPIRACIÓN: Eiza González
        # Rasgos: piel medium-tan, ojos grandes oscuros, mandíbula angular fuerte,
        # estructura ósea definida, cabello liso muy largo oscuro, presencia feroz
        "nombre": "La Mexicana",
        "brief_text": "bold fearless mexican model, fierce confidence, powerful bone structure",
        "photo_type": "Studio white background",
        "sex": "female",
        "ethnicity": "Latin American",
        "eye_shape": "almond-shaped",
        "eye_size": "large",
        "eye_tilt": "moderate upward tilt",
        "eye_color": "dark brown",
        "eyebrow_thickness": "thick",
        "eyebrow_shape": "angled",
        "eyebrow_color": "dark brown",
        "nose_profile": "high bridge",
        "nose_base": "narrow base",
        "nose_tip": "refined tip",
        "lips_volume": "full lips",
        "cupid_bow": "sharply defined bow",
        "lips_proportion": "fuller lower lip",
        "lips_color": "deep rose",
        "forehead": "average proportion",
        "cheekbones": "angular cheekbones",
        "jawline": "defined jawline",
        "chin": "pointed chin",
        "cheeks": "lean cheeks",
        "submental": "defined under-chin",
        "face_neck_transition": "elongated neck line",
        "hair_structure": "straight",
        "hair_length": "very long",
        "hair_volume": "thick and dense",
        "hair_color": "dark brown",
        "skin_tone": "medium",
        "skin_undertone": "warm undertone",
        "skin_texture": "smooth natural grain",
        "skin_micro_texture": "subtle pore detail",
        "skin_imperfections": "none visible",
        "skin_reflection": "satin finish",
        "wrinkles": "none",
        "scars": "none",
        "deformations": "none",
        "tone_loss": "none",
        "skin_marks": "none",
        "vitiligo": "none",
        "under_eye": "none",
        "expression": "neutral",
        "expression_variant": "confident",
    },
    {
        # INSPIRACIÓN: Adria Arjona + Jennifer Lopez
        # Rasgos: piel golden-tan caribeña, ojos grandes dark, labios muy llenos,
        # cabello ondulado voluminoso, energía sensual y cálida caribeña
        "nombre": "La Caribeña",
        "brief_text": "caribbean goddess energy, sensual magnetic warmth, irresistible tropical beauty",
        "photo_type": "Studio white background",
        "sex": "female",
        "ethnicity": "Caribbean",
        "eye_shape": "almond-shaped",
        "eye_size": "large",
        "eye_tilt": "slight upward tilt",
        "eye_color": "dark brown",
        "eyebrow_thickness": "thick",
        "eyebrow_shape": "high arch",
        "eyebrow_color": "dark brown",
        "nose_profile": "slightly convex",
        "nose_base": "medium base",
        "nose_tip": "rounded tip",
        "lips_volume": "very full lips",
        "cupid_bow": "heart-shaped cupid's bow",
        "lips_proportion": "fuller lower lip",
        "lips_color": "deep rose",
        "forehead": "average proportion",
        "cheekbones": "high cheekbones",
        "jawline": "defined jawline",
        "chin": "rounded chin",
        "cheeks": "full cheeks",
        "submental": "tight submental area",
        "face_neck_transition": "smooth transition",
        "hair_structure": "wavy",
        "hair_length": "very long",
        "hair_volume": "very voluminous",
        "hair_color": "dark brown",
        "skin_tone": "medium-tan",
        "skin_undertone": "golden undertone",
        "skin_texture": "soft velvety texture",
        "skin_micro_texture": "subtle pore detail",
        "skin_imperfections": "none visible",
        "skin_reflection": "natural dewy glow",
        "wrinkles": "none",
        "scars": "none",
        "deformations": "none",
        "tone_loss": "none",
        "skin_marks": "none",
        "vitiligo": "none",
        "under_eye": "none",
        "expression": "happiness",
        "expression_variant": "Duchenne smile",
    },
]

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def rand_seed():
    return random.randint(1, 999_999_999_999_999)

def build_workflow(params, seed):
    wf = json.loads(json.dumps(WORKFLOW))
    wf["78"]["inputs"]["seed"]       = seed
    wf["14"]["inputs"]["noise_seed"] = rand_seed()
    wf["73"]["inputs"]["seed"]       = rand_seed()
    skip = {"nombre"}
    for k, v in params.items():
        if k not in skip and k in wf["82"]["inputs"]:
            wf["82"]["inputs"][k] = v
    return wf

def post_json(url, data):
    body = json.dumps(data).encode()
    req  = urllib.request.Request(url, data=body,
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def get_json(url):
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.loads(r.read())

def queue_prompt(workflow):
    data = post_json(f"{COMFYUI_URL}/prompt",
                     {"prompt": workflow, "client_id": str(uuid.uuid4())})
    return data["prompt_id"]

def poll_result(prompt_id, nombre):
    print(f"  [{nombre}] Generando", end="", flush=True)
    for _ in range(150):
        time.sleep(2)
        try:
            data = get_json(f"{COMFYUI_URL}/history/{prompt_id}")
            if data.get(prompt_id, {}).get("outputs"):
                print(" ✓")
                return data[prompt_id]
        except Exception:
            pass
        print(".", end="", flush=True)
    raise TimeoutError("Timeout")

def extract_last_image(entry):
    imgs = []
    for out in entry.get("outputs", {}).values():
        imgs.extend(out.get("images", []))
    return imgs[-1] if imgs else None

def download_image(img, dest):
    url = (f"{COMFYUI_URL}/view"
           f"?filename={urllib.parse.quote(img['filename'])}"
           f"&type={img['type']}"
           f"&subfolder={urllib.parse.quote(img.get('subfolder',''))}")
    with urllib.request.urlopen(url, timeout=60) as r:
        dest.write_bytes(r.read())

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║  ZAMI GIRLS — 3 Nuevas Latinas Top 2025-2026         ║")
    print("║  Inspiradas en: Ana de Armas · Eiza · Adria Arjona   ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    print("▸ Verificando ComfyUI...")
    try:
        stats = get_json(f"{COMFYUI_URL}/system_stats")
        vram  = stats.get("system", {}).get("vram_total", 0)
        print(f"  ✓ Activo — VRAM: {vram // 1_000_000_000} GB\n")
    except Exception as e:
        print(f"  ✗ No conecta: {e}"); return

    OUTPUT_DIR.mkdir(exist_ok=True)

    print("▸ Perfiles a generar:\n")
    for p in PERFILES:
        print(f"  🌟 {p['nombre']}")
        print(f"     → {p['brief_text']}")
        print(f"     Etnia: {p['ethnicity']} | Piel: {p['skin_tone']} | Ojos: {p['eye_color']}")
        print(f"     Cabello: {p['hair_color']} {p['hair_length']} {p['hair_structure']}")
        print(f"     Expresión: {p['expression_variant']}\n")

    jobs = []
    for perfil in PERFILES:
        seed     = rand_seed()
        workflow = build_workflow(perfil, seed)
        pid      = queue_prompt(workflow)
        jobs.append({"pid": pid, "seed": seed, "perfil": perfil})
        print(f"  → {perfil['nombre']}: en cola ({pid[:8]}...)")
        time.sleep(0.4)

    print("\n▸ Generando (~2 min por modelo)...\n")
    results = []
    for job in jobs:
        nombre = job["perfil"]["nombre"]
        try:
            entry = poll_result(job["pid"], nombre)
            img   = extract_last_image(entry)
            if img:
                slug = nombre.replace(" ", "_").replace("La_", "")
                dest = OUTPUT_DIR / f"{slug}-seed{job['seed']}.png"
                download_image(img, dest)
                print(f"  ✓ {nombre}: {dest.name}")
                results.append({**job, "file": dest, "img": img, "comfyui_filename": img["filename"]})
        except Exception as e:
            print(f"\n  ✗ {nombre} falló: {e}")

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║  RESULTADOS                                          ║")
    print("╚══════════════════════════════════════════════════════╝")
    for r in results:
        url = (f"https://4yjpcxmu17d344-8188.proxy.runpod.net/view"
               f"?filename={urllib.parse.quote(r['img']['filename'])}&type={r['img']['type']}")
        print(f"\n  {r['perfil']['nombre']}")
        print(f"  Archivo ComfyUI : {r['comfyui_filename']}")
        print(f"  Seed            : {r['seed']}")
        print(f"  Ver             : {url}")
    print(f"\n✓ {len(results)}/3 modelos en: {OUTPUT_DIR}\n")

if __name__ == "__main__":
    main()
