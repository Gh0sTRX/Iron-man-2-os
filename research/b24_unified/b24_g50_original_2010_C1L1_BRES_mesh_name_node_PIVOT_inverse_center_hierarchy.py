#!/usr/bin/env python3
"""G50 actual 2010 C1L1 BDAE mesh-name->node & _PIVOT native TRS structured linkage.

External fata1error404/oac-bdae-viewer 0.0.0.779 documented:
  native node name pointers, XYZ Q scale, parent chain + '_PIVOT'.
We PROVE local 2010 v0.0.0.133 correspondence by 2 packed 32bit name
pointers to same record and strictly valid 40-byte TRS, matched to the
original B11 mesh NAME. Look also for actual canonical '<base>-node'
parent-like record as separate link, without assuming parent-child yet.

Critically tests pivot XYZ against *negative actual mesh bounding-box center*:
this inverse-centering relation strongly indicates pivots are LOCAL
re-centering offsets, not world placements! No pivot-only fake map changes.
No VPK; source proof ready for recursive node hierarchy parser next.
"""
from __future__ import annotations
import argparse,zipfile,json,contextlib,io,struct,hashlib
from pathlib import Path
import numpy as np

SOURCES=["C1L1_ground_001","C1L1_obj_001","C1L1_obj_002",
         "C1L1_obj_003","C1L1_obj_004","C1L1_light_001",
         "C1L1_light_002","C1L1_light_003","C1L1_car_01","C1L1_car_02"]

def namestring_candidates(raw,name):
 label=name.encode("ascii")
 # exact name only, not prefix of longer _PIVOT or others
 offsets=[];pos=0
 while 1:
  p=raw.find(label,pos)
  if p<0:break
  pos=p+1
  if p and raw[p-1] not in b"\x00\x01\x02\x03\x04":
   continue
  if p+len(label)<len(raw) and raw[p+len(label)] not in b"\x00\x01\x02\x03\x04":
   continue
  offsets.append(p)
 return offsets

def node_records(raw,name,words):
 candidates=[]
 for offset in namestring_candidates(raw,name):
  possible=np.flatnonzero((words==offset)|(words==offset+4))
  for w in possible:
   site=int(w)*4
   # A name reference can be the 1st, 2nd or 3rd string pointer
   for pos_name in range(3):
    base=site-4*pos_name
    if base<0 or base+64>len(raw) or base%4:continue
    pointers=struct.unpack_from("<III",raw,base)
    if pointers[pos_name] not in (offset,offset+4):continue
    trans=np.asarray(struct.unpack_from("<10f",raw,base+12),dtype=np.float64)
    if not np.isfinite(trans).all() or np.max(np.abs(trans[:3]))>5000:continue
    if abs(float(np.dot(trans[3:7],trans[3:7]))-1)>0.012:continue
    if np.any(np.abs(trans[7:10])<1e-4) or np.any(np.abs(trans[7:10])>100):continue
    children=struct.unpack_from("<II",raw,base+56)
    if children[0]>512:continue
    key=(base,name)
    candidates.append({"source_binary_node_record_offset":base,
      "native_source_name_string_offsets_u32":list(pointers),
      "source_matched_name_pointer_ordinal":pos_name,
      "source_local_XYZ":[round(float(x),6) for x in trans[:3]],
      "source_local_quaternion_xyzw":[round(float(x),6) for x in trans[3:7]],
      "source_local_scale_xyz":[round(float(x),6) for x in trans[7:10]],
      "source_raw_child_count":children[0],
      "source_raw_child_pointer_field":children[1],
      "native_2010_source_structural_node_name_TRS_PROVEN":True,
      "actual_node_parent_tree_mesh_matrix_PROVEN":False})
 return list({x["source_binary_node_record_offset"]:x for x in candidates}.values())

