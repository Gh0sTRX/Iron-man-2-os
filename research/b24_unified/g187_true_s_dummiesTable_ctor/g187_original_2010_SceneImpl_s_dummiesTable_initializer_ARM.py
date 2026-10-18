#!/usr/bin/env python3
"""G187 actual original 2010 SceneImpl::s_dummiesTable static initializer.

G186: 'global constructors keyed to SceneImpl::s_dummiesTable' @ 0x3c60
ARM b #0x3b80. This code is the proper initializer source; data symbol
0x4edca0 is in S_ZEROFILL __common (NOT file-backed). Recover exact
native method/opcodes, PC-relative initialized literals and called helpers.
No assumptions that source name-pattern ordinal equals GetDummy(14/33).
No source IPA or machine byte export, no Vita code/VPK.
"""
from __future__ import annotations
import argparse,collections,json,struct,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM, ARM_OP_MEM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

SIZE=248613763
CTOR_VM=0x3c60
INIT_VM=0x3b80
TABLE_VM=0x4edca0
def main(ipa:Path,out:Path):
 if ipa.stat().st_size!=SIZE:raise ValueError("2010 original user owner IPA expected")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("owner original IPA damaged")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("original ARM MachO length mismatch")
 base=parse_macho(exe)
 dem=subprocess.run(["c++filt"],input="\n".join(x[0] for x in base["entries"])+"\n",
   capture_output=True,text=True,check=True).stdout.splitlines()
 if len(dem)!=len(base["entries"]):raise ValueError("wrong native C++ demangler")
 syms=collections.defaultdict(set);raw=collections.defaultdict(set)
 for row,label in zip(base["entries"],dem):
  addr=row[1]&~1
  syms[addr].add(label);raw[addr].add(row[1]&1)
 if "global constructors keyed to SceneImpl::s_dummiesTable" not in syms[CTOR_VM]:
  raise ValueError("original dummy table constructor symbol missing")
 if "SceneImpl::s_dummiesTable" not in syms[TABLE_VM]:
  raise ValueError("original dummy table global address/name drift")
 sec=next((s for s in base["sections"] if s[3]=="__text" and s[0]<=INIT_VM and INIT_VM+0xe8<=s[0]+s[1]),None)
 if not sec:raise ValueError("initializer not in source text section")
 off=sec[2]+INIT_VM-sec[0]
 decoder=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);decoder.detail=True
 allins=list(decoder.disasm(exe[off:off+0xe8],INIT_VM))
 if len(allins)<25:raise ValueError("g187 missing initializer instructions")
 if not any(x.address==CTOR_VM and x.mnemonic=="mov" for x in allins):
  raise ValueError("initialization symbol not inside original method range")
 def vmread(vm,n):
  section=next((s for s in base["sections"] if s[0]<=vm and vm+n<=s[0]+s[1]
       and s[3] not in ("__common","__bss")),None)
  if section is None:return None
  ofs=section[2]+vm-section[0]
  if ofs<0 or ofs+n>len(exe):return None
  return exe[ofs:ofs+n]
 def u32(vm):
  b=vmread(vm,4)
  return struct.unpack("<I",b)[0] if b else None
 def cstr(vm):
  if not isinstance(vm,int):return None
  b=bytearray()
  for i in range(140):
   c=vmread(vm+i,1)
   if c is None:return None
   if c==b"\0":
    try:s=b.decode("ascii")
    except UnicodeDecodeError:return None
    return s if 1<len(s)<140 else None
   if not 32<=c[0]<127:return None
   b.append(c[0])
  return None
 calls=[];branch=[];literal=[];rows=[]
 for op in allins:
  rec={"VM":hex(op.address),"mnemonic":op.mnemonic,"args":op.op_str}
  rows.append(rec)
  if op.mnemonic in ("bl","blx") and op.operands and op.operands[0].type==ARM_OP_IMM:
   addr=op.operands[0].imm&~1
   calls.append({**rec,"target_VM":hex(addr),"original_native_symbol":sorted(syms.get(addr,()))[:6]})
  if op.mnemonic in ("b","beq","bne","bgt","blt","bge","ble") and op.operands and op.operands[-1].type==ARM_OP_IMM:
   branch.append({**rec,"target_VM":hex(op.operands[-1].imm&~1)})
  if op.mnemonic.startswith("ldr") and op.operands and any(p.type==ARM_OP_MEM and p.mem.base==capstone.arm.ARM_REG_PC for p in op.operands):
   pc_mem=[p for p in op.operands if p.type==ARM_OP_MEM and p.mem.base==capstone.arm.ARM_REG_PC]
   if len(pc_mem)!=1:continue
   ea=op.address+8+pc_mem[0].mem.disp
   value=u32(ea)
   literal.append({**rec,"original_literal_VM":hex(ea),
                   "raw_original_initializer_literal_uint32":value,
                   "raw_pointer_is_valid_mapped_initialized_string":cstr(value) if value is not None else None,
                   "string_from_indirect_runtime_PIC_proven":False})
 report={
  "origin":"User-owned real 2010 iOS ARM MachO C++ native global constructor",
  "source_original_ctor_symbol_VM":hex(CTOR_VM),
  "source_original_ctor_branch_target_VM":hex(INIT_VM),
  "original_dummy_table_symbol_VM":hex(TABLE_VM),
  "native_ctor_and_init_ARM_source_instruction_rows_no_binary":rows,
  "source_actual_initializer_direct_calls":calls,
  "source_native_initializer_branch_targets":branch,
  "source_native_initializer_literal_loads":literal,
  "original_2010_dynamic_scene_dummy_group_key_to_name14_PROVEN":False,
  "original_2010_dynamic_scene_dummy_group_key_to_name33_PROVEN":False,
  "original_2010_data_symbol_is_macho_zerofill":True,
  "string_literal_list_order_equals_runtime_scene_bucket_index_proven":False,
  "NO_VITA_GAMEPLAY_OR_HUD_CHANGED":True,"NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G187 original 2010 SceneImpl::s_dummiesTable constructor",hex(CTOR_VM),"->",hex(INIT_VM),
       "ins",len(rows),"calls",len(calls),"literal loads",len(literal))
 for x in rows:print("G187 NATIVE INIT ARM",x)
 for x in literal:print("G187 ORIGINAL PIC LITERAL",x)
 for x in calls:print("G187 SOURCE INIT CALL",x)
 print("G187 actual source 14/33 exact dummy names not proven yet, no Vita VPK")
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--ipa",required=True,type=Path)
 a.add_argument("--out",required=True,type=Path)
 t=a.parse_args()
 main(t.ipa,t.out)
