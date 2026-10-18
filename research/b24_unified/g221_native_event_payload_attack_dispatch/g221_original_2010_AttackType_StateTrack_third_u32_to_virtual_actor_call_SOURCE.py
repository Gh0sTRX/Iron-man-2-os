#!/usr/bin/env python3
"""G221 source-only TRUE ORIGINAL iOS 2010:
 StateData authored AttackType -> Actor::UpdateStateAttack ->
 StateTrack::GetEvent(previous,current) -> event INDEX -> event[INDEX].third u32 ->
 [Actor vtable + 0x110](AttackType, event third u32).

Reuses G213B exact source 55 group / 1487 named states / 3658 original
StateTracks; G219 all original ARM opcodes; G220 exact native CALLSITE graph.
This proves DATAFLOW to a VIRTUAL invocation, not virtual method identity
or that the third field means damage, missile, hit frame, or button.
No VPK, weapon, guessed time conversion.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path
def run(g213,g219,g220,out):
 d=json.loads(g213.read_text())
 arm=json.loads(g219.read_text())
 call=json.loads(g220.read_text())
 if not (
 d["source_original_2010_StateSet_count"]==55 and
 d["source_original_2010_StateData_count"]==1487 and
 d["source_original_StateTrack_count"]==3658 and
 d["source_original_AttackType_key_u32_value_count"]==379 and
 d["source_original_all_bytes_consumed_exactly"]):
  raise ValueError("G221 requires full REAL 2010 original StateData native decode")
 if (call["source_direct_ARM_GetEvent_BL_BLX_callsite_count"]!=5 or
     call["genuine_native_original_StateTrack_GetEvent_VM"]!="0xa14f0"):
  raise ValueError("G221 requires exact original G220 caller source BL provenance")
 cpp={c["owner_cpp_method"]:c for c in call["source_real_2010_direct_GetEvent_callsite_windows"]}
 if "Actor::UpdateStateAttack(int, State*)" not in cpp:
  raise ValueError("no original C++ Actor attack callsite")
 if cpp["Actor::UpdateStateAttack(int, State*)"]["original_source_callsite"]!="0xdb684":
  raise ValueError("original C++ event attack CALLSITE drift")
 actor=arm["real_native_original_methods_source"]["actor"]
 if actor["source_original_vm"]!="0xdb610":
  raise ValueError("source native Actor attack vm drift")
 actual={int(t["VM"],16):(t["opcode"],t["operands"])
    for t in actor["source_original_ARM_ops_no_machine_bytes"]}
 expected={
  0xdb65c:("bl","#0x9c340"), # StateData::GetParam("AttackType",-1)
  0xdb660:("cmp","r0, #1"),
  0xdb664:("cmpne","r0, #0x12"), # original 18
  0xdb668:("mov","sl, r0"), # AttackType retained on stack callee saved register
  0xdb674:("ldr","r1, [r5, #0x3e4]"),# previous event time
  0xdb678:("mov","r0, r8"), # StateTrack pointer
  0xdb67c:("ldr","r4, [lr, #0xc]"),# current time
  0xdb680:("mov","r2, r4"),
  0xdb684:("bl","#0xa14f0"),
  0xdb688:("str","r4, [r5, #0x3e4]"),
  0xdb68c:("subs","r1, r0, #0"), # index or -1
  0xdb690:("lslge","r3, r1, #4"),
  0xdb694:("ldrge","r0, [r8, #8]"),
  0xdb698:("subge","r3, r3, r1, lsl #2"),
  0xdb69c:("addge","r0, r3, r0"),
  0xdb6a0:("mvnlt","r2, #0"),
  0xdb6a4:("ldrge","r2, [r0, #8]"),# genuine 3rd u32 record value
  0xdb6c8:("mov","r1, sl"),# original AttackType passed in r1
  0xdb6d0:("mov","r0, r5"),# actor this pointer
  0xdb6d4:("mov","lr, pc"),# native vcall prologue
  0xdb6d8:("ldr","pc, [r3, #0x110]"),# VIRTUAL method not proven DoAttack
 }
 for addr,asm in expected.items():
  if actual.get(addr)!=asm:
   raise ValueError(f"G221 genuine source original 2010 Actor ARM drift {hex(addr)}: {actual.get(addr)} != {asm}")
 owner={x["original_2010_StateSet_name"]:x for x in d["source_original_2010_state_sets_all"]}
 groups=("IronMan","IronMan_suitcase","Warmachine","stealth")
 records=[];distrib={}
 for name in groups:
  states=owner[name]["source_authentic_2010_StateData"]
  if len(states)!=194:raise ValueError("native 2010 owner state count drift "+name)
  total=0
  hist=collections.Counter()
  for state in states:
   defs=state["source_original_attacktype_exact_definitions"]
   if len(defs)>1:raise ValueError("G221 StateData unexpected many AttackType")
   at=defs[0]["value"] if defs else None
   if at is None:continue
   for ch in state["source_original_event_channels"]:
    for track in ch["source_2010_attached_track_records"]:
     if track["native_original_track_name"] not in ("attack","Attack"):continue
     for e in track["source_authentic_2010_event_records"]:
      row={"real_source_2010_armor":name,
       "owner_state_source_name":state["source_original_state_name"],
       "owner_native_StateData_id":state["source_original_state_record_index"],
       "source_authored_AttackType":at,
       "source_original_track_name":track["native_original_track_name"],
       "original_event_record_start_raw":e["start_source_raw_integer"],
       "original_event_record_duration_raw":e["duration_source_raw_integer"],
       "original_event_record_third_u32_PASSABLE_TO_VIRTUAL":e["third_u32_unknown_semantics"],
       "source_native_2010_actor_vtable_plus_0x110_is_which_Method_PROVEN":False,
       "source_event_third_u32_IS_melee_damage_hit_ID_or_shot_type_PROVEN":False}
      records.append(row);total+=1;hist[e["third_u32_unknown_semantics"]]+=1
  distrib[name]={"source_true_2010_authored_attack_marker_records":total,
                 "original_2010_event_third_u32_value_frequencies":{str(k):v for k,v in sorted(hist.items())}}
  print("G221 genuine owner",name,"original authored AttackType-associated attack event records",total,
     "third field source numeric histogram",dict(hist),flush=True)
 output={
  "origin":"TRUE 2010 native C++ and full iOS StateData authored AttackType; indexed StateTrack::GetEvent returns index and Actor uses third u32 in original virtual attack handler",
  "source_original_StateData_GetParam_key_AttackType_native_VM":"0x9c340",
  "source_actual_ARM_StateTrack_GetEvent_native_VM":"0xa14f0",
  "source_original_real_actor_AttackType_event_caller_VM":"0xdb610",
  "source_real_actor_attack_GetEvent_CALL_VM":"0xdb684",
  "source_original_event_array_third_u32_READ_by_ACTOR_VM":"0xdb6a4",
  "original_2010_native_AttackType_argument_MOV_r1_sl_VM":"0xdb6c8",
  "original_2010_vtable_dynamic_dispatch_VM":"0xdb6d8",
  "original_2010_vtable_dynamic_method_offset_bytes":272,
  "source_original_event_third_u32_loaded_in_ARM_r2":True,
  "source_genuine_ARM_exact_instruction_count_verified":len(expected),
  "source_actual_native_2010_event_original_armor_values":distrib,
  "source_original_2010_AttackType_associated_named_attack_event_rows":records,
  "source_native_vtable_slot_0x110_function_identity_PROVEN":False,
  "source_original_attack_event_third_u32_means_hitframe_damage_or_missile_ID_PROVEN":False,
  "source_any_iOS_attacks_or_damage_executed_in_Vita":False,
  "source_G218_live_original_readonly_bridge_changed":False,
  "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n")
 print("G221 PASS original iOS 2010 dataflow AttackType r1 + authentic native StateTrack third u32 r2 at actor virtual slot +0x110, identity/meaning UNKNOWN; no fake Vita attack/VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for q in ("g213","g219","g220","out"):p.add_argument("--"+q,type=Path,required=True)
 a=p.parse_args();run(a.g213,a.g219,a.g220,a.out)
