#!/usr/bin/env python3
"""G45 seek genuine BRES 2010 per-mesh transforms, no fabricated root offsets.

Prior G44 proved 11048/11141 original city triangle CENTROIDS have Z<0
while source ground median local Z=0.18, and B11 Python BDAE parser returns
no parsed hierarchy/matrix fields. Native source BDAE binary can contain a
separate transform table, or use an engine runtime position change.

Scan actual BRES binary for 16×f32 4x4 rigid affine candidate transforms
at native 4-byte alignment, both row-major and column-major arrangements.
Keep only orthonormal plausible rotations with nontrivial Z translations.
Compare candidate addresses to 2010 mesh descriptors; does NOT imply the
candidate matrix is associated with that mesh. NO matrices are applied.
"""
from __future__ import annotations
import argparse,contextlib,io,hashlib,json,zipfile
from pathlib import Path
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

NAMES=["C1L1_ground_001","C1L1_obj_001","C1L1_obj_002","C1L1_obj_003",
       "C1L1_obj_004","C1L1_light_001","C1L1_light_002","C1L1_light_003",
       "C1L1_car_01","C1L1_car_02"]

def candidates(raw):
 arr=np.frombuffer(raw[:len(raw)//4*4],dtype="<f4")
 if len(arr)<16:return []
 views=sliding_window_view(arr,16)
 # Stored as 16 native float32 entries, 4-byte aligned, finite.
 fin=np.isfinite(views).all(axis=1)
 cands=[]
 for label,indices,translation in (
     ("colmajor", (3,7,11,15), (12,13,14)),
     ("rowmajor", (12,13,14,15), (3,7,11))):
  hits=np.where(fin &
   (np.abs(views[:,indices[0]])<.0005)&(np.abs(views[:,indices[1]])<.0005)&
   (np.abs(views[:,indices[2]])<.0005)&(np.abs(views[:,indices[3]]-1)<.0005))[0]
  for h in hits:
   v=views[int(h)]
   mat=v.reshape((4,4),order="F" if label=="colmajor" else "C")
   r=mat[:3,:3]
   if np.max(np.abs(r.T@r-np.eye(3)))>.004:continue
   det=float(np.linalg.det(r))
   if not .997<=det<=1.003:continue
   xyz=v[list(translation)].copy()
   if not np.isfinite(xyz).all() or max(abs(float(z)) for z in xyz)>5000:continue
   if abs(float(xyz[2]))<3.:continue # goal diagnostic significant Z correction
   cands.append({"native_offset":int(h)*4,"4x4_matrix_memory_order":label,
      "original_binary_matrix_translation_XYZ":[round(float(k),5) for k in xyz],
      "original_rotation_determinant":round(det,5),
      "raw_original_matrix_16_f32":[round(float(k),6) for k in v],
      "BRES_2010_mesh_association_proven":False})
 # same physical bytes can have dual naive interpretations
 return sorted(cands,key=lambda z:z["native_offset"])

def main():
 p=argparse.ArgumentParser();p.add_argument("--source-bdae-zip",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 args=p.parse_args()
 with zipfile.ZipFile(args.source_bdae_zip) as z:
  src=z.read("bdae_scene_parser.py")
  ns={"__name__":"source_decoder","__file__":"bdae_scene_parser.py"}
  exec(compile(src,"bdae_scene_parser.py","exec"),ns)
  output=[]
  for name in NAMES:
   b=z.read("original_models/"+name+".bdae")
   with contextlib.redirect_stdout(io.StringIO()):
    meshes,_=ns["parse"](b)
   offsets=[int(m["mesh_descriptor"]) for m in meshes]
   cands=candidates(b)
   for c in cands:
    c["nearest_source_mesh_descriptor_bytes"]=min(abs(c["native_offset"]-i) for i in offsets)
    c["nearest_source_mesh_descriptor_ordinal"]=int(np.argmin([abs(c["native_offset"]-i) for i in offsets]))
   high=sorted(cands,key=lambda x:x["nearest_source_mesh_descriptor_bytes"])
   output.append({"source_original_BRES":name,"source_file_sha256":hashlib.sha256(b).hexdigest(),
      "original_BRES_native_bytes":len(b),"original_mesh_descriptors":offsets,
      "genuine_rigid_16_f32_candidate_count_z_nonzero":len(cands),
      "candidates_near_native_mesh_descriptors_within_256B":sum(c["nearest_source_mesh_descriptor_bytes"]<=256 for c in cands),
      "nearest_candidates_source_forensic_only":high[:25],
      "native_mesh_descriptor_transform_link_PROVEN":False})
 report={"source_owner_2010_C1L1_static_BRES_files":len(output),
  "source_original_370_meshes":sum(len(r["original_mesh_descriptors"]) for r in output),
  "source_4x4_matrix_candidates_z_nonzero_across_10_BRES":
   sum(r["genuine_rigid_16_f32_candidate_count_z_nonzero"] for r in output),
  "source_mat4_candidates_near_mesh_descriptor":
   sum(r["candidates_near_native_mesh_descriptors_within_256B"] for r in output),
  "original_source_native_BRES_model_4x4_transform_candidates":output,
  "source_raw_binary_matrix_scanning_does_NOT_prove_scene_transform":True,
  "no_made_up_vertical_offset_no_VPK":True}
 assert report["source_original_370_meshes"]==370
 args.out.parent.mkdir(parents=True,exist_ok=True)
 args.out.write_text(json.dumps(report,indent=2)+"\n")
 print("G45 original 2010 BRES 10 files, 370 meshes, nontrivial raw native matrix-candidate count",
   report["source_4x4_matrix_candidates_z_nonzero_across_10_BRES"])
 print("G45 native 4x4 matrix candidate within 256 bytes of mesh descriptor",
   report["source_mat4_candidates_near_mesh_descriptor"])
 print("G45 individual BRES native candidate counts",[(r["source_original_BRES"],r["genuine_rigid_16_f32_candidate_count_z_nonzero"],
  r["candidates_near_native_mesh_descriptors_within_256B"]) for r in output])
 print("PASS G45 source-raw 2010 BRES affine matrix candidate forensic; do not treat candidate as proven root/world transform, NO VPK")
if __name__=="__main__":main()
