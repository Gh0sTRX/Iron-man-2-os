#!/usr/bin/env python3
"""G38 — Prove 2010 owner's CLARA Deco 0x4D numeric resource -> ORIGINAL models PACK filename.

There is a separate native named Gameloft resource archive, Payload/IronMan2.app/models.
Its source index is the original byte order (NOT alphabetically reordered!).
This forensic work checks whether original Deco 4-byte native resource indices
point exactly at the 2010 original models entries. Nine independent CLARA
Deco_car/light/obj names are used as a STRICT holdout check, plus all other
53 real Deco nodes are crosslinked if and only if the full 9/9 exact model
family match occurs with an unambiguous zero- or one-based offset.

This is NOT a scene graph world-parent transform or final original lighting.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,json,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact
from b24_g37_original_C1L1_Deco_resource_type_scene_instances import audit,FAMILY

def run(ipa:Path,out:Path,csv_out:Path):
 with zipfile.ZipFile(ipa) as z:
  pack=z.read("Payload/IronMan2.app/models")
  clev=z.read("Payload/IronMan2.app/clev")
 entries=decode(pack)
 level=get_exact(clev,decode(clev,".bclara"),"level1.bclara")
 props=audit(level)
 models=[{"source_archive_index_zero_based":i,
          "source_original_model_name":r.name,
          "source_model_pack_start":r.start,
          "source_model_pack_end":r.end,
          "source_original_model_bytes":r.end-r.start}
          for i,r in enumerate(entries)]
 source=props["source_decoded_native_Deco_0x4D_resource_fields_and_0x5C_transforms"]
 offsets=[]
 for shift in (-1,0,1):
  proven=[]
  for item in source:
   expected=FAMILY.get(item["native_raw_resource_type_uint32"])
   if not expected:continue
   idx=item["native_raw_resource_type_uint32"]+shift
   observed=entries[idx].name if 0<=idx<len(entries) else ""
   match=observed.removesuffix(".bdae").casefold()==expected.casefold()
   proven.append({"native_resource_value":item["native_raw_resource_type_uint32"],
                  "original_Deco_entity":item["source_Deco_name"],
                  "actual_original_model":observed,
                  "expected_original_BRES_family":expected,
                  "match":match})
  offsets.append({"candidate_model_pack_index_shift":shift,
                  "exact_independent_nine_source_correspondences":sum(x["match"] for x in proven),
                  "out_of_original_nine":len(proven),
                  "proof":proven})
 hits=[row for row in offsets if row["exact_independent_nine_source_correspondences"]==9]
 matched_shift=hits[0]["candidate_model_pack_index_shift"] if len(hits)==1 else None
 joined=[]
 for row in source:
  idx=(row["native_raw_resource_type_uint32"]+matched_shift
       if matched_shift is not None else None)
  target=models[idx] if idx is not None and 0<=idx<len(models) else None
  joined.append({**row,
      "source_archive_index_shift_from_original_CLARA_type":matched_shift,
      "source_models_original_zero_based_index":idx,
      "source_original_model_name":target["source_original_model_name"] if target else None,
      "source_original_model_byte_size":target["source_original_model_bytes"] if target else None,
      "original_CLARA_Deco_resource_index_to_model_pack_proven":matched_shift is not None and target is not None,
      "source_CLARA_Deco_local_transform_is_native":True,
      "original_BRES_mesh_to_actor_world_matrix_PROVEN":False})
 results={
  "owner_original_2010_native_models_archive_entries":len(models),
  "owner_original_models_pack_sha256":hashlib.sha256(pack).hexdigest(),
  "source_exact_gameloft_named_model_pack_entries_in_native_order":models,
  "source_nine_independent_native_Deco_resource_to_named_BRES_correspondence_tests":offsets,
  "native_resource_field_to_model_archive_index_shift_PROVEN":matched_shift,
  "original_source_Deco_node_count":len(joined),
  "source_original_actor_model_binding_proven":matched_shift is not None,
  "source_exact_2010_CLARA_Deco_model_resource_links_with_local_transforms":joined,
  "source_original_instance_world_parent_matrix_AND_runtime_visibility_PROVEN":False,
  "source_original_material_shader_and_alpha_reconstructed":False,
  "no_VPK_or_performance_changes":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(results,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 csv_out.parent.mkdir(parents=True,exist_ok=True)
 fields=["source_Deco_name","original_source_entity_ID","native_raw_resource_type_uint32",
          "native_raw_secondary_uint32","source_original_model_name",
          "source_models_original_zero_based_index","source_X","source_Y","source_Z",
          "source_quat_xyzw","source_scale_xyz",
          "original_CLARA_Deco_resource_index_to_model_pack_proven",
          "original_BRES_mesh_to_actor_world_matrix_PROVEN"]
 with csv_out.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields)
  w.writeheader();w.writerows({k:row.get(k) for k in fields} for row in joined)
 print("G38 true original 2010 'models' archive native entries",len(models))
 print("G38 independent nine sourced Deco-family source archive index checks:",
       [(r["candidate_model_pack_index_shift"],
         r["exact_independent_nine_source_correspondences"],r["out_of_original_nine"])
        for r in offsets])
 print("G38 original archive first 35 names:",[r.name for r in entries[:35]])
 print("G38 original resource index shift proven",matched_shift)
 if matched_shift is not None:
  print("G38 static actual native file mapping 53/53:",
        [(r["source_Deco_name"],r["native_raw_resource_type_uint32"],r["source_original_model_name"])
         for r in joined])
 else:
  print("G38 NOT PROVEN: no direct naive native models order match; engine resource registry indirect.")
 print("PASS G38 source-original native archive resource index analysis. Real actor mesh world positions NOT yet reconstructed. No VPK.")
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--ipa",type=Path,required=True)
 a.add_argument("--out",type=Path,required=True)
 a.add_argument("--csv",type=Path,required=True)
 p=a.parse_args();run(p.ipa,p.out,p.csv)
