#!/usr/bin/env python3
"""G198 source forensic: authentic 2010 iOS MainCharacter::DoAttack(int,int)
callers, r1 attack selector provenance, ARM/Thumb direct/tail sources,
and file-backed data/function-pointer references.

Native DoAttack switch 0..25 source-proven G196/197. This scan can
establish *which callers and which immediates* reach its input; it MUST
NOT extrapolate a touch button, active weapon, Aim_M or Vita event when
source call input remains dynamic / indirect.

ZIP and original ARM Mach-O stay in isolated runner. Source metadata
only, no user original machine bytes/images licensed assets, no VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,re,struct,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM,ARM_OP_MEM,ARM_OP_REG

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

DOATTACK_VM=0xf64f8
DOATTACK_NAME="MainCharacter::DoAttack(int, int)"
ORIGINAL_IPA_LEN=248613763
EXE_LEN=7480208
MAX_BYTES_PER_METHOD=24000
SOURCE_OPCODE_WINDOW=50

def is_conditional(mn:str)->bool:
 return mn.endswith(("eq","ne","lt","gt","le","ge","hi","ls","cs","cc","mi","pl","vs","vc"))

def summarize_input_r1(ops):
 """Bounded local straight-line evidence, NOT symbolic path execution.

 The true r1 passing register for 2010 ARM ABI can be overwritten by a
 call or taken from an unresolved memory load. If local sequence crosses a
 call, branch or conditional write, fail closed rather than guess.
 """
 if not ops:return {"kind":"unresolved","reason":"no preceding source opcode"}
 for op in reversed(ops[-25:]):
  m=op.mnemonic.lower().split(".")[0]
  if m in ("bl","blx"):
   return {"kind":"unresolved","reason":"earlier direct/indirect call may clobber r1",
           "barrier_vm":hex(op.address)}
  if m in ("b","bx") or (m.startswith("b") and m not in ("bic","bfi","bfx","bfc")):
   return {"kind":"unresolved","reason":"nearby control-flow branch crosses static input scan",
           "barrier_vm":hex(op.address)}
  if not op.operands or op.operands[0].type!=ARM_OP_REG:
   continue
  reg=op.reg_name(op.operands[0].reg)
  if reg!="r1":continue
  if is_conditional(m):
   return {"kind":"unresolved","reason":"conditional r1 producer: runtime predicate not traced",
           "source_vm":hex(op.address),"opcode":op.mnemonic,"args":op.op_str}
  if m in ("mov","movs") and len(op.operands)>=2 and op.operands[1].type==ARM_OP_IMM:
   k=int(op.operands[1].imm)
   return {"kind":"source_local_direct_immediate","value":k,
           "source_vm":hex(op.address),"source_opcode":op.mnemonic}
  return {"kind":"dynamic_register_or_memory_input",
          "source_vm":hex(op.address),"source_opcode":op.mnemonic,
          "source_args":op.op_str}
 return {"kind":"unresolved","reason":"no straight-line source r1 definition in bounded local window"}

def analyze(ipa:Path,out:Path):
 if ipa.stat().st_size!=ORIGINAL_IPA_LEN:raise ValueError("original 2010 owner IPA size mismatch")
 with zipfile.ZipFile(ipa) as archive:
  if archive.testzip() is not None:raise ValueError("2010 iOS original owner IPA CRC failed")
  exe=archive.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=EXE_LEN:raise ValueError("original 2010 Mach-O changed")
 macho=parse_macho(exe)
 src_names=subprocess.run(["c++filt"],input="\n".join(e[0] for e in macho["entries"])+"\n",
   capture_output=True,text=True,check=True).stdout.splitlines()
 if len(src_names)!=len(macho["entries"]):raise ValueError("source symbol table demangle mismatch")
 byaddr=collections.defaultdict(set)
 modes=collections.defaultdict(set)
 for rec,src_name in zip(macho["entries"],src_names):
  ea=rec[1]&~1
  byaddr[ea].add(src_name)
  modes[ea].add(rec[1]&1)
 if DOATTACK_NAME not in byaddr[DOATTACK_VM]:raise ValueError("original native DoAttack symbol not source grounded")
 textsecs=[s for s in macho["sections"] if s[3]=="__text"]
 sorted_addrs=sorted(byaddr)
 ARM=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 THUMB=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 for decoder in (ARM,THUMB):decoder.detail=True
 source_direct=[]
 source_tail=[]
 total_methods=0
 total_thumb=0
 total_arm=0
 indirect_calls=0
 for addr in sorted_addrs:
  sec=next((s for s in textsecs if s[0]<=addr<s[0]+s[1]),None)
  if sec is None:continue
  ix=bisect.bisect_right(sorted_addrs,addr)
  limit=sorted_addrs[ix] if ix<len(sorted_addrs) else sec[0]+sec[1]
  n=min(limit-addr,sec[0]+sec[1]-addr,MAX_BYTES_PER_METHOD)
  if n<4:continue
  off=sec[2]+addr-sec[0]
  mode_thumb=modes[addr]=={1}
  decoder=THUMB if mode_thumb else ARM
  ins=list(decoder.disasm(exe[off:off+n],addr))
  if not ins:continue
  total_methods+=1
  if mode_thumb:total_thumb+=1
  else:total_arm+=1
  for j,op in enumerate(ins):
   m=op.mnemonic.lower().split(".")[0]
   if m in ("bl","blx") and (not op.operands or op.operands[0].type!=ARM_OP_IMM):
    indirect_calls+=1
   if m not in ("bl","blx","b","beq","bne","bgt","blt","bge","ble",
                "bhi","bls","bcs","bcc","bmi","bpl","bvs","bvc"):
    continue
   if not op.operands or op.operands[0].type!=ARM_OP_IMM:continue
   target=op.operands[0].imm&~1
   if target!=DOATTACK_VM:continue
   prev=ins[max(0,j-SOURCE_OPCODE_WINDOW):j]
   row={
    "source_original_call_VM":hex(op.address),
    "source_original_caller_function_VM":hex(addr),
    "native_source_cpp_caller_names":sorted(byaddr[addr])[:7],
    "source_machine_mode":"THUMB" if mode_thumb else "ARM",
    "source_native_opcode":op.mnemonic,
    "source_original_direct_target_VM":hex(target),
    "native_original_PreCall_50_instructions_no_machine_bytes":[
     {"vm":hex(i.address),"opcode":i.mnemonic,"args":i.op_str} for i in prev],
    "source_local_r1_attack_selector_provenance":summarize_input_r1(prev),
    "touch_controller_mapping_PROVEN":False,
    "original_native_DoAttack_second_integer_r2_semantics_PROVEN":False,
    "source_runtime_callsite_reachable_PROVEN":False,
   }
   if m in ("bl","blx"):source_direct.append(row)
   else:source_tail.append(row)
 # Mach-O LC_SEGMENT / section_32 flag low 8 bits = type.
 # S_ZEROFILL is NOT file-backed: never repeat G184's incorrect read.
 pos=28
 magic,cpu,subcpu,ftype,ncmds,sizecmd,flags=struct.unpack_from("<IiiIIII",exe,0)
 native_pointers=[]
 initialized_sections=0
 for _ in range(ncmds):
  cmd,size=struct.unpack_from("<II",exe,pos)
  if cmd==1:
   nsects=struct.unpack_from("<I",exe,pos+48)[0]
   for si in range(nsects):
    secp=pos+56+si*68
    name=exe[secp:secp+16].split(b"\0",1)[0].decode("latin1")
    segname=exe[secp+16:secp+32].split(b"\0",1)[0].decode("latin1")
    vm,size_bytes,offset=struct.unpack_from("<III",exe,secp+32)
    f=struct.unpack_from("<I",exe,secp+56)[0]
    if f&255==1 or name=="__text":continue
    if offset+size_bytes>len(exe):continue
    initialized_sections+=1
    for delta in range(0,size_bytes-3,4):
     ptr=struct.unpack_from("<I",exe,offset+delta)[0]
     if ptr&~1!=DOATTACK_VM:continue
     native_pointers.append({
       "source_VM":hex(vm+delta),"section":name,"segment":segname,
       "native_2010_pointer_target_VM":hex(DOATTACK_VM),
       "original_thumb_state_bit":bool(ptr&1),
       "source_original_static_pointer_IS_FILE_BACKED":True,
       "runtime_indirect_dispatch_through_this_pointer_PROVEN":False
     })
  pos+=size
 totals=collections.Counter(x["source_local_r1_attack_selector_provenance"]["kind"] for x in source_direct)
 # One static callsite / enum argument != execution or attack mode mapping.
 report={
  "origin":"Original owner iOS Iron Man 2 2010 32-bit ARM Mach-O native source symbols and file-backed LC_SEGMENT data",
  "target_original_CPP_method":DOATTACK_NAME,
  "target_native_VM":hex(DOATTACK_VM),
  "source_named_text_methods_decoded":total_methods,
  "original_ARM_functions_decoded":total_arm,
  "original_Thumb_functions_decoded":total_thumb,
  "source_native_indirect_BLX_register_calls_total":indirect_calls,
  "source_original_direct_BL_BLX_to_DoAttack_count":len(source_direct),
  "source_original_branch_or_tail_target_DoAttack_count":len(source_tail),
  "source_original_direct_calls":[*source_direct],
  "source_original_branch_or_tail_candidates":[*source_tail],
  "source_local_r1_argument_kind_histogram":dict(totals),
  "source_macho_file_backed_nonzerofill_sections_scanned":initialized_sections,
  "source_initialized_DoAttack_function_pointer_candidates":native_pointers,
  "original_attack_switch_26_values_0_to_25_PROVEN":True,
  "source_2010_cpp_DoAttack_attackID_to_touch_control_or_animation_PROVEN":False,
  "source_virtual_indirect_calls_other_than_absolute_target_resolved":False,
  "source_original_runtime_used_this_callsite_PROVEN":False,
  "original_2010_owner_IPA_or_executable_exported":False,
  "no_source_attack_name_to_Vita_weapon_bindings_inferred":True,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G198 2010 original Native DoAttack callers target",hex(DOATTACK_VM),
       "source methods",total_methods,"ARM",total_arm,"THUMB",total_thumb)
 print("G198 total direct BL/BLX",len(source_direct),"possible tail",len(source_tail),
       "initialized pointer candidates",len(native_pointers))
 for x in source_direct:
  print("G198 ORIGINAL caller",x["source_original_caller_function_VM"],
        x["native_source_cpp_caller_names"],"CALL",x["source_original_call_VM"],
        "argument",x["source_local_r1_attack_selector_provenance"])
  for y in x["native_original_PreCall_50_instructions_no_machine_bytes"][-15:]:
   print("G198 ACTUAL PRECALL",x["source_original_call_VM"],y)
 for x in source_tail:print("G198 possible tail original",x["source_original_call_VM"],
       x["native_source_cpp_caller_names"])
 for x in native_pointers[:70]:print("G198 initialized function pointer",x)
 print("G198 original iOS controller mapping/weapon animation not inferred from call alone; no Vita code/VPK")
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("--ipa",type=Path,required=True)
 parser.add_argument("--out",type=Path,required=True)
 args=parser.parse_args()
 analyze(args.ipa,args.out)
