#!/usr/bin/env python3
"""G215 source-verified original iOS 2010 combat selector crosswalk:
G214 native owner IronMan/Suitcase/Stealth/WM 56 AttackType values EACH,
G196B original ARM DoAttack(int,int) full 26-entry native jump table.

This is first end-to-end original serialized AttackType u32 -> genuine
native DoAttack *switch target* structural alignment. The owner file
loader path StateData::GetParam("AttackType",-1) -> virtual DoAttack is
source-verified G198-G210 but whether all 56 StateData records are
actually executed during combat, or type ID means weapon/animation/
attack hitbox, is NOT YET runtime proven.

Vital distinction: IronMan 1/2 vs WarMachine 18/25 are DIFFERENT
original authored AttackType IDs but redirect to SAME two native jump
destinations. Do not remap WarMachine values to IronMan IDs in Vita;
branch target identity doesn't imply same 2010 WeaponDB ammo/animation.
No original proprietary game bytes or Vita VPK.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path
PLAYERS=["IronMan","IronMan_suitcase","Warmachine","stealth"]
def main(source_g196b,source_g214,out):
 native=json.loads(source_g196b.read_text())
 groups=json.loads(source_g214.read_text())
 switch=native["source_original_2010_attack_id_switch_0_to_25"]
 if len(switch)!=26 or not native["source_2010_original_native_dispatch_cmp_r5_25_jump_table_proven"]:
  raise ValueError("Original source ARM 26 jump destination mapping not proven")
 if set(groups["source_original_source_groups_compared"])!=set(PLAYERS):
  raise ValueError("Actual user owner 4 native armor source profiles are incomplete")
 raw=groups["source_4_native_set_profiles"]
 mappings={}
 for key in PLAYERS:
  x=raw[key]
  entries=x["original_source_AttackType_value_order"]
  if len(entries)!=56 or x["source_original_Attack_attack_event_candidates"]!=40:
   raise ValueError(f"real original {key} 56 source AttackType 40 candidate track expected")
  combined=[]
  hist=collections.Counter()
  for i,source_type in enumerate(entries):
   if not 0<=source_type<26:raise ValueError("native source input outside ARM 26 original cases")
   dest=switch[str(source_type)]["original_target_VM"]
   combined.append({"ordinal_state_2010_AttackType_record":i,
     "native_original_serialized_AttackType_u32":source_type,
     "original_ARM_MainCharacter_DoAttack_branch_VM":dest,
     "source_Cpp_weapon_attack_gameplay_outcome_proven":False})
   hist[(source_type,dest)]+=1
  mappings[key]={
   "source_native_2010_armor_StateSet":key,
   "source_authored_u32_56_AttackType_to_native_ARM_entry":combined,
   "source_original_unique_AttackType_integer_to_ARM_jump_targets":[
      {"source_original_native_AttackType_ID":i,"source_original_DoAttack_B_target":b,"owner_authored_occurrences":cnt}
      for (i,b),cnt in sorted(hist.items())],
   "source_original_native_all_56_AttackTypes_jump_destination_sequence":[r["original_ARM_MainCharacter_DoAttack_branch_VM"] for r in combined],
   "source_exact_native_symbolic_execution_of_weapon_event_PROVEN":False}
 pairs=[]
 for key in PLAYERS:
  if key=="IronMan":continue
  original=mappings["IronMan"];other=mappings[key]
  va=[r["native_original_serialized_AttackType_u32"] for r in original["source_authored_u32_56_AttackType_to_native_ARM_entry"]]
  vb=[r["native_original_serialized_AttackType_u32"] for r in other["source_authored_u32_56_AttackType_to_native_ARM_entry"]]
  ba=original["source_original_native_all_56_AttackTypes_jump_destination_sequence"]
  bb=other["source_original_native_all_56_AttackTypes_jump_destination_sequence"]
  pairs.append({
   "source_native_armor_A":"IronMan","source_native_armor_B":key,
   "source_56_original_AttackType_byte_value_different_count":sum(x!=y for x,y in zip(va,vb)),
   "source_original_native_56_ARM_switch_target_sequence_IDENTICAL":ba==bb,
   "original_native_Cpp_controller_attack_damage_animation_equivalent_PROVEN":False})
 names=[(1,18,0xf6930,15),(2,25,0xf6648,11)]
 verified_pairs=[]
 for a,b,dest,occur in names:
  assert switch[str(a)]["original_target_VM"]==hex(dest)
  assert switch[str(b)]["original_target_VM"]==hex(dest)
  left=collections.Counter(x["native_original_serialized_AttackType_u32"]
   for x in mappings["IronMan"]["source_authored_u32_56_AttackType_to_native_ARM_entry"])
  right=collections.Counter(x["native_original_serialized_AttackType_u32"]
   for x in mappings["Warmachine"]["source_authored_u32_56_AttackType_to_native_ARM_entry"])
  assert left[a]==right[b]==occur
  verified_pairs.append({"original_IronMan_AttackType":a,"original_WarMachine_AttackType":b,
   "same_real_2010_native_DoAttack_branch_address":hex(dest),
   "owner_authored_record_count_per_armor":occur,
   "real_gameplay_outcome_weapon_damage_animation_same_PROVEN":False})
 assert any(p["source_native_armor_B"]=="Warmachine" and
   p["source_56_original_AttackType_byte_value_different_count"]==26 and
   p["source_original_native_56_ARM_switch_target_sequence_IDENTICAL"] for p in pairs)
 result={
  "origin":"G215 source crossjoin original iOS owner G214 56 authored StateData AttackType u32 per player set and original G196B DoAttack native 26 ARM branch targets",
  "source_2010_canonical_original_26_attack_ARM_switch_proven":True,
  "source_2010_true_iOS_armors_original_Antique_AttackType_dispatch_reconciliation":mappings,
  "source_original_IronMan_to_other_suit_comparison":pairs,
  "source_original_WarMachine_distinct_ID_same_ARM_branch_pairs":verified_pairs,
  "source_2010_WeaponDB_UniBeam_Missile_Repulsor_type_semantics_PROVEN":False,
  "source_iOS_touchscreen_attack_button_or_joystick_full_mapping_PROVEN":False,
  "G83_G169_live_Vita_input_animator_combat_patched":False,
  "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
 print("G215 real original 2010 ARM 56 source AttackType by 4 player suits")
 for z in verified_pairs:print("G215 native SOURCE different suit AttackType but same original ARM jump",z)
 for r in pairs:print("G215 native original 56 order comparison",r)
 print("G215 PASS original 2010 1/18 and 2/25 same ARM native DoAttack branch with different real source AttackType IDs, game damage/weapon still unknown; NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for arg in ("g196","g214","out"):p.add_argument("--"+arg,required=True,type=Path)
 a=p.parse_args()
 main(a.g196,a.g214,a.out)
