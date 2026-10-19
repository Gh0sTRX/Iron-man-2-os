#!/usr/bin/env python3
"""G243 study authentic 2010 iOS ClaraFile::Load(BufferStream&) native ARM
method assembly and dataflow. Uses actual owner IPA and crosschecks G242
indexed contiguous 36-byte EntityData layout. No CLARA byte redistribution.
No claim that source serialized entity order equals RAM list order until
native parse/write sequence is independently verified.
"""
from __future__ import annotations
import argparse,bisect,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM, ARM_INS_BL, ARM_INS_BLX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
VM=0xd5a94
NAME="ClaraFile::Load(BufferStream&)"
def run(ipa:Path,g242:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("original owner IPA size drift")
 with zipfile.ZipFile(ipa) as z: exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("original MachO executable source drift")
 native=parse_macho(exe)
 if native["nsyms"]!=65500:raise ValueError("source native symbol count drift")
 syms=native["entries"]
 d=subprocess.run(["c++filt"],input="\n".join(q[0] for q in syms)+"\n",
     capture_output=True,text=True,check=True).stdout.splitlines()
 if len(d)!=len(syms):raise ValueError("source C++ name index mismatch")
 labels={}
 for row,name in zip(syms,d):labels.setdefault(row[1]&~1,set()).add(name)
 if NAME not in labels.get(VM,()):
  raise ValueError("authentic 2010 ClaraFile::Load signature changed")
 prev=json.loads(g242.read_text())
 observed={e["native_method_VM"]:e for e in prev[
  "original_native_ClaraFile_exact_GetEntitiesCount_and_GetEntityData_sources"]}
 a=observed.get("0xd31b4")
 if not a or [(op["opcode"],op["arg"]) for op in a["actual_original_ARM_ops"] if op["VM"] in
    ("0xd31b8","0xd31bc","0xd31c4")]!=[
    ("lsl","ip, r1, #2"),("lsl","r2, r1, #5"),("add","r1, ip, r2")]:
  raise ValueError("G243 authentic original 36-byte EntityData stride is missing")
 sec=next((x for x in native["sections"] if x[3]=="__text" and x[0]<=VM<x[0]+x[1]),None)
 if not sec:raise ValueError("original ClaraFile::Load __text missing")
 starts=sorted(k for k in labels if sec[0]<=k<sec[0]+sec[1])
 k=bisect.bisect_right(starts,VM)
 end=starts[k] if k<len(starts) else sec[0]+sec[1]
 size=end-VM
 if not 100<=size<=35000:raise ValueError(f"original ClaraFile loader size unexpected: {size}")
 base=sec[2]+VM-sec[0]
 asm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);asm.detail=True
 ops=list(asm.disasm(exe[base:base+size],VM))
 if len(ops)<60:raise ValueError("ClaraFile native Load instruction list too small")
 direct=[]
 for o in ops:
  if o.id in (ARM_INS_BL,ARM_INS_BLX) and o.operands and o.operands[0].type==ARM_OP_IMM:
   target=o.operands[0].imm&~1
   direct.append({"authentic_CALL_VM":hex(o.address),"target_VM":hex(target),
                  "exact_original_cpp_names":sorted(labels.get(target,()))[:5]})
 def contexts(a,b):
  return [{"native_VM":hex(o.address),"mnemonic":o.mnemonic,"args":o.op_str}
          for o in ops if a<=o.address<b]
 windows=[]
 # This bounded source is more useful than inventing a typed serialization ABI.
 lo=VM
 for k in range(5):
  hi=min(lo+800,end)
  if lo>=end:break
  windows.append({"source_region_VM_start":hex(lo),"source_region_VM_end":hex(hi),
   "source_original_ARM_opcode_rows":contexts(lo,hi),
   "real_runtime_input_record_iteration_order_confirmed":False})
  lo=hi
 load_ctors=[x for x in direct if any(
      "EntityData" in z or "ClaraFile" in z or "BufferStream" in z for z in x["exact_original_cpp_names"])]
 src={
   "origin":"G243 genuine unmodified 2010 user iOS Iron Man 2 ClaraFile::Load original 65500 symbol MachO source",
   "original_owner_MachO_SHA256":hashlib.sha256(exe).hexdigest(),
   "original_native_method_cpp":NAME,"native_original_method_VM":hex(VM),
   "original_method_native_ARM_instruction_count":len(ops),
   "original_method_byte_size":size,
   "native_original_Loader_first_five_bounded_opcode_windows":windows,
   "authentic_original_method_direct_CALLs":[*direct],
   "source_Clara_EntityData_BufferStream_direct_CALL_candidates":load_ctors,
   "original_native_GetEntityData_stride_bytes":36,
   "original_native_Clara_loader_RAM_EntityData_write_sequence_PROVEN":False,
   "original_native_Clara_Ram_order_equals_C1L1_disk_order_PROVEN":False,
   "original_WM_missile_or_Attack_type0_WeaponDB_index_named_PROVEN":False,
   "original_Vita_gameplay_modified":False,
   "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(src,indent=2,ensure_ascii=False)+"\n")
 print("G243 original ClaraFile Load",size,"bytes",len(ops),"ARM instructions")
 for c in load_ctors:
  print("G243 TRUE original C++ entity stream METHOD CALL",c)
 for win in windows:
  print("G243 TRUE original ARM WINDOW",win["source_region_VM_start"],"length",len(win["source_original_ARM_opcode_rows"]))
  for o in win["source_original_ARM_opcode_rows"][:135]:
   print("G243 original ARM",o)
 print("G243 original source only ClaraFile loader source verified, actual level1 runtime order still unproven NO VPK")
 return src
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--g242",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args();run(a.ipa,a.g242,a.out)
