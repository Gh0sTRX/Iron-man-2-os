#!/usr/bin/env python3
"""G247 original 2010 CLARA attack/weapon registration ORDER HYPOTHESIS audit.
This is not a runtime game trace. Cross-reference the 587 native typed scene
objects with the G241 real AddNew Attack/Weapon/Accessory source switch and
G245 true +0x14 parsed class ID. File name offsets are a candidate ranking,
not proof of ClaraFile GetEntityData(i) runtime slot or WeaponDB array index.
Never use conjectural rows to select missiles, gatling, damage, animations.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from b24_owner_pack_extract import decode,get_exact
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
SOURCES={"WeaponAccessory":104,"Weapon":107,"Attack":108}
def run(ipa:Path,g241:Path,g245:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("G247 original owner 2010 IPA changed")
 with zipfile.ZipFile(ipa) as z:
  raw=z.read("Payload/IronMan2.app/clev")
 scene_blob=get_exact(raw,decode(raw,".bclara"),"level1.bclara")
 if len(scene_blob)!=339733:raise ValueError("G247 original source level1 bytes changed")
 scene=summarize(scene_blob)
 original_state=json.loads(g241.read_text())
 native_entity=json.loads(g245.read_text())
 if not native_entity.get("real_original_2010_EntityData_source_class_ID_native_field_offset_0x14_proven"):
  raise ValueError("G247 needs verified original native EntityData +0x14 class")
 routes=original_state.get("real_native_original_2010_class_104_107_108_exact_ARM_dispatch")
 if not isinstance(routes,dict) or set(routes)!={"104","107","108"}:
  raise ValueError("G247 needs actual native game class switch proof")
 for cls,cn in SOURCES.items():
  if routes[str(cn)]["G25_native_class_name"]!=cls:
   raise ValueError("original scene typed class vs true ARM branch mismatched")
 records=sorted(scene["source_2010_typed_class_instances"],
  key=lambda row:row["original_name_offset"])
 typed=[r for r in records if r["original_class_name"] in SOURCES]
 freq=collections.Counter(r["original_class_name"] for r in typed)
 if (freq["Attack"],freq["Weapon"],freq["WeaponAccessory"])!=(26,13,1):
  raise ValueError("C1L1 true 2010 Attack/Weapon/Accessory typed counts drift")
 # Independent ranking by original scene name-offset and by scene node ID.
 # They are NOT legitimate indexes unless original storage construction
 # explicitly proves the native record enumeration order.
 ranks_by_source_offset={}
 rank_by_node_id={}
 lists={}
 for cls in SOURCES:
  rows=[r for r in typed if r["original_class_name"]==cls]
  filename=sorted(rows,key=lambda q:q["original_name_offset"])
  nodeid=sorted(rows,key=lambda q:q["original_numeric_name_id"])
  rank_by_node_id[cls]={r["original_numeric_name_id"]:i for i,r in enumerate(nodeid)}
  ranks_by_source_offset[cls]={r["original_numeric_name_id"]:i for i,r in enumerate(filename)}
  lists[cls]=[
   {"file_offset_sort_rank_source_only":rank,
    "original_typed_source_name":r["original_name"],
    "original_source_name_offset":r["original_name_offset"],
    "original_CLARA_scene_node_id":r["original_numeric_name_id"],
    "genuine_original_class_id":r["original_class_id"],
    "native_cpp_AddNew_type_dispatch_ARM_start":
      routes[str(SOURCES[cls])]["true_original_ARM_class_dispatch_destination_VM"],
    "node_id_sort_rank_source_only":rank_by_node_id[cls][r["original_numeric_name_id"]],
    "file_scan_rank_equals_node_id_sort_rank":rank==rank_by_node_id[cls][r["original_numeric_name_id"]],
    "file_scan_rank_IS_NOT_WEAPONDB_RUNTIME_INDEX":True,
    "live_CLARA_memory_index_or_weaponDB_index_confirmed":False,
   }for rank,r in enumerate(filename)]
 named={}
 for name in ("Attack_type0","Attack_type1","Attack_WM_Missile","Attack_F22_missile"):
  hits=[row for row in lists["Attack"] if row["original_typed_source_name"]==name]
  if len(hits)!=1:raise ValueError(f"source authentic named Attack class missing/duplicate {name}")
  named[name]=hits[0]
 file_order_agreement={
  cls:sum(1 for e in rows if e["file_scan_rank_equals_node_id_sort_rank"])
  for cls,rows in lists.items()}
 result={
  "source":"G247 original user-owned 2010 iOS 1.0.0 level1.bclara G25 scene and G241/G245 authenticated native loader",
  "original_source_level1_SHA256":hashlib.sha256(scene_blob).hexdigest(),
  "authentic_2010_C1L1_native_class_instances_total":scene["source_real_named_instances_with_proven_class_ID"],
  "original_class_104_107_108_typed_member_count":dict(freq),
  "original_Attack_named_entry_file_offset_vs_scene_nodeID_order_candidates":lists["Attack"],
  "original_Weapon_named_entry_file_offset_vs_scene_nodeID_order_candidates":lists["Weapon"],
  "original_WeaponAccessory_named_entry_candidates":lists["WeaponAccessory"],
  "named_source_attack_of_interest":named,
  "file_offset_and_nodeid_source_sort_positions_identical_count":file_order_agreement,
  "actual_original_2010_native_dispatch_per_class_confirmed":True,
  "actual_original_2010_EntityData_class_field_0x14_confirmed":True,
  "file_offset_scan_IS_NOT_original_ClaraFile_GetEntityData_RAM_array_index":True,
  "original_scene_load_order_may_include_other_levels_or_global_packs":True,
  "original_WeaponDB_index_0_1_4_names_confirmed":False,
  "original_WM_firing_buttons_projectiles_damage_confirmed":False,
  "vita_player_motion_weapon_damage_or_Mission000_modified":False,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
 print("G247 original level1 classed instances",len(records),"typed weapon/attack",dict(freq))
 for name,row in named.items():print("G247 SOURCE NAME (UNVERIFIED INDEX)",name,row)
 print("G247 original offset and scene-node-ID rank agreement",file_order_agreement)
 print("G247 PASS honest candidate ranking of authenticated original CLARA records; no WeaponDB runtime index claim or VPK")
 return result
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--ipa",type=Path,required=True)
 a.add_argument("--g241",type=Path,required=True)
 a.add_argument("--g245",type=Path,required=True)
 a.add_argument("--out",type=Path,required=True)
 q=a.parse_args();run(q.ipa,q.g241,q.g245,q.out)
