#!/usr/bin/env python3
"""G175B no new 248 MB IPA download: compare genuine G175 native ARM
C++ direct edges with 2010 Lua MissionTutorial_missile permission evidence.
Do not turn a Lua AttackType 1 flag into proof that Aim_M == missile.
Outputs exact native callees, with source/semantics separation. NO VPK.
"""
from __future__ import annotations
import argparse,collections,json,re
from pathlib import Path

OWNER_LABELS=("mission_attack_toggle","throw_missile","unibeam",
              "weapon_attack_lookup","weapon_attack_fire","weapon_projectile")
def audit(original:Path,report:Path,out:Path):
 d=json.loads(original.read_text())
 if not d.get("no_proprietary_executable_or_raw_arm_machine_bytes_published") or not d.get("NO_VPK"):
  raise ValueError("G175 requires owner-authentic safe original CALL metadata")
 if d.get("owner_iOS_arm_native_symbol_count")!=65500:raise ValueError("Real original 2010 symbol provenance changed")
 docs=report.read_text()
 if "11× (1,false)" not in docs or "1× (1,true)" not in docs or "MissionTutorial_missile_OnStart" not in docs:
  raise ValueError("2010 Lua source AttackType 1 permission provenance missing")
 targets=d["original_native_method_target_matches"]
 for label in OWNER_LABELS:
  if not targets[label]:raise ValueError("Missing genuine native weapon method "+label)
 methods=d["original_native_methods_selected_bounded_CALL_evidence"]
 lookup=collections.defaultdict(set)
 for m in methods:
  for n in m["source_names"]:lookup[m["native_address_hex"]].add(n)
 origin=d["source_direct_weapon_animation_related_callsite_evidence"]
 selected={}
 for name in OWNER_LABELS:
  addresses={p[0] for p in targets[name]}
  proof=[e for e in origin if e["original_caller_address"] in addresses]
  direct=[]
  for e in proof:
   direct.append({
    "original_callsite_VM":e["original_callsite_VM"],
    "actual_2010_called_VM":e["direct_callee_VM"],
    "verified_native_symbol_names":e["direct_callee_symbol"],
    "is_unresolved_external_or_no_symbol":not bool(e["direct_callee_symbol"]),
    "original_target_register_argument_semantics_proven":False,
   })
  selected[name]={
   "authentic_source_methods":targets[name],
   "verified_direct_call_count":len(direct),
   "direct_source_callees":direct,
   "live_2010_touchhle_runtime_called_proven":False
  }
 # Authored source static Lua permission changes are not specific
 # main-character original native animation assignments.
 unibeam_d=d["named_weapon_direct_function_edges"]["unibeam"]["weapon_attack_lookup"]
 attack_d=d["named_weapon_direct_function_edges"]["weapon_attack_fire"]["weapon_projectile"]
 if unibeam_d!=1 or attack_d!=1:
  raise ValueError("Source native direct-call graph no longer matches exact 2010 proof")
 report_obj={
  "source":"2010 owner iOS authentic G175 original Mach-O native CALL sites + G76 owner Level1 Lua bytecode provenance",
  "native_2010_attack_type_permission_lua_call_VM":"0x17b80",
  "original_Level1_Lua_native_script_static_evidence":{
     "MissionTutorial_missile_OnStart_SetAttackTypeEnabled_id1_true":True,
     "other_11_static_SetAttackTypeEnabled_id1_false_calls":True,
     "lua_function_named_missile_is_not_proof_of_g83_aim_m_suffix":True,
     "native_2010_whether_attacktype_1_is_a_specific_weapon_type_proven":False,
     "original_runtime_Lua_condition_path_replayed":False
  },
  "native_source_method_call_edges":selected,
  "source_direct_UniBeam_to_WeaponDB_GetAttackEntityByIndex":unibeam_d,
  "source_direct_AttackEntity_DoAttack_to_DoProjectileAttack":attack_d,
  "original_Aim_M_animation_to_WeaponDB_GetAttackEntityByIndex_binding_PROVEN":False,
  "original_ThrowMissile_to_WarMachineGun01_04_muzzle_binding_PROVEN":False,
  "native_original_2010_Lua_attack_permission_input_not_recreated_in_Vita":True,
  "automatic_2010_aim_m_missile_binding_allowed":False,
  "original_weapon_event_added_to_Vita":False,
  "original_hit_damage_frames_proven":False,
  "no_private_ipa_or_original_binary_republished":True,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report_obj,indent=2,ensure_ascii=False)+"\n")
 print("G175B source-matched 2010 Lua + native CALL graph, no new owner IPA download")
 for name,row in selected.items():
  print("G175B SOURCE",name,row["authentic_source_methods"])
  for direct in row["direct_source_callees"][:20]:
   print("G175B DIRECT CALL",direct["original_callsite_VM"],
       "→",direct["actual_2010_called_VM"],direct["verified_native_symbol_names"])
 print("G175B UniBeam real source DB lookup direct",unibeam_d,
       "AttackEntity::DoAttack real projectile call",attack_d)
 print("G175B input WeaponID=1 semantics and Aim_M linkage NOT proven; NO VPK")
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--g175",type=Path,required=True)
 a.add_argument("--report",type=Path,required=True)
 a.add_argument("--out",type=Path,required=True)
 opts=a.parse_args()
 audit(opts.g175,opts.report,opts.out)
