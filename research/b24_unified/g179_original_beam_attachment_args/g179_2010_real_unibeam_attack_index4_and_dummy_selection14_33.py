#!/usr/bin/env python3
"""G179 original 2010 iOS UniBeam:
 * MainCharacter::DoAttack three actual native BL DoUniBeam sites
   pass int first argument 14,14,33 via ARM r1.
 * DoUniBeamAttack forwards initial r1 through r5 into r2 for
   Object3D::GetDummyAbsolutePosition (hidden vector return in r0).
 * Separately gets exact WeaponDB::GetAttackEntityByIndex(4).

Direct original ARM register read/write source PROOF only. The numeric 14/33
are NOT assigned a bone/dummy NAME until the original ID→rig mapping is
decoded and verified. Does not set B24 port weapon/damage/particle/VPK.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
SITES={"0xf6638":(14,"0xf662c"),"0xf6d8c":(14,"0xf6d74"),
       "0xf6e04":(33,"0xf6de4")}

def provenance(site):
 ops=site["authentic_callsite_previous_38_instructions_NOT_MACHINE_BYTES"]
 return {x["arm_VM"]:x for x in ops}

def main(g177,g178,out):
 x=json.loads(g177.read_text())
 y=json.loads(g178.read_text())
 if not x["NO_VPK"] or not y["NO_VPK"] or not x["authored_original_2010_UniBeam_WeaponDB_index_proven"]:
  raise ValueError("Must use source-authenticated owner original ARM G177 and G178")
 if x["original_UniBeam_WeaponDB_attack_index_actual_int"]!=4:
  raise ValueError("Native original 2010 UniBeam index 4 source changed")
 if not x["original_dummy_lookup_first_int_from_UniBeam_function_int_param"]:
  raise ValueError("No proven AAPCS dummy arg flow")
 if set(y["actual_original_UniBeam_callsite_VMs"])!=set(SITES):
  raise ValueError("Original ARM DoAttack three source calls changed")
 proven=[]
 for site in y["native_callsite_source_context_no_bytes"]:
  dst=site["original_real_owner_DoAttack_callsite_VM"]
  if dst not in SITES:raise ValueError("Unverified ARM callsite "+dst)
  expected_int,writer=SITES[dst]
  ops=site["authentic_callsite_previous_38_instructions_NOT_MACHINE_BYTES"]
  table=provenance(site)
  wrote=table.get(writer)
  if not wrote or wrote["opcode"]!="mov" or wrote["args"]!=f"r1, #{hex(expected_int) if expected_int>9 else expected_int}":
   raise ValueError("original source r1 immediate mismatch at "+writer+" for "+dst)
  write_pos=next(k for k,row in enumerate(ops) if row["arm_VM"]==writer)
  call_pos=next(k for k,row in enumerate(ops) if row["arm_VM"]==dst)
  if call_pos!=len(ops)-1 or call_pos<=write_pos:raise ValueError("not native caller context")
  for row in ops[write_pos+1:call_pos]:
   opcode=row["opcode"]
   op=row["args"].strip()
   if (op.startswith("r1,") and opcode.startswith((
        "mov","add","sub","ldr","and","orr","eor","bic","mul","rsb","mvn","adc"))) or opcode.startswith(("bl","blx")):
    raise ValueError("native r1 argument changed or call clobbered after source literal")
  assert table[dst]["opcode"]=="bl" and table[dst]["args"]=="#0xf60ac"
  proven.append({"native_DoAttack_callsite_VM":dst,
    "authentic_original_source_MOV_r1_VM":writer,
    "actual_int_passed_to_DoUniBeamAttack":expected_int,
    "native_direct_call_DoUniBeam_VM":"0xf60ac",
    "source_register_AAPCS_forward_chain_proven":True,
    "final_original_dummy_3D_attachment_name_proven":False})
 if len(proven)!=3:raise ValueError("G179 expected three source-native calls")
 result={
  "source":"2010 authentic owner ARM Mach-O G177 source instructions and G178 real MainCharacter DoAttack 3 direct UniBeam calls",
  "original_UniBeam_WeaponDB_Attack_index_proven":4,
  "original_DoAttack_to_UniBeam_arg0_native_integer_values":[14,14,33],
  "original_three_exact_native_callsite_proofs":proven,
  "original_attached_dummy_selection_int_argument_14_33_proven_in_native_call_chain":True,
  "original_dummy_index14_actual_original_bone_or_scene_node_PROVEN":False,
  "original_dummy_index33_actual_original_bone_or_scene_node_PROVEN":False,
  "original_2010_attackID1_Lua_permission_IS_SAME_as_WeaponDB_index4":False,
  "original_2010_numerical_damage_for_WeaponDB_index4_PROVEN":False,
  "original_2010_uniBeam_source_HUD_trigger_and_aim_m_animation_PROVEN":False,
  "B24_game_weapon_or_Actor_state_modified":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print("G179 GENUINE original 2010 UniBeam WeaponDB index 4, 3 real DoAttack native callsites first int arguments 14 / 14 / 33")
 for row in proven:print("G179 SOURCE AUTHORED 2010",row)
 print("G179 original dummy source names and animation controller semantics still unresolved. NO VPK")
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--g177",type=Path,required=True)
 a.add_argument("--g178",type=Path,required=True)
 a.add_argument("--out",type=Path,required=True)
 p=a.parse_args()
 main(p.g177,p.g178,p.out)
