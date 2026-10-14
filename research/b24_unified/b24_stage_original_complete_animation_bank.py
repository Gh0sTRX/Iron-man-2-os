#!/usr/bin/env python3
"""Stage source-only G8 successor motion bank without overwriting its original 59.

59 shipped aliases + 304 real 2010 IronMan/WarMachine clips + 34 original
Underwater player clips. Do NOT claim 397 unique 2010 animations: some 59
are retargets/aliases, and 34 Underwater contain 29 unbound auxiliary verts.
All source IM2V are kept external so the future Vita runtime can lazy stream.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import struct
from pathlib import Path

def digest(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<18),b""):
            h.update(block)
    return h.hexdigest()

def validate(source:Path):
    with source.open("rb") as f:
        header=f.read(20)
    if len(header)!=20:
        raise ValueError("empty IM2V header: "+source.name)
    magic,nv,frames,fps,duration=struct.unpack("<4sIIII",header)
    if magic!=b"IM2V" or not 2<=nv<=16000 or not 1<=frames<=4000 or fps!=20 or duration>120000:
        raise ValueError("bad authentic IM2V header: "+source.name)
    actual=source.stat().st_size
    if actual != 20+nv*frames*12:
        raise ValueError("incorrect original IM2V file length: "+source.name)
    return {"vertices":nv,"frames":frames,"duration_ms":duration,
            "sha256":digest(source),"bytes":actual}

def stage(existing:Path,original:Path,underwater:Path,out:Path):
    meta=json.loads((original/"B24_ORIGINAL_304_SOURCE_BAKE_COVERAGE.json").read_text())
    umeta=json.loads((underwater/"B24_UNDERWATER_34_MOTION_MANIFEST.json").read_text())
    if (meta["processed"],meta["baked"],meta["rejected"])!=(304,304,0):
        raise ValueError("original main player anim bake is not complete")
    if len(umeta["source_motion_clips"])!=34:
        raise ValueError("underwater original 34 source tracks incomplete")
    base=sorted(existing.glob("*.im2v"))
    if len(base)!=59:
        raise ValueError(f"G8 unchanged baseline 59 clips expected, got {len(base)}")
    streams=out/"animations";streams.mkdir(parents=True,exist_ok=True)
    ledger=[]
    present=set()
    def copy(src,asset,kind,source_name=None,playable=False):
        if not src.is_file() or asset in present or not asset.endswith(".im2v"):
            raise ValueError("missing or colliding original motion: "+asset)
        info=validate(src)
        dest=streams/asset
        shutil.copyfile(src,dest)
        if digest(dest)!=info["sha256"]:
            raise ValueError("source clip digest changed during staging")
        info.update({"asset":asset,"source_name":source_name,"tier":kind,
                     "gameplay_state_connected_individually_verified":False,
                     "asset_already_shipped_in_G8":kind=="G8_BASELINE_59",
                     "underwater_29_aux_original_parent_proven":False})
        ledger.append(info)
        present.add(asset)
    for p in base:
        copy(p,p.name,"G8_BASELINE_59",None,True)
    for entry in meta["records"]:
        filename=entry["im2v_filename"]
        if digest(original/filename)!=entry["im2v_sha256"]:
            raise ValueError("304 source digest mismatch: "+filename)
        copy(original/filename,filename,"ORIGINAL_2010_PLAYER_304",
             entry["source_animation"],False)
    for entry in umeta["source_motion_clips"]:
        src=underwater/entry["im2v"]
        if digest(src)!=entry["im2v_sha256"]:
            raise ValueError("34 source underwater digest mismatch")
        # Keep separate namespace; original 29v portion remains unbound.
        copy(src,"uw_original_"+entry["im2v"].casefold(),
             "UNDERWATER_34_PARTIALLY_SKINNED",entry["source"],False)
    tiers={t:sum(x["tier"]==t for x in ledger)
           for t in ("G8_BASELINE_59","ORIGINAL_2010_PLAYER_304",
                     "UNDERWATER_34_PARTIALLY_SKINNED")}
    if tiers!={"G8_BASELINE_59":59,"ORIGINAL_2010_PLAYER_304":304,
               "UNDERWATER_34_PARTIALLY_SKINNED":34}:
        raise ValueError("G8 source bank tier count error "+repr(tiers))
    report={
        "project":"Iron Man 2 G8 successor source-only animation bank",
        "total_staged_stream_files":len(ledger),
        "counts_by_tier":tiers,
        "DOES_NOT_MEAN_397_DISTINCT_ORIGINAL_ACTIONS":True,
        "DOES_NOT_MEAN_ALL_G8_GAMEPLAY_STATES_WIRED":True,
        "IS_NOT_NEW_VITA_VPK":True,
        "source_304_all_original_skin_baked":True,
        "underwater_auxiliary_29_vertices_not_rigged":True,
        "all_original_2010_hit_windows_or_2010_input_timing_restored":False,
        "new_304_and_34_active_in_existing_G8_binary":False,
        "staged_animation_bytes":sum(x["bytes"] for x in ledger),
        "clips":ledger,
    }
    (out/"G8_PLUS_ORIGINAL_COMPLETE_SOURCE_BANK_MANIFEST.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("PASS B24 G8 SOURCE BANK",len(ledger),
          "G8 59 + SOURCE 304 + UNDERWATER 34",
          "bytes",report["staged_animation_bytes"],
          "NO VPK NO GAMEPLAY LINK CLAIM")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline-dir",type=Path,required=True)
    p.add_argument("--original-dir",type=Path,required=True)
    p.add_argument("--underwater-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    stage(a.baseline_dir,a.original_dir,a.underwater_dir,a.out)

if __name__=="__main__":
    main()
