#!/usr/bin/env python3
"""G33 independently quantify authentic 2010 BRES C1L1 map placement problem.

No assumed scene node transforms. Source raw mesh XYZ vs real BRES ground
polygon bounds, relative to independently decoded 2010 MainCharacter local
CLARA node. Result categorizes *source coordinate frames only*, not a claim
about actual 2010 in-engine world/render instance transforms.
"""
from __future__ import annotations
import argparse,collections,json,math,zipfile
from pathlib import Path
import numpy as np
from b24_g13_c1l1_light_dome_mesh_provenance_sheet import source
from b24_owner_pack_extract import decode as unpack,get_exact
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize

def compute(ipa,out):
 meshes,stats=source()
 exact={k:[] for k in ('ground','urban','vehicles','lights')}
 for row,pos,face in meshes:
  exact[row["original_scene_group"]].append((row,pos,face))
 assert sum(map(len,exact.values()))==370
 ground=np.concatenate([pos for _,pos,_ in exact['ground']],axis=0)
 lo=ground.min(axis=0);hi=ground.max(axis=0)
 span=(hi-lo)
 full=np.concatenate([pos for _,pos,_ in meshes],axis=0)
 overall_lo=full.min(axis=0);overall_hi=full.max(axis=0)
 def dist_rect(blo,bhi):
  dx=max(float(lo[0]-bhi[0]),0,float(blo[0]-hi[0]))
  dy=max(float(lo[1]-bhi[1]),0,float(blo[1]-hi[1]))
  return math.hypot(dx,dy)
 categories={}
 outside_examples=[]
 for group,rows in exact.items():
  n_total=0;tri_total=0;cent_inside=0;overlap=0;complete_outside=0
  raw_min=[math.inf]*3;raw_max=[-math.inf]*3
  distances=[]
  for r,pos,faces in rows:
   l=pos.min(axis=0);h=pos.max(axis=0);center=(l+h)/2.
   d=dist_rect(l,h)
   if lo[0]<=center[0]<=hi[0] and lo[1]<=center[1]<=hi[1]:cent_inside+=1
   if d==0:overlap+=1
   else:complete_outside+=1
   distances.append(d)
   n_total+=1;tri_total+=len(faces)
   raw_min=np.minimum(raw_min,l).tolist();raw_max=np.maximum(raw_max,h).tolist()
   if d>0:
    outside_examples.append({'name':r['source_mesh_name'],'group':group,
     'original_source_raw_mesh_bbox_low':[round(float(v),3) for v in l],
     'original_source_raw_mesh_bbox_high':[round(float(v),3) for v in h],
     'min_XY_AABB_distance_to_original_ground':round(d,3),
     'source_triangle_count':len(faces)})
  categories[group]={'original_mesh_count':n_total,'source_authored_triangles':tri_total,
    'source_XY_bbox_low':[round(float(v),3) for v in raw_min],
    'source_XY_bbox_high':[round(float(v),3) for v in raw_max],
    'mesh_center_inside_original_ground_bbox':cent_inside,
    'bbox_intersects_source_ground_bbox':overlap,
    'bbox_fully_outside_original_ground_bbox':complete_outside,
    'farthest_mesh_bbox_ground_rect_distance':round(max(distances),3)}
 with zipfile.ZipFile(ipa) as z:
  orig=z.read("Payload/IronMan2.app/clev")
  raw=get_exact(orig,unpack(orig,".bclara"),"level1.bclara")
 scene=summarize(raw)
 mc=scene["source_exact_MC_native_parent_child_transform"]["native_vec3_position"]
 grounded=(lo[0]<=mc[0]<=hi[0] and lo[1]<=mc[1]<=hi[1])
 original_name_literals={}
 for label in (b'C1L1_obj_001',b'C1L1_obj_002',b'C1L1_obj_003',
               b'C1L1_obj_004',b'C1L1_car_01',b'C1L1_ground_001',
               b'.bdae',b'C1L1_light_001',b'MC'):
  original_name_literals[label.decode()] = raw.count(label)
 report={
  'source_game':'Iron Man 2 Gameloft original 2010 iOS C1L1',
  'owner_original_BRES_source_meshes':370,
  'owner_original_BRES_source_triangles':22919,
  'original_source_ground_mesh_count':len(exact['ground']),
  'original_source_ground_raw_XYZ_bbox_min':[round(float(v),3) for v in lo],
  'original_source_ground_raw_XYZ_bbox_max':[round(float(v),3) for v in hi],
  'all_original_C1L1_BRES_meshes_raw_XYZ_bbox_min':[round(float(v),3) for v in overall_lo],
  'all_original_C1L1_BRES_meshes_raw_XYZ_bbox_max':[round(float(v),3) for v in overall_hi],
  'original_source_mesh_placement_bbox_statistics_by_group':categories,
  'raw_BRES_meshes_wholly_outside_original_ground_XY_AABB':sum(c['bbox_fully_outside_original_ground_bbox'] for c in categories.values()),
  'largest_raw_original_BRES_mesh_outside_ground_examples':sorted(outside_examples,key=lambda x:-x['min_XY_AABB_distance_to_original_ground'])[:40],
  'authentic_original_CLARA_local_MainCharacter_XYZ':mc,
  'raw_MC_xy_inside_ground_bounds_but_world_parent_unknown':bool(grounded),
  'source_CLARA_BRES_resource_reference_literal_occurrences':original_name_literals,
  'original_source_parent_world_matrix_and_level_actor_mesh_binds_NOT_derived':True,
  'M1_vita_3D_source_mesh_is_raw_coordinates_without_authored_CLARA_world_placement':True,
  'scene_IS_NOT_COMPLETE':True,
  'NO_VPK':True
 }
 assert sum(c['original_mesh_count'] for c in categories.values())==370
 assert sum(c['source_authored_triangles'] for c in categories.values())==22919
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G33 ORIGINAL GROUND BBOX",report['original_source_ground_raw_XYZ_bbox_min'],report['original_source_ground_raw_XYZ_bbox_max'])
 print("G33 ORIGINAL CATEGORY RAW XYZ/AABB",json.dumps(categories))
 print("G33 SOURCE MESHES WHOLE OUTSIDE GROUND XY BBOX",report['raw_BRES_meshes_wholly_outside_original_ground_XY_AABB'])
 print("G33 source CLARA original BRES resource name literal counts",original_name_literals)
 print("PASS G33 source world diagnostic not game world reconstruction, no invented placements or VPK.")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument('--ipa',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();compute(a.ipa,a.out)
