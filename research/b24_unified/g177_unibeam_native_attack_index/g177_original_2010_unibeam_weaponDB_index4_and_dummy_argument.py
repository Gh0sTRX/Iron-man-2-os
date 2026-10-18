#!/usr/bin/env python3
"""G177: original 2010 iOS exact source UniBeam attack DB index 4 and
dummy argument native ARM register chain. All evidence from authenticated
G97 and G175 owner-derived READ-ONLY metadata; no IPA download/VPK.

C++ AAPCS instance method GetAttackEntityByIndex(int):
  0xf60d0 BL WeaponDB::GetInstance     -> r0=this
  0xf60d4 MOV r1,#4                    -> arg0=4
  0xf60d8 BL WeaponDB::GetAttackEntityByIndex
No call/branch between the argument write and call.
Do NOT conflate this index 4 with Lua AttackType 1 permission or exact
damage/clip activation (still unproven).
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
SRC="MainCharacter::DoUniBeamAttack("
IDCALL=0xF60D8
DUMMYCALL=0xF611C
def main(g97,g175,out):
 m=json.loads(g97.read_text())
 g=json.loads(g175.read_text())
 if not m["NO_VPK"] or not g["NO_VPK"]:raise ValueError("Not genuine safe owner source metadata")
 matches=[r for r in m["original_CPP_methods"] if r.get("original_symbol_found")
          and r["source_method"].startswith(SRC)]
 if len(matches)!=1 or matches[0]["original_ARM_address_hex"]!="0xf60ac":
  raise ValueError("2010 source UniBeam method provenance changed")
 op={int(row["pc_hex"],16):row for row in matches[0]["full_bounded_original_source_opcode_metadata_NOT_machine_bytes"]}
 expected={
  0xF60D0:("bl","#0xab324"),
  0xF60D4:("mov","r1, #4"),
  0xF60D8:("bl","#0xab3ec"),
  0xF60C8:("mov","r5, r1"),
  0xF60FC:("add","r1, r8, #0x48"),
  0xF6100:("mov","r2, r5"),
  0xF60F8:("mov","r3, #1"),
  0xF610C:("sub","r3, r3, #1"),
  0xF6118:("add","r0, sp, #0x1c"),
  0xF611C:("bl","#0x159c4"),
 }
 for address,(mn,arg) in expected.items():
  native=op.get(address)
  if not native or native["mnemonic"].lower()!=mn or native["operand_register_or_literal"].lower()!=arg:
   raise ValueError("G177 exact original 2010 ARM opcode divergence "+hex(address)+" got "+repr(native))
 target=g["original_native_method_target_matches"]
 assert any(a=="0xab3ec" and "WeaponDB::GetAttackEntityByIndex(int)"==name
            for a,name in target["weapon_attack_lookup"])
 edges=g["source_direct_weapon_animation_related_callsite_evidence"]
 def real_edge(site,dst,label):
  found=[x for x in edges if x["original_caller_address"]=="0xf60ac"
   and x["original_callsite_VM"]==hex(site) and x["direct_callee_VM"]==hex(dst)
   and label in x["direct_callee_symbol"]]
  if len(found)!=1:raise ValueError("Missing authentic original 2010 native direct call "+hex(site))
  return found[0]
 real_edge(IDCALL,0xab3ec,"WeaponDB::GetAttackEntityByIndex(int)")
 real_edge(DUMMYCALL,0x159c4,"Object3D::GetDummyAbsolutePosition(int, int)")
 callers=[dict(caller_VM=x["original_caller_address"],callsite_VM=x["original_callsite_VM"],
               method_names=x["original_caller_symbol"])
          for x in edges if x["direct_callee_VM"]=="0xf60ac"]
 # Most important recovered fact: ORIGINAL 2010 WeaponDB ATTACK INDEX = 4.
 report={
  "source":"Original owner 2010 1.0.0 ARM C++ MachO, G97 instruction provenance + G175 exact native function symbols/callees",
  "original_UniBeam_function":"MainCharacter::DoUniBeamAttack(int, Actor*, float, float, vector3d const&)",
  "original_UniBeam_function_native_VM":"0xf60ac",
  "native_weaponDB_getinstance_VM":"0xab324",
  "original_UniBeam_WeaponDB_GetAttackEntityByIndex_VM":"0xab3ec",
  "authored_original_2010_UniBeam_WeaponDB_index_proven":True,
  "original_UniBeam_WeaponDB_attack_index_actual_int":4,
  "native_source_instruction_evidence":{
    hex(k):{"mnemonic":v[0],"operands":v[1]} for k,v in expected.items()},
  "original_source_native_dummy_lookup_VM":"0x159c4",
  "original_source_native_dummy_lookup_callsite_VM":"0xf611c",
  "original_dummy_lookup_first_int_from_UniBeam_function_int_param":True,
  "original_dummy_lookup_second_int_argument_directly_derived_as_zero":True,
  "original_dummy_lookup_final_rig_name_or_chest_socket_PROVEN":False,
  "original_UniBeam_genuine_direct_native_callers_in_selected_family":callers[:100],
  "original_UniBeam_attack_index4_equals_MissionTutorial_AttackType1":False,
  "original_UniBeam_attack_index4_maps_to_named_IM2V_Beam_clip_PROVEN":False,
  "original_UniBeam_AttackEntity_index4_numeric_damage_PROVEN":False,
  "native_UniBeam_attachment_dummy_index_parameter_runtime_value_PROVEN":False,
  "no_original_B16_weapon_damage_or_animation_mapping_auto_forged":True,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G177 PROVEN native 2010 iOS original UniBeam WeaponDB::GetAttackEntityByIndex(4) from ARM MOV r1,#4 + BL at 0xF60D8")
 print("G177 PROVEN source Object3D dummy lookup receives UniBeam first int method argument via r5 -> r2, r3 zero")
 print("G177 authenticated selected native direct CALLERS",callers[:35])
 print("G177 native AttackIndex=4 DOES NOT prove Aim_M/weapon damage/chest dummy id, NO VPK")
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--g97",type=Path,required=True)
 a.add_argument("--g175",type=Path,required=True)
 a.add_argument("--out",type=Path,required=True)
 p=a.parse_args()
 main(p.g97,p.g175,p.out)
