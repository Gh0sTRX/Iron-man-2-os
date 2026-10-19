#!/usr/bin/env python3
"""G250 authoritative 2010 iOS level1 SpawnPoint000..015 actual tagged
(12,16,12) source transforms + original 71 Lua callbacks' static typed
source links. Only creates read-only data header for actual G171/G75
collision experiments. A SpawnPoint node is NOT automatically original
player's runtime spawn or foot Z. No gameplay/teleport/VPK effects.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,math,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from b24_owner_pack_extract import decode,get_exact
from b24_g19_original_2010_level1_spawn_transforms_city_xy_map import exact_spawns
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
from b24_g27_original_source_lua51_native_global_call_sites import report as lua_report

def main(ipa:Path,out:Path,header:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("original owner IPA 1.0.0 expected")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip() is not None:raise ValueError("original owner IPA corrupted")
  packed=z.read("Payload/IronMan2.app/clev")
  data=get_exact(packed,decode(packed,".bclara"),"level1.bclara")
 if len(data)!=339733:raise ValueError("original 2010 C1L1 level1 changed")
 points=exact_spawns(data)
 typed=summarize(data)
 native=lua_report(data)
 assert len(points)==16 and len(typed["source_2010_typed_class_instances"])==587
 assert native["original_2010_lua_callback_count"]==71
 assert native["original_native_Lua_GLOBAL_CALL_candidates"]==1035
 byname=collections.defaultdict(list)
 for t in typed["source_2010_typed_class_instances"]:
  byname[t["original_name"]].append(t)
 links=collections.defaultdict(list)
 for cb in native["source_lua_static_CALLBACK_instructions_and_id_links"]:
  for call in cb["original_static_global_CALL_sites"]:
   for match in call["source_verified_named_entity_argument_candidates"]:
    if match["original_node_name"].startswith("SpawnPoint"):
     links[match["original_node_name"]].append({
      "lua_callback":cb["original_callback"],
      "original_bytecode_PC":call["source_bytecode_PC"],
      "original_native_global_CALL_name":call["native_global_function"],
      "original_node_ID":match["original_source_typed_node_ID"],
      "static_call_not_executed":True})
 for p in points:
  candidates=byname[p["node"]]
  p["matching_native_typed_source_nodes"]=[{
    "native_scene_ID":q["original_numeric_name_id"],
    "source_cpp_class":q["original_class_name"],
    "source_cpp_class_ID":q["original_class_id"]} for q in candidates]
  p["original_C1L1_static_Lua_direct_node_call_mentions"]=links[p["node"]]
  p["the_node_is_verified_original_story_player_spawn"]=False
  p["raw_node_Z_is_verified_actor_runtime_feet_Z"]=False
  p["source_scene_world_parent_transform_applied"]=False
  for a in p["position_XYZ"]:
   if not math.isfinite(a):raise ValueError("nonfinite original node pos")
  print("G250 TRUE 2010 SpawnPoint",p["node"],"XYZ",p["position_XYZ"],
   "typed",p["matching_native_typed_source_nodes"],
   "static_Lua_refs",len(p["original_C1L1_static_Lua_direct_node_call_mentions"]))
 mission_start=next(x for x in native["source_lua_static_CALLBACK_instructions_and_id_links"]
  if x["original_callback"]=="Mission000_OnStart")
 direct_in_start=[
  {"native_CALL_PC":call["source_bytecode_PC"],
   "native_GLOBAL":call["native_global_function"],"native_links":[
    ref for ref in call["source_verified_named_entity_argument_candidates"]
       if ref["original_node_name"].startswith("SpawnPoint")]}
  for call in mission_start["original_static_global_CALL_sites"]
  if any(ref["original_node_name"].startswith("SpawnPoint")
      for ref in call["source_verified_named_entity_argument_candidates"])]
 report={
  "origin":"G250 exact 2010 user-owned 339733-byte level1.bclara tagged original 16 spawn transforms and source original 71 Lua callbacks",
  "original_level1_SHA256":hashlib.sha256(data).hexdigest(),
  "actual_original_16_source_SpawnPoint_transforms":points,
  "original_source_16_spawnpoint_count":16,
  "original_native_2010_exact_tagged_12_16_12_source_transform":True,
  "original_source_2010_71_callbacks_1035_Lua_CALL_opcode_scan":True,
  "source_original_all_Lua_CALL_typed_SpawnPoint_node_links_count":sum(len(v) for v in links.values()),
  "original_Mission000_OnStart_static_typed_SpawnPoint_DIRECT_links":direct_in_start,
  "source_scene_graph_Mission000_Player_spawn_assignment_proven":False,
  "real_original_2010_gameplay_runtime_player_SpawnPoint_index_proven":False,
  "actual_original_scene_parent_world_transforms_proven":False,
  "authored_Source_SpawnPoint_Z_is_actual_player_foot_ground_height_proven":False,
  "Vita_actor_start_world_modified":False,
  "VPK":False}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 header.parent.mkdir(parents=True,exist_ok=True)
 code=[
 "/* G250 generated ONLY from original 2010 owner level1.bclara.",
  " * Read-only TEST candidate transforms; NO proven player runtime spawn/feet Z.",
  " * No fictional collision geometry or proprietary raw game bytes. */",
 "#ifndef G250_AUTHENTIC_2010_SPAWNPOINT_SOURCE_CANDIDATES_H",
 "#define G250_AUTHENTIC_2010_SPAWNPOINT_SOURCE_CANDIDATES_H",
 "typedef struct{const char *name;float x,y,z;int original_native_node_id;} G250SourceSpawnCandidate;",
 "static const G250SourceSpawnCandidate g250_source_spawns[16]={"]
 for p in points:
  typed_nodes=p["matching_native_typed_source_nodes"]
  node_id=typed_nodes[0]["native_scene_ID"] if len(typed_nodes)==1 else -1
  x,y,z=p["position_XYZ"]
  code.append(' {"%s",%.9ff,%.9ff,%.9ff,%d},'%(p["node"],x,y,z,node_id))
 code.extend(["};","#endif",""])
 header.write_text("\n".join(code))
 print("G250 original 2010 source typed static Lua SpawnPoint direct mentions",sum(len(v) for v in links.values()))
 print("G250 Mission000 OnStart source 16 SpawnPoint direct static references",len(direct_in_start))
 print("G250 PASS 16 original tagged SpawnPoint xyz and true source Lua crossrefs; exact runtime player spawn unknown, VPK=NO")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 p.add_argument("--header",type=Path,required=True)
 a=p.parse_args()
 main(a.ipa,a.out,a.header)
