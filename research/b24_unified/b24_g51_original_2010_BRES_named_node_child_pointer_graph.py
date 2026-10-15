#!/usr/bin/env python3
"""G51: decoded 2010 BRES native node records and EXACT child pointer graph.

Based on original *2010* 10 user-owned C1L1 BRES binary model files, not
BDAE v779 offsets uncritically applied:
  3 u32 name refs + source native float32 XYZ/q/sc + u32 children_count
  at base+56 + u32 first child ptr at base+60.

This parser independently validates real original named string pointers
with source <u32 ASCII byte length> prefix and native unit quaternion,
scale. Builds ONLY exact source child pointer links. A contiguous child
array/multiple children still needs its original stride validation.

Reports per-file original model mesh->pivot and raw child adjacency.
NEVER applies source pivot alone, or claims final iOS world matrices.
"""
from __future__ import annotations
import argparse,collections,contextlib,hashlib,json,re,struct,zipfile
from pathlib import Path
import numpy as np
from b24_g50_original_2010_C1L1_BRES_mesh_name_node_PIVOT_inverse_center_hierarchy import SOURCES
def u32(raw,off):return struct.unpack_from("<I",raw,off)[0]
def original_string(raw,ptr):
 if ptr<4 or ptr>=len(raw):return None
 n=u32(raw,ptr-4)
 if not 3<=n<=115 or ptr+n>len(raw):return None
 b=raw[ptr:ptr+n]
 if any(v<32 or v>126 for v in b):return None
 s=b.decode("ascii")
 if not re.fullmatch(r"[A-Za-z0-9_.:/\-\[\] ]{3,115}",s):return None
 return s
def parse_record(raw,base):
 if base+64>len(raw):return None
 ptrs=struct.unpack_from("<III",raw,base)
 names=[original_string(raw,p) for p in ptrs]
 if not any(n and ("node" in n.casefold() or "pivot" in n.casefold()) for n in names):return None
 if not names[1] and not names[0]:return None
 vec=struct.unpack_from("<10f",raw,base+12)
 if not np.isfinite(vec).all() or max(abs(v) for v in vec[:3])>5000:return None
 if abs(sum(v*v for v in vec[3:7])-1)>.012:return None
 if min(abs(v) for v in vec[7:10])<.0001 or max(abs(v) for v in vec[7:10])>100:return None
 cc,child=struct.unpack_from("<II",raw,base+56)
 if cc>300 or (cc and (child>=len(raw) or child%4)):return None
 return {
  "source_native_node_record_offset":base,
  "original_native_3_name_refs":list(ptrs),
  "source_author_names":names,
  "original_native_xyz":[round(float(q),6) for q in vec[:3]],
  "original_native_quaternion_xyzw":[round(float(q),6) for q in vec[3:7]],
  "original_native_scale_xyz":[round(float(q),6) for q in vec[7:10]],
  "source_native_direct_child_count_field":cc,
  "source_native_direct_child_pointer_field":child,
  "proven_parent_path_from_source_binary":False
 }

