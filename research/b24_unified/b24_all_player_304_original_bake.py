#!/usr/bin/env python3
"""Faithful batch conversion + per-clip forensic result for 2010 player animations.

Exactly the source owner IPA's 248 IronMan and 56 WarMachine named characters.
Use original per-character BRES skin palette, rig, B13 quaternion/keyframes.
No fallback/procedural poses, no guessed retarget, no zero-ms division, no VPK.
If a source clip is incompatible/corrupt, record REJECT with exact reason,
not a bogus playable file or a fabricated completion claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import tempfile
import traceback
import zipfile
from pathlib import Path
import numpy as np

from b24_hover_fire_authentic_pose_preview import TARGETS, prepare, source_meshes
from b24_hover_fire_directional_source import catalog
from b24_owner_pack_extract import decode, get_exact
from b24_underwater_source_34_im2v_bake import load_original_b13

FPS=20
STEP_MS=50
EXPECTED={"ironman":248,"warmachine":56}
MAX_FRAMES=4000


def source_catalog():
    entries=catalog()
    names=sorted((v for v in entries.values() if
                  v["filename"].casefold().startswith(("ironman","warmachine"))),
                 key=lambda r:r["filename"].casefold())
    assert len(names)==304,len(names)
    for armor in EXPECTED:
        count=sum(x["filename"].casefold().startswith(armor) for x in names)
        assert count==EXPECTED[armor], (armor,count)
    return names


def bake_clip(original, setup, raw, entry, nv, armor, output_dir):
    a=original.decode_anim(raw)
    source_name=entry["filename"]
    if len(a.names)!=entry["source_named_tracks"]:
        raise ValueError(f"track-name count source mismatch {len(a.names)} != {entry['source_named_tracks']}")
    duration=int(a.duration_ms)
    if duration!=entry["duration_ms"] or not 0<=duration<=120000:
        raise ValueError(f"authored duration mismatch/overflow {duration} != {entry['duration_ms']}")
    # Three 2010 source clips carry ZERO duration: one original pose,
    # runaway_fail and Ground_Raise1_1. Bake only a single static sample;
    # NEVER loop zero-duration assets as live cyclic animation.
    ticks=([0] if duration==0 else list(range(0,duration,STEP_MS))+[duration])
    if len(ticks)>MAX_FRAMES:
        raise ValueError(f"too many frame samples {len(ticks)}")
    frames=[]
    for t in ticks:
        pose=np.asarray(original.bake_pose(setup,a,t),dtype=np.float64)
        if pose.shape!=(nv,3) or not np.isfinite(pose).all():
            raise ValueError("real source skin produced invalid XYZ")
        if float(np.max(np.abs(pose)))>100000:
            raise ValueError("source pose contains huge/unbounded coordinates")
        frames.append(pose.astype("<f4",copy=False))
    stacked=np.stack(frames).astype("<f4",copy=False)
    binary=struct.pack("<4sIIII",b"IM2V",nv,len(ticks),FPS,duration)+stacked.tobytes()
    if len(binary)!=20+nv*len(ticks)*12:
        raise ValueError("IM2V binary length mismatch")
    stem=Path(source_name).stem.casefold()
    fname=armor+"_"+stem+".im2v"
    file=output_dir/fname
    file.write_bytes(binary)
    if file.stat().st_size != len(binary):
        raise IOError("IM2V write incomplete")
    movement=float(np.max(np.abs(stacked-stacked[0])))
    return {
        "status":"SOURCE_SKINNED_BAKED",
        "source_animation":source_name,"source_sha256":hashlib.sha256(raw).hexdigest(),
        "im2v_filename":fname,"im2v_sha256":hashlib.sha256(binary).hexdigest(),
        "duration_ms":duration,"frame_count":len(ticks),"fps":FPS,
        "vertex_count":nv,"source_track_label_count":len(a.names),
        "file_bytes":len(binary),"pose_max_deviation":movement,
        "zero_duration_source_pose_only":duration==0,
        "Vita_gameplay_connected":False,
        "original_2010_action_trigger_or_hit_frames_proven":False,
    }


def run(ipa,out,armor_selection="both",start=0,limit=1000):
    entries=source_catalog()
    with zipfile.ZipFile(ipa) as package:
        prefix="Payload/IronMan2.app/"
        models=package.read(prefix+"models")
        animations=package.read(prefix+"anims")
    model_recs=decode(models,".bdae")
    anim_recs=decode(animations,".anim")
    anim_by_name={e.name.casefold():e for e in anim_recs}
    out.mkdir(parents=True,exist_ok=True)
    report={"scope":"original 2010 iOS 304 player-named clips (248 IronMan/56 WarMachine)",
            "g8_shipped_baked_clips_unmodified":59,
            "underwater_34_separate_source_only":True,
            "source_catalog_total":len(entries),
            "original_Vita_combat_state_linked":False,
            "source_baker_20fps_sampled_not_2010_runtime":True,
            "per_armor":{},"records":[]}
    with tempfile.TemporaryDirectory(prefix="b24_original_304_") as tmp:
        b13=load_original_b13(Path(tmp))
        for armor,(model_name,nv) in TARGETS.items():
            if armor_selection not in ("both",armor):
                continue
            source=get_exact(models,model_recs,model_name)
            meshes=[m for m in source_meshes(source) if len(m["positions"])==nv]
            if len(meshes)!=1:
                raise ValueError("source BRES primary player topology changed")
            setup,err,nodes,palette=prepare(b13,source,np.asarray(meshes[0]["positions"]))
            all_armor=[entry for entry in entries
                       if entry["filename"].casefold().startswith(armor)]
            batch=all_armor[start:start+limit]
            report["per_armor"][armor]={
                "source_BRES":model_name,"source_vertex_count":nv,
                "original_rig_nodes":nodes,"bone_palette":palette,
                "source_rest_bind_max_error":err,
                "original_named_clip_count":len(all_armor),
                "batch_start":start,"batch_count":len(batch)}
            for index,entry in enumerate(batch,start):
                name=entry["filename"]
                rec={"armor":armor,"source_animation":name,
                     "source_catalog_duration_ms":entry["duration_ms"],
                     "source_catalog_track_label_count":entry["source_named_tracks"],
                     "catalog_index":index}
                try:
                    matched=anim_by_name.get(name.casefold())
                    if not matched:
                        raise KeyError("genuine anim bytes not found in IPA")
                    original_raw=get_exact(animations,anim_recs,matched.name)
                    rec.update(bake_clip(b13,setup,original_raw,entry,nv,armor,out))
                except Exception as exc:
                    rec.update({"status":"SOURCE_REJECTED_NOT_A_BAKED_CLIP",
                                "error_type":type(exc).__name__,
                                "error":str(exc)[:250],
                                "Vita_gameplay_connected":False})
                report["records"].append(rec)
            accepted=sum(r["status"]=="SOURCE_SKINNED_BAKED"
                         for r in report["records"] if r["armor"]==armor)
            print("2010 ORIGINAL PLAYER BATCH",armor,"records",len(batch),
                  "baked",accepted,"rejected",len(batch)-accepted,
                  "rig_nodes",nodes,"rest_err",err,flush=True)
    report["processed"]=len(report["records"])
    report["baked"]=sum(x["status"]=="SOURCE_SKINNED_BAKED" for x in report["records"])
    report["rejected"]=report["processed"]-report["baked"]
    report["baked_bytes"]=sum(x.get("file_bytes",0) for x in report["records"])
    manifest=out/"B24_ORIGINAL_304_SOURCE_BAKE_COVERAGE.json"
    manifest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print("RESULT ORIGINAL 2010 PLAYER CLIPS",report["processed"],
          "BAKED",report["baked"],"REJECTED",report["rejected"],
          "IM2V_BYTES",report["baked_bytes"],"NO VPK",flush=True)
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ipa",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--armor",choices=("ironman","warmachine","both"),default="both")
    p.add_argument("--start",type=int,default=0)
    p.add_argument("--limit",type=int,default=1000)
    args=p.parse_args()
    if args.start<0 or args.limit<1: p.error("invalid original clip batch")
    run(args.ipa,args.out,args.armor,args.start,args.limit)


if __name__=="__main__":
    main()
