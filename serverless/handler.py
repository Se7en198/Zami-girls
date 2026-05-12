#!/usr/bin/env python3
"""
Zami Girls — RunPod Serverless Handler

Input:
  {
    "workflow": { ...ComfyUI workflow JSON... },
    "job_name": "Cubana"          # opcional, para nombrar la salida
  }

Output:
  {
    "images": ["base64...", ...],
    "count":  1,
    "job_name": "Cubana"
  }
"""

import runpod
import time
import uuid
import base64
import subprocess
import requests

COMFYUI_URL = "http://127.0.0.1:8188"
_comfyui_proc = None


def _start_comfyui():
    """Arranca ComfyUI (solo en cold start)."""
    proc = subprocess.Popen(
        [
            "python3", "/comfyui/main.py",
            "--listen", "0.0.0.0",
            "--port", "8188",
            "--disable-auto-launch",
        ],
        stdout=open("/tmp/comfyui.log", "w"),
        stderr=subprocess.STDOUT,
    )
    print("[handler] Esperando ComfyUI...", flush=True)
    for _ in range(90):           # espera hasta 7.5 min
        try:
            r = requests.get(f"{COMFYUI_URL}/system_stats", timeout=3)
            if r.status_code == 200:
                vram = r.json().get("system", {}).get("vram_total", 0)
                print(f"[handler] ComfyUI listo ✓  VRAM: {vram // 1_000_000_000} GB", flush=True)
                return proc
        except Exception:
            pass
        time.sleep(5)
    raise RuntimeError("ComfyUI no respondió después de 7.5 min")


def _submit_workflow(workflow: dict) -> str:
    client_id = str(uuid.uuid4())
    r = requests.post(
        f"{COMFYUI_URL}/prompt",
        json={"prompt": workflow, "client_id": client_id},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["prompt_id"]


def _poll_result(prompt_id: str, timeout: int = 600) -> dict:
    """Espera hasta que ComfyUI termine el prompt."""
    for _ in range(timeout // 3):
        time.sleep(3)
        try:
            r = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10)
            data = r.json()
            if data.get(prompt_id, {}).get("outputs"):
                return data[prompt_id]
        except Exception:
            pass
    raise TimeoutError(f"Timeout esperando prompt {prompt_id[:8]}")


def _image_to_b64(img_info: dict) -> str:
    url = (
        f"{COMFYUI_URL}/view"
        f"?filename={img_info['filename']}"
        f"&type={img_info['type']}"
        f"&subfolder={img_info.get('subfolder', '')}"
    )
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return base64.b64encode(r.content).decode()


# ─── HANDLER PRINCIPAL ────────────────────────────────────────────────────────

def handler(event):
    global _comfyui_proc

    inp      = event.get("input", {})
    workflow = inp.get("workflow")
    job_name = inp.get("job_name", "model")

    if not workflow:
        return {"error": "'workflow' es requerido en el input"}

    # Cold start: arranca ComfyUI una sola vez por worker
    if _comfyui_proc is None:
        _comfyui_proc = _start_comfyui()

    # Envía el workflow y espera resultado
    prompt_id = _submit_workflow(workflow)
    print(f"[handler] En cola: {prompt_id[:8]}...", flush=True)

    entry      = _poll_result(prompt_id)
    images_b64 = []

    for node_output in entry.get("outputs", {}).values():
        for img_info in node_output.get("images", []):
            images_b64.append(_image_to_b64(img_info))

    if not images_b64:
        return {"error": "ComfyUI no generó imágenes. Revisa el workflow."}

    print(f"[handler] Generadas {len(images_b64)} imagen(es) ✓", flush=True)
    return {
        "job_name": job_name,
        "images":   images_b64,
        "count":    len(images_b64),
    }


runpod.serverless.start({"handler": handler})
