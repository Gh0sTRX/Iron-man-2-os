#!/usr/bin/env python3
"""G194 original 2010 iOS authored BDAE source rig: resolve newly PROVEN
native scene registry group 14 Dummy_Chest / 33 Dummy_Foot_L names to
ACTUAL existing named authored rig nodes and original rest world transforms.

No guessed rig offset, no animation root scale, no fake muzzle/projectile.
Generate a STATIC rig-source diagnostic PNG, NOT an in-game screenshot.
No licensed original model geometry exported, no new VPK.
"""
from __future__ import annotations
import argparse,json,math,re,sys,tempfile,zipfile
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode,get_exact
from b24_underwater_source_34_im2v_bake import load_original_b13
KEYS=[(14,"Dummy_Chest"),(33,"Dummy_Foot_L")]
MODELS=["Iron_man_mark6.bdae","LC_MC_SuitCase.bdae",
        "warmachine.bdae","LC_MC_WarMachine.bdae"]
OWNER_SIZE=248613763

def measure(ipa:Path,g193:Path,out:Path,png:Path):
 proof=json.loads(g193.read_text())
 if not proof["native_original_source_name_mapping_PROVEN"]:
  raise ValueError("G194 only uses SOURCE PROVEN 14/33 native registry keys")
 for key,name in KEYS:
  if proof[f"original_native_scene_group{key}_named_source_key"]!=name:
   raise ValueError("Original iOS dummy native enum binding drift")
 if ipa.stat().st_size!=OWNER_SIZE:raise ValueError("G194 needs original iOS 2010 owner assets")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("owner IPA CRC failed")
  raw_models=z.read("Payload/IronMan2.app/models")
 records=decode(raw_models,".bdae")
 rigs={}
 with tempfile.TemporaryDirectory(prefix="g194_source_2010_b13_") as temp:
  b13=load_original_b13(Path(temp))
  for filename in MODELS:
   raw=get_exact(raw_models,records,filename)
   nodes=b13.parse_rig(raw)
   worlds=b13.worlds(nodes)
   if not isinstance(worlds,dict):raise ValueError("G194 B13 original rest world transform owner drift")
   points=[];detected={str(k):[] for k,_ in KEYS}
   for node in nodes:
    name=node["name"]
    if not isinstance(name,str):raise ValueError("source name is not a string")
    matrix=np.asarray(worlds[name],dtype=np.float64)
    if matrix.shape!=(4,4) or not np.isfinite(matrix).all():
     raise ValueError("source BDAE native world rest matrix bad")
    xyz=[float(matrix[k,3]) for k in range(3)]
    if not all(math.isfinite(v) for v in xyz):raise ValueError("invalid genuine authored world")
    points.append((name,xyz))
    for k,stem in KEYS:
     # Real native CollectDummies uses stristr(name,pattern) and tests
     # pointer equality to start of actual name -> prefix match.
     if name.casefold().startswith(stem.casefold()):
      detected[str(k)].append({
        "source_BDAE_real_2010_rig_node":name,
        "source_original_node_record_offset":node.get("offset"),
        "source_original_parent_field":node.get("parent"),
        "original_source_rest_rig_world_translation":xyz,
        "original_source_rest_rig_world_matrix4x4":matrix.tolist(),
        "original_scene_runtime_first_dummy_child_binding_PROVEN":False,
        "Vita_original_VFX_renderer_mapped":False,
      })
   rigs[filename]={
    "original_source_rig_node_count":len(nodes),
    "author_2010_native_name_prefix_matches":detected,
    "source_BDAE_local_rest_world_points_only":len(points),
    "source_model_rest_bounds_xyz":{
     "min":[min(xyz[d] for _,xyz in points) for d in range(3)],
     "max":[max(xyz[d] for _,xyz in points) for d in range(3)]},
   }
   if filename=="Iron_man_mark6.bdae":
    rigs[filename]["source_diagnostic_view_points"]=points
 if rigs["Iron_man_mark6.bdae"]["original_source_rig_node_count"]!=96:
  raise ValueError("2010 authentic Mark VI rig source must have 96 nodes")
 if rigs["warmachine.bdae"]["original_source_rig_node_count"]!=112:
  raise ValueError("2010 authentic WarMachine rig source must have 112 nodes")
 # Static, data-driven figure: no constructed 3D character, physics, or VFX.
 import matplotlib
 matplotlib.use("Agg")
 import matplotlib.pyplot as plt
 source=rigs["Iron_man_mark6.bdae"]["source_diagnostic_view_points"]
 fig=plt.figure(figsize=(9,7),dpi=130)
 ax=fig.add_subplot(111,projection="3d")
 coords=np.asarray([p for _,p in source])
 ax.scatter(coords[:,0],coords[:,1],coords[:,2],s=10,alpha=.5,label="Real original BDAE nodes")
 for idx,name in KEYS:
  for match in rigs["Iron_man_mark6.bdae"]["author_2010_native_name_prefix_matches"][str(idx)]:
   x,y,z=match["original_source_rest_rig_world_translation"]
   ax.scatter([x],[y],[z],s=105,marker="x",linewidths=2.4,label=f"{idx}: {name}")
   ax.text(x,y,z,name,fontsize=9)
 ax.set_xlabel("BDAE rig X (authored)")
 ax.set_ylabel("BDAE rig Y (authored)")
 ax.set_zlabel("BDAE rig Z (authored)")
 ax.set_title("Iron Man 2 iOS 2010 • actual Mark VI BDAE REST nodes\nDummy_Chest (14) & Dummy_Foot_L (33) • NOT an in-game frame",fontsize=12)
 ax.legend(loc="upper left",fontsize=8)
 fig.tight_layout()
 png.parent.mkdir(parents=True,exist_ok=True);fig.savefig(png,facecolor="white")
 plt.close(fig)
 rigs["Iron_man_mark6.bdae"].pop("source_diagnostic_view_points")
 report={
  "source":"Real user owned 2010 iOS original BDAE rigs and source-proven native SceneImpl group14/33 names",
  "original_proven_native_group_label_names":{"14":"Dummy_Chest","33":"Dummy_Foot_L"},
  "models":rigs,
  "rest_rig_coordinates_are_NOT_actor_C1L1_final_world_transform":True,
  "original_scene_runtime_group0_selection_node_specific_to_suit_PROVEN":False,
  "original_WarMachine_rocket_and_gatling_socket_assignments_PROVEN":False,
  "original_2010_animated_skinned_muzzle_current_frame_transform_PROVEN":False,
  "Vita_game_particle_or_damage_integration_changed":False,
  "static_source_figure_is_not_a_render_of_last_Vita_build":True,
  "NO_PRIVATE_ORIGINAL_ASSET_EXPORT":True,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 for filename,d in rigs.items():
  print("G194 ORIGINAL SOURCE",filename,"nodes",d["original_source_rig_node_count"])
  for idx,name in KEYS:
   print("G194 real 2010 rig name pattern",idx,name,d["author_2010_native_name_prefix_matches"][str(idx)])
 print("G194 source verified only rest pose rig node world transforms, NOT original final game Vita 3D emitter. NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--g193",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 p.add_argument("--png",required=True,type=Path)
 a=p.parse_args()
 measure(a.ipa,a.g193,a.out,a.png)
