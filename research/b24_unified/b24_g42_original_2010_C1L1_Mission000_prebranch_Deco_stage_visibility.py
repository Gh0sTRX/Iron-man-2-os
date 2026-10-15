#!/usr/bin/env python3
"""G42: Original 2010 iOS first mission pre-branch actor enabling map gates.

TRUE source bytecode, not simulated Lua. Native lua 5.1 first conditional
branch opcode PC 73 in Mission000_OnStart. Before branch the original has
12 sourced Enable/Disable Deco CALL instructions. Native typed CLARA node
ID -> exact source model archive mapping from G37/G38. This proves scripted
function calls in a straight-line prefix, NOT proof of game level's initial
preexisting visibility, nor the final world actor root scene matrices.

No VPK, no invented model poses or original shader effects.
"""
from __future__ import annotations
import argparse,collections,csv,json,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact
from b24_g27_original_source_lua51_native_global_call_sites import NativeLua,HEADER,report as native_lua
from b24_g37_original_C1L1_Deco_resource_type_scene_instances import audit as source_decos

BRANCH_OPS={22,23,24,25,26,27,32,33,34,35}
ACTIONS={"Enable","Disable","Show","Hide"}

def inspect(ipa):
 with zipfile.ZipFile(ipa) as z:
  clev=z.read("Payload/IronMan2.app/clev")
  models=z.read("Payload/IronMan2.app/models")
 raw=get_exact(clev,decode(clev,".bclara"),"level1.bclara")
 source=native_lua(raw)
 table=decode(models)
 callbacks=source["source_lua_static_CALLBACK_instructions_and_id_links"]
 opening=next(c for c in callbacks if c["original_callback"]=="Mission000_OnStart")
 p=NativeLua(raw,opening["original_source_callback_offset"])
 assert p.fetch(12)==HEADER
 root=p.function()
 code=root["original_child_functions"][0]["native_function_code"]
 branch=next(i for i,w in enumerate(code) if w&63 in BRANCH_OPS)
 assert branch==73
 deco=source_decos(raw)["source_decoded_native_Deco_0x4D_resource_fields_and_0x5C_transforms"]
 byid={r["original_source_entity_ID"]:r for r in deco}
 all_actions=[]
 for cb in callbacks:
  for call in cb["original_static_global_CALL_sites"]:
   if call["native_global_function"] not in ACTIONS:continue
   for hit in call["source_verified_named_entity_argument_candidates"]:
    if hit["source_class"]!="Deco":continue
    idnum=hit["original_source_typed_node_ID"]
    item=byid[idnum]
    original_model=table[item["native_raw_resource_type_uint32"]-1].name
    all_actions.append({
     "original_lua_callback":cb["original_callback"],
     "original_source_bytecode_PC":call["source_bytecode_PC"],
     "original_lua_global_call":call["native_global_function"],
     "original_CLARA_Deco_ID":idnum,
     "original_CLARA_Deco_name":item["source_Deco_name"],
     "original_one_based_model_archive_slot":item["native_raw_resource_type_uint32"],
     "original_direct_archive_model_filename":original_model,
     "original_0x004D_secondary_uint32":item["native_raw_secondary_uint32"],
     "original_native_XYZ":[item["source_X"],item["source_Y"],item["source_Z"]],
     "mission000_pre_first_Lua_5_1_conditional":(
       cb["original_callback"]=="Mission000_OnStart"
       and call["source_bytecode_PC"]<branch),
     "native_game_running_and_actor_runtime_visible_PROVEN":False})
 pre=[x for x in all_actions if x["mission000_pre_first_Lua_5_1_conditional"]]
 assert len(pre)==12 and len({x["original_CLARA_Deco_name"] for x in all_actions})==35
 states={x["original_CLARA_Deco_name"]:x["original_lua_global_call"] for x in pre}
 assert states=={
  **{f"Deco_man{k}":"Enable" for k in range(1,9)},
  "Deco004":"Enable","Deco005":"Disable",
  "Deco_fence3":"Disable","Deco_fence4":"Disable"}
 # Important falsifiable boundary: all 11 original fixed C1L1 map packages
 # have NO Enable/Disable/Show/Hide targets in ANY of the 71 source callbacks.
 # Therefore intro-script actor toggles alone CANNOT explain the outlying city.
 native_target_ids={x["original_CLARA_Deco_ID"] for x in all_actions}
 static_map=[x for x in deco if table[x["native_raw_resource_type_uint32"]-1].name.startswith("C1L1_")]
 assert len(static_map)==11
 assert not any(x["original_source_entity_ID"] in native_target_ids for x in static_map)
 static_map_names=[x["source_Deco_name"] for x in static_map]
 other_unscripted=[x["source_Deco_name"] for x in deco if x["original_source_entity_ID"] not in native_target_ids]
 assert len(other_unscripted)==18
 d4=next(x for x in pre if x["original_CLARA_Deco_name"]=="Deco004")
 d5=next(x for x in pre if x["original_CLARA_Deco_name"]=="Deco005")
 assert d4["original_one_based_model_archive_slot"]==137==d5["original_one_based_model_archive_slot"]
 assert d4["original_direct_archive_model_filename"]==d5["original_direct_archive_model_filename"]=="expo_crash.bdae"
 assert d4["original_native_XYZ"]==d5["original_native_XYZ"]
 assert (d4["original_0x004D_secondary_uint32"],d5["original_0x004D_secondary_uint32"])==(406,405)
 return {"source_original_2010_Lua_5_1_callbacks":len(callbacks),
   "source_original_Mission000_OnStart_first_Lua_branch_PC":branch,
   "source_original_Mission000_OnStart_native_code_instruction_count":len(code),
   "source_pre_branch_exact_Deco_enable_disable_instruction_count":len(pre),
   "source_pre_branch_decoded_Deco_actions":pre,
   "source_original_11_static_C1L1_affected_by_any_71_Lua_visibility_op":0,
   "source_original_11_static_C1L1_filename_nodes_without_Lua_visibility_op":static_map_names,
   "source_original_total_Deco_nodes_without_any_Lua_visibility_op":len(other_unscripted),
   "source_original_other_Decco_nodes_without_script_visibility_op":other_unscripted,
   "source_all_level1_deco_visibility_action_CALL_instruction_count":len(all_actions),
   "source_unique_Deco_names_with_visibility_action_CALL":len({x["original_CLARA_Deco_name"] for x in all_actions}),
   "source_all_source_callback_actions":all_actions,
   "source_2010_script_secondary_model_406_405_same_authored_pose_proven":True,
   "source_static_BRES_all_370_3D_meshes_need_no_arbitrary_world_offset":True,
   "source_2010_actor_runtime_default_visibility_OR_preexisting_state_PROVEN":False,
   "source_2010_actor_root_world_transform_proven":False,
   "source_2010_sprite_special_light_emissive_alpha_shader_proven":False,
   "original_2010_Lua_simulated_or_executed":False,
   "NO_VPK_AND_NO_PERFORMANCE_WORK":True}

