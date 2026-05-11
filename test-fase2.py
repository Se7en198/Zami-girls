#!/usr/bin/env python3
"""
Zami Girls — Prueba Fase 2: Generación de Cuerpo
Uso: python3 test-fase2.py <filename_imagen_fase1>
Ejemplo: python3 test-fase2.py z-image_00018_.png
"""

import json, os, sys, random, time, urllib.request, urllib.parse, uuid
from pathlib import Path

COMFYUI_URL = "http://127.0.0.1:8188"
OUTPUT_DIR  = Path(__file__).parent / "test-output"
WORKFLOW    = json.loads((Path(__file__).parent / "src/workflows/body-generation.json").read_text())

# 4 variaciones de cuerpo — prompts SFW descriptivos
BODY_PROMPTS = [
    "Full body portrait, curvy voluptuous figure, hourglass silhouette, natural proportions, elegant pose, studio lighting",
    "Full body portrait, athletic toned body, fit physique, strong lean build, confident pose, studio lighting",
    "Full body portrait, slim petite frame, delicate features, graceful posture, soft natural lighting",
    "Full body portrait, thick full-figured body, feminine curves, warm confident expression, studio lighting",
]

def rand_seed():
    return random.randint(1, 999_999_999_999_999)

def build_workflow(face_filename, body_prompt, seed):
    wf = json.loads(json.dumps(WORKFLOW))
    # Input: imagen del rostro de Fase 1
    wf["41"]["inputs"]["image"] = face_filename
    # Prompt positivo con descripción del cuerpo
    wf["321"]["inputs"]["prompt"] = body_prompt
    # Seed aleatorio para variación
    wf["333"]["inputs"]["seed"] = seed
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
    pid  = data["prompt_id"]
    print(f"  → En cola: {pid}")
    return pid

def poll_result(prompt_id, idx):
    print(f"  [{idx+1}] Generando", end="", flush=True)
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
    raise TimeoutError("Timeout — más de 5 min")

def extract_images(entry):
    imgs = []
    for out in entry.get("outputs", {}).values():
        imgs.extend(out.get("images", []))
    return imgs

def download_image(filename, img_type, subfolder, dest):
    url = (f"{COMFYUI_URL}/view"
           f"?filename={urllib.parse.quote(filename)}"
           f"&type={img_type}"
           f"&subfolder={urllib.parse.quote(subfolder or '')}")
    with urllib.request.urlopen(url, timeout=60) as r:
        dest.write_bytes(r.read())

def main():
    print("\n╔══════════════════════════════════════════╗")
    print("║  ZAMI GIRLS — Prueba Fase 2: Cuerpo      ║")
    print("╚══════════════════════════════════════════╝\n")

    # Leer filename de Phase 1
    if len(sys.argv) < 2:
        # Buscar la imagen más reciente en test-output
        outputs = list(OUTPUT_DIR.glob("rostro-*.png"))
        if not outputs:
            print("✗ Uso: python3 test-fase2.py <filename_comfyui>")
            print("  Ejemplo: python3 test-fase2.py z-image_00018_.png")
            print("  (El filename que aparece en ComfyUI output, no la ruta completa)")
            sys.exit(1)
        # Usar la última generada
        latest = max(outputs, key=lambda f: f.stat().st_mtime)
        # Extraer el filename de ComfyUI del nombre guardado
        print(f"  ℹ Sin argumento — debes pasar el filename de ComfyUI")
        print(f"  Ejemplo: python3 test-fase2.py z-image_00018_.png")
        sys.exit(1)

    face_filename = sys.argv[1]
    print(f"▸ Imagen de Fase 1: {face_filename}")

    # Verificar ComfyUI
    print("▸ Verificando ComfyUI...")
    try:
        stats = get_json(f"{COMFYUI_URL}/system_stats")
        vram  = stats.get("system", {}).get("vram_total", 0)
        print(f"  ✓ Activo — VRAM: {vram // 1_000_000_000} GB\n")
    except Exception as e:
        print(f"  ✗ No conecta: {e}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Encolar 4 variaciones de cuerpo
    print("▸ Encolando 4 variaciones de cuerpo...")
    BODY_LABELS = ["Curvy", "Athletic", "Slim", "Thick"]
    jobs = []
    for i, prompt in enumerate(BODY_PROMPTS):
        seed     = rand_seed()
        workflow = build_workflow(face_filename, prompt, seed)
        pid      = queue_prompt(workflow)
        jobs.append({"pid": pid, "seed": seed, "idx": i, "label": BODY_LABELS[i]})
        time.sleep(0.4)

    # Esperar resultados
    print("\n▸ Generando 4 cuerpos...")
    results = []
    for job in jobs:
        try:
            entry  = poll_result(job["pid"], job["idx"])
            images = extract_images(entry)
            if images:
                img  = images[-1]
                dest = OUTPUT_DIR / f"cuerpo-{job['idx']+1}-{job['label'].lower()}-seed{job['seed']}.png"
                download_image(img["filename"], img["type"], img.get("subfolder",""), dest)
                print(f"  ✓ {job['label']}: {dest.name}")
                results.append({**job, "file": dest, "img": img})
        except Exception as e:
            print(f"\n  ✗ {job['label']} falló: {e}")

    # Resumen
    print("\n╔══════════════════════════════════════════╗")
    print("║  RESULTADOS                              ║")
    print("╚══════════════════════════════════════════╝")
    for r in results:
        url = (f"{COMFYUI_URL}/view?filename={urllib.parse.quote(r['img']['filename'])}"
               f"&type={r['img']['type']}")
        print(f"\n  {r['label']} | seed: {r['seed']}")
        print(f"  Archivo : {r['file'].name}")
        print(f"  Ver en  : {url}")
    print(f"\n✓ {len(results)}/4 cuerpos generados en: {OUTPUT_DIR}\n")

if __name__ == "__main__":
    main()
