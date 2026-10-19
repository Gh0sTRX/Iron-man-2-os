#!/usr/bin/env python3
"""G242 audit genuine ORIGINAL 2010 ClaraFile count and indexed EntityData
native C++ methods; compare source dataflow used by G241 LoadEntities.
Inspect original native decoded method opcodes, NEVER assert C1L1 file
order equals runtime array order without ClaraFile parser construction.
"""
from __future__ import annotations
import argparse,bisect,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
EXPECTED={
 0xd31a4:"ClaraFile::GetEntitiesCount()",
 0xd31b4:"ClaraFile::GetEntityData(int)",
}
def run(ipa:Path,g241:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("original owner source mismatch")
 with zipfile.ZipFile(ipa) as z:exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("original MachO size drift")
 native=parse_macho(exe)
 names=subprocess.run(["c++filt"],input="\n".join(x[0] for x in native["entries"])+"\n",
     text=True,capture_output=True,check=True).stdout.splitlines()
 if len(names)!=len(native["entries"]) or native["nsyms"]!=65500:
  raise ValueError("original symbol table source mismatch")
 syms={}
 for entry,name in zip(native["entries"],names):
  syms.setdefault(entry[1]&~1,set()).add(name)
 src=json.loads(g241.read_text())
 if src.get("real_native_original_iterator_GetEntitiesCount_VM")!="0xc2ea8" or src.get(
     "real_native_original_iterator_GetEntityData_index_SL_VM")!="0xc2ec4":
  raise ValueError("G242 needs G241 actual native call chain and provenance")
 methods=[]
 for vm,expected in EXPECTED.items():
  if expected not in syms.get(vm,()):
   raise ValueError(f"G242 missing real native ClaraFile C++ method {vm:#x}")
  section=next((s for s in native["sections"] if s[3]=="__text" and s[0]<=vm<s[0]+s[1]),None)
  if section is None:raise ValueError("native section missing for method")
  stops=sorted(x for x in syms if vm<x<section[0]+section[1])
  stop=stops[0] if stops else section[0]+section[1]
  length=stop-vm
  if not 4<=length<=2000:raise ValueError("unexpected genuine original ClaraFile method size")
  base=section[2]+vm-section[0]
  cs=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
  ops=list(cs.disasm(exe[base:base+length],vm))
  if not ops or ops[0].address!=vm:
   raise ValueError("native original 2010 ClaraFile ARM decode failure")
  methods.append({
    "real_original_2010_Cpp_method":expected,"native_method_VM":hex(vm),
    "native_text_byte_size":length,
    "actual_original_ARM_ops":[{"VM":hex(o.address),"opcode":o.mnemonic,"arg":o.op_str} for o in ops],
    "native_method_code_not_a_runtime_CLARA_list_order_observation":True})
 others=sorted([{"true_Cpp_method":name,"original_native_VM":hex(e[1]&~1),
              "ISA":"Thumb" if e[1]&1 else "ARM"}
             for e,name in zip(native["entries"],names) if name.startswith("ClaraFile::")],
             key=lambda x:(x["original_native_VM"],x["true_Cpp_method"]))
 result={
   "source":"G242 original user-supplied 2010 iOS Iron Man 2 MachO exact ClaraFile source symbols and ARM code",
   "owner_original_MachO_SHA256":hashlib.sha256(exe).hexdigest(),
   "original_native_ClaraFile_exact_GetEntitiesCount_and_GetEntityData_sources":methods,
   "authentic_original_other_ClaraFile_symbols_for_next_loader_order_probe":others,
   "real_G241_native_clara_count_then_index_selector_connected":True,
   "actual_C1L1_file_order_matches_memory_EntityData_index_PROVEN":False,
   "original_WeaponDB_0_1_4_named_Attack_objects_PROVEN":False,
   "original_2010_iOS_live_runtime_clara_loaded_PROVEN":False,
   "Vita_gameplay_or_physics_modified":False,
   "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
 for q in methods:
  print("G242 GENUINE ClaraFile",q["native_method_VM"],q["real_original_2010_Cpp_method"])
  for op in q["actual_original_ARM_ops"]:
   print("G242 ORIGINAL ARM",op)
 print("G242 authentic ClaraFile C++ symbols",len(others))
 for sym in others[:70]:print("G242 REAL CLARA METHOD",sym)
 print("G242 PASS original native ClaraFile count/index method source; NO fabricated WeaponDB array order")
 return result
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--g241",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 q=p.parse_args()
 run(q.ipa,q.g241,q.out)
