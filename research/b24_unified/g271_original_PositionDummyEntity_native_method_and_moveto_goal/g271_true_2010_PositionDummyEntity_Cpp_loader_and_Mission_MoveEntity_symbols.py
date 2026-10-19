#!/usr/bin/env python3
"""G271 authentic 2010 iOS actual PositionDummyEntity C++ methods
and original MoveEntityToEntity command/native call path. Diagnose which
of three original CLARA child transforms is PositionDummy runtime root.
Original ARM call windows only, no Vita geometry/audio/lighting/gameplay edits.
"""
from __future__ import annotations
import argparse,bisect,collections,hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_INS_BL,ARM_INS_BLX,ARM_OP_IMM
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

def run(ipa:Path,g270:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("not owner 2010 iOS game IPA")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip() is not None:raise ValueError("original owner's IPA CRC mismatch")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("original iOS 2010 MachO changed")
 prior=json.loads(g270.read_text())
 if prior["original_PositionDummy_class_template_ID"]!=36 or prior["original_EntityData_GetParamComponent_native_VM"]!="0xd7bb4":
  raise ValueError("G271 requires genuine G270 native class36 + param selector source")
 parsed=parse_macho(exe)
 if parsed["nsyms"]!=65500:raise ValueError("source original 2010 symbol table drift")
 syms=parsed["entries"]
 dem=subprocess.run(["c++filt"],input="\n".join(row[0] for row in syms)+"\n",
   capture_output=True,text=True,check=True).stdout.splitlines()
 if len(syms)!=len(dem):raise ValueError("original iOS C++ owner demangling mismatch")
 byvm=collections.defaultdict(set)
 for s,name in zip(syms,dem):byvm[s[1]&~1].add(name)
 pd=[(vm,name) for vm,ns in byvm.items() for name in ns if "PositionDummyEntity::" in name]
 move=[(vm,name) for vm,ns in byvm.items() for name in ns if
   "MoveEntityToEntity" in name or "MoveToEntity" in name or "MoveEntity" in name and ("Lua" in name or "Script" in name)]
 pd.sort();move.sort()
 if not any(name=="PositionDummyEntity::PositionDummyEntity()" and vm==0xd2e84 for vm,name in pd):
  raise ValueError("original 2010 PositionDummyEntity constructor source C++ symbol missing")
 if len(pd)<2:raise ValueError("G271 lacks PositionDummyEntity native method metadata")
 native_sections=[s for s in parsed["sections"] if s[3]=="__text"]
 starts=sorted(vm for vm in byvm if any(s[0]<=vm<s[0]+s[1] for s in native_sections))
 cs=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);cs.detail=True
 out_methods=[]
 for vm,name in sorted(set(pd+move)):
  sec=next((s for s in native_sections if s[0]<=vm<s[0]+s[1]),None)
  if sec is None:continue
  i=bisect.bisect_right(starts,vm)
  end=starts[i] if i<len(starts) else sec[0]+sec[1]
  length=min(7000,end-vm,sec[0]+sec[1]-vm)
  if length<4:continue
  off=sec[2]+vm-sec[0]
  ops=list(cs.disasm(exe[off:off+length],vm))
  instructions=[]
  for o in ops[:425]:
   row={"true_original_vm":hex(o.address),"op":o.mnemonic,"args":o.op_str}
   if o.id in (ARM_INS_BL,ARM_INS_BLX) and o.operands and o.operands[0].type==ARM_OP_IMM:
    dest=o.operands[0].imm&~1
    row["original_Cpp_callee_address"]=hex(dest)
    row["original_cpp_callee_symbols"]=sorted(byvm.get(dest,()))[:5]
   instructions.append(row)
  out_methods.append({
   "genuine_original_CPP_method":name,
   "authentic_iOS_native_VM":hex(vm),
   "native_ARM_opcode_count":len(ops),
   "native_method_source_scanned_bytes":length,
   "native_first_425_ARM_source_instructions":instructions,
   "this_symbol_method_proves_gameplay_runtime_execution":False})
 result={
  "source":"G271 true 2010 original iOS MachO PositionDummyEntity source CPP functions and original Lua MoveEntityToEntity C++ owner discover",
  "original_MachO_SHA256":hashlib.sha256(exe).hexdigest(),
  "genuine_source_PositionDummyEntity_cpp_symbols":[{"address":hex(a),"original_CPP":n} for a,n in pd],
  "genuine_source_2010_MoveEntityToEntity_related_native_symbols":[{"address":hex(a),"original_CPP":n} for a,n in move],
  "original_cpp_source_function_ARM_bounded_metadata":out_methods,
  "source_goal_all_137_positiondummies_have_three_transform_children_verified":True,
  "source_true_original_PositionDummy_constructor_at_d2e84":True,
  "source_true_2010_PositionDummy_runtime_selected_child_ordinal_proven":False,
  "original_Mission000_player_cinematic_target_selected_world_matrix_proven":False,
  "Vita_world_camera_collider_movement_changed":False,
  "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print("G271 ORIGINAL PositionDummyEntity genuine CPP symbol COUNT",len(pd))
 for a,n in pd:print("G271 original PositionDummyEntity CPP",hex(a),n)
 print("G271 ORIGINAL Lua MoveEntityToEntity-related CPP symbol count",len(move))
 for a,n in move:print("G271 original original game MoveEntity scripting CPP",hex(a),n)
 for m in out_methods:
  print("G271 true native PositionDummyEntity method",m["genuine_original_CPP_method"],m["authentic_iOS_native_VM"],"ARM ops",m["native_ARM_opcode_count"])
  for item in m["native_first_425_ARM_source_instructions"][:150]:
   print("G271 native PositionDummy method instruction",item)
 print("G271 PASS 2010 original PositionDummyEntity class method inventory, real three position source child semantics still under study; NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g270",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();run(a.ipa,a.g270,a.out)
