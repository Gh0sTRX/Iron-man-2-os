#!/usr/bin/env python3
"""G284 user-owned 133834240-byte PS Vita PSVUPDAT.PUP -> isolated Vita3K.
Genuine firmware download is in GH runner TEMP only; never committed/uploaded.
All checks fail closed; results do not falsely claim gameplay.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, signal, subprocess, time
from pathlib import Path
from sys import path as syspath
syspath.insert(0,str(Path(__file__).resolve().parents[1]/"g280_vita3k_ci"))
from g280_existing_vpk_optional_probe import get_one_vpk, validate_old_vpk
PUP_SIZE=133834240
PUP_SHA256="6ef6dc8da6db026f28647713e473486d770087a605c52a8d751bfca7478386cf"
SAMPLES=(10,25,45)

def sha256(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def verify_firmware(path):
    if not path.is_file() or path.stat().st_size!=PUP_SIZE:
        raise ValueError("G284 PUP size wrong; expected user-provided original media")
    if path.open("rb").read(6)!=b"SCEUF"+bytes([0]):
        raise ValueError("G284 PUP SCEUF header mismatch")
    h=sha256(path)
    if h!=PUP_SHA256:raise ValueError("G284 PUP SHA256 mismatch")
    return {"size_bytes":PUP_SIZE,"sha256":h,"signature":"SCEUF"}

def firmware_modules(root):
    home=root/"home"
    checked=[]
    for start in [home/".local/share/Vita3K",home/".config/Vita3K",root]:
        if not start.exists():continue
        for n in ("os0","vs0","sa0","pd0"):
            for p in start.rglob(n):
                if p.is_dir():
                    checked.append(str(p.relative_to(root))[:240])
                    if len(checked)>25:break
            if len(checked)>25:break
    return checked

def run_cmd(cmd,env,limit,log):
    with log.open("wb") as out:
        try:
            p=subprocess.run(cmd,env=env,stdout=out,stderr=subprocess.STDOUT,
                             timeout=limit,check=False)
            return "exit="+str(p.returncode)
        except subprocess.TimeoutExpired:
            return "timeout="+str(limit)

def probe(app,pup,vpk,out,private):
    if not os.getenv("DISPLAY"):raise RuntimeError("G284 requires private Xvfb display")
    app=app.resolve();pup=pup.resolve();vpk=vpk.resolve()
    if not app.is_file() or not os.access(app,os.X_OK):
        raise FileNotFoundError("Official pinned Vita3K executable not found")
    pup_check=verify_firmware(pup)
    vpk_check=validate_old_vpk(vpk)
    out.mkdir(parents=True,exist_ok=True)
    private.mkdir(parents=True,exist_ok=True)
    home=private/"home";home.mkdir(exist_ok=True)
    runtime=private/"xdg";runtime.mkdir(exist_ok=True,mode=0o700);runtime.chmod(0o700)
    env=os.environ.copy()
    env.update({"HOME":str(home),"XDG_RUNTIME_DIR":str(runtime),
                "LIBGL_ALWAYS_SOFTWARE":"1","GALLIUM_DRIVER":"llvmpipe",
                "SDL_AUDIODRIVER":"dummy","MESA_LOADER_DRIVER_OVERRIDE":"llvmpipe"})
    install_cmd=[str(app),"--firmware",str(pup)]
    install_status=run_cmd(install_cmd,env,90,out/"g284_firmware_install.log")
    partitions=firmware_modules(private)
    # Historical source VPK only; the LAST valid release is still on source branch.
    # Main-firmware install may still miss separate fonts; only dismiss observed warning.
    boot_cmd=[str(app),"--console","--backend-renderer","OpenGL",str(vpk)]
    start=time.monotonic();clicks=[];samples=[]
    with (out/"g284_G161_launch.log").open("wb") as log:
        proc=subprocess.Popen(boot_cmd,env=env,stdout=log,stderr=subprocess.STDOUT,
                              start_new_session=True)
        try:
            for t in SAMPLES:
                while time.monotonic()-start<t and proc.poll() is None:
                    if shutil.which("xdotool") and time.monotonic()-start>4:
                        search=subprocess.run(["xdotool","search","--name","Missing Firmware"],
                                              capture_output=True,text=True,timeout=3,check=False)
                        # One warning dismissal after verified "Missing Firmware" title only.
                        if search.returncode==0 and not clicks:
                            click=subprocess.run(["xdotool","mousemove","586","402","click","1"],
                                                 capture_output=True,text=True,timeout=3,check=False)
                            clicks.append({"type":"acknowledge_missing_firmware_warning_only",
                                           "tool_return_code":click.returncode})
                    time.sleep(.5)
                path=out/f"g284_G161_after_main_fw_{t:02d}s.png"
                if shutil.which("scrot"):
                    capture=subprocess.run(["scrot","-z","-o",str(path)],
                                           capture_output=True,text=True,timeout=8,check=False)
                else:raise RuntimeError("No scrot")
                win=subprocess.run(["xwininfo","-root","-tree"],
                                   capture_output=True,text=True,timeout=8,check=False)
                (out/f"g284_windows_{t:02d}s.txt").write_text(win.stdout[-17000:])
                samples.append({"second":t,"image_captured":path.is_file() and capture.returncode==0,
                                "image_bytes":path.stat().st_size if path.exists() else 0,
                                "game_window_detected":bool(re.search("Vita3K",win.stdout,re.I)),
                                "window_titles":[x.strip()[:160] for x in win.stdout.splitlines()
                                    if 'Vita3K' in x or 'Firmware' in x][:10]})
                if proc.poll() is not None:break
        finally:
            if proc.poll() is None:
                try:os.killpg(proc.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:proc.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    try:os.killpg(proc.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    proc.wait(timeout=3)
    status={
        "probe":"G284_USER_SUPPLIED_PSVUPDAT_MAIN_FW_G161",
        "firmware":pup_check,
        "firmware_install_process":install_status,
        "firmware_partition_directories":partitions,
        "legacy_vpk":{"title_id":vpk_check["title_id"],"members":vpk_check["files"]},
        "warning_dismissals":clicks,
        "frames":samples,
        "gameplay_confirmed":False,"fps_confirmed":False,
        "G171_current_gamecode_tested":False,
        "physical_vita_tested":False,"new_vpk_built":False,
        "official_fonts_separately_installed":False,
        "caveat":"Screenshots must be manually reviewed. Private firmware/VPK not uploaded. Old G161 lacks G279."
    }
    (out/"g284_report.json").write_text(json.dumps(status,indent=2)+"\n")
    print("G284 actual PUP hash verified, install process",install_status,
          "source G161 detected",vpk_check["title_id"],"partitions",len(partitions),
          "screenshots",[(x["second"],x["image_captured"],x["image_bytes"]) for x in samples],
          "gameplay UNVERIFIED; NO NEW VPK")
    return status

def main():
    p=argparse.ArgumentParser()
    for x in ("app","pup","folder","out","private"):
        p.add_argument("--"+x,required=True,type=Path)
    a=p.parse_args()
    probe(a.app,a.pup,get_one_vpk(a.folder),a.out.resolve(),a.private.resolve())

if __name__=="__main__":main()
