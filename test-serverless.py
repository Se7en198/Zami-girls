#!/usr/bin/env python3
"""
test-serverless.py — Prueba directa del endpoint RunPod Serverless (Fase 1)

Uso:
  export RUNPOD_API_KEY=rp_xxxx
  python3 test-serverless.py

Genera 1 rostro y lo guarda como test-output.png en el directorio actual.
"""

import os
import sys
import time
import json
import base64
import requests

ENDPOINT_ID = "aqzsu0jydlras1"
API_KEY      = os.environ.get("RUNPOD_API_KEY", "")
BASE         = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

WORKFLOW_PATH = "src/workflows/face-generation.json"
OUTPUT_FILE   = "test-output.png"

# Perfil de prueba: cubana básica
TEST_PARAMS = {
    "photo_type":  "Studio white background",
    "ethnicity":   "Hispanic",
    "skin_tone":   "medium",
    "skin_undertone": "warm",
    "eye_color":   "brown",
    "eye_shape":   "almond",
    "hair_color":  "dark brown",
    "hair_length": "shoulder-length",
    "expression":  "soft smile",
    "brief_text":  "beautiful latina woman, photorealistic",
}

import random

def build_workflow(params):
    with open(WORKFLOW_PATH) as f:
        wf = json.load(f)

    seed = random.randint(0, 999_999_999_999_999)
    if "78" in wf: wf["78"]["inputs"]["seed"] = seed
    if "14" in wf: wf["14"]["inputs"]["noise_seed"] = random.randint(0, 999_999_999_999_999)
    if "73" in wf: wf["73"]["inputs"]["seed"] = random.randint(0, 999_999_999_999_999)

    allowed = [
        "brief_text", "photo_type", "sex", "ethnicity", "skin_tone",
        "skin_undertone", "eye_color", "eye_shape", "eye_size", "eye_tilt",
        "eyebrow_color", "eyebrow_shape", "eyebrow_thickness",
        "hair_color", "hair_length", "hair_structure", "hair_volume",
        "nose_profile", "nose_base", "nose_tip",
        "lips_volume", "cupid_bow", "lips_proportion", "lips_color",
        "forehead", "cheekbones", "jawline", "chin", "cheeks",
        "expression", "expression_variant",
    ]
    if "82" in wf:
        for key in allowed:
            if key in params and params[key]:
                wf["82"]["inputs"][key] = params[key]

    print(f"  [build] Seed principal: {seed}")
    return wf


def submit_job(workflow):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }
    body = {"input": {"workflow": workflow, "job_name": "test_face"}}
    r = requests.post(f"{BASE}/run", json=body, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    print(f"  [submit] Job ID: {data['id']}  Status: {data['status']}")
    return data["id"]


def poll_job(job_id, timeout_min=15):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    max_tries = timeout_min * 60 // 4
    print(f"  [poll] Esperando resultado (timeout {timeout_min} min)...")

    for i in range(max_tries):
        time.sleep(4)
        r = requests.get(f"{BASE}/status/{job_id}", headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        status = data.get("status", "?")

        if i % 5 == 0 or status in ("COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"):
            elapsed = (i + 1) * 4
            print(f"  [poll] {elapsed:>4}s  Status: {status}")

        if status == "COMPLETED":
            return data
        if status in ("FAILED", "CANCELLED", "TIMED_OUT"):
            print(f"\n  ERROR: {json.dumps(data.get('error', data), indent=2)}")
            sys.exit(1)

    print("\n  ERROR: Timeout esperando el job.")
    sys.exit(1)


def save_image(result):
    images = result.get("output", {}).get("images", [])
    if not images:
        print("  ERROR: No se encontraron imágenes en output.images")
        sys.exit(1)

    img_bytes = base64.b64decode(images[0])
    with open(OUTPUT_FILE, "wb") as f:
        f.write(img_bytes)
    kb = len(img_bytes) // 1024
    print(f"  [save] Imagen guardada: {OUTPUT_FILE}  ({kb} KB)")


def main():
    if not API_KEY:
        print("ERROR: Define la variable de entorno RUNPOD_API_KEY")
        sys.exit(1)

    print(f"\n=== Test RunPod Serverless — Endpoint: {ENDPOINT_ID} ===\n")

    print("[1] Construyendo workflow...")
    wf = build_workflow(TEST_PARAMS)

    print("[2] Enviando job a RunPod...")
    job_id = submit_job(wf)

    print("[3] Esperando generación (cold start ~30-60s + generación ~30s)...")
    result = poll_job(job_id)

    count = result.get("output", {}).get("count", 0)
    print(f"\n[4] Completado ✓  Imágenes generadas: {count}")

    print("[5] Guardando imagen...")
    save_image(result)

    print(f"\n✅ Test exitoso. Abre '{OUTPUT_FILE}' para ver el resultado.\n")


if __name__ == "__main__":
    main()
