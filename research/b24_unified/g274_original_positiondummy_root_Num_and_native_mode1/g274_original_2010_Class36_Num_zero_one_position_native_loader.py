#!/usr/bin/env python3
"""G274 authentic original 2010 C1L1 PositionDummy 'Num' parsed from
37? actually 137 exact class36 EntityData typed root records; verified
against native PositionDummyEntity::LoadFromFile GetParamValue('Num'),
increment +1 and mode1 GetPosition(Position1). First named authored
PositionDummy source child may be Position1 but raw child-name index
requires separate explicit validation; never assert final gameplay world Z.
No Vita gameplay or VPK.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,struct,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from b24_owner_pack_extract import decode,get_exact
from b24_g24_original_clara_source_601_nodes_663_parent_links import audit
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize

def method(d,name):
 results=[v for v in d["original_cpp_source_function_ARM_bounded_metadata"]
          if v["genuine_original_CPP_method"]==name]
 if len(results)!=1:raise ValueError("2010 genuine C++ method missing "+name)
 return {int(x["true_original_vm"],16):x for x in results[0]["native_first_425_ARM_source_instructions"]}
def step(tbl,addr,mnem,args):
 q=tbl.get(addr)
 if not q or (q["op"],q["args"])!=(mnem,args):
  raise ValueError(f"G274 original 2010 {addr:#x} native source opcode drift {q}")
 return q
def run(ipa:Path,g271:Path,g272:Path,g273:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("not owner original 2010 game IPA")
 prev=json.loads(g271.read_text());text=json.loads(g272.read_text());source_prev=json.loads(g273.read_text())
 named={x["original_PositionDummy_native_property_kind"]:x["original_authentic_CPP_const_char_string"] for x in
   text["actual_native_original_four_typed_positiondummy_property_names"]}
 if named!={"PositionDummy_mode_integer":"Num","PositionDummy_component_1":"Position1",
  "PositionDummy_component_2":"Position2","PositionDummy_component_3":"Position3"}:
  raise ValueError("source previous actual PositionDummy string keys drift")
 if source_prev["original_Source_PositionDummy_type36_count"]!=137:
  raise ValueError("source original root control size changed")
 loader=method(prev,"PositionDummyEntity::LoadFromFile(EntityData*)")
 getter=method(prev,"PositionDummyEntity::GetPosition()")
 step(loader,0xd2efc,"bl","#0xd7548")
 step(loader,0xd2f04,"add","r0, r5, #1")
 step(loader,0xd2f08,"str","r0, [r4, #0xf0]")
 step(loader,0xd2f2c,"str","r5, [r4, #0xe4]")
 step(loader,0xd2f30,"bl","#0xd7bb4")
 step(getter,0xd306c,"ldr","r3, [r1, #0xf0]")
 step(getter,0xd3080,"cmp","r3, #1")
 step(getter,0xd3084,"beq","#0xd309c")
 for addr,op,args in [(0xd309c,"ldr","ip, [r1, #0xe4]"),
                      (0xd30a0,"ldr","r2, [ip, #4]"),
                      (0xd30a4,"ldr","r3, [ip, #8]"),
                      (0xd30a8,"ldr","r1, [ip, #0xc]")]:
  step(getter,addr,op,args)
 with zipfile.ZipFile(ipa) as z:
  if z.testzip() is not None:raise ValueError("original owner IPA CRC fails")
  clev=z.read("Payload/IronMan2.app/clev")
 raw=get_exact(clev,decode(clev,".bclara"),"level1.bclara")
 if len(raw)!=339733:raise ValueError("2010 owner first level bytes changed")
 types=summarize(raw)
 graph=audit(raw)
 poschild=collections.defaultdict(list)
 for v in graph["original_source_static_parent_record_links"]:
  if v["source_typed_record_field"]==92:poschild[v["original_parent_id"]].append(v)
 rows=[]
 for n in types["source_2010_typed_class_instances"]:
  if n["original_class_name"]!="PositionDummy":continue
  name=n["original_name"]
  id=n["original_numeric_name_id"]
  end=n["original_name_offset"]+len(name)
  if raw[end:end+5]!=bytes([0x80,255,255,255,255]):
   raise ValueError("source typed class pointer absent")
  if struct.unpack_from("<I",raw,end+5)[0]!=36:raise ValueError("source native PD classID 36 changed")
  records=sorted(poschild[id],key=lambda v:v["native_child_record_prefix_offset"])
  if len(records)!=3:raise ValueError("source native PositionDummy three child per entity drift")
  payload=raw[end+9:records[0]["native_child_record_prefix_offset"]]
  if len(payload)!=12:
   raise ValueError(f"original source Num 12-byte signed/int tag grammar not validated: {name}")
  if struct.unpack_from("<H",payload,4)[0]!=4 or struct.unpack_from("<H",payload,6)[0]!=4:
   raise ValueError("original 2010 C1L1 sole 4byte integer property size tags changed")
  value=struct.unpack_from("<i",payload,8)[0]
  if value not in (0,1,2):
   raise ValueError("original PositionDummy Num in C1L1 outside 0..2")
  rows.append({"source_original_entity_ID":id,"source_original_name":name,
    "source_real_class36_only_root_int_Num":value,
    "original_LoadFromFile_increments_Num_for_loaded_components":value+1,
    "original_three_source_Position_child_IDs":[x["original_child_id"] for x in records],
    "source_first_Position_child_scene_ID":records[0]["original_child_id"],
    "first_child_is_exact_source_Position1_structurally_proven":False})
 if len(rows)!=137:raise ValueError("original PositionDummy count changed")
 distribution=collections.Counter(v["source_real_class36_only_root_int_Num"] for v in rows)
 goal=next(x for x in rows if x["source_original_name"]=="PD_IM_jump_goal")
 control=next(x for x in rows if x["source_original_name"]=="PD_MC")
 if (goal["source_original_entity_ID"],goal["original_three_source_Position_child_IDs"])!=(1892,[1893,1894,1895]):
  raise ValueError("original target scene triple changed")
 if goal["source_real_class36_only_root_int_Num"]!=0 or control["source_real_class36_only_root_int_Num"]!=0:
  raise ValueError("original script source PositionDummy authored Num changed")
 child = next(x for x in graph["all_663_source_rigid_transforms_with_native_parent_child_name_ID_chain"]
  if x["original_child_node_ID"]==goal["source_first_Position_child_scene_ID"])
 cxxklass=next(x for x in types["source_class_schema"]
  if x["original_class_id"]==36)
 klass_off=cxxklass["original_class_name_file_offset"]
 keys={}
 for key in ("Num","Position1","Position2","Position3"):
  needle=key.encode("ascii")
  indexes=[]
  last=0
  while (p:=raw.find(needle,last,38719))>=0:
   indexes.append(p);last=p+len(needle)
  keys[key]=indexes
 result={
  "source":"G274 first-level 2010 iOS PositionDummyEntity authored Num signed int typed TLV, native explicit one/two/three GetPosition paths and Position1 source candidate",
  "original_C1L1_SHA256":hashlib.sha256(raw).hexdigest(),
  "source_2010_original_PD_class36_name_dictionary_offset":klass_off,
  "original_native_component_key_string_locations_in_C1L1_class_definition_region":keys,
  "genuine_source_137_PositionDummy_class36_Num_int_distribution":dict(distribution),
  "original_Mission000_goal_PD_IM_jump_goal_actual_root_Num_int":goal["source_real_class36_only_root_int_Num"],
  "original_Mission000_goal_PositionDummy_native_loaded_component_count":goal["original_LoadFromFile_increments_Num_for_loaded_components"],
  "original_goal_first_source_tlv_child_ID":goal["source_first_Position_child_scene_ID"],
  "original_goal_first_source_tlv_child_local_XYZ":child["native_vec3_position"],
  "original_control_PD_MC_actual_root_Num_int":control["source_real_class36_only_root_int_Num"],
  "original_named_goal_and_control_source_root_Num_records":[goal,control],
  "original_native_2010_PositionDummy_GetPosition_mode1_reads_Position1_XYZ":True,
  "first_serialized_child_is_Runtime_Position1_via_original_class_schema_confirmed":False,
  "real_original_runtime_Mission000_MC_move_target_absolute_world_XYZ_proven":False,
  "Vita_ground_root_or_collision_changed":False,
  "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
 print("G274 original source class36 Num root distribution",dict(distribution))
 print("G274 original 2010 first goal PD_IM_jump_goal typed root Num",goal)
 print("G274 source original PositionDummy class36 header name positions",keys,"class name dictionary offset",klass_off)
 print("G274 default-mode first source Position child local XYZ (not yet attributed to Position1 by name)",child["native_vec3_position"])
 print("G274 PASS source native C++ Num increments one Position1 GetPosition reads offset +e4, original Num=0 source, runtime untested and world XYZ unknown, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for a in ("ipa","g271","g272","g273","out"):p.add_argument("--"+a,type=Path,required=True)
 x=p.parse_args();run(x.ipa,x.g271,x.g272,x.g273,x.out)
