#!/usr/bin/env python3
"""G225 exact 2010 Iron Man 2 iOS authored StateTrack event[INDEX].third
u32 -> MainCharacter::DoAttack's ARM r2 -> retained r8, author AttackType
r1 -> retained r5, native 26-case branch, default original C++ base
Actor::DoAttack(int,int) explicitly receives the ORIGINAL two integers.

The path is a code branch, not proof that user's 2010 game enters it
at runtime. Preserve unknown 0/1/2/3 event meaning. Native original
case 1/18 and 2/25 split from default. NO VPK, no Vita gameplay change.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path
def main(g196:Path,g221:Path,out:Path):
 source=json.loads(g196.read_text());up=json.loads(g221.read_text())
 data=source["source_original_entire_DoAttack_646_ARM_opcode_metadata"]
 if len(data)!=646 or source["native_source_method_VM"]!="0xf64f8":
  raise ValueError("requires EXACT original 646 opcode DoAttack source")
 if (up["source_original_event_array_third_u32_READ_by_ACTOR_VM"]!="0xdb6a4"
     or up["source_original_real_actor_AttackType_event_caller_VM"]!="0xdb610"
     or up["source_original_event_third_u32_loaded_in_ARM_r2"] is not True):
  raise ValueError("requires G221 original true Actor C++ authored event register bridge")
 ins={int(x["vm"],16):(x["mnemonic"],x["args"]) for x in data}
 proven={
  0xf6508:("mov","r4, r0"),  # source C++ this
  0xf650c:("mov","r5, r1"),  # original AttackType kept in register
  0xf6518:("mov","r8, r2"),  # original event[index].third saved
  0xf6524:("cmp","r5, #0x19"),
  0xf6528:("addls","pc, pc, r5, lsl #2"),
  0xf652c:("b","#0xf6598"), # beyond 25 defaults
  0xf6598:("mov","r0, r4"), # base Actor object
  0xf659c:("mov","r1, r5"), # original authored attack type
  0xf65a0:("mov","r2, r8"), # original event third u32
  0xf65a4:("bl","#0xda5b8") # REAL C++ Actor::DoAttack(int,int)
 }
 for addr,expect in proven.items():
  if ins.get(addr)!=expect:raise ValueError("native owner 2010 DoAttack register provenance drift @"+hex(addr)+" "+str(ins.get(addr)))
 switch=source["source_original_2010_attack_id_switch_0_to_25"]
 if len(switch)!=26:raise ValueError("not authentic 26 ARM native table")
 case_dest=collections.defaultdict(list)
 for text_id,row in switch.items():
  idx=int(text_id);entry=0xf6530+idx*4
  if row["native_ARM_2010_entry_VM"]!=hex(entry):raise ValueError("source ARM original jump table drift")
  case_dest[row["original_target_VM"]].append(idx)
 cases=[{"source_ARM_destination":k,"original_2010_AttackType_IDs":sorted(v),
         "destination_is_native_base_Actor_fallback":k=="0xf6598"}
        for k,v in sorted(case_dest.items(),key=lambda x:int(x[0],16))]
 eventreg=[{"VM":x["vm"],"opcode":x["mnemonic"],"args":x["args"]}
  for x in data if "r8" in x["args"].replace(","," ").replace("["," ").replace("]"," ").split()]
 print("G225 original owner 2010 r8 second-event register uses count",len(eventreg))
 for x in eventreg:print("G225 true original event third-u32 r8 USE",x)
 print("G225 actual 2010 26-case native DoAttack dispatch distinct targets",len(cases))
 for c in cases:print("G225 original ARM attack type cases",c)
 assert "0xf6930" in case_dest and sorted(case_dest["0xf6930"])==[1,18]
 assert "0xf6648" in case_dest and sorted(case_dest["0xf6648"])==[2,12,25]
 assert 4 in case_dest.get("0xf65c4",[])
 assert "0xf6598" in case_dest
 result={
  "source":"2010 authentic owner MainCharacter::DoAttack complete original ARM and G221 Actor native StateTrack event provenance",
  "source_genuine_ARM_argument_register_and_fallback_opcode_match":len(proven),
  "source_original_cpp_this":"r4 preserved from r0",
  "source_original_authored_AttackType_argument":"r5 preserved from r1",
  "source_original_event_third_u32_argument":"r8 preserved from r2",
  "source_original_second_event_register_r8_uses":eventreg,
  "source_original_native_26_attacktype_switch_target_groups":cases,
  "source_distinct_original_native_cpp_attack_case_addresses":len(cases),
  "source_real_2010_default_base_CPP_Actor_DoAttack_target_VM":"0xda5b8",
  "source_real_second_event_u32_is_passed_UNMODIFIED_to_base_ActorDoAttack":True,
  "native_2010_original_named_unknown_AttackType_ID_to_weapon_aim_timing_meaning_PROVEN":False,
  "native_2010_original_second_event_int_value_0_1_2_3_semantics_PROVEN":False,
  "Vita_original_damage_hardware_walk_or_weapon_changed":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2)+"\n")
 print("G225 PASS 2010 real original 26-case AttackType dispatch, authentic StateTrack event second arg preserved r8 and parent fallback Actor DoAttack, no fabricated gameplay")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for x in ("g196","g221","out"):p.add_argument("--"+x,type=Path,required=True)
 a=p.parse_args();main(a.g196,a.g221,a.out)
