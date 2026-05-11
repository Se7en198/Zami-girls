#!/usr/bin/env python3
"""
Zami Girls — Prueba Fase 1: Generación de Rostros
Corre: python3 test-fase1.py
"""

import json, os, random, time, urllib.request, urllib.error, uuid
from pathlib import Path

# ─── CONFIG ───────────────────────────────────────────────────────────────────
COMFYUI_URL = "http://127.0.0.1:8188"   # local dentro de RunPod
OUTPUT_DIR  = Path(__file__).parent / "test-output"
WORKFLOW    = json.loads((Path(__file__).parent / "src/workflows/face-generation.json").read_text())

PARAMS = {
    "ethnicity":   "Hispanic",
    "skin_tone":   "medium",
    "eye_color":   "brown",
    "hair_color":  "dark brown",
    "hair_length": "shoulder-length",
    "expression":  "soft smile",
    "photo_type":  "Studio white background",
    "brief_text":  "beautiful latina woman, elegant, natural",
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def rand_seed():
    return random.randint(1, 999_999_999_999_999)

def build_workflow(params, seed):
    wf = json.loads(json.dumps(WORKFLOW))   # deep copy
    wf["78"]["inputs"]["seed"]           = seed
    wf["14"]["inputs"]["noise_seed"]     = rand_seed()
    wf["73"]["inputs"]["seed"]           = rand_seed()
    for k in ["brief_text","photo_type","ethnicity","skin_tone","eye_color",
              "hair_color","hair_length","expression"]:
        if params.get(k):
            wf["82"]["inputs"][k] = params[k]
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
    raise TimeoutError("ComfyUI tardó más de 5 min")

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

# ─── MAIN ─────────────────────────────────────────────────────────────────────
import urllib.parse

def main():
    print("\n╔══════════════════════════════════════════╗")
    print("║  ZAMI GIRLS — Prueba Fase 1: Rostros     ║")
    print("╚══════════════════════════════════════════╝\n")

    # Verificar ComfyUI
    print("▸ Verificando ComfyUI...")
    try:
        stats = get_json(f"{COMFYUI_URL}/system_stats")
        vram  = stats.get("system", {}).get("vram_total", 0)
        print(f"  ✓ ComfyUI activo — VRAM total: {vram // 1_000_000_000} GB\n")
    except Exception as e:
        print(f"  ✗ No se puede conectar: {e}")
        print(f"  URL usada: {COMFYUI_URL}")
        print("  Asegúrate de que ComfyUI está corriendo en el pod.\n")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Encolar 4 generaciones
    print("▸ Encolando 4 generaciones...")
    jobs = []
    for i in range(4):
        seed     = rand_seed()
        workflow = build_workflow(PARAMS, seed)
        pid      = queue_prompt(workflow)
        jobs.append({"pid": pid, "seed": seed, "idx": i})
        time.sleep(0.4)

    # Esperar resultados
    print("\n▸ Esperando resultados (~2 min por imagen)...")
    results = []
    for job in jobs:
        try:
            entry  = poll_result(job["pid"], job["idx"])
            images = extract_images(entry)
            if images:
                img  = images[-1]   # última = upscaled final
                dest = OUTPUT_DIR / f"rostro-{job['idx']+1}-seed{job['seed']}.png"
                download_image(img["filename"], img["type"], img.get("subfolder",""), dest)
                print(f"  ✓ Guardada: {dest.name}")
                results.append({**job, "file": dest, "img": img})
        except Exception as e:
            print(f"\n  ✗ Job {job['idx']+1} falló: {e}")

    # Resumen
    print("\n╔══════════════════════════════════════════╗")
    print("║  RESULTADOS                              ║")
    print("╚══════════════════════════════════════════╝")
    for r in results:
        url = (f"{COMFYUI_URL}/view?filename={urllib.parse.quote(r['img']['filename'])}"
               f"&type={r['img']['type']}")
        print(f"\n  Rostro {r['idx']+1} | seed: {r['seed']}")
        print(f"  Archivo : {r['file']}")
        print(f"  Ver en  : {url}")
    print(f"\n✓ {len(results)}/4 rostros generados en: {OUTPUT_DIR}\n")

if __name__ == "__main__":
    main()
