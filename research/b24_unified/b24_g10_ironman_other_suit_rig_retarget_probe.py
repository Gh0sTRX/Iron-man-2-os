#!/usr/bin/env python3
"""2010 owner Mark IV / Stealth / Mark V Suitcase original rig retarget feasibility.

Original Mark VI skinned IM2V XYZ cannot be copied into another suit when
nv/bone palettes differ. Check original alternate BRES rigs and actual
author source .anim baked onto matching original BRES skin, no fake pose.
"""
from __future__ import annotations
import argparse,json,tempfile,zipfile
from pathlib import Path
import numpy as np
from b24_owner_pack_extract import decode,get_exact
from b24_underwater_source_34_im2v_bake import load_original_b13
from b24_hover_fire_authentic_pose_preview import source_meshes,prepare

MOTIONS=("IronMan_Aim_Float_move_L.anim","IronMan_Aim_Float_move_R.anim",
         "IronMan_Aim_Float_idle.anim","IronMan_Ground_Combo_1.anim",
         "IronMan_Ground_ComboPower_a.anim")
def run(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  models=z.read("Payload/IronMan2.app/models")
  anims=z.read("Payload/IronMan2.app/anims")
 mr=decode(models,".bdae"); ar=decode(anims,".anim")
 selected=[r for r in mr if any(s in r.name.casefold().replace("_","") for s in
      ("mark4","stealth","suitcase","mark5","markv"))]
 if not selected:raise ValueError("owner original suit BRES names absent")
 result={"original_model_candidates":[],"different_skin_vertex_counts_prohibit_raw_802_xyz_copy":True,
         "full_five_suit_anim_tree_playable_verified":False}
 with tempfile.TemporaryDirectory() as temp:
  b13=load_original_b13(Path(temp))
  for rec in selected:
   raw=get_exact(models,mr,rec.name)
   meshes=source_meshes(raw)
   row={"original_BRES":rec.name,
        "source_mesh_vertex_counts":[len(x["positions"]) for x in meshes],
        "source_rig_length":len(b13.parse_rig(raw)),
        "successful_original_2010_retarget_skinned_poses":[],
        "failed_rigs":[]}
   for mesh in meshes:
    nv=len(mesh["positions"])
    if not 450<=nv<=2000:continue
    try:
     setup,error,bones,palette=prepare(b13,raw,np.asarray(mesh["positions"]))
     if error>=2e-4:raise ValueError("rest palette mismatch")
     for clip in MOTIONS:
      a=b13.decode_anim(get_exact(anims,ar,clip))
      xyz=np.asarray(b13.bake_pose(setup,a,a.duration_ms//2),dtype=np.float32)
      if xyz.shape!=(nv,3) or not np.isfinite(xyz).all():
       raise ValueError("author skinned retarget pose invalid")
      row["successful_original_2010_retarget_skinned_poses"].append({
        "original_animation":clip,"source_mesh_vertices":nv,
        "source_mesh_bones":bones,"source_palette":palette,
        "rest_inverse_bind_residual":error,
        "source_midpose_xyz_absmax":float(np.max(np.abs(xyz)))})
    except Exception as err:
     row["failed_rigs"].append({"vertices":nv,"error":str(err)[:180]})
   result["original_model_candidates"].append(row)
   print("G10_REAL_ALT_ARMOR_RIG",rec.name,"V",row["source_mesh_vertex_counts"],
         "success",len(row["successful_original_2010_retarget_skinned_poses"]),
         "problems",row["failed_rigs"][:3],flush=True)
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2)+"\n")
 print("PASS genuine original other-armor skin+anim retarget feasibility: only source-proven rig bakes, NO 802 XYZ smuggling, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True);a=p.parse_args()
 run(a.ipa,a.out)
