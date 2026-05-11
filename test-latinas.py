#!/usr/bin/env python3
"""
Zami Girls — 4 Rostros Latinas Exóticas
Corre: python3 test-latinas.py
"""

import json, random, time, urllib.request, urllib.parse, uuid
from pathlib import Path

COMFYUI_URL = "http://127.0.0.1:8188"
OUTPUT_DIR  = Path(__file__).parent / "test-output"
WORKFLOW    = json.loads((Path(__file__).parent / "src/workflows/face-generation.json").read_text())

# ─── 4 PERFILES LATINOS EXÓTICOS ──────────────────────────────────────────────

PERFILES = [
    {
        "nombre": "La Caleña",
        "brief_text": "exotic colombian valley woman, striking warm beauty, natural elegance",
        "photo_type": "Studio white background",
        "sex": "female",
        "ethnicity": "Latin American",
        "eye_shape": "almond-shaped",
        "eye_size": "large",
        "eye_tilt": "slight upward tilt",
        "eye_color": "amber",
        "eyebrow_thickness": "thick",
        "eyebrow_shape": "high arch",
        "eyebrow_color": "dark brown",
        "nose_profile": "slightly convex",
        "nose_base": "medium base",
        "nose_tip": "rounded tip",
        "lips_volume": "very full lips",
        "cupid_bow": "pronounced cupid's bow",
        "lips_proportion": "fuller lower lip",
        "lips_color": "coral toned",
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
        "skin_tone": "medium-tan",
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
        "expression_variant": "radiant joy",
    },
    {
        "nombre": "La Mexica",
        "brief_text": "mestiza mexican woman, strong indigenous features, powerful gaze, striking presence",
        "photo_type": "Studio white background",
        "sex": "female",
        "ethnicity": "Mestizo",
        "eye_shape": "almond-shaped",
        "eye_size": "medium",
        "eye_tilt": "neutral tilt",
        "eye_color": "dark brown",
        "eyebrow_thickness": "dense and full",
        "eyebrow_shape": "straight",
        "eyebrow_color": "dark brown",
        "nose_profile": "broad bridge",
        "nose_base": "wide base",
        "nose_tip": "broad tip",
        "lips_volume": "full lips",
        "cupid_bow": "rounded cupid's bow",
        "lips_proportion": "balanced upper and lower",
        "lips_color": "brownish pink",
        "forehead": "low forehead",
        "cheekbones": "prominent cheekbones",
        "jawline": "defined jawline",
        "chin": "rounded chin",
        "cheeks": "full cheeks",
        "submental": "tight submental area",
        "face_neck_transition": "defined angle",
        "hair_structure": "straight",
        "hair_length": "very long",
        "hair_volume": "thick and dense",
        "hair_color": "jet black",
        "skin_tone": "olive",
        "skin_undertone": "olive undertone",
        "skin_texture": "natural skin grain",
        "skin_micro_texture": "natural pore variation",
        "skin_imperfections": "none visible",
        "skin_reflection": "matte natural finish",
        "wrinkles": "none",
        "scars": "none",
        "deformations": "none",
        "tone_loss": "none",
        "skin_marks": "none",
        "vitiligo": "none",
        "under_eye": "none",
        "expression": "neutral",
        "expression_variant": "determined",
    },
    {
        "nombre": "La Boricua",
        "brief_text": "puerto rican caribbean beauty, exotic mixed heritage, warm and vibrant",
        "photo_type": "Studio white background",
        "sex": "female",
        "ethnicity": "Caribbean",
        "eye_shape": "round",
        "eye_size": "large",
        "eye_tilt": "moderate upward tilt",
        "eye_color": "hazel",
        "eyebrow_thickness": "medium thickness",
        "eyebrow_shape": "soft arch",
        "eyebrow_color": "medium brown",
        "nose_profile": "button nose profile",
        "nose_base": "compact nostrils",
        "nose_tip": "upturned tip",
        "lips_volume": "naturally plump",
        "cupid_bow": "heart-shaped cupid's bow",
        "lips_proportion": "slightly fuller lower",
        "lips_color": "rosy pink",
        "forehead": "average proportion",
        "cheekbones": "wide-set cheekbones",
        "jawline": "rounded jawline",
        "chin": "soft chin",
        "cheeks": "soft rounded cheeks",
        "submental": "soft submental area",
        "face_neck_transition": "smooth transition",
        "hair_structure": "loosely wavy",
        "hair_length": "shoulder length",
        "hair_volume": "very voluminous",
        "hair_color": "medium brown",
        "skin_tone": "medium",
        "skin_undertone": "golden undertone",
        "skin_texture": "soft velvety texture",
        "skin_micro_texture": "subtle pore detail",
        "skin_imperfections": "light freckles",
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
    {
        "nombre": "La Venezolana",
        "brief_text": "venezuelan model, classic latin beauty queen, striking bone structure, seductive elegance",
        "photo_type": "Studio white background",
        "sex": "female",
        "ethnicity": "Latin American",
        "eye_shape": "upturned",
        "eye_size": "very large",
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
        "forehead": "narrow forehead",
        "cheekbones": "angular cheekbones",
        "jawline": "tapered jawline",
        "chin": "pointed chin",
        "cheeks": "lean cheeks",
        "submental": "defined under-chin",
        "face_neck_transition": "elongated neck line",
        "hair_structure": "wavy",
        "hair_length": "mid-back length",
        "hair_volume": "very voluminous",
        "hair_color": "dark brown",
        "skin_tone": "deep tan",
        "skin_undertone": "golden undertone",
        "skin_texture": "smooth natural grain",
        "skin_micro_texture": "realistic micro detail",
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
        "expression_variant": "smirk",
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
    print("\n╔══════════════════════════════════════════════════╗")
    print("║  ZAMI GIRLS — 4 Rostros Latinas Exóticas         ║")
    print("╚══════════════════════════════════════════════════╝\n")

    print("▸ Verificando ComfyUI...")
    try:
        stats = get_json(f"{COMFYUI_URL}/system_stats")
        vram  = stats.get("system", {}).get("vram_total", 0)
        print(f"  ✓ Activo — VRAM: {vram // 1_000_000_000} GB\n")
    except Exception as e:
        print(f"  ✗ No conecta: {e}"); return

    OUTPUT_DIR.mkdir(exist_ok=True)

    print("▸ Encolando 4 perfiles...\n")
    for p in PERFILES:
        print(f"  📍 {p['nombre']}")
        print(f"     Etnia: {p['ethnicity']} | Piel: {p['skin_tone']} | Ojos: {p['eye_color']}")
        print(f"     Cabello: {p['hair_color']} {p['hair_length']} | Expresión: {p['expression_variant']}")

    print()
    jobs = []
    for perfil in PERFILES:
        seed     = rand_seed()
        workflow = build_workflow(perfil, seed)
        pid      = queue_prompt(workflow)
        jobs.append({"pid": pid, "seed": seed, "perfil": perfil})
        print(f"  → {perfil['nombre']}: {pid}")
        time.sleep(0.4)

    print("\n▸ Generando (~2 min por rostro)...\n")
    results = []
    for job in jobs:
        nombre = job["perfil"]["nombre"]
        try:
            entry = poll_result(job["pid"], nombre)
            img   = extract_last_image(entry)
            if img:
                dest = OUTPUT_DIR / f"{nombre.replace(' ','_').replace('La_','')}-seed{job['seed']}.png"
                download_image(img, dest)
                print(f"  ✓ Guardada: {dest.name}")
                results.append({**job, "file": dest, "img": img})
        except Exception as e:
            print(f"\n  ✗ {nombre} falló: {e}")

    print("\n╔══════════════════════════════════════════════════╗")
    print("║  RESULTADOS                                      ║")
    print("╚══════════════════════════════════════════════════╝")
    for r in results:
        url = (f"https://4yjpcxmu17d344-8188.proxy.runpod.net/view"
               f"?filename={urllib.parse.quote(r['img']['filename'])}&type={r['img']['type']}")
        print(f"\n  {r['perfil']['nombre']}")
        print(f"  Ver: {url}")
    print(f"\n✓ {len(results)}/4 rostros en: {OUTPUT_DIR}\n")

if __name__ == "__main__":
    main()
