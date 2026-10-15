#!/usr/bin/env python3
"""G48 external-method crosscheck on ORIGINAL Gameloft Iron Man 2 2010 source.

Inspired by known open-source (OTHER, newer format!) Gameloft BDAE native node
tree: fata1error404/oac-bdae-viewer, parserBDAE.cpp (~v0.0.0.779):
  3 node name pointers + float XYZ/Q/scale + node child count/off, parent
  cumulative matrices and _PIVOT helper.

This is explicitly a PROBE for compatibility with our 2010 v0.0.0.133 BRES,
NOT copying v779 offsets unverified and NOT applying unknown transforms.
Also extracts owner's CFBundleShortVersionString to see which touchHLE Iron
Man 2 compatibility report corresponds to actual user's owned IPA.
NO VPK/performance/reposition or guessed shader.
"""
from __future__ import annotations
import argparse,collections,json,hashlib,plistlib,struct,zipfile
from pathlib import Path
import numpy as np

NAME_STEMS=["C1L1_ground_001","C1L1_obj_001","C1L1_obj_002",
 "C1L1_obj_003","C1L1_obj_004","C1L1_light_001","C1L1_light_002",
 "C1L1_light_003","C1L1_car_01","C1L1_car_02"]

def contiguous_2010_native_trs_fingerprint(raw):
 # Transparent conservative heuristic:
 # scan four-byte aligned XYZ float3, unit quaternion float4,
 # nonzero finite scale float3, raw offsets contiguous 40 bytes.
 # Require nontrivial XYZ or quaternion and nonzero sensible scale.
 # It may find NON-nodes: don't assign to specific meshes.
 body=np.frombuffer(raw[:len(raw)//4*4],dtype="<f4")
 from numpy.lib.stride_tricks import sliding_window_view
 if len(body)<10:return []
 data=sliding_window_view(body,10)
 valid=np.isfinite(data).all(axis=1)
 valid &= np.all(np.abs(data[:,:3])<=5000,axis=1)
 quat=data[:,3:7]
 qlen=np.sum(quat*quat,axis=1)
 valid &= np.abs(qlen-1.)<=.005
 scl=data[:,7:10]
 valid &= np.all((np.abs(scl)>=.001)&(np.abs(scl)<=200.),axis=1)
 valid &= (np.any(np.abs(data[:,:3])>1e-3,axis=1)|
           np.any(np.abs(quat[:,:3])>.001,axis=1)|
           np.any(np.abs(scl-1.)>.005,axis=1))
 matched=np.flatnonzero(valid)
 # All candidate TRS have to be correlated with 2010 source node table
 # and actual mesh references before being accepted as real transforms.
 return [{"source_raw_offset":int(i*4),
          "candidate_local_XYZ":[round(float(v),5) for v in data[i,:3]],
          "candidate_quaternion_xyzw":[round(float(v),5) for v in data[i,3:7]],
          "candidate_scale_xyz":[round(float(v),5) for v in data[i,7:10]],
          "verified_native_BRES_node_transform":False}
         for i in matched[:800]]

def run(ipa,source_bdae_zip,out):
 with zipfile.ZipFile(ipa) as z:
  infos=[n for n in z.namelist() if n.endswith("/Info.plist") and n.startswith("Payload/IronMan2.app/")]
  if len(infos)!=1:raise RuntimeError("owner original Info.plist path unclear: "+repr(infos))
  pl=plistlib.loads(z.read(infos[0]))
  ident=pl.get("CFBundleIdentifier","")
  version=pl.get("CFBundleShortVersionString") or pl.get("CFBundleVersion") or ""
  build=pl.get("CFBundleVersion","")
  exe=pl.get("CFBundleExecutable","")
 assert exe and ident
 original=[]
 with zipfile.ZipFile(source_bdae_zip) as z:
  for name in NAME_STEMS:
   raw=z.read("original_models/"+name+".bdae")
   found=contiguous_2010_native_trs_fingerprint(raw)
   original.append({
     "original_2010_BRES_file":name,
     "source_binary_size":len(raw),
     "native_file_magic":raw[:4].hex(),
     "original_binary_sha256":hashlib.sha256(raw).hexdigest(),
     "original_source_PIVOT_plain_ascii_name_occurrences":raw.count(b"_PIVOT"),
     "original_source_all_PIVOT_case_insensitive_matches":raw.upper().count(b"PIVOT"),
     "original_source_mesh_related_ascii_refs":{t:raw.count(t.encode("ascii")) for t in ["mesh","Node","node","PIVOT"]},
     "source_float32_contiguous_TRS_possible_records_heuristic_count":len(found),
     "possible_raw_TRS_float32_sample_up_to_18":found[:18],
     "actual_2010_BRES_node_table_and_mesh_node_binding_DECIPHERED":False})
 report={
   "original_user_2010_iron_man_2_CFBundleIdentifier":ident,
   "original_user_2010_iron_man_2_CFBundleShortVersionString":version,
   "original_user_2010_iron_man_2_CFBundleVersion":build,
   "original_user_2010_iron_man_2_executable":exe,
   "touchHLE_compatibility_database_independent_external_versions":{
      "1.0.0":"5-star reported playable in touchHLE 0.2.3 for iPhone",
      "1.0.1":"3-star prior report",
      "1.0.3":"1-star in older 2024 touchHLE build; current behavior untested"},
   "touchHLE_owner_IPA_version_exact_report_1_0_0":str(version)=="1.0.0",
   "source_2010_static_BRES_files_analyzed":len(original),
   "external_comparison_BDAE_version_0_0_0_779_NODE_LAYOUT_SOURCE":
      "https://github.com/fata1error404/oac-bdae-viewer/blob/main/parserBDAE.cpp",
   "external_node_layout_claim_applies_unchanged_to_2010_BRES_0_0_0_133":False,
   "native_original_BRES_node_name_PIVOT_probe":original,
   "source_binary_node_hierarchy_semantics_verified_from_C1L1":False,
   "actual_original_2010_runtime_OpenGL_drawing_captured":False,
   "original_BRES_polygons_moved_or_shader_guess_applied":False,
   "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G48 original user-owned IPA Info.plist",ident,version,"build",build,"exe",exe)
 print("G48 original source 10 BRES _PIVOT literal counts",
   [(r["original_2010_BRES_file"],r["original_source_PIVOT_plain_ascii_name_occurrences"],
     r["source_float32_contiguous_TRS_possible_records_heuristic_count"]) for r in original])
 print("G48 source external adaptation of newer BDAE node system is HYPOTHESIS for our older data. No VPK, no fabricated root.")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--source-bdae-zip",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True);v=p.parse_args()
 run(v.ipa,v.source_bdae_zip,v.out)
