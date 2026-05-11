#!/usr/bin/env python3
"""
Zami Girls — Fase 1: Modelo Latina Lightskin
Rasgos: nariz prominente estilizada, cabello muy crespo, ojos azul profundo,
        labios pequeños carnosos, cejas grandes, piel lightskin con algunos granitos
"""

import json, random, time, urllib.request, urllib.parse, uuid
from pathlib import Path

COMFYUI_URL = "http://127.0.0.1:8188"
OUTPUT_DIR  = Path(__file__).parent / "test-output"
WORKFLOW    = json.loads((Path(__file__).parent / "src/workflows/face-generation.json").read_text())

# ─── PERFIL ──────────────────────────────────────────────────────────────────
PERFIL = {
    "nombre": "Latina Lightskin",

    # Encuadre
    "photo_type": "Studio white background",
    "brief_text": (
        "lightskin latina model, natural stunning beauty, striking deep blue eyes, "
        "gorgeous very tight curly hair, prominent stylized nose, small plump sexy lips, "
        "bold thick eyebrows, flirtatious smile directly at camera, a few natural skin blemishes"
    ),

    # Género y etnia
    "sex": "female",
    "ethnicity": "Latin American",

    # Ojos — azul profundo
    "eye_shape": "almond-shaped",
    "eye_size": "medium",
    "eye_tilt": "slight upward tilt",
    "eye_color": "deep blue",

    # Cejas — grandes / gruesas
    "eyebrow_thickness": "thick",
    "eyebrow_shape": "natural high arch",
    "eyebrow_color": "dark brown",

    # Nariz — prominente pero estilizada
    "nose_profile": "high bridge prominent",
    "nose_base": "medium base",
    "nose_tip": "rounded refined tip",

    # Labios — pequeños pero carnosos, forma sexy
    "lips_volume": "full lips",
    "cupid_bow": "sharply defined cupid's bow",
    "lips_proportion": "balanced full proportion",
    "lips_color": "natural nude rose",

    # Estructura ósea — estilizada y hermosa
    "forehead": "average proportion",
    "cheekbones": "high prominent cheekbones",
    "jawline": "defined elegant jawline",
    "chin": "rounded soft chin",
    "cheeks": "sculpted defined cheeks",
    "submental": "tight submental area",
    "face_neck_transition": "elongated smooth neck",

    # Cabello — muy crespo, voluminoso
    "hair_structure": "very tight coils",
    "hair_length": "medium shoulder length",
    "hair_volume": "very voluminous",
    "hair_color": "dark brown",

    # Piel — lightskin, algunos granitos (no acné)
    "skin_tone": "light",
    "skin_undertone": "warm golden undertone",
    "skin_texture": "smooth natural grain",
    "skin_micro_texture": "visible fine pores",
    "skin_imperfections": "few small blemishes",
    "skin_reflection": "natural dewy glow",
    "wrinkles": "none",
    "scars": "none",
    "deformations": "none",
    "tone_loss": "none",
    "skin_marks": "none",
    "vitiligo": "none",
    "under_eye": "none",

    # Expresión — sonrisa a cámara
    "expression": "happiness",
    "expression_variant": "Duchenne smile",
}

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

