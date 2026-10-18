#!/usr/bin/env python3
"""G191 original 2010 iOS / Game::DoInitInLogo actual 34
SceneImpl::DummiesTableAdd(char const*) callsites and argument string names.

Recover genuine native AAPCS r0 actual source string literal producer from
the immediately preceding LDR/ADD or LDR direct-pointer instructions.
Caution: 34 observed named ADD calls in startup do NOT prove the numeric
scene dummy group keys (14,33) are equivalent to zero-based list ordinals
until DummiesTableAdd/Create semantics are separately decoded.

No owner IPA, Mach-O or asset data is exported; only pointer/string
provenance and helper source opcodes. NO VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,re,struct,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM,ARM_OP_MEM,ARM_OP_REG,ARM_REG_PC
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

OWNER_SIZE=248613763
GAME=0x97e6c
ADD=0x641b4
CREATE=0x64684
EXPECTED=34
def main(ipa:Path,out:Path):
 if ipa.stat().st_size!=OWNER_SIZE:raise ValueError("Need authentic 2010 owner original IPA")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("source original IPA failed CRC")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("2010 original MachO size mismatch")
 m=parse_macho(exe)
 dem=subprocess.run(["c++filt"],input="\n".join(x[0] for x in m["entries"])+"\n",
                      capture_output=True,text=True,check=True).stdout.splitlines()
 if len(dem)!=len(m["entries"]):raise ValueError("original owner symbol mismatch")
 symbols=collections.defaultdict(set)
 for r,name in zip(m["entries"],dem):symbols[r[1]&~1].add(name)
 assert "Game::DoInitInLogo()" in symbols[GAME]
 assert "SceneImpl::DummiesTableAdd(char const*)" in symbols[ADD]
 assert "SceneImpl::DummiesTableCreate(int)" in symbols[CREATE]
 sects=m["sections"];text=[s for s in sects if s[3]=="__text"]
 def vm(addr,length):
  sec=next((s for s in sects if s[3] not in ("__bss","__common") and
      s[0]<=addr and addr+length<=s[0]+s[1]),None)
  if sec is None:return None
  offset=sec[2]+addr-sec[0]
  if offset<0 or offset+length>len(exe):return None
  return exe[offset:offset+length]
 def word(addr):
  b=vm(addr,4)
  return struct.unpack("<I",b)[0] if b else None
 def signed(value):
  return value if value<0x80000000 else value-0x100000000
 def ascii_source(addr):
  if addr is None:return None
  chars=bytearray()
  for j in range(100):
   b=vm(addr+j,1)
   if b is None:return None
   if b==b"\0":
    if not 2<=len(chars)<=95:return None
    try:return chars.decode("ascii")
    except UnicodeDecodeError:return None
   if not 32<=b[0]<=126:return None
   chars.extend(b)
  return None
 def decode(addr,maxsize=8192):
  sec=next((s for s in text if s[0]<=addr<s[0]+s[1]),None)
  if sec is None:raise ValueError("native C++ code not in __text")
  ordered=sorted(symbols)
  index=bisect.bisect_right(ordered,addr)
  end=ordered[index] if index<len(ordered) else sec[0]+sec[1]
  size=min(maxsize,end-addr,sec[0]+sec[1]-addr)
  if size<4:raise ValueError("original C++ method body too short")
  cs=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
  cs.detail=True
  start=sec[2]+addr-sec[0]
  return list(cs.disasm(exe[start:start+size],addr))
 ins=decode(GAME)
 adds=[];starts=[]
 for i,x in enumerate(ins):
  if x.mnemonic!="bl" or not x.operands or x.operands[0].type!=ARM_OP_IMM:continue
  dst=x.operands[0].imm&~1
  if dst not in (ADD,CREATE):continue
  context=ins[max(0,i-5):i+1]
  result={"source_real_CALL_VM":hex(x.address),"source_cpp_callee":sorted(symbols[dst])[:2],
          "source_2010_precall_ARM_not_machine_bytes":[{"VM":hex(z.address),"mnemonic":z.mnemonic,"args":z.op_str} for z in context],
          "literal_arg_pointer_VM":None,"source_original_dummy_string":None,
          "native_call_register_arg0_proven_constant":False,
          "source_parameter_provenance":"not decoded"}
  if i>=2:
   ldr,add=ins[i-2],ins[i-1]
   if (ldr.mnemonic.startswith("ldr") and add.mnemonic=="add" and
       ldr.operands and ldr.operands[0].type==ARM_OP_REG and
       any(q.type==ARM_OP_MEM and q.mem.base==ARM_REG_PC and q.mem.index==0 for q in ldr.operands) and
       add.op_str=="r0, pc, "+ldr.reg_name(ldr.operands[0].reg)):
    mem=next(q for q in ldr.operands if q.type==ARM_OP_MEM)
    lit=(ldr.address+8+mem.mem.disp)&0xffffffff
    delta=word(lit)
    if delta is not None:
     target=(add.address+8+signed(delta))&0xffffffff
     source_name=ascii_source(target)
     result.update({"source_literal_VM":hex(lit),"literal_arg_pointer_VM":hex(target),
      "source_original_dummy_string":source_name,
      "native_call_register_arg0_proven_constant":source_name is not None,
      "source_parameter_provenance":"r0=PC-relative literal delta + ARM add r0,pc,r0"})
  if i>=1:
   prev=ins[i-1]
   if (prev.mnemonic in ("mov","movs") and len(prev.operands)>=2 and
       prev.operands[0].type==ARM_OP_REG and prev.operands[0].reg==capstone.arm.ARM_REG_R0 and
       prev.operands[1].type==ARM_OP_IMM):
    result.update({"native_argument_immediate_integer":prev.operands[1].imm,
      "native_call_register_arg0_proven_constant":True,
      "source_parameter_provenance":"direct ARM MOV r0 immediate preceding BL"})
  if dst==CREATE:starts.append(result)
  else:adds.append(result)
 if len(adds)!=EXPECTED:raise ValueError("G191 count of original source named DummiesTableAdd is not 34: "+str(len(adds)))
 if len(starts)!=1:raise ValueError("original native DummiesTableCreate count not 1")
 # Exact native call setup: MOV r0,#0x22 at 0x97fcc, only stores to
 # separate r3/r4 memory afterwards, then BL Create at 0x97fd8.
 init_context=starts[0]["source_2010_precall_ARM_not_machine_bytes"]
 if not any(q["VM"]=="0x97fcc" and q["mnemonic"]=="mov" and
            q["args"]=="r0, #0x22" for q in init_context):
  raise ValueError("2010 owner original Create(34) native parameter drift")
 if not any(q["VM"]=="0x97fd8" and q["mnemonic"]=="bl" and
            q["args"]=="#0x64684" for q in init_context):
  raise ValueError("2010 original Create(34) native function call missing")
 # all 34 genuine source names have constant PIC strings. A missing
 # mapped value is a QA failure, not grounds for guessing its name.
 if sum(x["source_original_dummy_string"] is not None for x in adds)!=EXPECTED:
  raise ValueError("G191 one or more of the authentic 34 static string ARGs is not decoded")
 # if missing names, retain explicit null rather than deduce guessed rig node IDs.
 observed=[]
 for index,row in enumerate(adds):
  row["source_startup_CALL_order_zero_based"]=index
  observed.append(row)
 possible14=observed[14];possible33=observed[33]
 output={
  "origin":"Owner 2010 original iOS native Game::DoInitInLogo 34 exact source register arguments",
  "native_original_startup_method_VM":hex(GAME),
  "native_original_DummiesTableCreate_VM":hex(CREATE),
  "native_original_DummiesTableAdd_VM":hex(ADD),
  "native_original_startup_Create_context":starts,
  "source_original_Add_native_call_count":len(observed),
  "native_original_DummiesTableCreate_integer_argument_proven":34,
  "source_original_names_proven_by_native_r0_literal_count":sum(x["source_original_dummy_string"] is not None for x in observed),
  "source_original_registration_order_and_strings":observed,
  "candidate_group14_startup_list_entry_not_yet_semantic_mapping":possible14["source_original_dummy_string"],
  "candidate_group33_startup_list_entry_not_yet_semantic_mapping":possible33["source_original_dummy_string"],
  "native_original_scene_registry14_name_PROVEN":False,
  "native_original_scene_registry33_name_PROVEN":False,
  "original_index_mapping_requires_DummiesTableAdd_append_insertion_semantics":True,
  "source_original_2010_IPA_assets_were_not_exported":True,
  "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n")
 print("G191 real original 2010 C++ startup DummiesTableCreate source",starts)
 for k,item in enumerate(observed):
  print("G191 ORIGINAL ORDER",k,item["source_real_CALL_VM"],item["source_original_dummy_string"],
        "ARG_SOURCE",item["source_parameter_provenance"])
 print("G191 candidates, NOT confirmed native group names",14,possible14["source_original_dummy_string"],
       33,possible33["source_original_dummy_string"])
 print("G191 no fake binding to model skin or new Vita beam/VPK")
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("--ipa",type=Path,required=True)
 parser.add_argument("--out",type=Path,required=True)
 args=parser.parse_args()
 main(args.ipa,args.out)
