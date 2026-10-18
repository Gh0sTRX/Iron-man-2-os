#!/usr/bin/env python3
"""G216 source-only authentic 2010 iOS Mach-O DoAttack ARM source branch analysis.
Prior G215 verifies original IronMan state AttackType 1/2 and WarMachine 18/25
have exactly the same DoAttack C++ ARM switch branch entry points.
This script examines ACTUAL instructions at the shared branch to explain
why same switch destination != same weapon, projectile, animation, damage.
Disassembles ZERO fabricated instructions; uses previous real original
2010 ARM opcode inventory and G214 source owner player StateSet proof.

Never assign 'Aim_M' or 'missile' to 18 or 25 without genuine runtime,
weapon database, or true animated resource behavior. NO VPK.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main(g196:Path,g214:Path,out:Path):
 arm=json.loads(g196.read_text())
 profiles=json.loads(g214.read_text())["source_4_native_set_profiles"]
 if not arm["source_2010_original_native_dispatch_cmp_r5_25_jump_table_proven"]:
  raise ValueError("G216 original source ARM 26 switch not verified")
 rows=arm["source_original_entire_DoAttack_646_ARM_opcode_metadata"]
 if len(rows)!=646: raise ValueError("original native DoAttack instruction count changed")
 opcode={int(r["vm"],16):(r["mnemonic"],r["args"]) for r in rows}
 switch=arm["source_original_2010_attack_id_switch_0_to_25"]
 must={
 # Original shared case 1/18:
 0xf6930:("bl","#0x975e8"),
 0xf6934:("ldr","r2, [r0, #0x104]"),
 0xf6938:("cmp","r2, #1"),
 0xf6948:("bl","#0xc2528"),
 0xf694c:("ldrb","r6, [r0, #0xd]"),
 0xf6958:("ldr","r1, [sp, #0x24]"),
 0xf695c:("cmp","r1, #0"),
 0xf6960:("moveq","r5, #0x10"),
 0xf6964:("movne","r5, #0x16"),
 0xf6968:("ldr","r6, [r4, #0x5e4]"),
 0xf696c:("cmp","r6, #1"),
 0xf6970:("beq","#0xf6a4c"),
 0xf6974:("cmp","r6, #2"),
 0xf6978:("beq","#0xf6afc"),
 0xf697c:("cmp","r6, #0"),
 0xf6980:("bne","#0xf6b80"),
 0xf6990:("bl","#0xb1cf4"),
 0xf69a0:("bl","#0xab3ec"),
 0xf69e0:("mov","lr, pc"),
 0xf69e4:("ldr","pc, [ip, #0x128]"),
 # Original shared case 2/25:
 0xf6648:("add","r0, r4, #0x32c"),
 0xf664c:("bl","#0xb1cf4"),
 0xf6650:("mov","r6, r0"),
 0xf6654:("bl","#0xab324"),
 0xf6658:("mov","r1, r5"),
 0xf665c:("bl","#0xab3ec"),
 0xf6660:("cmp","r6, #0"),
 0xf6668:("beq","#0xf65b0"),
 0xf666c:("mov","r0, r6"),
 0xf6670:("bl","#0xc0bf4"),
 0xf6674:("cmp","r0, #0"),
 0xf6678:("bne","#0xf65b0"),
 0xf6688:("mov","r1, r5"),
 0xf668c:("mov","lr, pc"),
 0xf6690:("ldr","pc, [r3, #0x128]"),
 0xf6694:("ldr","r2, [r4, #0x950]"),
 0xf6698:("cmp","r2, #0"),
 0xf66ec:("bl","#0xc1078"),
 }
 for addr,proof in must.items():
  if opcode.get(addr)!=proof:raise ValueError(
    f"Original native 2010 branch source drift @{addr:x}: {opcode.get(addr)} not {proof}")
 expected=[
 (1,18,"0xf6930",15),
 (2,25,"0xf6648",11),
 ]
 pairs=[]
 for im,wm,entry,n in expected:
  if switch[str(im)]["original_target_VM"] != entry or switch[str(wm)]["original_target_VM"] != entry:
   raise ValueError("genuine source 2010 DoAttack jump destination mismatch")
  for name,src_id in (("IronMan",im),("Warmachine",wm)):
   source=profiles[name]["original_source_AttackType_value_order"]
   if source.count(src_id)!=n:raise ValueError("true original state value count changed "+name)
  pairs.append({"source_IronMan_authored_AttackType":im,
   "source_Warmachine_authored_AttackType":wm,
   "source_identical_true_native_DoAttack_ARM_switch_target":entry,
   "original_number_of_authored_source_records_each":n})
 for n in ("IronMan","IronMan_suitcase","Warmachine","stealth"):
  if len(profiles[n]["original_source_AttackType_value_order"])!=56:
   raise ValueError("original owner full 56 source entries missing "+n)
 verified=[{"address":hex(a),"opcode":op,"operands":arg} for a,(op,arg) in must.items()]
 report={
  "original_source":"G216 2010 original IronMan2 MachO DoAttack native ARM instruction source G196B + four armored player authored source StateSet values G214",
  "exact_source_asserted_original_ARM_instructions":len(verified),
  "source_checked_native_ARM_opcode_provenance":verified,
  "source_original_2010_armor_different_AttackType_but_shared_Cpp_switch_entry":pairs,
  "real_2010_shared_case_1_18_honors_native_runtime_object_member_at_R4_plus_0x5e4":True,
  "real_2010_shared_case_1_18_branches_source_R6_runtime_values_0_1_2":True,
  "source_real_Cpp_case_1_18_reselects_R5_values_0x10_and_0x16_conditionally":True,
  "original_Cpp_meaning_of_R4_plus_0x5e4_or_0x10_0x16_suit_weapon_identified":False,
  "source_real_2010_shared_case_1_18_calls_orig_weapon_manager_get_current":True,
  "source_2010_native_shared_case_2_25_calls_CurrentWeapon_and_virtual_0x128":True,
  "source_original_native_cpp_method_at_virtual_0x128_or_weapon_ID_proven":False,
  "2010_source_native_hit_damage_anim_missile_AimM_binding_proven":False,
  "original_source_same_branch_proves_same_weapon_effect_output":False,
  "Vita_G83_G169_original_animation_owner_or_input_modified":False,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G216 original 2010 IM1/WM18 -> 0xF6930 native actor mode R4+0x5e4 dynamic branches (0,1,2) and conditional R5 selection")
 print("G216 original 2010 IM2/WM25 -> 0xF6648 genuine WeaponMgr GetCurrentWeapon and C++ virtual +0x128 guarded calls")
 print("G216 PASS",len(must),"REAL native 2010 ARM instructions, real original 56*4 state metadata; original weapon IDs and hitframes unproven; no Vita VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for arg in ("g196","g214","out"):p.add_argument("--"+arg,required=True,type=Path)
 a=p.parse_args()
 main(a.g196,a.g214,a.out)
