#!/usr/bin/env python3
"""B24 canonical player animation coverage report: authentic SOURCE NAMES vs baked IM2V.

B15 source archive is the 2010 iOS 304-name metadata audit, NOT full raw .anim
keyframe contents. It is incorrect to claim a named source clip is already
baked or appears on real PS Vita. Use --vita-animations-dir after B24 overlays
are assembled to inventory actual shipped .im2v files, else source-only mode.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import zipfile
ROOT=Path(__file__).resolve().parents[2]
ARCH=ROOT/"research/B15_Original_All_Mechanics_Audit.zip"
SOURCE_MD="B15_COMPLETE_304_PLAYER_CLIPS.md"
NAME=re.compile(r"(?i)\b((?:ironman|warmachine)[a-z0-9_]*\.anim)\b")
REQUIRED={
    "locomotion": ["IronMan_Walk_F","IronMan_run","IronMan_Air_Idel",
                   "Ironman_Fly_F","Ironman_Fly_F_RUSH","IronMan_Air_land_s_start"],
    "repulsor": ["IronMan_Aim_Ground_move_F"],
    "melee": ["IronMan_Ground_Combo_1","IronMan_Ground_Combo_2",
              "IronMan_Ground_Combo_3","IronMan_Ground_ComboPower1",
              "IronMan_Air_CounterAtt","IronMan_PushAway_Ground"],
    "warmachine": ["Warmachine_Aim_Fly_M","Warmachine_Aim_Float_move_F",
                   "Warmachine_Aim_Ground_move_F","Warmachine_Fly_Att_ready"],
}
def run(out:Path, vita_dir:Path|None):
    with zipfile.ZipFile(ARCH) as z:
        assert z.testzip() is None
        text=z.read(SOURCE_MD).decode("utf-8")
    names=sorted(set(m.group(1) for m in NAME.finditer(text)),key=str.lower)
    iron=[x for x in names if x.lower().startswith("ironman")]
    wm=[x for x in names if x.lower().startswith("warmachine")]
    # Original report contains 248 IronMan + 56 WarMachine. Do not fabricate
    # clipping of the catalog if B15 document's presentation excludes a name.
    if len(names)<200:
        raise AssertionError(f"too few authentic named player clips extracted: {len(names)}")
    shipped=sorted(p.name for p in vita_dir.glob("*.im2v")) if vita_dir and vita_dir.is_dir() else None
    original_norm={n.lower().removesuffix(".anim") for n in names}
    priority={family:[
      {"source":x+".anim","catalogued":x.lower() in original_norm,
       "direct_baked_stem_match":shipped is not None and any(
           b.lower()==x.lower()+".im2v" for b in shipped),
       "gameplay_pose_and_attachment_verified":False}
      for x in clips] for family,clips in REQUIRED.items()}
    manifest={
      "status":"SOURCE-NAMES audit only; not original raw keyframe recovery",
      "source_archive":str(ARCH.relative_to(ROOT)),
      "count_named_player_clips_extracted":len(names),
      "count_ironman_named":len(iron),"count_warmachine_named":len(wm),
      "expected_original_catalog":304,
      "raw_keyframes_in_this_B15_audit":False,
      "vita_baked_count":len(shipped) if shipped is not None else None,
      "baked_stems":shipped,
      "named_source_list":names,
      "priority_families":priority,
      "all_304_available_for_baking":False,
      "all_304_verified_playing_on_real_vita":False,
      "needs":"original animation bytes, B13 bake + B7 quaternion/rig validation, original 3D attachment and per-suit animation state",
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(f"Original player clip NAMES: {len(names)} = IronMan {len(iron)} + WarMachine {len(wm)}")
    print(f"Physical B24 IM2V assets: {len(shipped) if shipped is not None else 'not supplied to audit'}")
    for cat,items in priority.items():
        print(cat,":", ", ".join(x["source"]+(" [FOUND NAME]" if x["catalogued"] else " [NOT LISTED]") for x in items))
    print("Audited source names; no unsupported claims of raw 304 keyframes or Vita playback")
    return manifest
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--vita-animations-dir",type=Path)
    args=p.parse_args()
    run(args.out,args.vita_animations_dir)