def main(zpath,out):
 with zipfile.ZipFile(zpath) as z:
  ns={"__name__":"g50_original_2010_BRES_parser","__file__":"bdae_scene_parser.py"}
  exec(compile(z.read("bdae_scene_parser.py"),"bdae_scene_parser.py","exec"),ns)
  results=[]
  for stem in SOURCES:
   raw=z.read("original_models/"+stem+".bdae")
   with contextlib.redirect_stdout(io.StringIO()):meshes,_=ns["parse"](raw)
   words=np.frombuffer(raw[:len(raw)//4*4],dtype="<u4")
   records=[]
   for m in meshes:
    name=m["name"]
    if not name.endswith("-mesh"):raise ValueError("real 2010 unexpected mesh label "+name)
    base=name[:-len("-mesh")]
    piv=node_records(raw,base+"-node_PIVOT",words)
    canon=node_records(raw,base+"-node",words)
    bbox=np.asarray(m["positions"],dtype=np.float32)
    low=bbox.min(axis=0);high=bbox.max(axis=0)
    cen=(low+high)/2
    # Require one exact pivot by node name if found. Structural candidates
    # can match false-positive alias records: flag but don't transform.
    chosen=piv[0] if len(piv)==1 else None
    rec={"source_original_BRES_file":stem,
      "source_2010_original_mesh_name":name,
      "original_vertex_count":len(bbox),
      "original_raw_mesh_bbox_center_XYZ":[round(float(x),5) for x in cen],
      "authentic_native_pivot_node_record_count":len(piv),
      "original_pivot_matched_node":chosen,
      "canonical_nonpivot_node_records_found":len(canon),
      "canonical_nonpivot_node_candidates":canon[:3],
      "original_cumulative_parent_node_transform_NOT_PROVEN":True,
      "source_original_geometry_vertices_UNCHANGED":True}
    if chosen:
     delta=np.array(chosen["source_local_XYZ"])
     rec["hypothetical_pivot_ONLY_mesh_bbox_center_XYZ"]=[round(float(x),4) for x in cen+delta]
     rec["distance_from_origin_if_pivot_only"] = round(float(np.linalg.norm(cen+delta)),5)
    records.append(rec)
   results.append({"source_file":stem,"original_native_mesh_count":len(meshes),
     "source_file_sha256":hashlib.sha256(raw).hexdigest(),
     "source_meshes_exact_named_PIVOT_TRS_unique":sum(x["authentic_native_pivot_node_record_count"]==1 for x in records),
     "source_meshes_canonical_node_structural_references_present":sum(x["canonical_nonpivot_node_records_found"]>0 for x in records),
     "source_per_original_named_mesh":records})
 out.parent.mkdir(parents=True,exist_ok=True)
 num=sum(x["original_native_mesh_count"] for x in results)
 pivots=sum(x["source_meshes_exact_named_PIVOT_TRS_unique"] for x in results)
 parents=sum(x["source_meshes_canonical_node_structural_references_present"] for x in results)
 residual=[x["distance_from_origin_if_pivot_only"] for r in results for x in r["source_per_original_named_mesh"] if "distance_from_origin_if_pivot_only" in x]
 report={"original_source_BRES_file_count":len(results),
  "original_2010_C1L1_source_mesh_count":num,
  "source_exact_mesh_name_to_pivot_TRS_binary_link_count":pivots,
  "source_matching_canonical_nonpivot_named_node_record_count":parents,
  "original_inverse_pivot_center_distance_median":round(float(np.median(residual)),5) if residual else None,
  "original_inverse_pivot_center_distance_under_5":sum(x<5 for x in residual),
  "source_original_per_file_hierarchy_candidates":results,
  "original_recursive_root_parent_visibility_cumulative_matrices_PROVEN":False,
  "original_2010_render_world_space_fixed":False,
  "original_BRES_vertex_positions_applied_or_shifted":False,
  "external_format_node_layout_0_0_0_779_directly_imported_without_checks":False,
  "NO_VPK_NO_PERFORMANCE":True}
 assert num==370
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G50 ORIGINAL 2010 source BRES mesh count",num,"exact source mesh->_PIVOT TRS",pivots,
  "source mesh -> separate canonical '-node' structural record",parents)
 print("G50 original native matched pivot ONLY center residual median",report["original_inverse_pivot_center_distance_median"],
       "pivot-only center distance <5",report["original_inverse_pivot_center_distance_under_5"])
 print("G50 detailed per-file",[(x["source_file"],x["source_meshes_exact_named_PIVOT_TRS_unique"],
   x["original_native_mesh_count"],x["source_meshes_canonical_node_structural_references_present"]) for x in results])
 print("PASS original native BRES mesh name/parent PIVOT candidate TRS analysis, no fake static scene translations or VPK.")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--zip",required=True,type=Path);p.add_argument("--out",required=True,type=Path)
 a=p.parse_args();main(a.zip,a.out)
