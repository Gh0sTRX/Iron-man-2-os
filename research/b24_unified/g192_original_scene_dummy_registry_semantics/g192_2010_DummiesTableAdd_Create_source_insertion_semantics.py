#!/usr/bin/env python3
"""G192 recover genuine 2010 iOS SceneImpl::DummiesTableCreate and
DummiesTableAdd method implementation and compare to Game::DoInitInLogo's
34 original argument strings (G191). Detect native index/insertion logic.

Never equate original 0-based startup sequence with internal scene lookup
key until original native append semantics/field offsets are proven.
No Vita emitter/weapon behavior or VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_MEM,ARM_OP_IMM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
IPA_SIZE=248613763
TARGETS={
 "DummiesTableAdd":(0x641b4,"SceneImpl::DummiesTableAdd(char const*)"),
 "DummiesTableCreate":(0x64684,"SceneImpl::DummiesTableCreate(int)"),
 "SceneImpl_GetDummy":(0x61724,"SceneImpl::GetDummy(int, unsigned int)")
}
def main(ipa:Path,g191:Path,out:Path):
 if ipa.stat().st_size!=IPA_SIZE:raise ValueError("owner original 2010 IPA size required")
 evidence=json.loads(g191.read_text())
 names=evidence["source_original_registration_order_and_strings"]
 if len(names)!=34 or not all(n["source_original_dummy_string"] for n in names):
  raise ValueError("G191 verified original 34 input names required")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("2010 original IPA broken")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 native=parse_macho(exe)
 dem=subprocess.run(["c++filt"],input="\n".join(x[0] for x in native["entries"])+"\n",text=True,capture_output=True,check=True).stdout.splitlines()
 if len(dem)!=len(native["entries"]):raise ValueError("wrong original symbols")
 namesByVM=collections.defaultdict(set)
 for rec,n in zip(native["entries"],dem):namesByVM[rec[1]&~1].add(n)
 addrlist=sorted(namesByVM)
 sec=[s for s in native["sections"] if s[3]=="__text"]
 cs=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);cs.detail=True
 methods={}
 for label,(addr,symbol) in TARGETS.items():
  if symbol not in namesByVM[addr]:raise ValueError("native original 2010 method name mismatch "+label)
  seg=next((s for s in sec if s[0]<=addr<s[0]+s[1]),None)
  if seg is None:raise ValueError("not original native __text "+label)
  j=bisect.bisect_right(addrlist,addr)
  stop=addrlist[j] if j<len(addrlist) else seg[0]+seg[1]
  length=min(stop-addr,seg[0]+seg[1]-addr,8000)
  if length<20:raise ValueError("original method truncated "+label)
  start=seg[2]+addr-seg[0]
  instructions=list(cs.disasm(exe[start:start+length],addr))
  if len(instructions)<5:raise ValueError("could not decode original "+label)
  code=[{"vm":hex(x.address),"mnemonic":x.mnemonic,"args":x.op_str} for x in instructions]
  calls=[];loads=[];stores=[];branches=[]
  for x in instructions:
   if x.mnemonic in ("bl","blx") and x.operands and x.operands[0].type==ARM_OP_IMM:
    target=x.operands[0].imm&~1
    calls.append({"vm":hex(x.address),"targetVM":hex(target),"real_CPP_symbol":sorted(namesByVM.get(target,()))[:4]})
   if x.mnemonic.startswith(("ldr","str","ldm","stm")):
    (loads if x.mnemonic.startswith(("ldr","ldm")) else stores).append(
      {"vm":hex(x.address),"op":x.mnemonic,"args":x.op_str})
   if x.mnemonic.startswith("b") and x.mnemonic not in ("bl","blx"):
    branches.append({"vm":hex(x.address),"op":x.mnemonic,"args":x.op_str})
  methods[label]={
    "method_VM":hex(addr),"method_CPP":symbol,
    "source_original_ARM_instructions":code,
    "native_real_C++_calls":calls,
    "native_loads":loads,"native_stores":stores,
    "native_control_branches":branches,
    "source_original_instruction_count":len(code),
    "source_real_2010_member_index_append_semantics_PROVEN":False
  }
 proof={
   "source":"original 2010 iOS owner ARM C++ methods and original verified G191 34 static names",
   "native_real_methods":methods,
   "original_startup_table_size_argument":34,
   "original_true_startup_34_source_names":[e["source_original_dummy_string"] for e in names],
   "authored_startup_entry14":"Dummy_Chest",
   "authored_startup_entry33":"Dummy_Foot_L",
   "original_scene_GetDummy_registry14_actual_name_PROVEN":False,
   "original_scene_GetDummy_registry33_actual_name_PROVEN":False,
   "native_registration_append_source_needs_full_controlflow_proof":True,
   "native_methods_executed_in_touchHLE_real_story_scene_proven":False,
   "no_Vita_emitter_or_weapon_changes":True,
   "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+"\n")
 print("G192 ORIGINAL native 2010 C++ original Create/Add/GetDummy register semantics")
 for key,r in methods.items():
  print("G192 original "+key,r["method_VM"],"total",r["source_original_instruction_count"],
        "stores",len(r["native_stores"]),"calls",len(r["native_real_C++_calls"]))
  for x in r["source_original_ARM_instructions"][:310]:
   print("G192 ARM",key,x["vm"],x["mnemonic"],x["args"])
 for idx,n in enumerate(proof["original_true_startup_34_source_names"]):
  print("G192 source startup order",idx,n)
 print("G192 14/33 actual world dummy name semantics NOT finalized until C++ index proof. NO VPK.")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g191",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 args=p.parse_args()
 main(args.ipa,args.g191,args.out)
