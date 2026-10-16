#!/usr/bin/env python3
"""Rebuild G9's *actual successful* complete game engine, replacing ONLY
its native-GPU scene backend with the independently PS Vita proven G68 C1L1.
G70 old gameplay now restores to correct repository root (not research/).\nPurposefully consumes existing G9 CI recipe; no second gameplay main loop.
Does not alter or dispatch original G9/G68 workflows/artifacts.
This driver MUST run on an opt-in GitHub Action after 3 artifact downloads.
"""
import os
import re
import subprocess
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[3]
WORKFLOW=ROOT/".github/workflows/b24-gpu-g9-original-city-combat-beta.yml"
TEXT=WORKFLOW.read_text()
assert TEXT.count("name: Iron Man 2 GPU G9 BETA")==1, "G9 known-good recipe changed"
config=yaml.safe_load(TEXT)
steps=config["jobs"]["build"]["steps"]
assert len(steps)>=19, "G9 recipe truncated"
build=ROOT/"research/b24_unified/g70_reverse_merge"
vpk="IronMan2_GPU_B24_G70_G68_WORLD.vpk"
expected="IronMan2_GPU_B24_G9_BETA.vpk"
assets=ROOT/"work/assets"
source_vpk=Path("/tmp/g70_verified_g68_world/IronMan2_B24_G68_MarkV_Expo_Combat.vpk")

def patch_script(script:str, name:str)->str:
    if expected in script:
        script=script.replace(expected,vpk)
    script=script.replace("IM2G00034","IM2G70001")
    script=script.replace("Iron Man 2 - GPU B24 G9 BETA","Iron Man 2 - B24 G70 Merge")
    # One and only legacy G9 source assembly. Do not copy G68 main.c.
    marker="python3 research/b24_unified/apply_b24_g8_original_motion_source_only.py"
    if marker in script:
        assert script.count(marker)==1
        insert=f"""
          python3 research/b24_unified/g70_reverse_merge/g70_stage_g68_source_scene.py \\
            --vpk /tmp/g70_verified_g68_world/IronMan2_B24_G68_MarkV_Expo_Combat.vpk \\
            --out work/assets
          python3 research/b24_unified/g70_reverse_merge/apply_b24_g70_scene_backend.py"""
        script=script.replace(marker,marker+insert)
    cmake="-DB24_ENABLE_GPU=ON -DB24_ENABLE_NATIVE_HUD=ON"
    if cmake in script:
        assert script.count(cmake)==1
        script=script.replace(cmake,cmake+" -DB24_G68_CITY_BACKEND=ON")
    # Include native original G68 files in final VPK without touching older files.
    anchor="(cd work && zip -q build-vita/"+vpk+" maps/C1L1_environment.im2map"
    if anchor in script:
        assert script.count(anchor)==1
        script=script.replace(anchor,'''(cd work && zip -q build-vita/'''+vpk+''' assets/G66_city.g66m assets/G66_city_tex_*.g66t assets/G66_original_collision.g66c)
          '''+anchor)
    # Old workflow contains machine-independent G9 assertions for source-only
    # archival col mesh; keep alongside real G68 collider for audit.
    return script

def step_run(index,step):
    name=step.get("name",f"STEP_{index}")
    if "uses" in step:
        if step["uses"].startswith("actions/upload-artifact"):
            print(f"SKIP {name}: G70 workflow handles output upload",flush=True)
            return
        if step["uses"].startswith(("actions/checkout","actions/download-artifact")):
            print(f"SKIP {name}: G70 workflow performs dedicated checkout/artifact downloads",flush=True)
            return
        raise RuntimeError("Unexpected G9 workflow uses step: "+name)
    script=step.get("run")
    if not script:
        raise RuntimeError("G9 empty step "+name)
    script=patch_script(script,name)
    assert "IM2G00034" not in script and expected not in script
    print(f"\n======= G70 [{index:02d}/{len(steps)}] {name} =======",flush=True)
    env=dict(os.environ)
    # Native GitHub Actions execution uses one fresh shell per original step,
    # retaining filesystem changes only. No secrets logged.
    call=subprocess.run(["bash","-eo","pipefail"],input=script,text=True,
                        cwd=ROOT,env=env,check=False)
    if call.returncode:
        raise RuntimeError(f"G70 original G9 step {index} failed: {name}, rc={call.returncode}")

def validate_output():
    import struct,zipfile
    from hashlib import sha256
    generated=ROOT/"work/build-vita"/vpk
    assert generated.is_file(),str(generated)
    with zipfile.ZipFile(generated) as z:
        assert z.testzip() is None
        n=set(z.namelist())
        assert len([x for x in n if x.startswith("models/") and x.endswith(".im2t")])==5
        assert len([x for x in n if x.startswith("animations/") and x.endswith(".im2v")])==363
        assert len([x for x in n if x.startswith("animations/") and x.endswith(".im2k")])==6
        assert len([x for x in n if x.startswith("assets/G66_city_tex_") and x.endswith(".g66t")])==31
        assert struct.unpack_from("<4I",z.read("assets/G66_city.g66m"),4)==(1,67323,32,31)
        assert struct.unpack_from("<II",z.read("assets/G66_original_collision.g66c"),4)==(1,1910)
        assert "eboot.bin" in n
        assert b"IM2G70001" in z.read("sce_sys/param.sfo")
    print("G70 VERIFIED LINKED VPK",generated.stat().st_size,"SHA256",sha256(generated.read_bytes()).hexdigest(),flush=True)
    print("5 original G9 suits; 363 original IM2V; six WM streams; EXACT tested G68 31 atlases + native 1910 collision",flush=True)

def main():
    assert source_vpk.is_file(), "Missing downloaded G68 tested VPK snapshot"
    original_names=[s.get("name","") for s in steps]
    assert sum("Combine known-good viewer" in n for n in original_names)==1
    assert sum("Rebuild pinned vitaGL" in n for n in original_names)==1
    assert sum("Install C1L1 original game" in n for n in original_names)==1
    assert sum("G9 beta package verify" in n for n in original_names)==1
    for i,s in enumerate(steps,1):
        step_run(i,s)
    validate_output()

if __name__=="__main__":
    main()
