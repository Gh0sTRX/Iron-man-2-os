#!/usr/bin/env python3
"""Optional manual G280 isolated Vita3K attempt for ALREADY BUILT G161 VPK.
Best-effort emulator capability probe, not new VitaSDK build nor valid
physical Vita performance/movement verification. No game asset uploaded.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
import zipfile

def get_one_vpk(folder:Path)->Path:
    candidates=[x for x in folder.rglob("*.vpk") if x.is_file()]
    if len(candidates)!=1:raise ValueError(f"One existing VPK required; found {len(candidates)}")
    p=candidates[0]
    if p.stat().st_size>450*1024*1024 or p.stat().st_size<50000:
        raise ValueError("Existing VPK size outside supported bounded test")
    return p

def validate_old_vpk(vpk:Path)->dict:
    with zipfile.ZipFile(vpk) as z:
        if len(z.infolist())>4000:raise ValueError("Too many VPK file members")
        names=set()
        total=0
        for f in z.infolist():
            name=f.filename
            if name.startswith("/") or "\\" in name or ".." in name.split("/") or not name:
                raise ValueError("Unsafe VPK path")
            if name in names:raise ValueError("Duplicate VPK archive member")
            names.add(name)
            total+=f.file_size
            if total>900*1024*1024:raise ValueError("Unbounded VPK content")
        if not {"eboot.bin","sce_sys/param.sfo"}.issubset(names):
            raise ValueError("Not a minimal Vita runnable VPK")
        if z.testzip() is not None:raise ValueError("Corrupt VPK ZIP")
        sfo=z.read("sce_sys/param.sfo")
        if b"IM2G16101" not in sfo:
            raise ValueError("Wrong VPK title ID (only historic user-authorized G161 accepted)")
        return {"vpk_name":vpk.name,"files":len(names),"bytes":vpk.stat().st_size,
                "title_id":"IM2G16101","legacy_G161":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--app",required=True,type=Path)
    p.add_argument("--folder",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    vpk=get_one_vpk(args.folder)
    meta=validate_old_vpk(vpk)
    app=args.app.resolve()
    if not app.is_file():raise ValueError("Vita3K extracted AppRun missing")
    log=args.output/"g280_existing_G161_emulator_attempt.txt"
    cmd=["xvfb-run","-a","-s","-screen 0 960x544x24",
         str(app),"--console",str(vpk.resolve())]
    env=os.environ.copy()
    env["LIBGL_ALWAYS_SOFTWARE"]="1"
    env["GALLIUM_DRIVER"]="llvmpipe"
    env["SDL_AUDIODRIVER"]="dummy"
    env["XDG_RUNTIME_DIR"]=str((args.output/"xdg_runtime").resolve())
    Path(env["XDG_RUNTIME_DIR"]).mkdir(mode=0o700,exist_ok=True)
    env["HOME"]=str((args.output/"emulator_home").resolve())
    Path(env["HOME"]).mkdir(exist_ok=True)
    start=time.monotonic()
    with log.open("w") as f:
        f.write("G280 EXISTING ORIGINAL OWNER G161 VPK ONE EMULATOR ATTEMPT\n")
        f.write("This is NOT a boot-success assertion, without firmware or real Vita device.\n")
        f.flush()
        try:
            proc=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,
                timeout=60,check=False)
            status=f"process_returned={proc.returncode}"
        except subprocess.TimeoutExpired:
            status="process_timed_out_after_60s_UNVERIFIED"
        f.write("\nG280 "+status+"\n")
    # A process remaining alive or returning zero is NOT proof it got to game.
    report={**meta,"attempted":True,"observed_process":status,
            "game_boot_confirmed":False,"rendered_frame_confirmed":False,
            "fps_confirmed":False,"ground_walk_confirmed":False,
            "hardware_tested":False,"firmware_installed_by_this_job":False,
            "new_vpk_built":False,
            "diagnosis":"Vita3K CLI exploratory only. Human firmware/setup and game-frame review needed."}
    (args.output/"g280_emulator_result.json").write_text(json.dumps(report,indent=2)+"\n")
    print("G280 OPTIONAL existing G161 emulator probe finished:",status,
          "boot/gpu/fps/gameplay all UNVERIFIED; source game untouched, NO NEW VPK")

if __name__=="__main__":
    main()
