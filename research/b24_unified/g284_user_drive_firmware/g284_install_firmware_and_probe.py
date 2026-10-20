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

def initialize_first_run(app, env, out):
    """Vita3K GUI first-run must create config in the same isolated HOME,
    otherwise --firmware on a clean Linux profile throws boost create_directories
    Invalid argument before any real PUP install. No arbitrary dialog acceptance.
    """
    start=time.monotonic()
    with (out/"g285_first_run_bootstrap.log").open("wb") as log:
        proc=subprocess.Popen([str(app)],env=env,stdout=log,stderr=subprocess.STDOUT,
                              start_new_session=True)
        clicked=False
        try:
            while time.monotonic()-start<11 and proc.poll() is None:
                if not clicked and time.monotonic()-start>3 and shutil.which("xdotool"):
                    d=subprocess.run(["xdotool","search","--name","Welcome to Vita3K"],
                                     timeout=3,capture_output=True,text=True,check=False)
                    if d.returncode==0:
                        p=subprocess.run(["xdotool","mousemove","135","407","click","1"],
                                         timeout=3,capture_output=True,text=True,check=False)
                        clicked=p.returncode==0
                time.sleep(.35)
        finally:
            if proc.poll() is None:
                try:os.killpg(proc.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:proc.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    try:os.killpg(proc.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    proc.wait(timeout=3)
    return {"welcome_ok_clicked":clicked,"process_return":proc.returncode,
            "config_candidates":[str(p.relative_to(Path(env["HOME"]))) for p in Path(env["HOME"]).rglob("config.yml")][:15]}

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
    config_home=private/"config";config_home.mkdir(exist_ok=True)
    cache_home=private/"cache";cache_home.mkdir(exist_ok=True)
    data_home=home/".local/share";data_home.mkdir(parents=True,exist_ok=True)
    env.update({"HOME":str(home),"XDG_RUNTIME_DIR":str(runtime),
                "XDG_CONFIG_HOME":str(config_home.resolve()),
                "XDG_CACHE_HOME":str(cache_home.resolve()),
                "XDG_DATA_HOME":str(data_home.resolve()),
                "LIBGL_ALWAYS_SOFTWARE":"1","GALLIUM_DRIVER":"llvmpipe",
                "SDL_AUDIODRIVER":"dummy","MESA_LOADER_DRIVER_OVERRIDE":"llvmpipe"})
    first_run=initialize_first_run(app,env,out)
    install_cmd=[str(app),"--firmware",str(pup)]
    install_status=run_cmd(install_cmd,env,90,out/"g284_firmware_install.log")
    partitions=firmware_modules(private)
    # Historical source VPK only; the LAST valid release is still on source branch.
    # Main-firmware install may still miss separate fonts; only dismiss observed warning.
    # G290 real error: the GitHub Xvfb/OpenGL driver cannot create the
    # requested minimum GL4.4 context. Native Vita3K Vulkan renderer through
    # Mesa lavapipe is an independent software-GPU smoke path; do not claim
    # it models physical Vita performance.
    # Ubuntu/Mesa 25 may install lavapipe manifests under different names.
    # Only set explicit ICD when an actual verified manifest exists.
    icd_paths=sorted(Path("/usr/share/vulkan/icd.d").glob("*lvp*.json"))
    if icd_paths:
        env["VK_ICD_FILENAMES"]=str(icd_paths[0])
    else:
        env.pop("VK_ICD_FILENAMES",None)
    boot_cmd=[str(app),"--console","--backend-renderer","Vulkan",str(vpk)]
    start=time.monotonic();clicks=[];samples=[];welcome_dismissed=False;update_modal_attempts=0;font_modal_attempts=0
    with (out/"g284_G161_launch.log").open("wb") as log:
        proc=subprocess.Popen(boot_cmd,env=env,stdout=log,stderr=subprocess.STDOUT,
                              start_new_session=True)
        try:
            for t in SAMPLES:
                while time.monotonic()-start<t and proc.poll() is None:
                    if shutil.which("xdotool") and time.monotonic()-start>3:
                        # Vita3K Qt first run welcome has "Show next time" checked.
                        # Dismiss only observed welcome UI; do not install other files.
                        if not welcome_dismissed:
                            welcome=subprocess.run(["xdotool","search","--name","Welcome to Vita3K"],
                                capture_output=True,text=True,timeout=3,check=False)
                            if welcome.returncode==0:
                                c1=subprocess.run(["xdotool","mousemove","722","407","click","1"],
                                    capture_output=True,text=True,timeout=3,check=False)
                                c2=subprocess.run(["xdotool","mousemove","135","407","click","1"],
                                    capture_output=True,text=True,timeout=3,check=False)
                                welcome_dismissed=(c1.returncode==0 and c2.returncode==0)
                                clicks.append({"type":"welcome_uncheck_show_next_time_then_OK",
                                               "tool_return_code":int(not welcome_dismissed)})
                                time.sleep(.5)
                        # Observed G288 Vita3K "Update Available" obstructs the
                        # already installed old-G161's Font warning. NEVER upgrade
                        # pinned Build4206; click only informational OK x548,y376.
                        update=subprocess.run(["xdotool","search","--onlyvisible","--name","Update Available"],
                            capture_output=True,text=True,timeout=3,check=False)
                        if update.returncode==0 and update_modal_attempts<3:
                            update_modal_attempts+=1
                            u_id=update.stdout.strip().splitlines()[-1]
                            subprocess.run(["xdotool","windowactivate",u_id],capture_output=True,
                                           text=True,timeout=3,check=False)
                            ack=subprocess.run(["xdotool","mousemove","--window",u_id,"100","135","click","1"],
                                               capture_output=True,text=True,timeout=3,check=False)
                            clicks.append({"type":"dismiss_exact_Update_Available_without_upgrading",
                                           "attempt":update_modal_attempts,"return_code":ack.returncode})
                        else:
                            search=subprocess.run(["xdotool","search","--onlyvisible","--name","Missing Firmware"],
                                                  capture_output=True,text=True,timeout=3,check=False)
                            if search.returncode==0 and font_modal_attempts<3:
                                font_modal_attempts+=1
                                wid=search.stdout.strip().splitlines()[-1]
                                focus=subprocess.run(["xdotool","windowactivate",wid],
                                    timeout=3,capture_output=True,text=True,check=False)
                                time.sleep(.2)
                                click=subprocess.run(["xdotool","mousemove","--window",wid,"98","175","click","1"],
                                    timeout=3,capture_output=True,text=True,check=False)
                                clicks.append({"type":"acknowledge_optional_missing_Font_package_only",
                                    "attempt":font_modal_attempts,"tool_return_code":click.returncode,
                                    "focus_return_code":focus.returncode})
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
        "probe":"G291_USER_SUPPLIED_PSVUPDAT_MAIN_FW_G161_VULKAN_LAVAPIPE",
        "renderer_probe":"Vulkan lavapipe, no physical PS Vita GPU",
        "firmware":pup_check,
        "first_run_bootstrap":first_run,
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
    print("G285 first-run initialized",first_run,"PUP install process",install_status,
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
