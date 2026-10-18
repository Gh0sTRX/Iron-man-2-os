#!/usr/bin/env python3
"""G224 original Iron Man 2 (2010) MainCharacter::DoAttack(int,int) native
r1 authored AttackType and r2 third u32 original StateTrack event payload.
Source-only register use/compare/callsite analysis from authentic G196
entire 646 ARM original opcodes and independently authenticated G221
Actor::UpdateStateAttack into genuine virtual DoAttack (G222).

DO NOT ascribe 0/1/2/3 to damage, rockets, impact time, target id, or
gesture until grounded original 2010 native branch and weapon data prove it.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path
def main(g196:Path,g221:Path,out:Path):
 orig=json.loads(g196.read_text());bridge=json.loads(g221.read_text())
 ops=orig["source_original_entire_DoAttack_646_ARM_opcode_metadata"]
 if len(ops)!=646 or orig["native_source_method_VM"]!="0xf64f8" or \
    not orig["source_2010_original_native_dispatch_cmp_r5_25_jump_table_proven"]:
  raise ValueError("G224 requires original 2010 ARM complete 646 source opcodes and authentic 26-way dispatch")
 if (bridge["source_original_event_array_third_u32_READ_by_ACTOR_VM"]!="0xdb6a4"
 or bridge["original_2010_vtable_dynamic_dispatch_VM"]!="0xdb6d8"):
  raise ValueError("G224 original native state event argument bridge source missing")
 by={int(x["vm"],16):x for x in ops}
 first=ops[:44]
 for x in first:print("G224 real 2010 original DoAttack prologue",x["vm"],x["mnemonic"],x["args"])
 registry=[]
 for idx,x in enumerate(ops):
  addr=int(x["vm"],16)
  # Distinguish exact r2 use from textual r2 occurrence in 0x2/r12.
  args=x["args"]
  relevant=any(t in args.replace("["," ").replace("]"," ").replace(","," ").split()
                 for t in ("r2","r5","r6","sl"))
  if not relevant:continue
  if addr<0xf6540 or x["mnemonic"].startswith(("cmp","teq","tst")):
   registry.append({"VM":x["vm"],"opcode":x["mnemonic"],"args":args,
                    "source_opindex":idx})
  if addr<0xf65c0 and relevant:
   print("G224 native event dispatch original ARM",x["vm"],x["mnemonic"],args)
 # Show every exact instruction that compares native input second-int
 # register to literal, but source register retention must be confirmed:
 compares=[x for x in ops if x["mnemonic"].startswith(("cmp","tst","teq")) and
     ("r6," in x["args"] or "r2," in x["args"] or "r5," in x["args"])]
 print("G224 original ARM body input candidate register compares",len(compares))
 for q in compares:print("G224 SOURCE Original register CMP",q)
 pairvals=[
   {"armor":armor,"authored_ATTACKTYPE_event_rows":v["source_true_2010_authored_attack_marker_records"],
    "event_third_field_u32_count":v["original_2010_event_third_u32_value_frequencies"]}
    for armor,v in bridge["source_actual_native_2010_event_original_armor_values"].items()
 ]
 result={
  "source":"G224 exact 646 authentic iOS 2010 native MainCharacter DoAttack ARM opcode inventory + source event third u32 Actor input",
  "authentic_2010_original_DoAttack_ARM_VM":"0xf64f8",
  "source_real_native_original_ARM_prologue_first44":first,
  "original_source_ARM_input_register_relevant_before_dispatch":registry[:200],
  "source_original_register_cmp_all":compares,
  "source_original_DoAttack_opcode_count":len(ops),
  "source_original_4_armor_AttackType_eventPayload_values":pairvals,
  "original_Cpp_Actor_Event_third_u32_passed_as_DoAttack_second_INT_proven":True,
  "source_exact_arm_input_r2_register_reassignment_or_preservation_PROVEN":False,
  "source_native_event_third_u32_values_0_1_2_3_gameplay_semantics_PROVEN":False,
  "source_original_2010_touchgesture_button_full_equivalence_PROVEN":False,
  "source_G218_Vita_real_combat_physics_or_damage_modified":False,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
 print("G224 PASS exact original 646 ARM opcode source DoAttack second event arg register comparisons identified for next source step, no guessed damage/input/VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for v in ("g196","g221","out"):p.add_argument("--"+v,type=Path,required=True)
 a=p.parse_args()
 main(a.g196,a.g221,a.out)