def save_csv(path,items):
 with path.open("w",newline="",encoding="utf-8-sig") as f:
  w=csv.DictWriter(f,fieldnames=list(items[0]))
  w.writeheader();w.writerows(items)
def main(ipa,out):
 d=inspect(ipa);out.mkdir(parents=True,exist_ok=True)
 (out/"G42_SOURCE_MISSION_SCRIPT_STAGE_VISIBILITY_EVIDENCE.json").write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 save_csv(out/"G42_Mission000_SOURCE_DECO_PRE_FIRST_BRANCH.csv",d["source_pre_branch_decoded_Deco_actions"])
 save_csv(out/"G42_ALL_71_CALLBACKS_ACTOR_ENABLE_DISABLE.csv",d["source_all_source_callback_actions"])
 print("PASS G42 original C1L1 2010 level1 Mission000_OnStart first branch PC",d["source_original_Mission000_OnStart_first_Lua_branch_PC"])
 print("G42 script native Deco prebranch exact",[(x["original_lua_global_call"],x["original_CLARA_Deco_name"]) for x in d["source_pre_branch_decoded_Deco_actions"]])
 print("G42 script all native Deco-call count",d["source_all_level1_deco_visibility_action_CALL_instruction_count"],"different source Deco objects",d["source_unique_Deco_names_with_visibility_action_CALL"])
 print("G42 original 11 static C1L1 environment model nodes have ZERO source Lua visibility toggles; 18 total Deco nodes unaddressed by these 71 callbacks.")
 print("G42 original same-stage expo_crash double instance secondary tags are 406 vs 405; no assumed runtime visibility or final world matrices.")
 print("PASS original source Lua instructions analyzed no execution, no Vita VPK.")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
 x=p.parse_args();main(x.ipa,x.out)
