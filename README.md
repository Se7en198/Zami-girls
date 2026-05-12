# Zami Girls — AI Virtual Influencer UGC Studio

Automated pipeline for generating AI virtual influencer content using ComfyUI on RunPod Serverless. The system uses an on-demand endpoint that scales to zero, optimizing costs and eliminating the legacy daemon-polling logic.

---

## Automation Rules — READ FIRST

This system is FULLY AUTOMATED via RunPod Serverless.

### How it works:
1. User interacts with Dashboard/Claude → Request sent to RunPod API.
2. RunPod Serverless Endpoint (`aqzsu0jydlras1`) activates a GPU worker.
3. Worker executes the ComfyUI workflow → Returns images in base64.
4. Dashboard displays the results immediately.

### Key Deployment Info:
- **Endpoint ID**: `aqzsu0jydlras1`
- **Worker Repo**: [Se7en198/comfyui-aion-creador-de-rostros-con-nano-banana-pro](https://github.com/Se7en198/comfyui-aion-creador-de-rostros-con-nano-banana-pro)
- **API Key**: (Stored in .env)

### User NEVER needs to:

- Open a pod terminal
- Copy-paste commands
- Manually trigger anything

### User ONLY does once (initial setup):
1. Run `bash /workspace/Zami-girls/daemon/setup.sh` on the pod
2. Enter GitHub PAT when prompted (needs repo write scope)

### If Claude can't push to GitHub:
- This happens when the MCP write token expires for a specific session
- Fix: Start a new Claude Code session (takes 30 seconds)
- The system design is correct — this is a temporary session issue

- **Repo**: https://github.com/Se7en198/Zami-girls
- **Branch**: `claude/ugc-profile-generator-PxVGb`
- **Pod**: `4yjpcxmu17d344` — 1001 GB Network Volume
- **ComfyUI**: `http://127.0.0.1:8188` (proxy: `https://4yjpcxmu17d344-8188.proxy.runpod.net`)

---

## Architecture

```
  Claude Code (local / web)
        │
        │  writes daemon/current-job.sh
        │  reads  daemon/results/ + daemon/output/
        ▼
  GitHub (branch: claude/ugc-profile-generator-PxVGb)
        │
        │  git fetch every 20s
        ▼
  RunPod Pod (4yjpcxmu17d344)
  ┌─────────────────────────────────┐
  │  zami-daemon.sh                 │
  │    polls GitHub → runs job      │
  │    pushes results back          │
  │                                 │
  │  ComfyUI (port 8188)            │
  │    Phase 1: face-generation     │
  │    Phase 2: body-generation     │
  └─────────────────────────────────┘
        │
        │  daemon/output/*.png
        │  daemon/results/*.txt
        ▼
  GitHub (results visible to Claude)
```

---

## 6-Phase Pipeline

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Face generation (AION + z_image_turbo) | Active |
| 1b | Character sheet (GeminiNanoBanana2, 5-view) | Requires Gemini API key |
| 2 | Body generation (Qwen Image Edit) | Active |
| 3 | Profile / persona creation | Planned |
| 4 | Content calendar | Planned |
| 5 | Community responses | Planned |
| 6 | KPI analysis | Planned |

---

## Pod Setup (one-time)

Run this in the RunPod web terminal:

```bash
git clone -b claude/ugc-profile-generator-PxVGb \
  https://github.com/Se7en198/Zami-girls.git /workspace/Zami-girls

bash /workspace/Zami-girls/daemon/setup.sh
```

When prompted, paste a GitHub PAT with `repo` (write) scope. The daemon starts automatically in the background.

**What setup.sh does:**
1. Saves PAT to `/workspace/.zami_pat` (mode 600)
2. Clones or updates the repo to `/workspace/Zami-girls`
3. Kills any previous daemon instance
4. Launches `zami-daemon.sh` via `nohup` and saves PID to `/tmp/zami-daemon.pid`

---

## Daemon Reference

**File**: `daemon/zami-daemon.sh`

The daemon loops every 20 seconds:
1. Fetches `daemon/current-job.sh` from GitHub (only that file — does not reset local commits)
2. Computes MD5 of the job file
3. If hash is new (not in `/tmp/zami-done/`), runs `bash current-job.sh`
4. Marks hash as done; job pushes its own results via `git push`

**Useful commands on the pod:**

```bash
# View live logs
tail -f /workspace/Zami-girls/daemon/daemon.log

# Check daemon is running
cat /tmp/zami-daemon.pid && ps aux | grep zami-daemon

# Restart daemon manually
bash /workspace/Zami-girls/daemon/setup.sh
```

**Dispatching a job (from Claude or locally):**

Edit `daemon/current-job.sh` with your script, then commit and push to the branch. The daemon will pick it up within 20 seconds.

Job scripts must push their own results:
```bash
# Standard result push pattern inside a job script
PAT=$(cat /workspace/.zami_pat | tr -d '\n\r ')
REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
BRANCH="claude/ugc-profile-generator-PxVGb"
REPO_DIR="/workspace/Zami-girls"

cd "$REPO_DIR"
git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH"
git reset --hard refs/remotes/origin/"$BRANCH"
mkdir -p daemon/results
echo "output here" > daemon/results/my-result.txt
git add daemon/results/my-result.txt
git commit -m "result: my-result"
git push "$REMOTE" HEAD:"$BRANCH"
```

---

## Workflows

### Phase 1 — Face Generation

**File**: `src/workflows/face-generation.json`

Key models:
- `z_image_turbo_bf16.safetensors` — main image model
- `qwen_3_4b.safetensors` (lumina2) — language backbone
- LoRA: `skin-texture`
- LoRA: `RealisticSnapshot`

Key nodes:

| Node | Type | Role |
|------|------|------|
| 82 | `AionFluxPrompterNode` | 33 morphological parameters |
| 78 | KSampler | main seed |
| 14 | KSamplerAdvanced | noise_seed |
| 73 | SeedVarianceEnhancer | seed variance |
| 6, 57 | SaveImage | output |

### Phase 1b — Character Sheet (multi-view)

**File**: `src/workflows/face-generation-nano-banana.json`

Adds `GeminiNanoBanana2` node to produce 5-view character sheets. Requires a Gemini API key (free tier available at [aistudio.google.com](https://aistudio.google.com)).

### Phase 2 — Body Generation

**File**: `src/workflows/body-generation.json`

Key models:
- `qwen_image_edit_2511_bf16.safetensors` — image editing backbone
- `qwen_2.5_vl_7b_fp8_scaled.safetensors` — vision-language model

Key nodes:

| Node | Type | Role |
|------|------|------|
| 41 | LoadImage | Phase 1 face reference |
| 321 | `TextEncodeQwenImageEditPlus` | body prompt |
| 333 | KSampler | seed |
| 334 | SEXGOD LoRA | style LoRA |

---

## Test Scripts

All scripts run locally on the pod with ComfyUI active at `http://127.0.0.1:8188`.

### Generate 3 Latina profiles (recommended)

```bash
cd /workspace/Zami-girls && python3 test-nuevas-latinas.py
```

Generates 4 face variants for each of the 3 pre-designed profiles. Output saved to `test-output/`.

### Generate 4 generic face variants

```bash
cd /workspace/Zami-girls && python3 test-fase1.py
```

Uses a basic Hispanic template with medium skin, brown eyes, dark brown shoulder-length hair.

### Generate 4 body variants from a face

```bash
cd /workspace/Zami-girls && python3 test-fase2.py <comfyui_filename>
# Example:
python3 test-fase2.py z-image_00018_.png
```

`<comfyui_filename>` is the filename as ComfyUI saved it (shown in the Phase 1 output summary), not a full path.

Generates 4 body type variations: Curvy, Athletic, Slim, Thick.

---

## Latina Model Profiles

Three top-ranked latina identities pre-designed in `test-nuevas-latinas.py`:

| Profile | Inspiration | Skin | Eyes | Hair | Expression |
|---------|-------------|------|------|------|------------|
| La Cubana | Ana de Armas | light warm olive | large almond dark brown | long wavy dark brown | warm smile |
| La Mexicana | Eiza González | medium warm | large almond dark brown | very long straight dark brown | confident |
| La Caribeña | Adria Arjona / JLo | medium-tan golden | large almond dark brown | very long wavy voluminous | Duchenne smile |

---

## AION Portrait Parameters (33 total)

Full reference in `PORTRAIT-GENERATOR.md`. Key groups:

| Group | Parameters |
|-------|-----------|
| Demographics | `sex`, `ethnicity`, `photo_type` |
| Eyes | `eye_shape`, `eye_size`, `eye_tilt`, `eye_color`, `eyebrow_thickness`, `eyebrow_shape`, `eyebrow_color` |
| Nose | `nose_profile`, `nose_base`, `nose_tip` |
| Lips | `lips_volume`, `cupid_bow`, `lips_proportion`, `lips_color` |
| Face structure | `forehead`, `cheekbones`, `jawline`, `chin`, `cheeks`, `submental`, `face_neck_transition` |
| Hair | `hair_structure`, `hair_length`, `hair_volume`, `hair_color` |
| Skin | `skin_tone`, `skin_undertone`, `skin_texture`, `skin_micro_texture`, `skin_imperfections`, `skin_reflection` |
| Skin defects | `wrinkles`, `scars`, `deformations`, `tone_loss`, `skin_marks`, `vitiligo`, `under_eye` (all `none` for models) |
| Expression | `expression`, `expression_variant` |

To override a parameter in a script, set it in `wf["82"]["inputs"][key] = value` before queuing the prompt.

---

## Quality Gates (Phase 1 → Phase 2)

Before advancing a face image to body generation:

- Single person, clean and fully visible face
- Photorealistic — not beauty-CGI or plastic
- No watermarks, text, or collage artifacts
- Features consistent with the designed ethnic profile
- Natural and compelling expression
- Realistic skin texture (visible pores, not airbrushed)

---

## File Structure

```
Zami-girls/
├── daemon/
│   ├── zami-daemon.sh        # main daemon loop
│   ├── setup.sh              # one-time pod setup
│   ├── current-job.sh        # current job (rewritten by Claude)
│   ├── results/              # text results pushed by jobs
│   └── output/               # images pushed by jobs
├── src/workflows/
│   ├── face-generation.json              # Phase 1 API workflow
│   ├── face-generation-nano-banana.json  # Phase 1b with character sheets
│   └── body-generation.json             # Phase 2 API workflow
├── test-fase1.py             # 4 generic face variants
├── test-fase2.py             # 4 body variants from a face
├── test-nuevas-latinas.py    # 3 latina profiles (recommended)
├── test-latinas.py           # alternate latina profiles
└── PORTRAIT-GENERATOR.md     # full AION parameters reference
```

---

## Troubleshooting

**Daemon not running:**
```bash
# Check PID
cat /tmp/zami-daemon.pid
ps aux | grep zami

# Restart
bash /workspace/Zami-girls/daemon/setup.sh
```

**ComfyUI not responding:**
```bash
# Check if process is up
ps aux | grep comfyui

# Test endpoint
curl -s http://127.0.0.1:8188/system_stats | python3 -m json.tool
```

**Job not being picked up:**
- Verify `daemon/current-job.sh` was actually pushed to the branch
- Check daemon log: `tail -20 /workspace/Zami-girls/daemon/daemon.log`
- The job only runs if its MD5 hash is new. To re-run the same job, add a comment or whitespace change to force a new hash.

**Push fails in job script:**
- PAT may be expired. Re-run `setup.sh` and enter a fresh PAT.
- Check PAT has `repo` write scope, not just `read`.

**Phase 1b (GeminiNanaBanana) fails:**
- Node requires a Gemini API key. Get a free key at https://aistudio.google.com
- Verify the custom node is installed in `/workspace/runpod-slim/ComfyUI/custom_nodes/`
