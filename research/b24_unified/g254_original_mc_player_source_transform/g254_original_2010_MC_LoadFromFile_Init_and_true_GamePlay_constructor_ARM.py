#!/usr/bin/env python3
"""G254 inspect real original iOS 2010 MC creation and position source
without equating authored MC local Z=25.054 with runtime feet/spawn Z.
Bounded native ARM windows and calls from MAIN player loader, character
constructor/LoadFromFile/Init and Entity3D/PositionData.
No Vita movement, geometry, animation or VPK modified.
"""
from __future__ import annotations
import argparse,bisect,collections,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM,ARM_INS_BL,ARM_INS_BLX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
METHODS={
 0xc2e8c:"GS_GamePlay::LoadEntities()",
 0xec108:"MainCharacter::MainCharacter()",
 0xec2cc:"MainCharacter::LoadFromFile(EntityData*, StateDatabase*)",
 0xeec64:"MainCharacter::Init()",
 0x12c78:"Entity3D::LoadFromFile(EntityData*)",
 0xc8200:"PositionData::PositionData()",
 0xdbbe0:"Actor::Init()",
 0xda93c:"Actor::LoadFromFile(EntityData*, StateDatabase*)",
}
def run(ipa:Path,g253:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("not original 2010 owner IPA")
 with zipfile.ZipFile(ipa) as z:exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("wrong original MachO executable")
 parent=json.loads(g253.read_text())
 if parent["source_CPP_bootstrap_candidates_total"]<15:
  raise ValueError("requires true G253 source original MainCharacter symbols")
 macho=parse_macho(exe)
 if macho["nsyms"]!=65500:raise ValueError("original native LC_SYMTAB symbol count drift")
 src=macho["entries"]
 dem=subprocess.run(["c++filt"],input="\n".join(q[0] for q in src)+"\n",
    capture_output=True,text=True,check=True).stdout.splitlines()
 if len(src)!=len(dem):raise ValueError("real original C++ symbol index mismatch")
 byname=collections.defaultdict(set)
 for item,name in zip(src,dem):byname[item[1]&~1].add(name)
 textsec=[s for s in macho["sections"] if s[3]=="__text"]
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);arm.detail=True
 outmethods={}
 for vm,name in METHODS.items():
  if name not in byname.get(vm,()):
   raise ValueError(f"G254 original C++ method address drift {vm:#x} {name}")
  section=next((s for s in textsec if s[0]<=vm<s[0]+s[1]),None)
  if not section:raise ValueError("true method text section missing")
  starts=sorted(a for a in byname if section[0]<=a<section[0]+section[1])
  index=bisect.bisect_right(starts,vm)
  end=starts[index] if index<len(starts) else section[0]+section[1]
  length=end-vm
  if not 4<=length<=30000:raise ValueError("real original C++ method unexpectedly sized")
  off=section[2]+vm-section[0]
  ops=list(arm.disasm(exe[off:off+length],vm))
  if not ops:raise ValueError("actual native method cannot disassemble")
  segments=[]
  if vm==0xc2e8c:
   target=[o for o in ops if 0xc36b0<=o.address<=0xc3850]
  elif vm==0x12c78:
   target=ops
  elif vm==0xec2cc:
   target=ops
  else:target=ops[:260]
  for op in target:
   row={"original_VM":hex(op.address),"op":op.mnemonic,"args":op.op_str}
   if op.id in (ARM_INS_BL,ARM_INS_BLX) and op.operands and op.operands[0].type==ARM_OP_IMM:
    addr=op.operands[0].imm&~1
    row["genuine_direct_bl_target_VM"]=hex(addr)
    row["genuine_target_cpp_name"]=sorted(byname.get(addr,()))[:5]
   segments.append(row)
  calls=[]
  for op in ops:
   if op.id in (ARM_INS_BL,ARM_INS_BLX) and op.operands and op.operands[0].type==ARM_OP_IMM:
    dest=op.operands[0].imm&~1
    calls.append({"native_callsite_VM":hex(op.address),"real_cpp_callee":sorted(byname.get(dest,()))[:3],"real_callee_VM":hex(dest)})
  outmethods[hex(vm)]={
   "original_cpp":name,"real_original_native_VM":hex(vm),
   "actual_original_ARM_method_bytes":length,"source_actual_ARM_instruction_count":len(ops),
   "native_original_source_active_constructor_or_data_window":segments,
   "original_full_method_direct_call_metadata":calls,
   "actual_iOS_L1_player_spawn_runtime_trace":False,
  }
  print("G254 original 2010 CPP",name,hex(vm),"ops",len(ops),"BL count",len(calls))
  for item in calls:
   if any("Position" in nm or "Transform" in nm or "Entity" in nm or "Actor" in nm or "State" in nm for nm in item["real_cpp_callee"]):
    print("G254 native MC/Position load call",item)
 first=outmethods["0xc2e8c"]
 if not any(row["native_callsite_VM"]=="0xc36fc" and "MainCharacter::MainCharacter()" in row["real_cpp_callee"]
            for row in first["original_full_method_direct_call_metadata"]):
  raise ValueError("G254 real original game MC construction source BL 0xC36FC missing")
 report={
  "source":"G254 exact original 2010 native iOS actor creation/position data C++ methods and real ARM source",
  "original_iOS_MachO_SHA256":hashlib.sha256(exe).hexdigest(),
  "true_original_native_constructor_MainCharacter_LoadFromFile_and_Init_methods":outmethods,
  "source_direct_GamePlay_LoadEntities_BL_MainCharacter_ctor_VM":"0xc36fc",
  "original_SpawnPoint_is_separate_native_cpp_class":True,
  "original_Mission000_initial_player_position_globalXYZ_proven":False,
  "original_MC_local_entity_transform_equals_real_player_feet_world_xyz_proven":False,
  "source_native_PlayerBoot_was_executed_on_real_iPhone":False,
  "Vita_B14_ground_start_player_root_changes":False,
  "VPK":False
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 for op in first["native_original_source_active_constructor_or_data_window"]:
  print("G254 ORIGINAL LoadEntities MainCharacter branch ARM",op)
 print("G254 PASS genuine original 2010 MC construction and load methods, source World XYZ still unknown. NO VPK.")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g253",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 q=p.parse_args();run(q.ipa,q.g253,q.out)
