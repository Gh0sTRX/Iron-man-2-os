#!/usr/bin/env python3
"""G240 source-authenticated 2010 GS_GamePlay::LoadEntities native branch
metadata around original exact AddNewWeapon* calls. Original method caller
proved by G238. Labels via original owner Mach-O. No assumptions about
serialized C1L1 order, global attack indices or weapon effects.
"""
from __future__ import annotations
import argparse,bisect,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM, ARM_INS_BL, ARM_INS_BLX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
MACHO="Payload/IronMan2.app/IronMan2"
OWNER_BYTES=248613763
METHOD_VM=0xc2e8c
METHOD_NAME="GS_GamePlay::LoadEntities()"
CALLS={
 0xc365c:(0xabbd4,"WeaponDB::AddNewWeaponAccessory(EntityData*)"),
 0xc3678:(0xabf14,"WeaponDB::AddNewWeapon(EntityData*)"),
 0xc3694:(0xab894,"WeaponDB::AddNewAttackEntity(EntityData*)"),
}
def run(ipa:Path,g238:Path,out:Path):
 if ipa.stat().st_size!=OWNER_BYTES:raise ValueError("original owner IPA size changed")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip() is not None:raise ValueError("original owner IPA CRC failure")
  exe=z.read(MACHO)
 if len(exe)!=7480208:raise ValueError("original 2010 ARM executable size changed")
 orig=parse_macho(exe)
 syms=orig["entries"]
 dem=subprocess.run(["c++filt"],input="\n".join(r[0] for r in syms)+"\n",
  capture_output=True,text=True,check=True).stdout.splitlines()
 if len(syms)!=len(dem) or orig["nsyms"]!=65500:
  raise ValueError("original owner native symbol table drift")
 names={}
 for row,name in zip(syms,dem):
  names.setdefault(row[1]&~1,set()).add(name)
 if METHOD_NAME not in names.get(METHOD_VM,()):
  raise ValueError("G240 original native GS_GamePlay::LoadEntities symbol drift")
 for vm,(dst,nm) in CALLS.items():
  if nm not in names.get(dst,()):
   raise ValueError(f"G240 original exact native callee symbol changed {dst:#x}")
 prior=json.loads(g238.read_text())
 if not prior["source_direct_native_loader_calls_found_total"]>=4 or (
     prior["original_source_class_instance_counts"].get("Attack")!=26):
  raise ValueError("G240 requires genuine G238 source method callers")
 for vm,(dst,_) in CALLS.items():
  rows=prior["actual_original_2010_direct_BL_BLX_callers_of_loader_methods"][hex(dst)]
  if not any(x["genuine_iOS_2010_direct_callsite_VM"]==hex(vm)
     and x["real_original_cpp_caller_entry_VM"]==hex(METHOD_VM) for x in rows):
   raise ValueError("G240 original G238 direct AddNew* caller proof mismatch")
 section=next((s for s in orig["sections"] if s[3]=="__text"
    and s[0]<=METHOD_VM<s[0]+s[1]),None)
 if section is None:raise ValueError("native actual 2010 __text section missing")
 native_starts=sorted(x for x in names if section[0]<=x<section[0]+section[1])
 ix=bisect.bisect_right(native_starts,METHOD_VM)
 stop=native_starts[ix] if ix<len(native_starts) else section[0]+section[1]
 if not (max(CALLS)<stop and METHOD_VM<min(CALLS)):
  raise ValueError("original 2010 LoadEntities bounds cannot cover expected callsites")
 size=stop-METHOD_VM
 if size>14000:raise ValueError("native original method unexpectedly large")
 fileoff=section[2]+METHOD_VM-section[0]
 asm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 asm.detail=True
 allops=list(asm.disasm(exe[fileoff:fileoff+size],METHOD_VM))
 byvm={x.address:x for x in allops}
 if len(allops)<200:raise ValueError("original source LoadEntities method unexpectedly small")
 for site,(target,_) in CALLS.items():
  i=byvm.get(site)
  if (not i or i.mnemonic!="bl" or not i.operands or
      i.operands[0].type!=ARM_OP_IMM or (i.operands[0].imm&~1)!=target):
   raise ValueError(f"G240 actual original native opcode changed at {site:#x}")
  # All three authentic typed AddNew branches use one source iterator:
  # increment sl, feed EntityData in r6, compare with fp count, jump back
  # to 0xC2EB8, or continue to 0xC32D0 when complete.
  guard={
     site-8:("add","sl, sl, #1"),
     site-4:("mov","r1, r6"),
     site+4:("cmp","sl, fp"),
     site+8:("bne","#0xc2eb8"),
     site+12:("b","#0xc32d0")
  }
  for vm,expected in guard.items():
   op=byvm.get(vm)
   if not op or (op.mnemonic,op.op_str)!=expected:
    raise ValueError(f"G240 original shared type iterator guard drift at {vm:#x}: {None if not op else (op.mnemonic,op.op_str)}")
 windows=[]
 for site,(target,name) in CALLS.items():
  range_ops=[i for i in allops if site-176<=i.address<=site+56]
  extracted=[{
      "authentic_original_ARM_VM":hex(i.address),
      "opcode":i.mnemonic,"args":i.op_str,
      "is_original_source_direct_AddNew_call":i.address==site,
      "callee_exact_Cpp_name":name if i.address==site else None
     }for i in range_ops]
  windows.append({
   "original_Method_Cpp":METHOD_NAME,
   "real_original_native_callsite_VM":hex(site),
   "original_native_AddNew_target_VM":hex(target),
   "source_exact_2010_cpp_target":name,
   "source_original_ARM_control_flow_neighborhood":extracted,
   "branch_conditions_are_source_only_not_path_satisfiability":True,
   "live_C1L1_registration_sequence_proven":False,
  })
 directcalls=[]
 for op in allops:
  if op.id in (ARM_INS_BL,ARM_INS_BLX) and op.operands and op.operands[0].type==ARM_OP_IMM:
   target=op.operands[0].imm&~1
   directcalls.append({"VM":hex(op.address),"target_VM":hex(target),
    "source_exact_CPP_symbol_names":sorted(names.get(target,()))[:3]})
 report={
  "source":"G240 original 2010 iOS MachO exact GS_GamePlay::LoadEntities native ARM source",
  "original_owner_MachO_SHA256":hashlib.sha256(exe).hexdigest(),
  "true_original_native_method_VM":hex(METHOD_VM),
  "true_original_native_method_CPP":METHOD_NAME,
  "real_original_method_number_of_ARM_decoded_instructions":len(allops),
  "original_native_method_bounded_bytes":size,
  "original_native_method_direct_calls_metadata":directcalls,
  "real_original_three_weapon_registration_subbranches":windows,
  "source_original_three_typed_AddNew_share_iterator_sl_and_EntityData_r6":True,
  "source_original_three_typed_AddNew_share_iteration_backedge_0xC2EB8":True,
  "real_iOS_original_WeaponDB_record_index0_name_AUTHENTICATED":False,
  "true_2010_scene_file_order_equal_registration_sequence_proven":False,
  "real_original_runtime_GetEntityData_iteration_order_proven":False,
  "original_2010_iOS_touch_missile_gatling_input_mapped":False,
  "Vita_original_level1_gameplay_changed":False,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G240 original LoadEntities source instructions",len(allops),
   "true original code bytes",size,"source direct calls",len(directcalls))
 for item in windows:
  print("G240 true original 2010 CALL",item["real_original_native_callsite_VM"],
   "->",item["source_exact_2010_cpp_target"])
  for i in item["source_original_ARM_control_flow_neighborhood"]:
   print("G240 actual LoadEntities ARM",i["authentic_original_ARM_VM"],
      i["opcode"],i["args"])
 print("G240 TRUE original source LoadEntities three Attack Weapon Accessory cases, runtime index not guessed, NO VPK")
 return report
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g238",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 run(a.ipa,a.g238,a.out)
