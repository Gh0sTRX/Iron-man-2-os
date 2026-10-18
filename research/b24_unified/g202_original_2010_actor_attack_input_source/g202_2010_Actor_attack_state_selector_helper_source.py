#!/usr/bin/env python3
"""G202 original user-owned 2010 iOS Actor::UpdateStateAttack
value/data provenance to MainCharacter::DoAttack via virtual slot 68.

The Actor state-machine:
 LDR sl,[State* + 4]  # source state record selection index
 indexed state-owned subtable, 2010 native CALL @0xDB65C to 0x9C340
 CMP helper result == 1 OR 18; MOV sl,helper result, branch
 ...
 MOV r1,sl; MOV lr,pc; LDR pc,[this->vtable + 0x110]

Determine genuine CPP method symbols at 0x9C340, 0xA14F0 et al and
bounded original native method call graph, without assuming helper result
is a weapon category or on-screen control type.
"""
from __future__ import annotations
import argparse,bisect,collections,json,struct,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
OWNER=248613763
UPDATE=0xdb610
HELPERS={
 "attack_index_helper":0x9c340,
 "state_attack_transition":0xa14f0,
 "state_get_state":0xb1cf4,
 "actor_action_1":0xc0bec,
 "actor_action_2":0xc0c0c,
 "attack_animation_transition":0x6a0b8,
 "attack_animation_alt":0x6a0a4,
}
def run(ipa:Path,out:Path):
 if ipa.stat().st_size!=OWNER:raise ValueError("authentic 2010 original iOS IPA size expected")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("Original owner ZIP corrupt")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("original native ARM MachO executable size changed")
 native=parse_macho(exe)
 names=subprocess.run(["c++filt"],input="\n".join(t[0] for t in native["entries"])+"\n",
                      text=True,capture_output=True,check=True).stdout.splitlines()
 if len(names)!=len(native["entries"]):raise ValueError("genuine C++ symbol table mismatch")
 byname=collections.defaultdict(set);bits=collections.defaultdict(set)
 for rec,n in zip(native["entries"],names):
  loc=rec[1]&~1
  byname[loc].add(n);bits[loc].add(rec[1]&1)
 if "Actor::UpdateStateAttack(int, State*)" not in byname[UPDATE]:
  raise ValueError("Actor source original 2010 function changed")
 addresses=sorted(byname)
 textsects=[s for s in native["sections"] if s[3]=="__text"]
 csarm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);csarm.detail=True
 csthumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB);csthumb.detail=True
 def decode(addr,nmax=2800):
  sec=next((s for s in textsects if s[0]<=addr<s[0]+s[1]),None)
  if sec is None:return []
  ix=bisect.bisect_right(addresses,addr)
  bound=addresses[ix] if ix<len(addresses) else sec[0]+sec[1]
  nbytes=min(bound-addr,sec[0]+sec[1]-addr,nmax)
  if nbytes<8:return []
  decoder=csthumb if bits[addr]=={1} else csarm
  start=sec[2]+addr-sec[0]
  return list(decoder.disasm(exe[start:start+nbytes],addr))
 source=decode(UPDATE)
 m={x.address:x for x in source}
 exact={
  0xdb61c:("ldr","r1, [r2, #0x58]"),
  0xdb630:("ldr","sl, [r2, #4]"),
  0xdb634:("ldr","r0, [r2, #0x90]"),
  0xdb63c:("ldr","ip, [r0, #0x34]"),
  0xdb650:("ldr","r8, [r3, r1, lsl #2]"),
  0xdb65c:("bl","#0x9c340"),
  0xdb660:("cmp","r0, #1"),
  0xdb664:("cmpne","r0, #0x12"),
  0xdb668:("mov","sl, r0"),
  0xdb66c:("bne","#0xdb730"),
  0xdb6c8:("mov","r1, sl"),
  0xdb6d8:("ldr","pc, [r3, #0x110]")
 }
 for a,(opcode,args) in exact.items():
  instruction=m.get(a)
  if not instruction or instruction.mnemonic!=opcode or instruction.op_str!=args:
   raise ValueError("native Actor::UpdateStateAttack argument-to-vtable source drift "+hex(a))
 # Actual PIC string supplied to original StateData::GetParam:
 # at 0xdb654 LDR r1,[PC,#0x120], 0xdb658 ADD r1,PC,r1.
 # 0xdb77c is literal pool DATA, not an ARM instruction; G201's
 # unbounded disassembler would render it as an arbitrary opcode.
 if not (m[0xdb654].mnemonic=="ldr" and m[0xdb654].op_str=="r1, [pc, #0x120]" and
         m[0xdb658].mnemonic=="add" and m[0xdb658].op_str=="r1, pc, r1" and
         m[0xdb65c].mnemonic=="bl" and m[0xdb65c].op_str=="#0x9c340"):
  raise ValueError("G203 original Actor StateData::GetParam PIC source drift")
 pool_vm=0xdb654+8+0x120
 source_sec=next((s for s in native["sections"] if s[3]=="__text"
             and s[0]<=pool_vm< s[0]+s[1]),None)
 if source_sec is None:raise ValueError("original state source PIC pool not mapped")
 location=source_sec[2]+pool_vm-source_sec[0]
 delta=struct.unpack_from("<i",exe,location)[0]
 original_key_vm=(0xdb658+8+delta)&0xffffffff
 def original_string(ptr):
  sec=next((s for s in native["sections"] if s[3] not in ("__bss","__common")
            and s[0]<=ptr<s[0]+s[1]),None)
  if sec is None:return None
  o=sec[2]+ptr-sec[0];b=bytearray()
  for t in range(96):
   if o+t>=len(exe):return None
   value=exe[o+t]
   if value==0:
    if not 1<=len(b)<=95:return None
    try:return b.decode("ascii")
    except UnicodeDecodeError:return None
   if value<32 or value>126:return None
   b.append(value)
  return None
 attack_param=original_string(original_key_vm)
 if attack_param is None:
  raise ValueError("Source original 2010 StateData::GetParam attack selector string unresolved")
 print("G203 ORIGINAL 2010 StateData::GetParam name source PIC",
       hex(pool_vm),"signed delta",delta,
       "key VM",hex(original_key_vm),"key",attack_param)
 result={}
 for label,where in HELPERS.items():
  s=decode(where,3000)
  if not s:raise ValueError("native source requested helper absent from text "+hex(where))
  direct=[]
  for i in s:
   if i.mnemonic not in ("bl","blx") or not i.operands or i.operands[0].type!=ARM_OP_IMM:continue
   target=i.operands[0].imm&~1
   if len(direct)<90:
    direct.append({"source_real_CALL_VM":hex(i.address),
      "original_native_callee_VM":hex(target),
      "original_CPP_target_names":sorted(byname.get(target,()))[:5]})
  result[label]={
    "real_native_method_VM":hex(where),
    "original_native_CPP_name":sorted(byname.get(where,()))[:7],
    "original_source_bounded_instruction_count":len(s),
    "real_original_direct_cpp_calls":direct,
    "source_original_first_110_opcode_metadata_no_binary":[
     {"VM":hex(i.address),"mnemonic":i.mnemonic,"args":i.op_str} for i in s[:110]],
    "returned_integer_exact_runtime_weapon_semantics_proven":False,
   }
 proof={
   "origin":"2010 original iOS owner ARM C++ Actor UpdateStateAttack selector helper source",
   "source_native_actor_update_attack_function_VM":hex(UPDATE),
   "original_native_real_direct_helper_CALL_VM":"0xdb65c",
   "original_native_attack_selector_helper_VM":"0x9c340",
   "original_native_StateData_GetParam_key_literal_VM":hex(pool_vm),
   "original_native_StateData_GetParam_key_VM":hex(original_key_vm),
   "original_native_StateData_GetParam_actual_string_key":attack_param,
   "original_real_ARM_2010_StateData_GetParam_param2_default_minus_one":True,
   "source_native_string_key_proven_from_owner_ARM_PIC":True,
   "original_real_attack_state_slot_Source_from_State_plus_4":True,
   "native_original_actor_attack_control_comparisons":[1,18],
   "source_original_helper_r0_move_to_SL_before_virtual_attack_proven":True,
   "source_original_r1_passes_SL_to_virtual_DoAttack_0x110":True,
   "original_native_cpp_method_helper_inventory":result,
   "original_2010_iOS_Aim_M_animation_exact_binding_proven":False,
   "source_original_weapon_enum_or_touch_mapping_proven":False,
   "source_2010_branch_1_vs_18_defines_attack_weapon_kind_proven":False,
   "source_runtime_Actor_receiver_currently_MainCharacter_PROVEN":False,
   "No_Vita_2010_gameplay_patch_applied":True,
   "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(proof,indent=2,ensure_ascii=False)+"\n")
 print("G202 native 2010 Actor UpdateStateAttack verified State+4 original selector -> 0x9c340 native helper r0 -> sl -> virtual attack r1")
 for key,v in result.items():
  print("G202 real original C++ helper",key,v["real_native_method_VM"],v["original_native_CPP_name"],
        "source opcode count",v["original_source_bounded_instruction_count"])
  for r in v["real_original_direct_cpp_calls"][:20]:print("G202 helper direct native CALL",key,r)
 print("G202 comparing 1 and 18 in native code proven, not enough to assign on-screen weapon/Aim_M state. No VPK.")
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--ipa",required=True,type=Path)
 a.add_argument("--out",required=True,type=Path)
 o=a.parse_args()
 run(o.ipa,o.out)
