#!/usr/bin/env python3
"""G201 original 2010 iOS ARM: Actor::UpdateStateAttack(int,State*) is
a REAL virtual dispatch source for MainCharacter::DoAttack(int,int)
through shared slot68 (+0x110). Check original native vtable word in
Actor and MainCharacter source, exact this->vtable load and r1 argument.

This proves *potential dynamic override dispatch* if the receiver really
is MainCharacter; runtime handler/event and which attack input ID is
triggered still require source callsite or touchHLE runtime evidence.
Never claim G83 Aim_M or Vita live combat already completed. NO VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,struct,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
ORIGINAL=248613763
FN=0xdb610
BRANCH=0xdb6d8
ACTOR_VTABLE=0x4bd474
MAIN_VTABLE=0x4bd85c
SLOT=68
METH=0xf64f8
def analyze(ipa:Path,out:Path):
 if ipa.stat().st_size!=ORIGINAL:raise ValueError("requires original owner iOS 2010 IPA")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("original owned ZIP damaged")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("source 2010 executable length drift")
 dat=parse_macho(exe)
 dem=subprocess.run(["c++filt"],input="\n".join(e[0] for e in dat["entries"])+"\n",
                    text=True,capture_output=True,check=True).stdout.splitlines()
 if len(dem)!=len(dat["entries"]):raise ValueError("native C++ symbol mismatch")
 by=collections.defaultdict(set)
 for e,n in zip(dat["entries"],dem):by[e[1]&~1].add(n)
 wanted={FN:"Actor::UpdateStateAttack(int, State*)",
         MAIN_VTABLE:"vtable for MainCharacter",
         ACTOR_VTABLE:"vtable for Actor",
         METH:"MainCharacter::DoAttack(int, int)"}
 for addr,name in wanted.items():
  if name not in by[addr]:raise ValueError("original source C++ method drift "+hex(addr)+" "+name)
 def ptr(vm):
  sec=next((s for s in dat["sections"] if s[0]<=vm and vm+4<=s[0]+s[1] and s[3]=="__const"),None)
  if sec is None:raise ValueError("real vtable word not file-backed __const "+hex(vm))
  return struct.unpack_from("<I",exe,sec[2]+vm-sec[0])[0]
 actor_vm=ACTOR_VTABLE+8+SLOT*4
 main_vm=MAIN_VTABLE+8+SLOT*4
 actor_call=ptr(actor_vm)
 main_call=ptr(main_vm)
 if main_call&~1!=METH:raise ValueError("MainCharacter override native slot68 changed")
 if actor_call&~1==0:raise ValueError("Actor virtual source slot68 empty")
 sec=next(s for s in dat["sections"] if s[3]=="__text" and s[0]<=FN<s[0]+s[1])
 starts=sorted(by);i=bisect.bisect_right(starts,FN)
 end=starts[i] if i<len(starts) else sec[0]+sec[1]
 length=min(end-FN,sec[0]+sec[1]-FN,8192)
 if length<=BRANCH-FN:raise ValueError("source original attack update incomplete")
 decoder=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);decoder.detail=True
 o=sec[2]+FN-sec[0]
 ins=list(decoder.disasm(exe[o:o+length],FN))
 mapped={op.address:op for op in ins}
 exact={
  0xdb6bc:("ldr","r0, [r5, #0x3dc]"),
  0xdb6c0:("ldr","r3, [r5]"),
  0xdb6c4:("add","ip, r0, #1"),
  0xdb6c8:("mov","r1, sl"),
  0xdb6cc:("str","ip, [r5, #0x3dc]"),
  0xdb6d0:("mov","r0, r5"),
  0xdb6d4:("mov","lr, pc"),
  0xdb6d8:("ldr","pc, [r3, #0x110]")
 }
 for vm,(op,args) in exact.items():
  native=mapped.get(vm)
  if native is None or native.mnemonic!=op or native.op_str!=args:
   raise ValueError("original actual Actor virtual DoAttack bridge drift "+hex(vm))
 # Source register sl provenance: find named ARM opcodes assigning it
 # prior to this exact call. We do not infer its content from the type
 # of the State* pointer or an unverified runtime trace.
 prior=[op for op in ins if op.address<BRANCH]
 sl_updates=[{"source_VM":hex(op.address),"opcode":op.mnemonic,"args":op.op_str}
   for op in prior if op.op_str.startswith("sl,") and
    op.mnemonic.startswith(("mov","ldr","add","sub","mvn","orr","and"))]
 branches=[{"source_VM":hex(op.address),"opcode":op.mnemonic,"args":op.op_str}
   for op in prior if op.mnemonic.startswith(("cmp","tst","beq","bne","blt","bgt","ble","bge","bhi","bls"))]
 source={
  "source":"original 2010 iOS ARM Actor and MainCharacter C++ vtables and exact Actor::UpdateStateAttack native function",
  "original_source_Actor_UpdateStateAttack_VM":hex(FN),
  "Actor_base_original_vtable_symbol_VM":hex(ACTOR_VTABLE),
  "MainCharacter_derived_original_vtable_symbol_VM":hex(MAIN_VTABLE),
  "native_Cpp_zero_based_virtual_slot":SLOT,
  "source_virtual_CALL_byte_offset":0x110,
  "source_Actor_vtable_slot68_entry_VM":hex(actor_vm),
  "source_Actor_vtable_slot68_method_VM":hex(actor_call&~1),
  "source_Actor_vtable_slot68_method_cpp":sorted(by.get(actor_call&~1,()))[:8],
  "source_MainCharacter_vtable_slot68_entry_VM":hex(main_vm),
  "source_MainCharacter_vtable_slot68_method_VM":hex(main_call&~1),
  "source_MainCharacter_vtable_slot68_method_cpp":sorted(by.get(main_call&~1,()))[:8],
  "source_actual_Actor_UpdateStateAttack_indirect_CALL_VM":hex(BRANCH),
  "native_2010_Actor_this_vtable_load_r5_proven":True,
  "native_2010_virtual_dispatch_through_slot68_proven":True,
  "native_2010_actual_param1_r1_from_sl_register_proven":True,
  "native_2010_maincharacter_override_vtable_virtual_dispatch_possible":True,
  "source_original_Actor_UpdateStateAttack_all_ARM_no_bytes":[
    {"vm":hex(i.address),"opcode":i.mnemonic,"args":i.op_str} for i in ins],
  "source_original_SL_producer_opcodes":sl_updates,
  "source_native_original_branch_comparisons":branches,
  "source_Actor_receiver_is_MainCharacter_during_real_2010_gameplay_PROVEN":False,
  "source_which_of_26_attack_input_values_loaded_into_SL_PROVEN":False,
  "source_touchHLE_event_to_original_Actor_UpdateStateAttack_PROVEN":False,
  "source_G83_Aim_M_or_G169_beam_to_native_selector_mapping_PROVEN":False,
  "new_Vita_actor_or_weapon_logic_applied":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(source,indent=2,ensure_ascii=False)+"\n")
 print("G201 REAL ORIGINAL 2010 Actor source vtable",hex(actor_vm),
       source["source_Actor_vtable_slot68_method_cpp"],
       "derived MainCharacter override",hex(main_vm),
       source["source_MainCharacter_vtable_slot68_method_cpp"])
 print("G201 original 2010 Actor::UpdateStateAttack -> this vtable slot68 +0x110 @",hex(BRANCH),
       "native 2010 r1 attack argument MOV r1,sl source")
 for row in sl_updates:print("G201 ORIGINAL SL producer",row)
 for row in branches[:30]:print("G201 ORIGINAL attack state guard",row)
 for row in source["source_original_Actor_UpdateStateAttack_all_ARM_no_bytes"][:100]:
  print("G201 ORIGINAL Actor ARM",row)
 print("G201 source virtual dispatch bridge PROVEN, runtime controller selector NOT YET PROVEN. NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 analyze(a.ipa,a.out)
