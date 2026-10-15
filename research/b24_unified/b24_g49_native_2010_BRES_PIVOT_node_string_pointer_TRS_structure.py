#!/usr/bin/env python3
"""G49 exact ORIGINAL 2010 BDAE source _PIVOT string-to-node relationship scan.

New EXTERNAL FACT from fata1error404/oac-bdae-viewer newer 0.0.0.779:
node struct has 3 name pointers, native XYZ/quaternion/scale and child links;
_PIVOT helper affects effective parent mesh transform. We discovered literal
_PIVOT in ALL TEN authentic original 2010 0.0.0.133 source BRES archives.

Test whether 2010 BRES string name offsets are referenced as native 32-bit
absolute pointers or signed/unsigned relative pointers, and whether genuine
float32 XYZ/Q/S exists near those pointer fields.

NO attempt to apply external layout blindly. Only mark structural candidates;
NEVER reposition source geometry without model-node attachment proof.
"""
from __future__ import annotations
import argparse,collections,json,zipfile,re,hashlib
from pathlib import Path
import numpy as np

STEMS=["C1L1_ground_001","C1L1_obj_001","C1L1_obj_002",
       "C1L1_obj_003","C1L1_obj_004","C1L1_light_001",
       "C1L1_light_002","C1L1_light_003","C1L1_car_01","C1L1_car_02"]
PIVOT_RE=re.compile(rb'[A-Za-z0-9_./-]{1,100}_PIVOT')

def trs_at(raw,offset):
 if offset<0 or offset+40>len(raw) or offset%4:return None
 try: v=np.frombuffer(raw,dtype="<f4",count=10,offset=offset).astype(np.float64)
 except (ValueError,TypeError):return None
 if not np.isfinite(v).all():return None
 if np.any(np.abs(v[:3])>5000.):return None
 if abs(float(v[3:7]@v[3:7])-1)>0.01:return None
 if np.any((np.abs(v[7:10])<.0001)|(np.abs(v[7:10])>100)):return None
 return {
    "source_raw_candidate_TRS_byte_offset":int(offset),
    "source_raw_xyz":[round(float(x),5) for x in v[:3]],
    "source_raw_quaternion_xyzw":[round(float(x),5) for x in v[3:7]],
    "source_raw_scale_xyz":[round(float(x),5) for x in v[7:10]],
    "source_original_engine_mesh_bind_PROVEN":False
 }

def audit_native(raw):
 words=np.frombuffer(raw[:len(raw)//4*4],dtype="<u4")
 addresses=(np.arange(len(words),dtype="<u8")*4)
 found=[]
 for m in PIVOT_RE.finditer(raw):
  start,end=m.start(),m.end()
  name=m.group().decode("ascii",errors="replace")
  if len(name)>110:continue
  data=[]
  for target in {start,end,start+4,start-4}:
   if target<0 or target>=len(raw):continue
   absolute=(words==target)
   relative=((words.astype("<u8")+addresses)&0xffffffff)==target
   for typ,mask in (("absolute_direct_32bit",absolute),("relative_add_from_word_u32",relative)):
    hits=np.flatnonzero(mask)
    if len(hits)>1000:continue
    for h in hits:
     off=int(h)*4
     potentials=[]
     for pos in (off+4,off+8,off+12,off+16,off+20,off+24,off+32):
      t=trs_at(raw,pos)
      if t:potentials.append(t)
     data.append({"original_source_binary_reference_field_offset":off,
       "target_original_string_byte_offset":target,
       "reference_encoding_hypothesis":typ,
       "nearby_native_TRS_candidate_count":len(potentials),
       "nearby_native_TRS_values_forensic_only":potentials[:2]})
  found.append({
   "original_SOURCE_PIVOT_string":name,
   "source_PIVOT_ascii_offset":start,
   "number_of_native_absolute_or_relative_string_pointer_candidates":len(data),
   "source_candidate_name_pointer_records":sorted(data,key=lambda x:(-x["nearby_native_TRS_candidate_count"],x["original_source_binary_reference_field_offset"]))[:24],
   "original_source_BDAE_0_0_0_133_actual_node_record_transform_PROVEN":False})
 return found

def main():
 p=argparse.ArgumentParser();p.add_argument("--zip",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
 args=p.parse_args()
 result=[]
 with zipfile.ZipFile(args.zip) as z:
  for stem in STEMS:
   raw=z.read("original_models/"+stem+".bdae")
   n=audit_native(raw)
   result.append({"source_model":stem,"owner_original_2010_BRES_sha256":hashlib.sha256(raw).hexdigest(),
     "native_binary_bytes":len(raw),
     "exact_original_PIVOT_label_count":len(n),
     "native_original_PIVOT_strings_with_pointers":sum(x["number_of_native_absolute_or_relative_string_pointer_candidates"]>0 for x in n),
     "native_original_PIVOT_labels_with_nearby_TRS_pointer_records":
      sum(any(y["nearby_native_TRS_candidate_count"] for y in x["source_candidate_name_pointer_records"]) for x in n),
     "sample_pivot_node_pointer_structures":n[:12],
     "source_PROVEN_original_mesh_node_hierarchy":False})
 report={"source_original_BRES_tested":len(result),
   "original_2010_all_BRES_strings_with_PIVOT":
    sum(x["exact_original_PIVOT_label_count"] for x in result),
   "original_2010_pivot_nodes_with_raw_referencing_u32_fields":
    sum(x["native_original_PIVOT_strings_with_pointers"] for x in result),
   "source_original_PIVOT_labels_with_pointer_near_valid_float32_TRS":
    sum(x["native_original_PIVOT_labels_with_nearby_TRS_pointer_records"] for x in result),
   "source_original_c1l1_BRES_PIVOT_and_native_pointer_structural_evidence":result,
   "external_BDAE_reference":"https://github.com/fata1error404/oac-bdae-viewer/blob/main/parserBDAE.cpp",
   "older_original_2010_0_0_0_133_layout_assumed_equal_to_new_0_0_0_779":False,
   "original_native_mesh_name_to_node_name_mapping_verified":False,
   "original_native_mesh_vertex_matrix_applied":False,
   "NO_VPK":True}
 assert len(result)==10 and all(x["exact_original_PIVOT_label_count"]>0 for x in result)
 args.out.parent.mkdir(parents=True,exist_ok=True)
 args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G49 original source 10 static BRES native literal _PIVOT labels",
       report["original_2010_all_BRES_strings_with_PIVOT"])
 print("G49 source _PIVOT name references as 32bit absolute/relative",
       report["original_2010_pivot_nodes_with_raw_referencing_u32_fields"])
 print("G49 _PIVOT literal name pointer references beside plausible native float32 TRS",
       report["source_original_PIVOT_labels_with_pointer_near_valid_float32_TRS"])
 print("G49 per original BRES source model",[(x["source_model"],
   x["exact_original_PIVOT_label_count"],x["native_original_PIVOT_strings_with_pointers"],
   x["native_original_PIVOT_labels_with_nearby_TRS_pointer_records"]) for x in result])
 print("PASS source native original literal _PIVOT and source pointer structural audit, not false world placement, no VPK.")
if __name__=="__main__":main()