def poll_result(prompt_id, nombre, timeout=300):
    print(f"  [{nombre}] Generando", end="", flush=True)
    for _ in range(timeout // 2):
        time.sleep(2)
        try:
            data = get_json(f"{COMFYUI_URL}/history/{prompt_id}")
            if data.get(prompt_id, {}).get("outputs"):
                print(" ✓")
                return data[prompt_id]
        except Exception:
            pass
        print(".", end="", flush=True)
    raise TimeoutError(f"Timeout después de {timeout}s")

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
    with urllib.request.urlopen(url, timeout=120) as r:
        dest.write_bytes(r.read())

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  ZAMI GIRLS — Fase 1: Modelo Latina Lightskin            ║")
    print("║  Nariz prominente · Ojos azul profundo · Cabello crespo  ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    print("▸ Verificando ComfyUI...")
    try:
        stats = get_json(f"{COMFYUI_URL}/system_stats")
        vram  = stats.get("system", {}).get("vram_total", 0)
        print(f"  ✓ Activo — VRAM: {vram // 1_000_000_000} GB\n")
    except Exception as e:
        print(f"  ✗ No conecta: {e}"); return

    OUTPUT_DIR.mkdir(exist_ok=True)

    print("▸ Perfil:")
    print(f"  Nombre   : {PERFIL['nombre']}")
    print(f"  Brief    : {PERFIL['brief_text'][:80]}...")
    print(f"  Etnia    : {PERFIL['ethnicity']} | Piel: {PERFIL['skin_tone']}")
    print(f"  Ojos     : {PERFIL['eye_color']} | Cejas: {PERFIL['eyebrow_thickness']}")
    print(f"  Nariz    : {PERFIL['nose_profile']}")
    print(f"  Labios   : {PERFIL['lips_volume']} — {PERFIL['cupid_bow']}")
    print(f"  Cabello  : {PERFIL['hair_structure']} {PERFIL['hair_length']} {PERFIL['hair_color']}")
    print(f"  Piel     : {PERFIL['skin_imperfections']}")
    print(f"  Expresión: {PERFIL['expression_variant']}\n")

    seed     = rand_seed()
    workflow = build_workflow(PERFIL, seed)
    pid      = queue_prompt(workflow)
    print(f"  → En cola: {pid[:8]}... (seed: {seed})\n")

    print("▸ Generando (~2-3 min)...\n")
    try:
        entry = poll_result(pid, PERFIL["nombre"])
        img   = extract_last_image(entry)
        if not img:
            print("  ✗ No se generó imagen"); return

        dest = OUTPUT_DIR / f"latina-lightskin-seed{seed}.png"
        download_image(img, dest)
        print(f"\n  ✓ Imagen guardada: {dest.name}")

        view_url = (f"https://4yjpcxmu17d344-8188.proxy.runpod.net/view"
                    f"?filename={urllib.parse.quote(img['filename'])}&type={img['type']}")
        print(f"\n╔══════════════════════════════════════════════════════════╗")
        print(f"║  RESULTADO                                               ║")
        print(f"╚══════════════════════════════════════════════════════════╝")
        print(f"  Archivo : {img['filename']}")
        print(f"  Seed    : {seed}")
        print(f"  Ver     : {view_url}")

    except Exception as e:
        print(f"\n  ✗ Falló: {e}"); return

    # ─── GIT PUSH ─────────────────────────────────────────────────────────────
    import subprocess, shutil

    pat_file = Path("/workspace/.zami_pat")
    if not pat_file.exists():
        print("\n⚠  /workspace/.zami_pat no encontrado — saltando git push")
        return

    pat    = pat_file.read_text().strip().strip("\n\r ")
    remote = f"https://{pat}@github.com/Se7en198/Zami-girls.git"
    branch = "claude/ugc-profile-generator-PxVGb"
    repo   = Path(__file__).parent

    def run(cmd, **kw):
        return subprocess.run(cmd, shell=True, cwd=repo, capture_output=True, text=True)

    print("\n▸ Pusheando a GitHub...")
    run(f'git fetch "{remote}" {branch}:refs/remotes/origin/{branch}')
    run(f'git reset --hard refs/remotes/origin/{branch}')

    daemon_out = repo / "daemon" / "output"
    daemon_out.mkdir(parents=True, exist_ok=True)

    src  = OUTPUT_DIR / f"latina-lightskin-seed{seed}.png"
    dest = daemon_out / src.name
    if src.exists():
        shutil.copy2(src, dest)
        run("git add daemon/output/")
        run(f'git commit -m "output: latina lightskin seed{seed}"')
        result = run(f'git push "{remote}" HEAD:{branch}')
        if result.returncode == 0:
            print(f"  ✓ Imagen pusheada a GitHub: daemon/output/{dest.name}")
            # Auto-sync main
            sync = repo / "daemon" / "sync-main.sh"
            if sync.exists():
                r = subprocess.run(f'bash "{sync}"', shell=True, cwd=repo,
                                   capture_output=True, text=True)
                if r.returncode == 0:
                    print("  ✓ main sincronizado automáticamente")
                else:
                    print(f"  ⚠ sync-main: {r.stderr[:100]}")
        else:
            print(f"  ✗ Push falló: {result.stderr}")

    print("\n✓ Fase 1 completa\n")

if __name__ == "__main__":
    main()
