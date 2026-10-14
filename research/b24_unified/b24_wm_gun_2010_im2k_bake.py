#!/usr/bin/env python3
"""Source-verified 2010 War Machine rigid Gun01-04 & Green-Gun node IM2K streams.

These are actual B13.worlds(node hierarchy, original .anim, sampled ms) world
transforms, not invented gun animations. Intended as SOURCE-ONLY attachment
timelines. Original nozzle identity + hit/particle assignment still UNKNOWN.
IM2K header: '<4sIIII' magic, nodes=5, frames, fps=20, duration_ms;
each frame: six 4x4 LE float32 world matrices in declared manifest order.
"""
from __future__ import annotations
import argparse,hashlib,json,struct,tempfile,zipfile
from pathlib import Path
import numpy as np
from b24_owner_pack_extract import decode,get_exact
from b24_underwater_source_34_im2v_bake import load_original_b13
from b24_wm_original_animated_gun_kinematics import ANIMATIONS

ORDER=("Gun01-node","Gun02-node","Gun03-node","Gun04-node",
       "Dummy_Green_Gun-node","DummyE_Green_Gun-node")

def main(ipa,out):
    with zipfile.ZipFile(ipa) as z:
        original_models=z.read("Payload/IronMan2.app/models")
        original_anims=z.read("Payload/IronMan2.app/anims")
    original=get_exact(original_models,decode(original_models,".bdae"),"warmachine.bdae")
    recs=decode(original_anims,".anim")
    out.mkdir(parents=True,exist_ok=True)
    summary={"format":"IM2K","node_order":list(ORDER),"source_rig":"warmachine.bdae",
             "original_owner2010":True,"source_scene_parent_hierarchy":True,
             "verified_right_gatling_emitter":False,
             "verified_left_rocket_emitter":False,
             "G8_gameplay_currently_using_IM2K":False,
             "clips":[]}
    with tempfile.TemporaryDirectory(prefix="b24_original_wm_sourcegun_") as tmp:
        b13=load_original_b13(Path(tmp))
        nodes=b13.parse_rig(original)
        assert len(nodes)==112
        assert set(ORDER).issubset({n["name"] for n in nodes})
        for original_name in ANIMATIONS:
            raw=get_exact(original_anims,recs,original_name)
            animation=b13.decode_anim(raw)
            duration=animation.duration_ms
            assert 0<duration<10000
            times=list(range(0,duration,50))+[duration]
            if len(times)>512:raise ValueError("source clip too many frames")
            frames=[]
            for t in times:
                world=b13.worlds(nodes,animation,t)
                transforms=[]
                for name in ORDER:
                    m=np.asarray(world[name],dtype=np.float64)
                    if m.shape!=(4,4) or not np.isfinite(m).all():
                        raise ValueError("source BRES gun node invalid 4x4")
                    if np.max(np.abs(m))>100000:raise ValueError("gun node transform outlier")
                    transforms.append(m.astype("<f4"))
                frames.append(np.stack(transforms))
            matrix=np.stack(frames)
            header=struct.pack("<4sIIII",b"IM2K",len(ORDER),len(times),20,duration)
            body=matrix.astype("<f4",copy=False).tobytes()
            expected=20+len(times)*len(ORDER)*16*4
            if len(header)+len(body)!=expected:raise ValueError("IM2K ABI size")
            name=Path(original_name).stem.casefold()+".im2k"
            data=header+body
            (out/name).write_bytes(data)
            summary["clips"].append({
                "source_animation":original_name,
                "output":name,
                "duration_ms":duration,"frames":len(times),
                "source_animation_sha256":hashlib.sha256(raw).hexdigest(),
                "im2k_sha256":hashlib.sha256(data).hexdigest(),
                "bytes":len(data),
                "node_count":5,
            })
            print("PASS 2010 WM TRUE RIGID GUN STREAM",name,
                  "original BRES 112 scene nodes",len(times),"frames",len(data),"bytes")
    assert len(summary["clips"])==6 and len(ORDER)==6
    (out/"G8_WM_2010_ORIGINAL_GUN01_04_IM2K_SOURCE_MANIFEST.json").write_text(
        json.dumps(summary,indent=2)+"\n")
    print("PASS 6 original War Machine gun rigid source clips, 6 named matrix nodes each including Dummy/DummyE marker pair, no VPK or proven muzzle")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--ipa",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    main(a.ipa,a.out)
