# Zami Girls — Automation Design

## The Golden Rule

**Claude writes to GitHub. The daemon executes. Results come back.**
Users never type pod commands after initial setup.

---

## Complete Automation Loop

```
  ┌─────────────────────────────────────────────────────────┐
  │  USER                                                   │
  │  "Generate a Latina model, olive skin, wavy hair"       │
  └──────────────────────┬──────────────────────────────────┘
                         │  (just talks to Claude)
                         ▼
  ┌─────────────────────────────────────────────────────────┐
  │  CLAUDE CODE  (local or web session)                    │
  │  • Builds job script (current-job.sh)                   │
  │  • Pushes to GitHub via MCP tools                       │
  └──────────────────────┬──────────────────────────────────┘
                         │  git push → branch
                         ▼
  ┌─────────────────────────────────────────────────────────┐
  │  GITHUB  (branch: claude/ugc-profile-generator-PxVGb)  │
  │  • Stores daemon/current-job.sh                         │
  │  • Stores daemon/results/*.txt                          │
  │  • Stores daemon/output/*.png                           │
  └──────────────────────┬──────────────────────────────────┘
                         │  git fetch every 20s
                         ▼
  ┌─────────────────────────────────────────────────────────┐
  │  RUNPOD POD  (4yjpcxmu17d344)                           │
  │                                                         │
  │  zami-daemon.sh  ──► sees new job hash                  │
  │       │                                                 │
  │       ▼                                                 │
  │  bash current-job.sh                                    │
  │       │                                                 │
  │       ▼                                                 │
  │  ComfyUI API (port 8188)                                │
  │       │  generates images                               │
  │       ▼                                                 │
  │  git push results → GitHub                              │
  └──────────────────────┬──────────────────────────────────┘
                         │  results visible on branch
                         ▼
  ┌─────────────────────────────────────────────────────────┐
  │  CLAUDE CODE  reads results via MCP                     │
  │  • Shows image filenames / summaries to user            │
  └─────────────────────────────────────────────────────────┘
```

---

## What Each File Does

| File | Who touches it | Purpose |
|------|---------------|---------|
| `daemon/current-job.sh` | Claude (writes), daemon (reads) | The active job script — rewritten for each new request |
| `daemon/zami-daemon.sh` | Daemon only | Main polling loop — runs on the pod, never edited by Claude |
| `daemon/setup.sh` | User (once) | One-time pod bootstrap — installs PAT, starts daemon |
| `daemon/results/*.txt` | Job scripts (write), Claude (reads) | Text output: filenames, logs, status |
| `daemon/output/*.png` | Job scripts (write), Claude (reads) | Generated images pushed from pod |
| `/tmp/zami-daemon.pid` | setup.sh (write), daemon (runtime) | PID file for the running daemon process |
| `/workspace/.zami_pat` | setup.sh (write), daemon (runtime) | GitHub PAT stored on pod, mode 600 |

---

## Daemon Internals

`zami-daemon.sh` loop (runs every 20 seconds):

1. `git fetch` only `daemon/current-job.sh` from GitHub (does not reset local work)
2. Compute MD5 hash of the fetched file
3. Check `/tmp/zami-done/<hash>` — if file exists, job already ran, skip
4. If hash is new: run `bash current-job.sh`
5. Write hash to `/tmp/zami-done/<hash>` so it never runs twice
6. Job script is responsible for pushing its own results via `git push`

---

## Debugging: Daemon Not Picking Up Jobs

Work through these steps in order:

### Step 1 — Confirm the job was actually pushed
```bash
# On pod: check if current-job.sh matches what Claude pushed
cd /workspace/Zami-girls
git fetch origin claude/ugc-profile-generator-PxVGb
git show origin/claude/ugc-profile-generator-PxVGb:daemon/current-job.sh | head -5
```

### Step 2 — Check if daemon is alive
```bash
cat /tmp/zami-daemon.pid
ps aux | grep zami-daemon | grep -v grep
```
If no process: run `bash /workspace/Zami-girls/daemon/setup.sh` to restart.

### Step 3 — Read the daemon log
```bash
tail -30 /workspace/Zami-girls/daemon/daemon.log
```
Look for:
- `[new job]` — daemon detected the job and ran it
- `[skip]` — same hash as before (job script unchanged — add a whitespace tweak to force new hash)
- Error lines from ComfyUI or git

### Step 4 — Check job hash deduplication
```bash
ls /tmp/zami-done/
```
If the hash of the current job is already there, the daemon considers it done.
To force a re-run, change any byte in `daemon/current-job.sh` (e.g., add a comment).

### Step 5 — Verify ComfyUI is responding
```bash
curl -s http://127.0.0.1:8188/system_stats | python3 -m json.tool
```
If no response, ComfyUI is down — restart it via the RunPod UI.

### Step 6 — Check PAT validity
```bash
PAT=$(cat /workspace/.zami_pat)
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: token $PAT" \
  https://api.github.com/repos/Se7en198/Zami-girls
```
Should return `200`. If `401`, PAT is expired — re-run `setup.sh` with a fresh PAT.

---

## Emergency Manual Trigger (JupyterLab)

If Claude cannot push to GitHub (expired MCP session) and you need to run a job immediately:

1. Open JupyterLab on the pod: `http://<pod-ip>:8888` (RunPod proxy port 8888)
2. Open a terminal in JupyterLab
3. Run the job script directly:
```bash
cd /workspace/Zami-girls
bash daemon/current-job.sh
```

Or write and run a custom script directly in a JupyterLab notebook cell:
```python
import subprocess
result = subprocess.run(
    ["bash", "/workspace/Zami-girls/daemon/current-job.sh"],
    capture_output=True, text=True
)
print(result.stdout)
print(result.stderr)
```

**Note**: This is emergency-only. The normal path is always Claude → GitHub → daemon.

---

## MCP Session Token Expiry

Claude uses MCP (Model Context Protocol) tools to push to GitHub. These tools require a write-scoped token that is bound to the Claude Code session. If a session is long-lived, this token can expire.

**Symptom**: Claude reports it cannot push or gets a permission error from GitHub.

**Fix**: Start a new Claude Code session. Takes ~30 seconds. The system design is correct — this is not a code bug.

The daemon's PAT (stored in `/workspace/.zami_pat`) is separate and does not expire unless you manually revoke it.
