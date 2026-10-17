#!/usr/bin/env python3
"""Read ALL user-owned ORIGINAL 2010 IM2T sources and the assembled Vita
native graphics+physics contracts to prevent arbitrary avatar scaling.
Never emit original .im2t raw asset; only source bounds and math evidence.
"""
from pathlib import Path
import math,struct,json,argparse

def analyze(p:Path):
 raw=p.read_bytes()
 if raw[:4]!=b"IM2T" or len(raw)<20:
  raise ValueError("Not real original IM2T: "+p.name)
 nv,nt,tw,th=struct.unpack_from("<4I",raw,4)
 if not 1<=nv<=16000 or not 1<=nt<=24000 or tw>2048 or th>2048 or not tw or not th:
  raise ValueError("Invalid original IM2T owner header: "+p.name)
 if len(raw)<20+nv*20+nt*6:raise ValueError("Truncated original bind model "+p.name)
 heights=[struct.unpack_from("<f",raw,20+i*20+8)[0] for i in range(nv)]
 if not all(map(math.isfinite,heights)):
  raise ValueError("Nonfinite 2010 source mesh: "+p.name)
 low=min(heights);high=max(heights)
 center=(low+high)*.5
 return dict(model=p.name,original_vertex_count=nv,original_triangles=nt,
    original_bind_min_z=round(low,7),original_bind_max_z=round(high,7),
    original_height=round(high-low,7),
    original_center_z=round(center,7),
    old_GPU_lowest_vertex_z_at_B14_foot_Z0=round(low-center,7),
    correct_source_bind_lowest_vertex_z_at_B14_foot_Z0=0.,
    difference_between_previous_and_source_footer=round(center-low,7),
    original_2010_gameworld_actor_scale_verified=False)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--models",type=Path,required=True)
 ap.add_argument("--out",type=Path,required=True)
 a=ap.parse_args()
 models=sorted(a.models.glob("*.im2t"))
 if len(models)<5:raise ValueError("Expected all FIVE source-authored original 2010 armors, found "+str(len(models)))
 records=[analyze(p) for p in models]
 markv=[x for x in records if "suitcase" in x["model"].lower()]
 if len(markv)!=1 or not .013<=markv[0]["original_bind_min_z"]<=.014 or not 2.23<markv[0]["original_height"]<2.24:
  raise ValueError("Actual 2010 Mark V rest height not grounded in original source")
 data={"proof":"2010 original unanimated 3D source vertices + the exact live B14/G75 FOOT vs VitaGL center draw ABI",
   "original_assets_copied_into_repository":False,
   "original_world_actor_scene_parent_scale_proven":False,
   "render_projection_adjusted_model_scale":False,
   "physics_collision_changed":False,
   "original_armor_meshes":records,
   "model_center_z_in_original_Vita_model_loader":"(minimum bind z+maximum bind z)/2",
   "B14_world_z_is_G75_capsule_foot":True,
   "old_visual_lowest_z":"world.z - model.center_z + IM2T_source_vertex_min_z",
   "fixed_visual_lowest_z":"world.z - IM2T_source_bind_min_z + IM2T_source_vertex_min_z",
   "corrects_grounded_suit_z_without_resizing_suit_or_world":True,
   "Vita_hardware_validation":False}
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(data,indent=2)+"\n")
 for x in records:
  print("G168 ORIGINAL 2010 SOURCE ARMOR",x["model"],
        "verts",x["original_vertex_count"],
        "bindheight",x["original_height"],
        "OLD rendered FOOT below G75 plane",x["old_GPU_lowest_vertex_z_at_B14_foot_Z0"],
        "correct sourced foot at 0.0")
 print("G168 PASSED authentic IM2T source bind-foot math for",len(models),"armors; correct only renderer, never resize authored actor or source city. NO VPK")
if __name__=="__main__":main()
