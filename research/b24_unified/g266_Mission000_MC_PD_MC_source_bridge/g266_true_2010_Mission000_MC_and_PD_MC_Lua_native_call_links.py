#!/usr/bin/env python3
"""G266 original 2010 first-level Mission000 native Lua static references
to separately-typed MC (MainCharacter, ID1062) and PD_MC (PositionDummy,
ID1195 whose attached Position bind points TO MC ID1062).
Source bytecode GETGLOBAL/CALL only; not executed and cannot prove final
actor boot/world XYZ without runtime state.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from b24_owner_pack_extract import decode,get_exact
from b24_g27_original_source_lua51_native_global_call_sites import report as orig_calls
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
from b24_g24_original_clara_source_601_nodes_663_parent_links import audit
import struct

def run(ipa:Path,g265:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("not original 2010 owner source IPA")
 with zipfile.ZipFile(ipa) as z:
  blob=z.read("Payload/IronMan2.app/clev")
 raw=get_exact(blob,decode(blob,".bclara"),"level1.bclara")
 original=summarize(raw)
 typed={x["original_name"]:x for x in original["source_2010_typed_class_instances"]}
 if typed["MC"]["original_class_name"]!="MainCharacter" or typed["MC"]["original_numeric_name_id"]!=1062:
  raise ValueError("G266 native original MC class or ID changed")
 if typed["PD_MC"]["original_class_name"]!="PositionDummy" or typed["PD_MC"]["original_numeric_name_id"]!=1195:
  raise ValueError("G266 native original mission PD_MC class or ID changed")
 parent=json.loads(g265.read_text())
 if parent["original_MC_Position_Bind_To_Entity"]!=-1 or parent["original_MC_Position_AttachType"]!=0:
  raise ValueError("G266 source MC attachment changed")
 pd=[x for x in parent["original_C1L1_nonnegative_bound_Position_records"]
     if x["original_name"]=="PD_MC"]
 if len(pd)!=1 or pd[0]["original_iOS_Bind_To_Entity_typed_int"]!=1062 or pd[0]["original_iOS_AttachType_typed_int"]!=1:
  raise ValueError("G266 original PD_MC -> MC native attachment source changed")
 script=orig_calls(raw)
 if script["original_2010_lua_callback_count"]!=71 or script["original_native_Lua_GLOBAL_CALL_candidates"]!=1035:
  raise ValueError("original Lua callback source differs")
 matches=[]
 for callback in script["source_lua_static_CALLBACK_instructions_and_id_links"]:
  for call in callback["original_static_global_CALL_sites"]:
   named=[x for x in call["source_verified_named_entity_argument_candidates"]
          if x["original_source_typed_node_ID"] in (1062,1195)]
   if not named:continue
   matches.append({
     "original_2010_Lua_callback":callback["original_callback"],
     "native_Lua_CALL_PC":call["source_bytecode_PC"],
     "original_native_Lua_global":call["native_global_function"],
     "authentic_2010_MC_or_PD_MC_entity_arg_nodes":named,
     "original_2010_static_entire_CALL_arguments":call["literal_or_statically_tracked_arguments"],
     "other_typed_entity_argument_nodes_in_same_CALL":[x for x in call["source_verified_named_entity_argument_candidates"]
                      if x["original_source_typed_node_ID"] not in (1062,1195)],
     "source_Lua_static_CALL_not_executed":True,
   })
 mc_start_moves=[
  entry for entry in matches
  if entry["original_2010_Lua_callback"]=="Mission000_OnStart"
  and entry["original_native_Lua_global"]=="MoveEntityToEntity"
  and any(hit["original_node_name"]=="MC" for hit in entry["authentic_2010_MC_or_PD_MC_entity_arg_nodes"])
 ]
 if len(mc_start_moves)!=1 or mc_start_moves[0]["native_Lua_CALL_PC"]!=170:
  raise ValueError("original 2010 Mission000 MC scripted move source PC drift")
 source_move=mc_start_moves[0]
 if source_move["original_2010_static_entire_CALL_arguments"]!=[1062.0,1892.0,3000.0]:
  raise ValueError("G268 original Mission000 MC source first cinematic MoveEntityToEntity arguments drift")
 if typed["PD_IM_jump_goal"]["original_numeric_name_id"]!=1892 or typed["PD_IM_jump_goal"]["original_class_name"]!="PositionDummy":
  raise ValueError("G268 player initial scripted movement goal is not genuine original PositionDummy")
 graph=audit(raw)
 jump=[x for x in graph["all_663_source_rigid_transforms_with_native_parent_child_name_ID_chain"]
   if x["original_named_parent"]=="PD_IM_jump_goal"]
 if len(jump)!=1:raise ValueError("G268 source original scripted MoveEntityToEntity destination Position transform missing")
 goal=jump[0]; pos_offset=goal["native_transform_source_offset"]
 pre=raw[pos_offset-36:pos_offset]
 if pre[8:12]!=b"\\x06\\x00\\x04\\x00" or pre[16:18]!=b"\\x04\\x00" or pre[22:24]!=b"\\x0c\\x00":
  raise ValueError("G268 script actual PD_IM_jump_goal typed positional record format drift")
 goal_mode=struct.unpack_from("<i",pre,12)[0]
 goal_bind=struct.unpack_from("<i",pre,18)[0]
 goal_offset=[round(z,6) for z in struct.unpack_from("<3f",pre,24)]
 named_goal={
   "genuine_original_Mission000_native_MoveEntityToEntity_VM_PC":170,
   "original_2010_source_mc_actor_class112_ID":1062,
   "original_2010_script_destination_name":"PD_IM_jump_goal",
   "original_2010_script_destination_PositionDummy_ID":1892,
   "source_native_child_PositionData_ID":goal["original_child_node_ID"],
   "source_original_goal_XYZ_local":goal["native_vec3_position"],
   "source_original_goal_quaternion":goal["native_quaternion_xyzw"],
   "source_original_goal_scale":goal["native_vec3_scale"],
   "source_original_goal_AttachType":goal_mode,
   "source_original_goal_Bind_To_Entity":goal_bind,
   "source_original_goal_AttachOffset":goal_offset,
   "original_source_script_third_arg_raw_3000":3000,
   "third_arg_duration_unit_in_real_iOS_runtime_proven":False,
   "actual_original_iOS_MC_world_end_position_reached_or_correct_collision_proven":False
 }
 freq=collections.Counter((m["original_native_Lua_global"],hit["original_node_name"])
  for m in matches for hit in m["authentic_2010_MC_or_PD_MC_entity_arg_nodes"])
 start=next(x for x in script["source_lua_static_CALLBACK_instructions_and_id_links"]
   if x["original_callback"]=="Mission000_OnStart")
 opening=[{"native_Lua_CALL_PC":x["source_bytecode_PC"],"original_Lua_global":x["native_global_function"],
   "source_named_MC_PD_reference":[k for k in x["source_verified_named_entity_argument_candidates"]
                                   if k["original_source_typed_node_ID"] in (1062,1195)],
   "source_global_args":x["literal_or_statically_tracked_arguments"]}
   for x in start["original_static_global_CALL_sites"] if x["source_bytecode_PC"]<=73]
 result={
   "source":"G266 original owner 2010 C1L1 71 Lua callback static original MC/PD_MC references and native G265 PositionData direction",
   "original_2010_c1l1_source_sha256":hashlib.sha256(raw).hexdigest(),
   "source_Mission000_original_MC_class112_ID":1062,
   "source_Original_PD_MC_PositionDummy_node_ID":1195,
   "source_MC_actual_AttachType":0,
   "source_MC_actual_Bind_To_Entity":-1,
   "source_PD_MC_actual_AttachType":1,
   "source_PD_MC_actual_Bind_To_Entity":1062,
   "source_Mission000_71_Lua_native_callback_count":71,
   "source_Mission000_total_original_Lua_global_CALLs":1035,
   "source_2010_all_MC_PD_MC_statically_identified_entity_argument_calls":matches,
   "source_true_original_Mission000_OnStart_MC_MoveEntityToEntity_PC170_target_source":mc_start_moves[0],
   "source_true_original_Mission000_MC_initial_scripted_goal_PositionDummy_typed_transform_and_binding":named_goal,
   "source_Mission000_MoveEntityToEntity_source_target_name_if_typed":
      next((x["original_node_name"] for x in mc_start_moves[0]["other_typed_entity_argument_nodes_in_same_CALL"] if x["argument_index"]==1),None),
   "source_2010_MC_PD_MC_Lua_global_frequency":[
       {"real_native_call":a,"native_named_entity":n,"num_static_CALLs":count}
       for (a,n),count in sorted(freq.items())],
   "original_Mission000_OnStart_native_first_conditional_PC":73,
   "original_Mission000_OnStart_source_calls_pre_first_branch_PC73":opening,
   "original_source_PD_MC_mission_relative_attachment_to_MC_confirmed":True,
   "MC_gameplay_world_position_overwritten_by_this_Lua_source_proven":False,
   "original_iOS_live_story_Mission000_boot_player_world_transform_proven":False,
   "original_touch_gameplay_device_run_or_combat_proven":False,
   "Vita_movement_camera_lighting_or_mission_runtime_modified":False,
   "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
 print("G266 source real 2010 MC ID1062 Position no-bind; PD_MC ID1195 Bind MC AttachType1")
 print("G266 original Lua MC+PD_MC source-typed CALL count",len(matches))
 print("G266 TRUE ORIGINAL Mission000 OnStart MC MoveEntityToEntity PC170 ACTUAL TARGET",mc_start_moves[0])
 print("G268 real original 2010 Mission000 scripted MC goal native PositionDummy typed transform",named_goal)
 for x in matches:print("G266 original Lua typed MC/PD_MC node source CALL",x)
 print("G266 Mission000 original native OnStart <=PC73 source CALL count",len(opening))
 for x in opening:print("G266 genuine pre-first-branch source CALL",x)
 print("G266 PASS original Mission000 MC vs PD_MC entity-reference provenance; no dynamic runtime player boot or teleport claim, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g265",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 x=p.parse_args();run(x.ipa,x.g265,x.out)
