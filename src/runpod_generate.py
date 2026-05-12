#!/usr/bin/env python3
"""
Zami Girls — RunPod On-Demand Generator
1. Enciende el pod si está apagado
2. Espera a ComfyUI
3. Envía el workflow
4. Descarga la imagen
5. Apaga el pod
"""

import json, os, time, random, uuid, base64, sys
from pathlib import Path
import requests

# ─── CONFIG ───────────────────────────────────────────────────────────────────
API_KEY    = os.environ["RUNPOD_API_KEY"]
POD_ID     = os.environ.get("POD_ID", "4yjpcxmu17d344")
JOB_NAME   = os.environ.get("JOB_NAME", "model")
PROFILE_JSON = os.environ.get("PROFILE_JSON", "{}")
COMFYUI_URL = f"https://{POD_ID}-8188.proxy.runpod.net"
OUTPUT_DIR  = Path("daemon/output")

GRAPHQL_URL = "https://api.runpod.io/graphql"
HEADERS_GQL = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# ─── RUNPOD API ───────────────────────────────────────────────────────────────

def gql(query, variables=None):
    r = requests.post(GRAPHQL_URL, headers=HEADERS_GQL,
                      json={"query": query, "variables": variables or {}},
                      timeout=30)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL error: {data['errors']}")
    return data["data"]

def pod_status():
    data = gql('{ pod(input: {podId: "%s"}) { desiredStatus runtime { uptimeInSeconds } } }' % POD_ID)
    pod = data.get("pod") or {}
    return pod.get("desiredStatus", "UNKNOWN")

def start_pod():
    print("▸ Encendiendo pod...")
    gql('''
    mutation { podResume(input: {podId: "%s", gpuCount: 1}) { id desiredStatus } }
    ''' % POD_ID)

def stop_pod():
    print("▸ Apagando pod...")
    gql('mutation { podStop(input: {podId: "%s"}) { id desiredStatus } }' % POD_ID)

# ─── COMFYUI API ──────────────────────────────────────────────────────────────

def wait_comfyui(timeout=300):
    print(f"▸ Esperando ComfyUI ({COMFYUI_URL})...", end="", flush=True)
    for _ in range(timeout // 5):
        try:
            r = requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
            if r.status_code == 200:
                vram = r.json().get("system", {}).get("vram_total", 0)
                print(f" ✓ (VRAM: {vram // 1_000_000_000}GB)")
                return True
        except Exception:
            pass
        print(".", end="", flush=True)
        time.sleep(5)
    return False

def build_workflow(profile: dict, seed: int) -> dict:
    wf = json.loads((Path("src/workflows/face-generation.json")).read_text())
    wf["78"]["inputs"]["seed"]       = seed
    wf["14"]["inputs"]["noise_seed"] = random.randint(1, 999_999_999_999_999)
    wf["73"]["inputs"]["seed"]       = random.randint(1, 999_999_999_999_999)
    skip = {"nombre"}
    for k, v in profile.items():
        if k not in skip and k in wf["82"]["inputs"]:
            wf["82"]["inputs"][k] = v
    return wf

def submit_workflow(workflow: dict) -> str:
    r = requests.post(f"{COMFYUI_URL}/prompt",
                      json={"prompt": workflow, "client_id": str(uuid.uuid4())},
                      timeout=15)
    r.raise_for_status()
    return r.json()["prompt_id"]

def poll_result(prompt_id: str, timeout=300):
    print(f"  Generando", end="", flush=True)
    for _ in range(timeout // 3):
        time.sleep(3)
        try:
            r = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10)
            data = r.json()
            if data.get(prompt_id, {}).get("outputs"):
                print(" ✓")
                return data[prompt_id]
        except Exception:
            pass
        print(".", end="", flush=True)
    raise TimeoutError("Timeout esperando resultado")

def download_image(img_info: dict, dest: Path):
    url = (f"{COMFYUI_URL}/view"
           f"?filename={img_info['filename']}"
           f"&type={img_info['type']}"
           f"&subfolder={img_info.get('subfolder', '')}")
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    dest.write_bytes(r.content)

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("\n╔══════════════════════════════════════════════════╗")
    print("║  ZAMI GIRLS — GitHub Actions Generator          ║")
    print("╚══════════════════════════════════════════════════╝\n")

    profile = json.loads(PROFILE_JSON) if PROFILE_JSON.strip() else {}
    seed    = random.randint(1, 999_999_999_999_999)

    # 1. Verificar / encender pod
    status = pod_status()
    print(f"▸ Pod status: {status}")
    if status != "RUNNING":
        start_pod()
        print("  Esperando que arranque (90s)...")
        time.sleep(90)

    # 2. Esperar ComfyUI
    if not wait_comfyui(timeout=300):
        print("✗ ComfyUI no respondió")
        sys.exit(1)

    # 3. Generar
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    workflow  = build_workflow(profile, seed)
    prompt_id = submit_workflow(workflow)
    print(f"  En cola: {prompt_id[:8]}...")

    entry = poll_result(prompt_id)
    imgs  = []
    for out in entry.get("outputs", {}).values():
        imgs.extend(out.get("images", []))

    if not imgs:
        print("✗ Sin imágenes en el resultado")
        sys.exit(1)

    img  = imgs[-1]
    dest = OUTPUT_DIR / f"{JOB_NAME}-seed{seed}.png"
    download_image(img, dest)
    print(f"\n✓ Imagen guardada: {dest}")

    # 4. Apagar pod
    stop_pod()
    print("✓ Pod apagado\n")

if __name__ == "__main__":
    main()
