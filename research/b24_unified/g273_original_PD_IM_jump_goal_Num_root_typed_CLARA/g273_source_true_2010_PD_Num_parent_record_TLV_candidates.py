#!/usr/bin/env python3
"""G273 original user-owned 2010 C1L1 PositionDummy 'Num' root parameter
candidate enumeration. Genuine original iOS native GetParamValue('Num')
found G272. Decode named class36 entity prefix between class pointer
and first tagged Position child; do not assign a Num value until CLARA
TLV class/schema establishes its byte offset and type.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,struct,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from b24_owner_pack_extract import decode,get_exact
from b24_g24_original_clara_source_601_nodes_663_parent_links import audit
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
def inspect(ipa:Path,g272:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("not original owner IPA")
 prev=json.loads(g272.read_text())
 props={v["original_PositionDummy_native_property_kind"]:v["original_authentic_CPP_const_char_string"]
       for v in prev["actual_native_original_four_typed_positiondummy_property_names"]}
 if props!={"PositionDummy_mode_integer":"Num","PositionDummy_component_1":"Position1",
           "PositionDummy_component_2":"Position2","PositionDummy_component_3":"Position3"}:
  raise ValueError("2010 native PositionDummy original class source key names not verified")
 with zipfile.ZipFile(ipa) as z:
  clev=z.read("Payload/IronMan2.app/clev")
 raw=get_exact(clev,decode(clev,".bclara"),"level1.bclara")
 if len(raw)!=339733:raise ValueError("original owner level1 bytes drift")
 native=summarize(raw);graph=audit(raw)
 typed=[x for x in native["source_2010_typed_class_instances"] if x["original_class_name"]=="PositionDummy"]
 if len(typed)!=137:raise ValueError("original 2010 PositionDummy instance count drift")
 transform=collections.defaultdict(list)
 for row in graph["original_source_static_parent_record_links"]:
  if row["source_typed_record_field"]==92:
   transform[row["original_parent_id"]].append(row)
 results=[]
 for entry in typed:
  ident=entry["original_numeric_name_id"]
  records=sorted(transform[ident],key=lambda x:x["native_child_record_prefix_offset"])
  if len(records)!=3:raise ValueError("original source PositionDummy not three Position1-3 records")
  named_end=entry["original_name_offset"]+len(entry["original_name"])
  if raw[named_end:named_end+5]!=bytes([0x80,0xff,0xff,0xff,0xff]) or struct.unpack_from("<I",raw,named_end+5)[0]!=36:
   raise ValueError("PositionDummy class template pointer after native original name changed")
  end=records[0]["native_child_record_prefix_offset"]
  body_start=named_end+9
  body=raw[body_start:end]
  if len(body)>300 or len(body)<2:raise ValueError("PositionDummy root typed prefix unexpectedly sized")
  candidates=[]
  for off in range(len(body)-5):
   if body[off:off+2]==bytes([4,0]):
    iv=struct.unpack_from("<i",body,off+2)[0]
    candidates.append({"relative_to_root_class_id_end":off,"absolute_clara_byte_offset":body_start+off,
      "original_tlv_u16_length_tag":4,"candidate_LE_i32":iv,
      "Num_source_attribute_name_binding_proven":False})
  results.append({
    "original_source_name":entry["original_name"],"original_scene_node_ID":ident,
    "source_root_class_pointer_end_absolute_offset":body_start,
    "source_first_real_tag92_child_absolute_offset":end,
    "original_source_parent_record_payload_length":len(body),
    "original_PD_root_header_hex_metadata_for_parser_validation":body[:75].hex(),
    "source_typed_i32_0x0004_candidate_patterns":candidates,
    "original_true_Num_source_C1L1_value_PROVEN":False,
    "original_true_PositionDummy_local_or_world_runtime_goal_XYZ_PROVEN":False})
 counts=collections.Counter(x["original_source_parent_record_payload_length"] for x in results)
 candidate_offsets=collections.Counter((v["relative_to_root_class_id_end"],v["candidate_LE_i32"])
     for row in results for v in row["source_typed_i32_0x0004_candidate_patterns"])
 target=next(x for x in results if x["original_source_name"]=="PD_IM_jump_goal")
 pdmc=next(x for x in results if x["original_source_name"]=="PD_MC")
 report={
  "source":"G273 actual original 2010 iOS PositionDummy Num first-class integer parameter root TLV candidate proof across 137 nodes; no premature guess",
  "original_level1_sha256":hashlib.sha256(raw).hexdigest(),
  "authentic_native_2010_PositionDummy_source_key_Num":"Num",
  "original_Source_PositionDummy_type36_count":len(results),
  "original_all_PD_parent_root_payload_sizes":dict(counts),
  "native_source_137_entity_root_4byte_integer_tag_patterns":[
      {"relative_offset":o,"original_value":v,"frequency":n}
      for (o,v),n in candidate_offsets.most_common(50)],
  "PD_IM_jump_goal_actual_native_root_tlv_candidates":target,
  "PD_MC_actual_native_root_tlv_candidates_control":pdmc,
  "other_source_PD_root_examples":results[:10],
  "genuine_2010_Num_attribute_file_offset_resolved":False,
  "original_goal_C1L1_Num_real_value_resolved":False,
  "genuine_original_runtime_Mission000_move_to_goal_world_XYZ_proven":False,
  "Vita_ground_render_or_world_root_mutated":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G273 original 2010 native PositionDummy root prefix length frequencies",dict(counts))
 print("G273 source 137 PositionDummy 4-byte int tagged candidates",candidate_offsets.most_common(40))
 print("G273 original PD_IM_jump_goal header",target)
 print("G273 original PD_MC control header",pdmc)
 print("G273 PASS original 2010 class36 root-Num candidate TLV data audited; do not equate arbitrary tag to Num, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g272",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 q=p.parse_args();inspect(q.ipa,q.g272,q.out)
