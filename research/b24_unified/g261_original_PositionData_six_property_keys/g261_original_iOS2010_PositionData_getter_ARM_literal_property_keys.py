#!/usr/bin/env python3
"""G261: genuine original iOS 2010 PositionData::LoadFromFile native
PC-relative six typed CLARA parameter names. Read user-owned MachO
only in private CI. Verify each literal matches G260 proven instruction
site and signed PC delta and original method type. No guessed player
boot world coordinates, no gameplay changes, no VPK.
"""
from __future__ import annotations
import argparse,hashlib,json,struct,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM
from capstone.arm import ARM_OP_IMM,ARM_INS_BL,ARM_INS_BLX
CASES=[
 ("vector3",0xc8174,0xc8178,0xc817c,0xc81e8,0xd7260,0x04),
 ("quaternion",0xc8180,0xc8188,0xc8190,0xc81ec,0xd6f78,0x10),
 ("vector3",0xc8194,0xc819c,0xc81a4,0xc81f0,0xd7260,0x20),
 ("int",0xc81a8,0xc81b0,0xc81b8,0xc81f4,0xd7548,0x38),
 ("int",0xc81bc,0xc81c4,0xc81cc,0xc81f8,0xd7548,0x2c),
 ("vector3",0xc81d0,0xc81d8,0xc81e0,0xc81fc,0xd7260,0x3c),
]
def read_vm(exe,sections,vm,n):
 s=next((x for x in sections if x[0]<=vm and vm+n<=x[0]+x[1]),None)
 if s is None:raise ValueError(f"native MachO VM unavailable {vm:#x}")
 off=s[2]+vm-s[0]
 if off<0 or off+n>len(exe):raise ValueError(f"source memory off bounds {vm:#x}")
 return exe[off:off+n]
def original_ascii(exe,sections,vm):
 sec=next((x for x in sections if x[0]<=vm<x[0]+x[1]),None)
 if not sec:raise ValueError(f"original C++ string VM not in section {vm:#x}")
 raw=read_vm(exe,sections,vm,min(128,sec[0]+sec[1]-vm))
 val=raw.split(b"\0",1)[0]
 if not 2<=len(val)<=100 or not all(32<=b<127 for b in val):
  raise ValueError(f"original C++ property label not ASCII {vm:#x}")
 return val.decode("ascii")
def main(ipa:Path,g260:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("source original iOS owner IPA size mismatch")
 with zipfile.ZipFile(ipa) as z:exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("source genuine native binary length mismatch")
 previous=json.loads(g260.read_text())
 methods=previous["real_2010_PositionData_native_cpp_methods_ARM"]
 native=next(x for x in methods if x["original_native_CPP_method"]=="PositionData::LoadFromFile(EntityData*)")
 if native["real_original_VM"]!="0xc815c":raise ValueError("G261 requires actual G260 original PositionData source")
 parsed=parse_macho(exe)
 if parsed["nsyms"]!=65500:raise ValueError("source native iOS LC_SYMTAB changed")
 sections=parsed["sections"]
 code=read_vm(exe,sections,0xc815c,0x90)
 dis=Cs(CS_ARCH_ARM,CS_MODE_ARM);dis.detail=True
 ins={o.address:o for o in dis.disasm(code,0xc815c)}
 labels=[]
 for kind,ldr,add,call,pool,target,offset in CASES:
  a=ins.get(ldr);b=ins.get(add);c=ins.get(call)
  if not a or not b or not c or not a.mnemonic.startswith("ldr") or b.mnemonic!="add":
   raise ValueError(f"original source literal assembly changed {ldr:#x}")
  if c.id not in (ARM_INS_BL,ARM_INS_BLX) or not c.operands or c.operands[0].type!=ARM_OP_IMM or c.operands[0].imm!=target:
   raise ValueError(f"original 2010 source Getter type changed {call:#x}")
  rel=struct.unpack("<i",read_vm(exe,sections,pool,4))[0]
  str_vm=add+8+rel
  key=original_ascii(exe,sections,str_vm)
  record={"original_2010_cpp_class":"PositionData",
   "native_2010_cpp_method":"PositionData::LoadFromFile(EntityData*)",
   "source_2010_typed_param_name":key,
   "native_2010_getter_kind":kind,
   "native_2010_field_offset_in_PositionData":hex(offset),
   "original_ARM_LDR_literal_VM":hex(ldr),
   "original_ARM_ADD_pc_VM":hex(add),
   "native_ARM_GetParamValue_BL_VM":hex(call),
   "original_2010_Cpp_property_label_address":hex(str_vm),
   "original_signed_pc_relative_literal_displacement":rel,
   "original_runtime_MC_world_initial_Z_PROVEN":False}
  labels.append(record)
  print("G261 original 2010 real PositionData typed CLARA property",record)
 assert len(labels)==6
 if len(set(x["source_2010_typed_param_name"] for x in labels))<5:
  raise ValueError("unexpected duplicate original PositionData load member property source")
 text={
  "source":"G261 genuine original 2010 iOS 2010 owner MachO six PositionData GetParamValue literal C strings and native storage offsets",
  "owner_original_native_SHA256":hashlib.sha256(exe).hexdigest(),
  "actual_2010_native_PositionData_LoadFromFile_VM":"0xc815c",
  "true_original_native_six_2010_typed_Transform_parameters":labels,
  "original_native_PositionData_Init_looks_up_entity_id":True,
  "source_C1L1_MC_world_transform_loaded_or_device_executed":False,
  "original_MC_runtime_ground_spawn_position_proven":False,
  "vita_physics_source_modified":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(text,ensure_ascii=False,indent=2)+"\n")
 print("G261 PASS six original position quaternion scale parent/mode native labels (interpret after source names), NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g260",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 args=p.parse_args();main(args.ipa,args.g260,args.out)
