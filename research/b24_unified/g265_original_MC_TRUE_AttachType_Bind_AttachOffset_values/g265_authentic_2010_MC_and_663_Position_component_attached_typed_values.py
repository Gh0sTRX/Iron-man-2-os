#!/usr/bin/env python3
"""G265 actual original 2010 C1L1 PositionData AttachType/Bind_To_Entity/
AttachOffset SOURCE VALUES. Decode three explicitly tagged typed fields
out of each of 663 G24-proven Position child records, cross-check labels
and native ARM getter/data offsets from G261/G262/G263/G264.

The original MC local Position Z25.054 is NOT claimed to be the final
2010 runtime foot position nor the Vita game's spawn.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,math,struct,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from b24_owner_pack_extract import decode,get_exact
from b24_g24_original_clara_source_601_nodes_663_parent_links import audit,native_names

def scan(ipa:Path, g261:Path, g263:Path, g264:Path, output:Path):
 j261=json.loads(g261.read_text())
 j263=json.loads(g263.read_text())
 j264=json.loads(g264.read_text())
 required={
  "AttachType":("int","0x38"),
  "Bind_To_Entity":("int","0x2c"),
  "AttachOffset":("vector3","0x3c"),
 }
 props={v["source_2010_typed_param_name"]:v for v in j261["true_original_native_six_2010_typed_Transform_parameters"]}
 for k,(kind,off) in required.items():
  if (props[k]["native_2010_getter_kind"],props[k]["native_2010_field_offset_in_PositionData"])!=(kind,off):
   raise ValueError("G265 original native getter type/field changed "+k)
 if not j263["original_C1L1_field_92_child_parent_tag_structure_proven"] or j264["total_original_2010_tag92_source_position_components"]!=663:
  raise ValueError("G265 authentic source record grammar predecessor proof absent")
 if ipa.stat().st_size!=248613763:raise ValueError("G265 genuine user owner iOS IPA size drift")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip() is not None:raise ValueError("source 2010 IPA corrupted")
  raw=get_exact(z.read("Payload/IronMan2.app/clev"),decode(z.read("Payload/IronMan2.app/clev"),".bclara"),"level1.bclara")
 if len(raw)!=339733:raise ValueError("original C1L1 changed")
 graph=audit(raw)
 if len(graph["all_663_source_rigid_transforms_with_native_parent_child_name_ID_chain"])!=663:
  raise ValueError("source 663 Position component nodes not stable")
 names={x["original_numeric_name_id"]:x["original_name"] for x in native_names(raw)}
 modes=collections.Counter(); bindings=collections.Counter()
 bound_refs=[]; source_values=[]
 for entry in graph["all_663_source_rigid_transforms_with_native_parent_child_name_ID_chain"]:
  p=entry["native_transform_source_offset"]
  pre=raw[p-36:p]
  if not (pre[8:12]==b"\x06\x00\x04\x00" and pre[16:18]==b"\x04\x00" and pre[22:24]==b"\x0c\x00"):
   raise ValueError(f"G265 original typed Attach fields length tags changed at {p}")
  mode=struct.unpack_from("<i",pre,12)[0]
  bind=struct.unpack_from("<i",pre,18)[0]
  offset=struct.unpack_from("<3f",pre,24)
  if not all(math.isfinite(v) for v in offset):
   raise ValueError("G265 source original nonfinite Bind_AttachOffset")
  modes[mode]+=1;bindings[bind]+=1
  row={
   "original_name":entry["original_named_parent"],
   "source_parent_node_ID":entry["original_named_parent_source_ID"],
   "original_Position_component_child_ID":entry["original_child_node_ID"],
   "native_original_CLARA_position_record_offset":p,
   "original_iOS_AttachType_typed_int":mode,
   "original_iOS_Bind_To_Entity_typed_int":bind,
   "original_iOS_AttachOffset_typed_vector3":[round(v,6) for v in offset],
   "source_binding_node_name_if_same_C1L1_name_ID_exists":names.get(bind),
   "original_actual_runtime_player_world_root_proven":False}
  if bind>=0:bound_refs.append(row)
  if entry["original_named_parent"] in {"MC","Sun001","SpawnPoint000","SpawnPoint001"}:
   source_values.append(row)
 mc=[x for x in source_values if x["original_name"]=="MC"]
 if len(mc)!=1:raise ValueError("genuine native MC original Position component not unique")
 mc=mc[0]
 if (mc["source_parent_node_ID"],mc["original_Position_component_child_ID"])!=(1062,1064):
  raise ValueError("MC source identity mismatched")
 if (mc["original_iOS_AttachType_typed_int"],mc["original_iOS_Bind_To_Entity_typed_int"],
     mc["original_iOS_AttachOffset_typed_vector3"])!=(0,-1,[0.0,0.0,0.0]):
  raise ValueError("G265 source MC typed attachment values changed; do not infer world transform")
 report={
  "source":"G265 genuine owner 2010 iOS level1.bclara ALL 663 true typed PositionData AttachType int, Bind_To_Entity int, AttachOffset vec3 from self-consistent length-tagged binary and native C++ getters",
  "original_2010_source_level1_sha256":hashlib.sha256(raw).hexdigest(),
  "authentic_source_Position_component_count":663,
  "original_source_AttachType_distribution":{str(k):v for k,v in sorted(modes.items())},
  "original_source_Bind_To_Entity_top_values":[{"original_bind_id":v,"count":n,"bound_named_C1L1_node":names.get(v)} for v,n in bindings.most_common(20)],
  "original_source_nonnegative_bind_pointer_records_count":len(bound_refs),
  "original_C1L1_nonnegative_bound_Position_records":bound_refs,
  "original_source_named_test_entities_exact_typed_attachment_records":source_values,
  "original_MC_Position_AttachType":mc["original_iOS_AttachType_typed_int"],
  "original_MC_Position_Bind_To_Entity":mc["original_iOS_Bind_To_Entity_typed_int"],
  "original_MC_Position_AttachOffset":mc["original_iOS_AttachOffset_typed_vector3"],
  "source_native_six_Attach_property_type_and_offset_verification":True,
  "original_MC_has_positive_attach_binding_through_authored_PositionData":False,
  "original_MC_story_start_runtime_world_Z_or_foot_position_PROVEN":False,
  "real_physical_Vita_walk_in_place_fixed":False,
  "vita_engine_movement_camera_lighting_or_combat_modified":False,
  "NO_VPK":True
 }
 output.parent.mkdir(parents=True,exist_ok=True)
 output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G265 original 2010 MC ATTACH TYPED SOURCE VALUES",mc)
 print("G265 all 663 PositionData native source AttachType distribution",dict(modes))
 print("G265 source count bound-to-another-entity",len(bound_refs),"bindings top",bindings.most_common(20))
 for row in bound_refs[:25]:print("G265 source actually attached node sample",row)
 print("G265 PASS original MC PositionData AttachType=0 Bind_To_Entity=-1 AttachOffset=(0,0,0); no runtime world boot inference, no Vita gameplay changes, NO VPK")
 return report
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g261",type=Path,required=True)
 p.add_argument("--g263",type=Path,required=True)
 p.add_argument("--g264",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 q=p.parse_args()
 scan(q.ipa,q.g261,q.g263,q.g264,q.out)
