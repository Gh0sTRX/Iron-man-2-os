#!/usr/bin/env python3
"""G220 original 2010 Iron Man 2 iOS StateTrack::GetEvent exact BL caller
audit, derived from user's own complete 32-bit ARM Mach-O (not guessing
from G218 C11 motion stem names).

Discover:
1) Every DIRECT native ARM BL/BLX into original StateTrack::GetEvent,
2) original C++ name and bounded true source method of caller,
3) source 20-instruction call-site dataflow window,
4) original C++ methods explicitly called Event/StateTrack accessors,
5) unrelated indirect virtual consumers remain UNKNOWN.

No original IPA/game bytes in outputs, no Vita VPK and no
fabricated damage/weapon/attack event timestamp.
"""
from __future__ import annotations
import argparse,bisect,collections,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

OWNER_BYTES=248613763
GETEVENT_VM=0xA14F0
def run(ipa:Path,out:Path):
 if ipa.stat().st_size!=OWNER_BYTES:
  raise ValueError("G220 requires actual user's original 2010 iOS game IPA")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("2010 original owner IPA checksum CRC fail")
  image=z.read("Payload/IronMan2.app/IronMan2")
 if len(image)!=7480208:raise ValueError("2010 native original Mach-O wrong size")
 mach=parse_macho(image)
 dem=subprocess.run(["c++filt"],input="\n".join(r[0] for r in mach["entries"])+"\n",check=True,text=True,capture_output=True).stdout.splitlines()
 if len(dem)!=len(mach["entries"]):raise ValueError("C++ original 2010 symbol names truncated")
 names=collections.defaultdict(set);modes=collections.defaultdict(set)
 for a,n in zip(mach["entries"],dem):
  addr=a[1]&~1
  names[addr].add(n);modes[addr].add(a[1]&1)
 if "StateTrack::GetEvent(int, int)" not in names[GETEVENT_VM]:
  raise ValueError("G220 original owner native GetEvent symbol missing")
 starts=sorted(names)
 secs=[s for s in mach["sections"] if s[3]=="__text"]
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);arm.detail=True
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB);thumb.detail=True
 def callable_name(addr:int):
  idx=bisect.bisect_right(starts,addr)-1
  if idx<0:return ("UNKNOWN",None)
  base=starts[idx]
  # no crossing segment/size assumptions: bounded 0x1000 bytes closest
  if addr-base>8192:return ("UNVERIFIED_method_range",hex(base))
  return (" | ".join(sorted(names[base])[:3]),hex(base))
 callers=[]
 decoded_real=0
 text_sections=[]
 valid_text_method_sources=0
 thumb_text_functions=0
 arm_text_functions=0
 # Original owner 2010 iOS binary is mixed ARM + Thumb interworking.
 # Disassembling all __text as ARM misses REAL Thumb BL callsites and
 # may mistakenly call data instructions. Partition by SYMTAB method
 # start and original ARM/Thumb mode (symbol low bit).
 for sec in secs:
  vmsize=sec[1]
  data=image[sec[2]:sec[2]+vmsize]
  if len(data)!=vmsize:raise ValueError("source original MachO __text section bounds changed")
  text_sections.append({"source_vm_start":hex(sec[0]),"source_text_bytes":len(data)})
  funcstarts=[a for a in starts if sec[0]<=a<sec[0]+sec[1]]
  for mi,start in enumerate(funcstarts):
   if mi+1<len(funcstarts):end=funcstarts[mi+1]
   else:end=sec[0]+sec[1]
   maxlen=min(end-start,16384)
   if maxlen<4:continue
   m=modes[start]
   if m=={1}:engine=thumb;thumb_text_functions+=1
   elif m=={0}:engine=arm;arm_text_functions+=1
   else:
    # Potential same virtual address has mixed alias symbol low bit;
    # ambiguous begins are fail-closed, never decode guessed mode.
    continue
   begin=start-sec[0]
   ops=list(engine.disasm(data[begin:begin+maxlen],start))
   if not ops:continue
   valid_text_method_sources+=1
   decoded_real+=len(ops)
   for k,ins in enumerate(ops):
    if ins.mnemonic not in ("bl","blx") or not ins.operands:
     continue
    if ins.operands[0].type!=ARM_OP_IMM:
     continue
    dest=ins.operands[0].imm&~1
    if dest!=GETEVENT_VM:continue
    ctx=[{"vm":hex(i.address),"asm":i.mnemonic+" "+i.op_str}
          for i in ops[max(0,k-14):min(len(ops),k+14)]]
    callers.append({"original_source_callsite":hex(ins.address),
       "owner_cpp_method":" | ".join(sorted(names[start])[:3]),
       "nearest_symbol_method_start":hex(start),
       "original_source_owner_opcode_mode":"THUMB" if m=={1} else "ARM",
       "native_original_GetEvent_target":hex(dest),
       "original_source_window_ARM_28_instructions":ctx,
       "original_instructions_guarantee_event_is_damage_or_weapon_spawn":False})
 print("G220 REAL owner source correct split native ARM methods",arm_text_functions,
       "THUMB methods",thumb_text_functions,"decoded C++ funcs",valid_text_method_sources,
       "instruction count",decoded_real,flush=True)
 original_accessors=[
  {"vm":hex(a),"source_owner_cpp_names":sorted(ns)[:5]}
  for a,ns in sorted(names.items())
  if any("StateTrack::" in n or
    ("StateData::" in n and ("Track" in n or "Event" in n)) or
    ("State::" in n and ("Track" in n or "Event" in n)) for n in ns)
 ]
 summary=collections.Counter(c["owner_cpp_method"] for c in callers)
 for caller in callers:
  print("G220 REAL 2010 C++ native GetEvent CALLSITE",caller["original_source_callsite"],
   "C++",caller["owner_cpp_method"],"native source start",caller["nearest_symbol_method_start"])
  print("G220 OWNER NATIVE CALL 28 ARM window",json.dumps(caller["original_source_window_ARM_28_instructions"]))
 print("G220 original StateTrack/StateData/Event named symbol accessors",len(original_accessors))
 for accessor in original_accessors[:125]:
  print("G220 owner C++ source accessor",accessor["vm"],accessor["source_owner_cpp_names"])
 out.parent.mkdir(parents=True,exist_ok=True)
 report={
  "original_data":"owner real 2010 Iron Man 2 iOS 32-bit ARM native MachO source",
  "genuine_native_original_StateTrack_GetEvent_VM":hex(GETEVENT_VM),
  "original_ARM_text_sections":text_sections,
  "source_real_2010_ARM_instructions_decoded":decoded_real,
  "source_native_2010_ARM_method_count":arm_text_functions,
  "source_native_2010_THUMB_method_count":thumb_text_functions,
  "source_native_original_function_sources_decoded":valid_text_method_sources,
  "source_direct_ARM_GetEvent_BL_BLX_callsite_count":len(callers),
  "source_real_2010_direct_GetEvent_callsite_windows":callers,
  "source_real_2010_GetEvent_caller_Cpp_name_distribution":dict(summary),
  "source_original_StateTrack_Event_named_cpp_methods":original_accessors,
  "original_indirect_virtual_GetEvent_consumers_fully_analyzed":False,
  "source_real_2010_direct_callsite_zero_means_event_unused":False,
  "original_2010_event_payload_third_field_semantics_PROVEN":False,
  "original_iOS_AttackType_Event_to_WarMachine_rocket_repulsor_or_damage_PROVEN":False,
  "native_2010_Event_time_values_as_milliseconds_PROVEN":False,
  "G218_live_original_Vita_state_observer_changed":False,
  "NO_VPK":True}
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G220 PASS real native source full ARM .text GetEvent direct callsites",len(callers),
  "C++ callers",dict(summary),"no fabricated damage/hit events, no VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args();run(a.ipa,a.out)
