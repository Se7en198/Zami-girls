#!/usr/bin/env python3
"""
Zami Girls — Local Job Trigger
================================
Writes a job script to /workspace/zami-next-job.sh so the daemon picks it up
on its next loop (≤20 s) WITHOUT needing GitHub write access.

Usage:
    python3 trigger-job.py <job_name>

Available jobs:
    latinas      — Generate 3 latinas (Cubana + Mexicana + Caribena)
    face-cubana  — Generate Cubana face profile
    face-mexicana — Generate Mexicana face profile
    face-caribena — Generate Caribena face profile
    inspect      — List repo contents / sanity-check env
"""

import sys
import os
import stat
import hashlib
import textwrap

TRIGGER_PATH = "/workspace/zami-next-job.sh"
JOBS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobs")

# ── Inline job definitions (fallback when the .sh file doesn't exist) ─────────

INLINE_JOBS = {
    "latinas": textwrap.dedent("""\
        #!/bin/bash
        # Job: generate 3 latinas (Cubana + Mexicana + Caribena)
        PAT=$(cat /workspace/.zami_pat | tr -d '\\n\\r ')
        REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
        BRANCH="claude/ugc-profile-generator-PxVGb"
        cd /workspace/Zami-girls
        git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" 2>/dev/null
        git reset --hard refs/remotes/origin/"$BRANCH"
        mkdir -p daemon/output test-output
        python3 test-nuevas-latinas.py
        cp test-output/*.png daemon/output/ 2>/dev/null || true
        git add daemon/output/
        git commit -m "output: 3 latinas Cubana+Mexicana+Caribena" 2>/dev/null || true
        git push "$REMOTE" HEAD:"$BRANCH" && echo "OK imagenes pusheadas"
    """),

    "face-cubana": textwrap.dedent("""\
        #!/bin/bash
        # Job: generate Cubana face profile
        PAT=$(cat /workspace/.zami_pat | tr -d '\\n\\r ')
        REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
        BRANCH="claude/ugc-profile-generator-PxVGb"
        cd /workspace/Zami-girls
        git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" 2>/dev/null
        git reset --hard refs/remotes/origin/"$BRANCH"
        mkdir -p daemon/output test-output
        python3 generate-face.py --nationality cubana
        cp test-output/*.png daemon/output/ 2>/dev/null || true
        git add daemon/output/
        git commit -m "output: face cubana" 2>/dev/null || true
        git push "$REMOTE" HEAD:"$BRANCH" && echo "OK face cubana pusheada"
    """),

    "face-mexicana": textwrap.dedent("""\
        #!/bin/bash
        # Job: generate Mexicana face profile
        PAT=$(cat /workspace/.zami_pat | tr -d '\\n\\r ')
        REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
        BRANCH="claude/ugc-profile-generator-PxVGb"
        cd /workspace/Zami-girls
        git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" 2>/dev/null
        git reset --hard refs/remotes/origin/"$BRANCH"
        mkdir -p daemon/output test-output
        python3 generate-face.py --nationality mexicana
        cp test-output/*.png daemon/output/ 2>/dev/null || true
        git add daemon/output/
        git commit -m "output: face mexicana" 2>/dev/null || true
        git push "$REMOTE" HEAD:"$BRANCH" && echo "OK face mexicana pusheada"
    """),

    "face-caribena": textwrap.dedent("""\
        #!/bin/bash
        # Job: generate Caribena face profile
        PAT=$(cat /workspace/.zami_pat | tr -d '\\n\\r ')
        REMOTE="https://${PAT}@github.com/Se7en198/Zami-girls.git"
        BRANCH="claude/ugc-profile-generator-PxVGb"
        cd /workspace/Zami-girls
        git fetch "$REMOTE" "$BRANCH":refs/remotes/origin/"$BRANCH" 2>/dev/null
        git reset --hard refs/remotes/origin/"$BRANCH"
        mkdir -p daemon/output test-output
        python3 generate-face.py --nationality caribena
        cp test-output/*.png daemon/output/ 2>/dev/null || true
        git add daemon/output/
        git commit -m "output: face caribena" 2>/dev/null || true
        git push "$REMOTE" HEAD:"$BRANCH" && echo "OK face caribena pusheada"
    """),

    "inspect": textwrap.dedent("""\
        #!/bin/bash
        # Job: sanity-check / inspect environment
        echo "=== date ===" && date
        echo "=== whoami ===" && whoami
        echo "=== pwd ===" && pwd
        echo "=== /workspace contents ===" && ls /workspace/
        echo "=== Zami-girls repo ===" && ls /workspace/Zami-girls/
        echo "=== git log (last 5) ===" && git -C /workspace/Zami-girls log --oneline -5
        echo "=== python3 version ===" && python3 --version
        echo "=== PAT present ===" && [ -f /workspace/.zami_pat ] && echo YES || echo NO
    """),
}


def load_job(job_name: str) -> str:
    """Return job script content: prefer file in jobs/, fall back to inline."""
    job_file = os.path.join(JOBS_DIR, f"{job_name}.sh")
    if os.path.isfile(job_file):
        with open(job_file) as f:
            return f.read()
    if job_name in INLINE_JOBS:
        return INLINE_JOBS[job_name]
    return None


def main():
    available = sorted(set(list(INLINE_JOBS.keys()) + [
        os.path.splitext(f)[0]
        for f in os.listdir(JOBS_DIR)
        if f.endswith(".sh")
    ])) if os.path.isdir(JOBS_DIR) else sorted(INLINE_JOBS.keys())

    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        print(f"Available jobs: {', '.join(available)}")
        sys.exit(0 if len(sys.argv) == 1 else 1)

    job_name = sys.argv[1].lower()
    content = load_job(job_name)

    if content is None:
        print(f"ERROR: Job '{job_name}' not found.")
        print(f"Available jobs: {', '.join(available)}")
        sys.exit(1)

    # Check if the same content is already waiting (avoid duplicate triggers)
    new_hash = hashlib.md5(content.encode()).hexdigest()
    if os.path.exists(TRIGGER_PATH):
        with open(TRIGGER_PATH) as f:
            existing_hash = hashlib.md5(f.read().encode()).hexdigest()
        if existing_hash == new_hash:
            print(f"[trigger-job] '{job_name}' ya está en cola (mismo hash). El daemon lo recogerá pronto.")
            sys.exit(0)
        print(f"[trigger-job] Sobreescribiendo trigger anterior con '{job_name}'.")

    with open(TRIGGER_PATH, "w") as f:
        f.write(content)

    # Make executable (daemon runs it via bash, but good practice)
    os.chmod(TRIGGER_PATH, os.stat(TRIGGER_PATH).st_mode | stat.S_IXUSR | stat.S_IXGRP)

    print(f"[trigger-job] Job '{job_name}' escrito en {TRIGGER_PATH}")
    print(f"[trigger-job] Hash: {new_hash}")
    print(f"[trigger-job] El daemon lo ejecutara en menos de {20}s.")
    print(f"[trigger-job] Sigue el progreso: tail -f /workspace/Zami-girls/daemon/daemon.log")


if __name__ == "__main__":
    main()
