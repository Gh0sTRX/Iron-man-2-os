#!/usr/bin/env python3
"""G275 source-only read-only game scenario: original class36
PositionDummy field lexical order Num, Position1, Position2, Position3
and exact G269 three child source vectors versus native iOS PositionDummy
Num0 GetPosition only Position1 and real Mission000 MoveEntityToEntity
MC(1062)->PD_IM_jump_goal(1892) raw duration3000. C11 metadata reference
for host collision QA, never mutate Vita player/root or fabricate world Z.
"""
from __future__ import annotations
import argparse,json,math,re
from pathlib import Path

def compare(g269:Path,g271:Path,g272:Path,g274:Path,out:Path,header:Path):
 k=json.loads(g269.read_text())
 c=json.loads(g271.read_text())
 props=json.loads(g272.read_text())
 mod=json.loads(g274.read_text())
 if k["original_native_MoveEntityToEntity_source_args"]!=[1062,1892,3000]:
  raise ValueError("G275 authentic original Mission000 Lua source movement args drift")
 pts=k["genuine_original_goal_3_different_typed_component_records"]
 if len(pts)!=3 or [p["child_ID"] for p in pts]!=[1893,1894,1895]:
  raise ValueError("G275 true triple child source identity drift")
 keys={p["original_PositionDummy_native_property_kind"]:p["original_authentic_CPP_const_char_string"]
       for p in props["actual_native_original_four_typed_positiondummy_property_names"]}
 if keys!={"PositionDummy_mode_integer":"Num","PositionDummy_component_1":"Position1",
          "PositionDummy_component_2":"Position2","PositionDummy_component_3":"Position3"}:
  raise ValueError("G275 source authentic 2010 native C++ PositionDummy field strings changed")
 defs=mod["original_native_component_key_string_locations_in_C1L1_class_definition_region"]
 class_start=mod["source_2010_original_PD_class36_name_dictionary_offset"]
 positions=[next((x for x in defs[name] if class_start<x<class_start+400),None)
            for name in ("Num","Position1","Position2","Position3")]
 if any(p is None for p in positions) or positions!=sorted(positions):
  raise ValueError("G275 exact original iOS class36 source parameter names are not in ordered component prototype region")
 if not all(positions[k]<positions[k+1] for k in range(3)):
  raise ValueError("source original PositionDummy properties not strictly ordered")
 if mod["original_Mission000_goal_PD_IM_jump_goal_actual_root_Num_int"]!=0:
  raise ValueError("G275 original PD jump goal source Num should be zero")
 if mod["original_Mission000_goal_PositionDummy_native_loaded_component_count"]!=1:
  raise ValueError("G275 native +1 PositionDummy loading mode changed")
 if mod["original_goal_first_source_tlv_child_ID"]!=1893:
  raise ValueError("G275 original first component child source changed")
 if mod["original_goal_first_source_tlv_child_local_XYZ"]!=pts[0]["local_position_xyz"]:
  raise ValueError("G275 original local goal XYZ inconsistent with source original G269")
 if not mod["original_native_2010_PositionDummy_GetPosition_mode1_reads_Position1_XYZ"]:
  raise ValueError("original GetPosition mode1 source instruction not verified")
 if not any(x["genuine_original_CPP_method"]=="MoveEntityToEntity(lua_State*)" and x["authentic_iOS_native_VM"]=="0x19ba0"
            for x in c["original_cpp_source_function_ARM_bounded_metadata"]):
  raise ValueError("original MoveEntityToEntity(lua_State*) genuine native CPP source missing")
 local=pts[0]["local_position_xyz"]
 if not all(math.isfinite(x) for x in local):raise ValueError("nonfinite source original goal")
 report={
  "source":"G275 2010 owner-authentic class36 PositionDummy Num0/Position1 native code and original C1L1 first child source coordinate crosswalk. NO runtime movement, file is a QA reference.",
  "original_Mission000_OnStart_source_Lua_PC":170,
  "original_Lua_MoveEntityToEntity_source_args":[1062,1892,3000],
  "original_native_cpp_function_address":"0x19ba0",
  "authentic_2010_PositionDummy_class36_schema_component_names_in_order":["Num","Position1","Position2","Position3"],
  "source_original_class36_schema_component_names_offsets":positions,
  "original_source_PD_IM_jump_goal_Num":0,
  "authentic_native_LoadFromFile_Num_plus_1_component_count":1,
  "genuine_original_first_serialized_position_child_ID":1893,
  "source_original_first_serialized_child_local_XYZ":local,
  "original_source_all_three_child_XYZs":[p["local_position_xyz"] for p in pts],
  "component1_source_association_with_native_Position1_by_original_schema_and_ordinal_supported":True,
  "exact_original_2010_serialized_child_to_Component_2010_RAM_lookup_index_proven":False,
  "real_original_Mission000_script_move_executed_on_device_proven":False,
  "actual_MC_cinematic_destination_in_world_coordinates_or_feet_ground_height_PROVEN":False,
  "vita_world_player_collider_render_light_and_mission_code_modified":False,
  "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 header.parent.mkdir(parents=True,exist_ok=True)
 lines=[
 "/* G275 AUTHENTIC 2010 original level1 source, read-only host test candidate.",
 " * Destination world XYZ / actual runtime C1L1 scene transform NOT proven.",
 " * DO NOT patch Vita world actor startup, ground level, movement or VPK. */",
 "#ifndef IM2_G275_ORIGINAL_2010_MISSION000_MOVETO_SOURCE_H",
 "#define IM2_G275_ORIGINAL_2010_MISSION000_MOVETO_SOURCE_H",
 "typedef struct {int source_actor_id;int source_target_id;int original_lua_duration_arg;",
 " int original_source_PositionDummy_Num;int native_selected_component_count;",
 " int original_first_child_id;float first_authored_local_x;",
 " float first_authored_local_y;float first_authored_local_z;} IM2G275OriginalGoal;",
 "static const IM2G275OriginalGoal im2_g275_original_mission000_move_source={",
 f" 1062,1892,3000,0,1,1893,{local[0]:.9f}f,{local[1]:.9f}f,{local[2]:.9f}f",
 "};","#endif",""]
 header.write_text("\n".join(lines))
 print("G275 authentic source exact typed 2010 class36 schema Num Position1 Position2 Position3 source offsets",positions)
 print("G275 true original Mission000 scripted MC local first Position1 component candidate",local)
 print("G275 PASS original source C++ Num0/Position1 association schema ordinal, no verified RAM selector or player world position, no Vita world/physics edits, NO VPK")
 return report
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for a in ("g269","g271","g272","g274","out","header"):p.add_argument("--"+a,type=Path,required=True)
 q=p.parse_args();compare(q.g269,q.g271,q.g272,q.g274,q.out,q.header)
