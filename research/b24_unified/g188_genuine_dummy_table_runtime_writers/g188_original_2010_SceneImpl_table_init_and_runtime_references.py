#!/usr/bin/env python3
"""G188 source-original 2010 SceneImpl::s_dummiesTable runtime xrefs.

G187 source C++ global init initializes its vector-like BSS header fields
to ZERO at 0x3c0c,0x3c10,0x3c14. Establish this via signed ARM PIC and
trace SceneImpl named methods reading/loading the same actual VM 0x4edca0.
No claim that ordinal 14/33 maps to any exact bone/asset label.

All evidence from original owner's 2010 ARM Mach-O in transient GitHub CI.
No IPA, binary, or VPK committed.
"""
from __future__ import annotations
import argparse,bisect,collections,json,re,struct,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_MEM,ARM_OP_IMM,ARM_REG_PC
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
SIZE=248613763
TABLE=0x4edca0
CTOR=0x3b80

def run(ipa:Path,out:Path):
 if ipa.stat().st_size!=SIZE:raise ValueError("Not original user-provided 2010 IPA")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("owner original IPA damaged")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("2010 executable bytes changed")
 m=parse_macho(exe)
 names=subprocess.run(["c++filt"],input="\n".join(x[0] for x in m["entries"])+"\n",
  check=True,text=True,capture_output=True).stdout.splitlines()
 if len(names)!=len(m["entries"]):raise ValueError("native symbols demangling mismatch")
 symbol=collections.defaultdict(set);thumb=collections.defaultdict(set)
 for row,name in zip(m["entries"],names):
  a=row[1]&~1;symbol[a].add(name);thumb[a].add(row[1]&1)
 if "SceneImpl::s_dummiesTable" not in symbol[TABLE]:
  raise ValueError("s_dummiesTable original 2010 VM and symbol drift")
 sections=m["sections"]
 def vmread(vm,n):
  sec=next((s for s in sections if s[3] not in ("__common","__bss") and
             s[0]<=vm and vm+n<=s[0]+s[1]),None)
  if sec is None:return None
  at=sec[2]+vm-sec[0]
  if at<0 or at+n>len(exe):return None
  return exe[at:at+n]
 def value32(vm):
  b=vmread(vm,4)
  return struct.unpack("<i",b)[0] if b else None
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 th=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 for cs in (arm,th):cs.detail=True
 secs=[s for s in sections if s[3]=="__text"]
 addr=sorted(symbol)
 def decode(where,maxbytes=8192):
  sec=next((s for s in secs if s[0]<=where<s[0]+s[1]),None)
  if sec is None:return []
  idx=bisect.bisect_right(addr,where)
  nxt=addr[idx] if idx<len(addr) else sec[0]+sec[1]
  size=min(nxt-where,sec[0]+sec[1]-where,maxbytes)
  if size<4:return []
  o=sec[2]+where-sec[0]
  return list((th if thumb[where]=={1} else arm).disasm(exe[o:o+size],where))
 # Prove original global init's actual pointer = current 2010 native table.
 ins=decode(CTOR,400)
 byaddr={x.address:x for x in ins}
 verify={0x3bf4:("ldr","r3, [pc, #0x58]"),
         0x3bfc:("add","r1, pc, r3"),
         0x3c0c:("str","r5, [r1]"),
         0x3c10:("str","r5, [r1, #4]"),
         0x3c14:("str","r5, [r1, #8]"),
         0x3bcc:("mov","r5, #0")}
 for where,(op,arg) in verify.items():
  i=byaddr.get(where)
  if i is None or i.mnemonic!=op or i.op_str!=arg:
   raise ValueError("native original BSS table initializer dataflow changed "+hex(where))
 delta=value32(0x3c54)
 if delta is None or 0x3bfc+8+delta!=TABLE:
  raise ValueError("s_dummiesTable exact native 2010 PIC delta not table")
 # Inspect genuine class native methods for PC-rel table references.
 found=[]
 scanned=0
 for where,labels in sorted(symbol.items()):
  if not any(x.startswith(("SceneImpl::","SceneMgr::")) for x in labels):continue
  original=decode(where)
  if not original:continue
  scanned+=1
  refs=[]
  for k,i in enumerate(original):
   if not i.mnemonic.startswith("ldr"):continue
   mem=[x for x in i.operands if x.type==ARM_OP_MEM and x.mem.base==ARM_REG_PC]
   if len(mem)!=1:continue
   # only simple PC immediate literal; exclude [pc,rX] dynamic index.
   if mem[0].mem.index!=0:continue
   literal=(i.address+8+mem[0].mem.disp)&0xffffffff
   value=value32(literal)
   if value is None:continue
   nexti=original[k+1:k+6]
   for follow in nexti:
    if not follow.mnemonic.startswith("add"):continue
    # For the original compiler's PIC: add reg, pc, loaded_reg
    parts=[q.strip() for q in follow.op_str.split(",")]
    dst=i.reg_name(i.operands[0].reg) if i.operands and i.operands[0].type==capstone.arm.ARM_OP_REG else ""
    if len(parts)!=3 or parts[1]!="pc" or parts[2]!=dst:continue
    target=(follow.address+8+value)&0xffffffff
    if target!=TABLE:continue
    k2=next(j for j,x in enumerate(original) if x.address==follow.address)
    refs.append({
      "literal_VM":hex(literal),"native_original_LOAD_VM":hex(i.address),
      "native_original_PIC_ADD_VM":hex(follow.address),
      "actual_pcrel_resolved_target_VM":hex(target),
      "source_context_not_machine_bytes":[{
          "VM":hex(x.address),"op":x.mnemonic,"args":x.op_str}
          for x in original[max(0,k-6):min(len(original),k2+15)]]})
  if refs:
   found.append({"original_native_method_VM":hex(where),
     "cpp_name":sorted(labels)[:6],"native_actual_original_table_PIC_refs":refs})
 proof={
  "origin":"owner 2010 iOS original ARM s_dummiesTable ctor init and class method PIC references",
  "table_source_native_CPP":"SceneImpl::s_dummiesTable",
  "source_table_VM":"0x4edca0",
  "original_ctor_VM":"0x3b80",
  "original_ctor_real_table_pic_literal_VM":"0x3c54",
  "original_ctor_PIC_resolved_table_VM":hex(0x3bfc+8+delta),
  "original_ctor_table_fields_zero_initialized":True,
  "original_ctor_table_zero_fields_VM":["0x4edca0","0x4edca4","0x4edca8"],
  "source_original_SceneImpl_and_SceneMgr_methods_scanned":scanned,
  "source_actual_named_class_s_dummiesTable_pic_references":found,
  "native_original_runtime_population_method_fully_proven":False,
  "source_dynamic_dummy_register_enum14_name_proven":False,
  "source_dynamic_dummy_register_enum33_name_proven":False,
  "old_G184_G185_unbacked_raw___common_byte_data_valid":False,
  "source_DummyTable_initial_contents_from_file_proven":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+"\n")
 print("G188 PROVEN native original 2010 s_dummiesTable PIC 0x3bfc+8+",delta,
       "=",hex(TABLE),"ctor clears three words 0x3c0c..0x3c14")
 print("G188 original actual named SceneImpl/Mgr methods scanned",scanned,"PIC table xref methods",len(found))
 for r in found:
  print("G188 SOURCE CLASS xref",r["original_native_method_VM"],r["cpp_name"])
  for x in r["native_actual_original_table_PIC_refs"]:
   print("G188 REAL TABLE ARM",x["native_original_LOAD_VM"],x["native_original_PIC_ADD_VM"])
 print("G188 initialized EMPTY name table, true 14/33 scene socket names remain unproven, NO VPK")
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--ipa",type=Path,required=True)
 a.add_argument("--out",type=Path,required=True)
 d=a.parse_args()
 run(d.ipa,d.out)