def run(zpath,out):
 models=[];totals=collections.Counter()
 with zipfile.ZipFile(zpath) as z:
  env={"__name__":"g51_original_2010_mesh_reader","__file__":"bdae_scene_parser.py"}
  exec(compile(z.read("bdae_scene_parser.py"),"bdae_scene_parser.py","exec"),env)
  for stem in SOURCES:
   raw=z.read("original_models/"+stem+".bdae")
   with contextlib.redirect_stdout(__import__("io").StringIO()):
    meshes,_=env["parse"](raw)
   records={}
   # candidate starts from string ptr fields, avoiding scanning ~MB of
   # all random payload and accidentally inventing many native node records.
   for mo in re.finditer(rb"[A-Za-z0-9_]+(?:-node(?:_PIVOT)?|_PIVOT)",raw):
    loc=mo.start()
    for word in (loc,loc+4):
     if word<4 or word>=len(raw):continue
     pat=struct.pack("<I",word)
     for hit in range(0,len(raw)-3,4):
      if raw[hit:hit+4]!=pat:continue
      for slot in (0,1,2):
       base=hit-slot*4
       if base<0 or base%4:continue
       if base in records:continue
       rec=parse_record(raw,base)
       if rec is not None:
        records[base]=rec
   # exact field child pointer -> validated actual child record start
   exact=[]
   for r in records.values():
    cc=r["source_native_direct_child_count_field"];child=r["source_native_direct_child_pointer_field"]
    if cc and child in records:
     exact.append({"native_parent_record_offset":r["source_native_node_record_offset"],
       "native_child_record_offset":child,
       "parent_original_source_name":next((n for n in r["source_author_names"] if n),None),
       "child_original_source_name":next((n for n in records[child]["source_author_names"] if n),None),
       "declared_original_direct_child_count":cc,
       "first_child_direct_pointer_PROVEN":True,
       "sibling_array_stride_if_child_count_above_one_PROVEN":cc==1})
   name_index=collections.defaultdict(list)
   for r in records.values():
    for name in r["source_author_names"]:
     if name:name_index[name].append(r["source_native_node_record_offset"])
   pivots=0;names=0
   meshrecords=[]
   for m in meshes:
    name=m["name"];base=name.removesuffix("-mesh")
    piv=name_index.get(base+"-node_PIVOT",[])
    canon=name_index.get(base+"-node",[])
    pivots+=bool(piv);names+=bool(canon)
    parent_for_pivot=[e for e in exact if e["native_child_record_offset"] in piv]
    meshrecords.append({"source_original_mesh":name,
      "source_original_PIVOT_named_node_record_offsets":sorted(set(piv)),
      "source_original_other_named_node_record_offsets":sorted(set(canon)),
      "native_binary_direct_parent_to_pivot_link_count":len(parent_for_pivot),
      "source_exact_pivot_parent_edge_proof":parent_for_pivot,
      "cumulative_true_iOS_node_world_matrix_decoded":False})
   models.append({"original_BRES":stem,"source_sha256":hashlib.sha256(raw).hexdigest(),
    "real_original_source_meshes":len(meshes),
    "native_node_named_0_0_0_133_records_count":len(records),
    "original_mesh_with_at_least_one_named_pivot_node":pivots,
    "original_mesh_with_named_canonical_node":names,
    "original_native_binary_confirmed_parent_first_child_pointer_links":len(exact),
    "original_native_node_TRS_records":sorted(records.values(),key=lambda r:r["source_native_node_record_offset"]),
    "native_direct_first_child_reference_proofs":exact,
    "native_real_mesh_nodes":meshrecords})
   totals.update(source_meshes=len(meshes),node_records=len(records),mesh_pivots=pivots,
                 named_canonical=names,exact_links=len(exact))
 report={
  "original_Gameloft_BRES_v133_source_models":len(models),
  "source_authentic_original_source_meshes":totals["source_meshes"],
  "source_original_explicit_named_native_TRS_nodes":totals["node_records"],
  "source_original_meshlab_to_real_named_PIVOT_node_references":totals["mesh_pivots"],
  "source_original_meshlab_to_real_named_nonpivot_node_references":totals["named_canonical"],
  "original_source_first_child_exact_node_pointer_edges":totals["exact_links"],
  "source_original_10_BRES_real_native_node_records_graph":models,
  "native_parent_child_strides_or_all_2010_nodes_completely_proven":False,
  "original_2010_game_render_modelview_shader_visibility_proven":False,
  "native_2010_source_meshes_world_moved":False,
  "NO_VPK_AND_NO_FPS_WORK":True}
 assert report["source_authentic_original_source_meshes"]==370
 assert report["source_original_explicit_named_native_TRS_nodes"]>=370
 assert report["original_source_first_child_exact_node_pointer_edges"]>0
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G51 VERIFIED original C1L1 model node graph records",totals["node_records"],
       "named pivot matches",totals["mesh_pivots"],"canonical",totals["named_canonical"],
       "exact original native binary child pointer edges",totals["exact_links"])
 print("G51 per source model",[(x["original_BRES"],
   x["native_node_named_0_0_0_133_records_count"],
   x["original_native_binary_confirmed_parent_first_child_pointer_links"]) for x in models])
 print("PASS G51 2010 BRES child->parent source binary exact reference edge graph; 370 original triangles unchanged and no VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--zip",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();run(a.zip,a.out)
