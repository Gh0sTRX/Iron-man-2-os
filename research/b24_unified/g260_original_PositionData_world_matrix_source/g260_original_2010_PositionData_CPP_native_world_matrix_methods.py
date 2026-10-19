#!/usr/bin/env python3
"""G260 authentic 2010 iOS original PositionData/transform routines.
Follow G258 native GetParamComponent("Position") -> PositionData*, inspect
real Mach-O native C++ PositionData owner, getter/setter, actor world transform.
Does NOT infer actor boot coordinates from C1L1 local transform; no Vita mods.
"""
from __future__ import annotations
import argparse,bisect,collections,hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM,ARM_INS_BL,ARM_INS_BLX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
FOCUS=re.compile(r"^PositionData::|^PositionComponent::|^Position::|^Entity3D::|^MainCharacter::|^Actor::")
RANK=re.compile(r"PositionData::|PositionComponent::|GetPosition|SetPosition|GetWorld|SetWorld|GetRotation|SetRotation|GetMatrix|GetTransform|MovePosition|UpdatePosition|OnSpawn|SetParent|GetParent",re.I)
def main(ipa:Path,g258:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("original iOS 2010 owner IPA size drift")
 with zipfile.ZipFile(ipa) as z:exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("not genuine original owner MachO")
 earlier=json.loads(g258.read_text())
 named={x["component_type"]:x["original_native_C_string_argument"] for x in earlier["original_native_source_typed_components"]}
 if named!={"PositionData":"Position","ModelData":"Model"}:
  raise ValueError("G260 requires original ARM source typed property C strings")
 parsed=parse_macho(exe)
 if parsed["nsyms"]!=65500:raise ValueError("original MachO nsyms changed")
 syms=parsed["entries"]
 dem=subprocess.run(["c++filt"],input="\n".join(s[0] for s in syms)+"\n",
   capture_output=True,text=True,check=True).stdout.splitlines()
 if len(dem)!=len(syms):raise ValueError("source native C++ symbols desynchronized")
 labels=collections.defaultdict(set)
 for s,name in zip(syms,dem):labels[s[1]&~1].add(name)
 position=[{"vm":hex(vm),"true_original_CPP_name":name} for vm,vals in labels.items() for name in vals
   if FOCUS.search(name) and RANK.search(name)]
 position.sort(key=lambda x:(x["true_original_CPP_name"],x["vm"]))
 owners=[(vm,name) for vm,vals in labels.items() for name in vals if name.startswith("PositionData::")]
 owners=sorted(set(owners))
 if len(owners)<3 or not position:raise ValueError("2010 PositionData actual source methods not found")
 sections=[s for s in parsed["sections"] if s[3]=="__text"]
 starts=sorted(vm for vm in labels if any(s[0]<=vm<s[0]+s[1] for s in sections))
 cs=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);cs.detail=True
 methods=[]
 for vm,name in owners:
  sec=next((s for s in sections if s[0]<=vm<s[0]+s[1]),None)
  if not sec:continue
  i=bisect.bisect_right(starts,vm)
  end=starts[i] if i<len(starts) else sec[0]+sec[1]
  length=min(4096,end-vm,sec[0]+sec[1]-vm)
  if length<4:continue
  off=sec[2]+vm-sec[0]
  ops=list(cs.disasm(exe[off:off+length],vm))
  rows=[]
  for ins in ops:
   row={"original_VM":hex(ins.address),"opcode":ins.mnemonic,"args":ins.op_str}
   if ins.id in (ARM_INS_BL,ARM_INS_BLX) and ins.operands and ins.operands[0].type==ARM_OP_IMM:
    target=ins.operands[0].imm&~1
    row["real_native_direct_call_VM"]=hex(target)
    row["original_CPP_callee"]=sorted(labels.get(target,()))[:5]
   rows.append(row)
  methods.append({"original_native_CPP_method":name,"real_original_VM":hex(vm),
   "method_source_scan_bytes":length,"original_ARM_opcodes":rows[:420],
   "source_full_method_opcode_count":len(rows),
   "real_original_initial_player_world_transform_proven":False})
 report={
  "source":"G260 original 2010 user-owned iOS MachO true C++ PositionData and Entity3D/Actor transform owner inventory",
  "original_owner_executable_SHA256":hashlib.sha256(exe).hexdigest(),
  "authentic_original_Entity3D_GetParamComponent_2010_key":"Position",
  "authentic_native_2010_PositionData_field_owner_symbols":owners and [
     {"vm":hex(vm),"cpp":n} for vm,n in owners],
  "true_2010_position_related_Entity3D_Actor_MainCharacter_method_symbols":position,
  "real_2010_PositionData_native_cpp_methods_ARM":methods,
  "native_original_player_world_initialization_source_proven":False,
  "original_MC_C1L1_authored_transform_is_runtime_player_feet_Z_proven":False,
  "Vita_world_collision_velocity_player_mutated":False,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G260 original MachO PositionData C++ method count",len(owners))
 for row in position:print("G260 original transform method",row)
 for item in methods:
  print("G260 original PositionData native method",item["original_native_CPP_method"],item["real_original_VM"],item["source_full_method_opcode_count"])
  for op in item["original_ARM_opcodes"][:48]:print("G260 genuine original PositionData ARM",op)
 print("G260 PASS original 2010 PositionData method source inventory, no runtime actor XY/Z invented, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g258",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();main(a.ipa,a.g258,a.out)
