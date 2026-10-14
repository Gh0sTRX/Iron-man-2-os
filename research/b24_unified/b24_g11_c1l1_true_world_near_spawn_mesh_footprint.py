#!/usr/bin/env python3
"""2010 real C1L1 visual geometry near B14 (0,0) vs actual game asset bounds.

Illustrates exact original B11 22,919 triangles, not any fabricated building,
and checks if G9 player's arbitrary x/y zero starts in plausible city
visibility. Source GLB meshes are native original Z-up; no camera projection.
"""
from __future__ import annotations
import argparse,collections,json,math,zipfile
from pathlib import Path
import numpy as np
from export_b24_c1_gpu_mesh import SOURCE,MEMBER,decode_glb,arr,category
def main(out):
 out.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(SOURCE) as z:d,bb=decode_glb(z.read(MEMBER))
 verts=[[] for _ in range(4)]
 trigs=[[] for _ in range(4)]
 report=[]
 for m in d["meshes"]:
  p=m["primitives"][0]
  positions=np.asarray(arr(d,bb,p["attributes"]["POSITION"]),dtype=np.float64)
  inds=np.asarray(arr(d,bb,p["indices"]),dtype=np.int32).reshape(-1,3)
  faces=positions[inds]
  group=category(m["name"])
  trigs[group].append(faces)
  xmin,ymin,zmin=positions.min(axis=0)
  xmax,ymax,zmax=positions.max(axis=0)
  report.append({"source_mesh":m["name"],"category":group,"tris":len(faces),
    "original_min_xyz":[xmin,ymin,zmin],"original_max_xyz":[xmax,ymax,zmax]})
 stats={}; plots={}
 import matplotlib
 matplotlib.use("Agg")
 import matplotlib.pyplot as plt
 for g,name in enumerate(("source_ground","source_city_objects","source_original_vehicles","source_light_structures")):
  t=np.concatenate(trigs[g],axis=0)
  centers=t.mean(axis=1)
  for radius in (10,25,50,100,250):
   inside=np.max(np.abs(centers[:,:2]),axis=1)<=radius
   nearplane=(centers[:,2]>=-3)&(centers[:,2]<45)
   stats[f"{name}_within_abs_xy_{radius}"]={
    "triangles_near_center":int((inside&nearplane).sum()),
    "share_of_group":round(float((inside&nearplane).mean()),5)}
  stats[name+"_global"]={"count":len(t),
      "min_xyz":t.reshape(-1,3).min(axis=0).tolist(),
      "max_xyz":t.reshape(-1,3).max(axis=0).tolist()}
  fig,ax=plt.subplots(figsize=(11,8),dpi=115)
  selection=(np.abs(centers[:,0])<=140)&(np.abs(centers[:,1])<=140)&(
      centers[:,2]>=-5)&(centers[:,2]<=45)
  sub=t[selection]
  from matplotlib.collections import PolyCollection
  polys=PolyCollection(sub[:,:,[0,1]],closed=True,alpha=.12,
                        facecolors=(.18,.67,.78,.18),edgecolors='none')
  ax.add_collection(polys)
  ax.set(xlim=(-140,140),ylim=(-140,140),aspect='equal',xlabel="REAL iOS world X",
         ylabel="REAL iOS world Y",title=f'2010 ORIGINAL C1L1 2010 BDAE {name} XY face footprints')
  ax.scatter([0],[0],s=65,c='red',marker='x',label='current prototype spawn 0,0')
  ax.legend(loc="upper right");ax.grid(alpha=.35)
  output=f'G11_AUTHENTIC_C1L1_{name}_WORLD_FOOTPRINT.png'
  fig.savefig(out/output,bbox_inches='tight')
  plt.close(fig)
  plots[name]=output
 with np.errstate(invalid='ignore'):
  nearest=sorted((x for x in report if x['category']==1),
     key=lambda r:(max(0,r['original_min_xyz'][0],-r['original_max_xyz'][0])**2+
                    max(0,r['original_min_xyz'][1],-r['original_max_xyz'][1])**2))[:20]
 result={"original_2010_scene_meshes":len(report),
  "source_triangle_total":sum(x['tris'] for x in report),
  "prototype_spawn_from_B14_not_original_mission":(0,0),
  "category_footprints":stats,"nearby_original_source_objects":nearest,
  "generated_static_world_data_overviews":plots,
  "original_game_spawn_location_proven":False,
  "host_screenshots_are_not_true_Vita_GPU_camera":True}
 if result["source_triangle_total"]!=22919:raise ValueError('source geometry drift')
 (out/"G11_2010_ORIGINAL_C1L1_REAL_WORLD_NEAR_SPAWN_GEOMETRY.json").write_text(
    json.dumps(result,indent=2)+"\n")
 print("G11_REAL_2010_CITY_TRIANGLE_NEAR_TEST_SPAWN",stats,flush=True)
 print("PASS exact 22919 source original 3D 2010 city polygon footprints vs current user-visible center test spawn, no VPK",flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);a=p.parse_args()
 main(a.out)
