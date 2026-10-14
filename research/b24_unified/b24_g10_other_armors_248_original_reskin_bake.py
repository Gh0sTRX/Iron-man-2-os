#!/usr/bin/env python3
"""2010 original source Iron Man 248 animation clips -> real MarkIV/Stealth/Suitcase
matching BRES inverse-bind weighted skins, NEVER copy MarkVI 802-XYZ to 629v.

Three separate authentic suit skin topologies, B13 authored rotation tracks;
only CPU source bake / IM2V streams, no invented vertex retarget and NO VPK.
Source original IPA accessible only in ephemeral GitHub runner.
"""
import argparse,hashlib,json,struct,tempfile,zipfile
from pathlib import Path
import numpy as np
from b24_all_player_304_original_bake import source_catalog
from b24_hover_fire_authentic_pose_preview import source_meshes,prepare
from b24_owner_pack_extract import decode,get_exact
from b24_underwater_source_34_im2v_bake import load_original_b13
SUITS={
 "mark4":("Iron_man_mark4.bdae",802),
 "stealth":("LC_MC_Stealth.bdae",802),
 "suitcase":("suitcase.bdae",629),
}
def main(ipa,out):
 out.mkdir(parents=True,exist_ok=True)
 catalog=[x for x in source_catalog()
          if x["filename"].casefold().startswith("ironman")]
 if len(catalog)!=248:raise ValueError("2010 248 original player clips catalogue mismatch")
 with zipfile.ZipFile(ipa) as z:
  models=z.read("Payload/IronMan2.app/models")
  anims=z.read("Payload/IronMan2.app/anims")
 mi=decode(models,".bdae");ai=decode(anims,".anim")
 report={"source_year":2010,"authentic_source_clips_per_suit":248,
  "alternate_armor_source_BRES_reskinned_not_MarkVI_vertex_copy":True,
  "all_animations_live_gameplay_control_linked":False,
  "outfits":{}}
 with tempfile.TemporaryDirectory(prefix="b24_alt_2010_") as td:
  b13=load_original_b13(Path(td))
  for suit,(bdae,nv) in SUITS.items():
   raw=get_exact(models,mi,bdae)
   meshs=source_meshes(raw)
   matching=[mesh for mesh in meshs if len(mesh["positions"])==nv]
   if len(matching)!=1:
    raise ValueError("2010 real alternate armor source geometry ambiguous "+bdae)
   orig=np.asarray(matching[0]["positions"],dtype=np.float64)
   setup,err,nodes,weights=prepare(b13,raw,orig)
   records=[]
   for entry in catalog:
    name=entry["filename"]
    authored=get_exact(anims,ai,name)
    anim=b13.decode_anim(authored)
    duration=int(anim.duration_ms)
    if duration!=entry["duration_ms"]:raise ValueError("catalog duration drift "+name)
    frames=([0] if duration==0 else list(range(0,duration,50))+[duration])
    if len(frames)>4000:raise ValueError("too many real source frames")
    binary=bytearray(struct.pack("<4sIIII",b"IM2V",nv,len(frames),20,duration))
    for t in frames:
     pose=np.asarray(b13.bake_pose(setup,anim,t),dtype=np.float64)
     if pose.shape!=(nv,3) or not np.isfinite(pose).all() or np.abs(pose).max()>100000:
      raise ValueError("original 2010 skin invalid pose "+suit+" "+name)
     binary.extend(pose.astype("<f4").tobytes())
    dest_name=suit+"_"+Path(name).stem.casefold()+".im2v"
    dest=out/dest_name
    dest.write_bytes(binary)
    if len(binary)!=20+len(frames)*nv*12:raise ValueError("IM2V bytes mismatch")
    records.append({
       "real_2010_clip":name,"asset":dest_name,"bytes":len(binary),
       "source_sha256":hashlib.sha256(authored).hexdigest(),
       "im2v_sha256":hashlib.sha256(binary).hexdigest(),
       "frames":len(frames),"duration_ms":duration,"vertices":nv
    })
   assert len(records)==248
   report["outfits"][suit]={"source_model":bdae,"vertices":nv,"rig_nodes":nodes,
     "inverse_bind_error":err,"clip_count":len(records),
     "records":records}
   print("G10_AUTHENTIC_ORIGINAL_ALT_ARMOR_248",suit,bdae,"vertices",nv,
         "clips",len(records),"bytes",sum(r["bytes"] for r in records),
         "original_inverse_bind_error",err,flush=True)
 (out/"G10_MARK4_STEALTH_SUITCASE_ALL_248_ORIGINAL_SKIN_ANIMATIONS.json").write_text(json.dumps(report,indent=2)+"\n")
 if len(list(out.glob("*.im2v")))!=744:raise ValueError("expected genuine 3*248")
 print("PASS G10 actual 2010 BRES+all 248 authored IronMan clips independently skinned onto THREE ORIGINAL SUITS. 744 source IM2V (all controls not yet live), NO VPK",flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();main(a.ipa,a.out)
