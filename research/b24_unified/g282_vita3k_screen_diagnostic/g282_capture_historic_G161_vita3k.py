#!/usr/bin/env python3
"""G282: real Vita3K historical-owner G161 process + SCREEN DIAG, NO NEW VPK.

Run INSIDE xvfb-run; framebuffer captures show what GUI really rendered.
No screenshot is ever classified as gameplay without human review.
The old G161 VPK is strictly validated; proprietary VPK is not copied to
output. Vita system firmware is NOT downloaded or installed by this task.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time
from typing import Any

from sys import path as sys_path
sys_path.insert(0, str(Path(__file__).resolve().parents[1] / "g280_vita3k_ci"))
from g280_existing_vpk_optional_probe import get_one_vpk, validate_old_vpk

SAMPLES=(10,25,43)
LOG_MAX=6*1024*1024
KEYWORDS={
    "firmware": re.compile(r"firmware|\bpup\b|system modules|no modules|sysmodule",re.I),
    "initial_setup": re.compile(r"welcome|first run|set.up|initiali[sz].*config|config.*initial",re.I),
    "app_loader": re.compile(r"eboot|title.?id|install.*app|load.*app|installed.*app",re.I),
    "graphics": re.compile(r"vulkan|opengl|shader|swapchain|gpu|render",re.I),
    "errors": re.compile(r"\berror\b|\bfail(?:ed|ure)?\b|\bwarn(?:ing)?\b|exception",re.I),
}

def compact_log(p:Path,max_lines:int=65)->dict[str,list[str]]:
    if not p.exists():return {k:[] for k in KEYWORDS}
    if p.stat().st_size>LOG_MAX:raise RuntimeError("G282 log exceeded bounded collection budget")
    lines=p.read_text(encoding="utf-8",errors="replace").splitlines()
    out={}
    for category,rx in KEYWORDS.items():
        # Strip runner paths and potential personal local variables.
        found=[re.sub(r"/home/runner/[^ ]+","[runner-path]",s)[:320] for s in lines if rx.search(s)]
        out[category]=found[-max_lines:]
    return out

def run(app:Path,vpk:Path,out:Path)->dict[str,Any]:
    if not os.environ.get("DISPLAY"):
        raise RuntimeError("G282 needs Xvfb-run exported DISPLAY; refuse unguarded desktop capture")
    if not app.is_file() or not os.access(app,os.X_OK):
        raise FileNotFoundError("G282 verified official Vita3K AppRun not executable")
    meta=validate_old_vpk(vpk)
    if not shutil.which("scrot") or not shutil.which("xwininfo"):
        raise FileNotFoundError("G282 requires scrot/xwininfo to observe actual X display")
    out.mkdir(parents=True,exist_ok=True)
    home=out/"isolated_home"
    home.mkdir(exist_ok=True)
    runtime=out/"xdg_runtime"
    runtime.mkdir(exist_ok=True,mode=0o700)
    runtime.chmod(0o700)
    env=os.environ.copy()
    env.update({
        "HOME":str(home.resolve()),"XDG_RUNTIME_DIR":str(runtime.resolve()),
        "LIBGL_ALWAYS_SOFTWARE":"1","GALLIUM_DRIVER":"llvmpipe",
        "SDL_AUDIODRIVER":"dummy","MESA_LOADER_DRIVER_OVERRIDE":"llvmpipe",
    })
    cmd=[str(app.resolve()),"--console","--backend-renderer","OpenGL",str(vpk.resolve())]
    log=out/"vita3k_stdout_stderr.txt"
    snaps=[]
    start=time.monotonic()
    exit_code=None
    with log.open("wb") as fd:
        proc=subprocess.Popen(cmd,stdout=fd,stderr=subprocess.STDOUT,
                              env=env,start_new_session=True)
        try:
            for t in SAMPLES:
                while time.monotonic()-start<t and proc.poll() is None:
                    time.sleep(.35)
                frame=out/f"vita3k_display_{t:02d}s.png"
                windows=out/f"vita3k_windows_{t:02d}s.txt"
                take=subprocess.run(["scrot","-z","-o",str(frame)],
                                    timeout=10,check=False,capture_output=True,text=True)
                tree=subprocess.run(["xwininfo","-root","-tree"],
                                    timeout=10,check=False,capture_output=True,text=True)
                windows.write_text((tree.stdout or tree.stderr)[-18000:],encoding="utf-8")
                snaps.append({
                    "time_requested_seconds":t,
                    "screenshot_captured":take.returncode==0 and frame.is_file(),
                    "screenshot_bytes":frame.stat().st_size if frame.is_file() else 0,
                    "mapped_vita3k_window_name":bool(re.search("Vita3K",tree.stdout or "",re.I)),
                    "exit_at_sample":proc.poll(),
                })
                if proc.poll() is not None:break
        finally:
            if proc.poll() is None:
                try:os.killpg(proc.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    try:os.killpg(proc.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    proc.wait(timeout=3)
            exit_code=proc.returncode
    report={
        "probe":"G282_REAL_OLD_G161_VITA3K_SCREEN_AND_STARTUP",
        "package":{"historic_title_id":meta["title_id"],"members":meta["files"],"size_bytes":meta["bytes"]},
        "emulator":"official Vita3K 4206, software OpenGL via Xvfb",
        "time_seconds":round(time.monotonic()-start,1),
        "emulator_exit_code_after_termination":exit_code,
        "screen_evidence":snaps,
        "log_findings":compact_log(log),
        "initial_wizard_or_firmware_state":"TO_BE_REVIEWED_FROM_CAPTURED_SCREEN",
        "gameplay_frame_confirmed":False,
        "world_motion_confirmed":False,
        "fps_confirmed":False,
        "physical_vita_confirmed":False,
        "new_vpk_built":False,
        "technical_qualification":"Screenshots/window/log are evidence only. They do not establish C1L1 gameplay, G171 motion or current G279 without explicit inspection."
    }
    (out/"g282_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    # Use summary instead of printing entire potentially noisy emulator log.
    print(f"G282 reached old-G161 Vita3K attempt for {len(snaps)} screenshot sample(s); "
          f"mapped Vita3K windows={sum(x['mapped_vita3k_window_name'] for x in snaps)}; "
          f"exit_code={exit_code}. NO NEW VPK. GAMEPLAY NOT CLAIMED.")
    print("G282 bounded log evidence categories: "+", ".join(f"{k}={len(v)}" for k,v in report["log_findings"].items()))
    for k in ("errors","initial_setup","firmware","app_loader"):
        for s in report["log_findings"][k][-8:]:
            print("G282 "+k+": "+s[:220])
    return report

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--app",type=Path,required=True)
    p.add_argument("--folder",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.app,get_one_vpk(a.folder),a.out.resolve())

if __name__=="__main__":
    main()
