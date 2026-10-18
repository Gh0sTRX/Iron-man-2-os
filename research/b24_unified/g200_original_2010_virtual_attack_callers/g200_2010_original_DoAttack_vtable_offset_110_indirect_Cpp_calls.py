#!/usr/bin/env python3
"""G200 inspect original 2010 iOS MainCharacter::DoAttack virtual dispatch
via proven MainCharacter::vtable slot 68 at +0x110 (G199).

Source static fact: vtable MainCharacter @ 0x4BD85C, header +8,
DoAttack pointer @ 0x4BD974 => zero-based 68 / BYTE offset 0x110.
Scan ALL native ARM/Thumb original named method bodies (G199 selected
only ~1251) for LDR PC,[vtableReg,#0x110] or LDR reg then BLX reg,
keeping caller C++ method and REAL preceding opcode metadata.

CAUTION: identical offset in OTHER virtual classes is not a confirmed
MainCharacter call; even source "vtable style" is candidate until receiver
object points to MainCharacter. Do not invent native attack selector IDs,
touch controller, Vita engine changes or a VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_MEM,ARM_OP_REG

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
OWNER_SIZE=248613763
TARGET_VM=0xf64f8
VTABLE_VM=0x4bd85c
VTABLE_SLOT_POINTER_VM=0x4bd974
VTABLE_SLOT_INDEX=68
MEMORY_SLOT_OFFSET=0x110

def scan(ipa:Path,out:Path):
 if ipa.stat().st_size!=OWNER_SIZE:raise ValueError("exact original 2010 iOS owner IPA expected")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("original ZIP CRC invalid")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("native iOS 2010 original MachO length changed")
 native=parse_macho(exe)
 real_cpp=subprocess.run(["c++filt"],input="\n".join(t[0] for t in native["entries"])+"\n",
                         capture_output=True,text=True,check=True).stdout.splitlines()
 if len(real_cpp)!=len(native["entries"]):raise ValueError("2010 native C++ symbols changed")
 names=collections.defaultdict(set);rawmodes=collections.defaultdict(set)
 for raw,name in zip(native["entries"],real_cpp):
  a=raw[1]&~1;names[a].add(name);rawmodes[a].add(raw[1]&1)
 for addr,n in ((TARGET_VM,"MainCharacter::DoAttack(int, int)"),
                (VTABLE_VM,"vtable for MainCharacter")):
  if n not in names[addr]:raise ValueError("G199 source original vtable symbol changed "+n)
 if VTABLE_SLOT_POINTER_VM-VTABLE_VM!=8+VTABLE_SLOT_INDEX*4:
  raise ValueError("source original 2010 ABI vtable pointer index changed")
 code_sections=[s for s in native["sections"] if s[3]=="__text"]
 offsets=sorted(names)
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);arm.detail=True
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB);thumb.detail=True
 found=[];nmethods=0;n_loads=0;n_arm=0;n_thumb=0
 for start in offsets:
  section=next((sec for sec in code_sections if sec[0]<=start<sec[0]+sec[1]),None)
  if section is None:continue
  ix=bisect.bisect_right(offsets,start)
  end=offsets[ix] if ix<len(offsets) else section[0]+section[1]
  size=min(end-start,section[0]+section[1]-start,32000)
  if size<4:continue
  decoder=thumb if rawmodes[start]=={1} else arm
  pc_mode="THUMB" if decoder==thumb else "ARM"
  src=section[2]+start-section[0]
  ops=list(decoder.disasm(exe[src:src+size],start))
  if not ops:continue
  nmethods+=1
  if decoder==thumb:n_thumb+=1
  else:n_arm+=1
  for i,op in enumerate(ops):
   if not op.mnemonic.startswith(("ldr","ldm")):continue
   mems=[m for m in op.operands if m.type==ARM_OP_MEM and
         m.mem.disp==MEMORY_SLOT_OFFSET and m.mem.index==0]
   if not mems:continue
   n_loads+=1
   base=op.reg_name(mems[0].mem.base)
   dst=op.reg_name(op.operands[0].reg) if op.operands and op.operands[0].type==ARM_OP_REG else None
   prev=ops[max(0,i-18):i]
   later=ops[i+1:i+10]
   if dst=="pc":
    category="DIRECT_VIRTUAL_BRANCH_BY_LDR_PC"
    # Native ARM calling convention "MOV LR, PC ; LDR PC,[vtable,#0x110]"
    # is common for register dispatch. Merely a pattern, not proof.
    call_like=any(x.mnemonic in ("mov","movs") and x.op_str.replace(" ","")=="lr,pc"
                  for x in prev[-4:])
    closer=prev[-4:]
   else:
    invocations=[x for x in later if x.mnemonic in ("blx","bx","mov") and
      (x.op_str.strip()==dst or (x.mnemonic=="mov" and x.op_str.startswith("pc, "+str(dst))))]
    if not invocations:continue
    category="REGISTER_INDIRECT_BRANCH_AFTER_SLOT_LOAD"
    call_like=any(x.mnemonic=="blx" and x.op_str.strip()==dst for x in invocations)
    closer=prev[-4:]
   row={
    "source_original_cpp_caller_start_VM":hex(start),
    "source_native_cpp_caller_methods":sorted(names[start])[:6],
    "source_ARM_or_Thumb":pc_mode,
    "source_original_vtable_like_member_load_site_VM":hex(op.address),
    "source_original_arm_opcode":op.mnemonic,
    "source_original_arm_arguments":op.op_str,
    "source_register_holding_vtable_pointer":base,
    "source_offset_loaded_in_bytes":MEMORY_SLOT_OFFSET,
    "source_destination_register":dst,
    "source_pattern_category":category,
    "source_nearby_branch_is_call_like_pattern":call_like,
    "source_original_nearby_before":[
      {"VM":hex(x.address),"mnemonic":x.mnemonic,"args":x.op_str}
      for x in prev],
    "source_original_nearby_after":[
      {"VM":hex(x.address),"mnemonic":x.mnemonic,"args":x.op_str}
      for x in later[:8]],
    "source_real_receiver_vtable_is_MainCharacter_PROVEN":False,
    "source_direct_virtual_target_is_DoAttack_PROVEN":False,
    "source_attack_selector_r1_value_PROVEN":False,
    "source_controller_touch_input_mapping_PROVEN":False,
    "Vita_native_combat_routed":False
   }
   found.append(row)
 group=collections.Counter(x["source_pattern_category"] for x in found)
 callerclasses=collections.Counter(
   x["source_native_cpp_caller_methods"][0].split("::",1)[0]
   if x["source_native_cpp_caller_methods"] else "unknown" for x in found)
 proof={
  "origin":"G200 user-owned original iOS 2010 ARM and Thumb native method symbols, all named original code and G199 proven vtable slot",
  "original_vtable_cpp":"vtable for MainCharacter",
  "source_MainCharacter_original_vtable_symbol_vm":hex(VTABLE_VM),
  "original_DoAttack_function_VM":hex(TARGET_VM),
  "original_DoAttack_source_vtable_pointer_VM":hex(VTABLE_SLOT_POINTER_VM),
  "source_original_DoAttack_vtable_slot_zero_based":VTABLE_SLOT_INDEX,
  "source_original_DoAttack_vtable_slot_BYTE_offset":MEMORY_SLOT_OFFSET,
  "source_ALL_original_native_CPP_methods_scanned":nmethods,
  "original_ARM_methods_scanned":n_arm,
  "original_Thumb_methods_scanned":n_thumb,
  "original_vtable_offset_memory_loads_observed":n_loads,
  "source_Cpp_virtual_dispatch_candidate_patterns":found,
  "source_candidate_pattern_category_counts":dict(group),
  "source_candidate_cpp_class_counts":dict(callerclasses),
  "exact_G200_real_DoAttack_runtime_receiver_proven":False,
  "exact_G200_touch_control_to_native_attackID_mapping_proven":False,
  "original_world_Vita_renderer_or_combat_modified":False,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(proof,indent=2,ensure_ascii=False)+"\n")
 print("G200 original 2010 source all methods",nmethods,"ARM",n_arm,"Thumb",n_thumb,
       "all slot0x110 native member loads",n_loads,
       "virtual pattern candidates",len(found),"types",dict(group))
 for x in found[:110]:
  print("G200 NATIVE 2010 virtual 0x110 pattern",
       x["source_original_cpp_caller_start_VM"],
       x["source_native_cpp_caller_methods"],
       "site",x["source_original_vtable_like_member_load_site_VM"],
       x["source_original_arm_opcode"],x["source_original_arm_arguments"],
       "call-like",x["source_nearby_branch_is_call_like_pattern"])
  for ins in x["source_original_nearby_before"][-9:]:
   print("G200 GENUINE SOURCE PRE",x["source_original_vtable_like_member_load_site_VM"],ins)
 print("G200 same vtable offset in other classes is NOT PROOF of MainCharacter DoAttack invocation, no invented Vita input/VPK")
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--ipa",type=Path,required=True)
 ap.add_argument("--out",type=Path,required=True)
 args=ap.parse_args()
 scan(args.ipa,args.out)
