#!/usr/bin/env python3
"""G236 source-only ORIGINAL Iron Man 2 iOS 2010 WeaponDB index 0/1
provenance audit, comparing *distinct* Game WeaponDB C++ method symbols
and exact 2010 level1.bclara Attack class instances (26), Weapon (13).
Never equate 'Attack_type0' text with WeaponDB array[0] without proving
native runtime load/insertion/order. NO VPK / damage / native bytes export.
"""
from __future__ import annotations
import argparse
import bisect
import collections
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import capstone
from capstone.arm import ARM_OP_IMM

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/"g76_original_combat"))
sys.path.insert(0,str(HERE))
from g76_2010_native_arm_combat_method_provenance import parse_macho
from b24_owner_pack_extract import decode,get_exact
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize

OWNER_BYTES=248613763
EXEC_NAME="Payload/IronMan2.app/IronMan2"
EXPECTED_EXE_BYTES=7480208
METHOD_ANCHORS={
 "WeaponDB::GetAttackEntityByIndex(int)":0xab3ec,
 "WeaponDB::GetInstance()":0xab324,
 "WeaponMgr::GetWeapon(int)":0xb1f14,
 "WeaponMgr::GetAssistantWeapon(int)":0xb1d2c,
}
def run(ipa:Path,out:Path)->dict:
 if ipa.stat().st_size!=OWNER_BYTES:
  raise ValueError("G236 original owner's source IPA size drift")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip() is not None:raise ValueError("original owner IPA CRC failure")
  exe=z.read(EXEC_NAME)
  pack=z.read("Payload/IronMan2.app/clev")
 if len(exe)!=EXPECTED_EXE_BYTES:
  raise ValueError("original ARM executable size drift")
 native=parse_macho(exe)
 named=native["entries"]
 cpp=subprocess.run(["c++filt"],input="\n".join(e[0] for e in named)+"\n",
                    capture_output=True,text=True,check=True).stdout.splitlines()
 if len(cpp)!=len(named) or native["nsyms"]<60000:
  raise ValueError("original iOS symbol decoding incomplete")
 syms=collections.defaultdict(set)
 byclass=collections.defaultdict(list)
 for row,dem in zip(named,cpp):
  vm=row[1]&~1
  syms[vm].add(dem)
  if dem.startswith(("WeaponDB::","WeaponMgr::","AttackEntity::",
                     "WeaponEntity::","WeaponAccessory::")):
   byclass[dem.split("::")[0]].append({"vm":hex(vm),"method":dem,"thumb":bool(row[1]&1)})
 for name,vm in METHOD_ANCHORS.items():
  if name not in syms.get(vm,()):
   raise ValueError(f"original true native C++ identity changed {name} @ {vm:#x}")
 records=decode(pack,".bclara")
 first=get_exact(pack,records,"level1.bclara")
 scene=summarize(first)
 targets=[{"original_source_object":r["original_name"],
           "original_2010_typed_class":r["original_class_name"],
           "source_original_instance_numeric_id":r["original_numeric_name_id"],
           "source_original_name_offset":r["original_name_offset"],
           "is_original_WeaponDB_runtime_entry_index_proven":False}
          for r in scene["source_2010_typed_class_instances"]
          if r["original_class_name"] in ("Attack","Weapon","WeaponAccessory")]
 freq=collections.Counter(x["original_2010_typed_class"] for x in targets)
 if freq["Attack"]!=26 or freq["Weapon"]!=13:
  raise ValueError("G236 true 2010 level1 26 attack 13 weapon instances changed")
 text_sec=[s for s in native["sections"] if s[3]=="__text"]
 starts=sorted(a for a in syms if any(s[0]<=a<s[0]+s[1] for s in text_sec))
 decoder_arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM); decoder_arm.detail=True
 decoder_thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB); decoder_thumb.detail=True
 owners={}
 calls=[]
 for cls,rows in sorted(byclass.items()):
  for obj in sorted(rows,key=lambda x:int(x["vm"],16)):
   vm=int(obj["vm"],16)
   if vm in owners:continue
   sec=next((s for s in text_sec if s[0]<=vm<s[0]+s[1]),None)
   if sec is None:continue
   k=bisect.bisect_right(starts,vm)
   stop=starts[k] if k<len(starts) else sec[0]+sec[1]
   length=min(stop-vm,sec[0]+sec[1]-vm,6400)
   if length<4:continue
   ofs=sec[2]+vm-sec[0]
   if ofs<0 or ofs+length>len(exe):raise ValueError("original 2010 source bounds mismatch")
   cs=decoder_thumb if obj["thumb"] else decoder_arm
   ops=list(cs.disasm(exe[ofs:ofs+length],vm))
   bl=[]
   for op in ops:
    if op.mnemonic.startswith(("bl","blx")):
     direct=(op.operands and op.operands[0].type==ARM_OP_IMM)
     dest=op.operands[0].imm&~1 if direct else None
     item={"callsite_VM":hex(op.address),
           "native_direct_callee_VM":hex(dest) if dest is not None else None,
           "genuine_original_Cpp_target_names":sorted(syms.get(dest,()))[:5] if dest is not None else [],
           "actual_direct_call":bool(direct)}
     bl.append(item)
     if (dest in METHOD_ANCHORS.values() or
         (dest is not None and any("AttackEntity" in n or "WeaponDB" in n
                     for n in syms.get(dest,())))):
      calls.append({"source_original_cpp_method":obj["method"],"original_cpp_VM":hex(vm),**item})
   owners[vm]={"method":obj["method"],"original_function_VM":hex(vm),
               "native_ARM_or_THUMB":"THUMB" if obj["thumb"] else "ARM",
               "bounded_original_text_byte_count":length,
               "native_direct_calls":bl[:120],
               "entire_original_method_semantics_verified":False}
 # A level1 Attack class ID may be unrelated to global WeaponDB order.
 # Report where such names actually occur, but do not force index matches.
 source_attack_names=[x for x in targets if x["original_2010_typed_class"]=="Attack"]
 named01=[x for x in source_attack_names if x["original_source_object"] in
          ("Attack_type0","Attack_type1")]
 report={
  "source":"G236 exact original owner 2010 MachO C++ weapon methods + authentic level1 CLARA typed entity class instances",
  "source_original_MachO_SHA256":hashlib.sha256(exe).hexdigest(),
  "original_native_Cpp_symbol_total":native["nsyms"],
  "genuine_WeaponDB_WeaponMgr_AttackEntity_WeaponEntity_method_inventory":
      {k:sorted(v,key=lambda x:int(x["vm"],16)) for k,v in byclass.items()},
  "actual_original_2010_weapon_method_bounded_source_callgraph":[owners[k] for k in sorted(owners)],
  "native_cross_weaponDB_getattackentity_related_direct_edges":calls,
  "original_level1_native_scene_source_objects":targets,
  "original_C1L1_2010_typed_attack_count":freq["Attack"],
  "original_C1L1_2010_typed_weapon_count":freq["Weapon"],
  "original_named_Attack_type0_1_scene_instances":named01,
  "original_2010_WeaponDB_entry_0_is_Attack_type0_PROVEN":False,
  "original_2010_WeaponDB_entry_1_is_Attack_type1_PROVEN":False,
  "original_global_weaponDB_array_insertion_order_proven":False,
  "original_genuine_iOS_2010_Cpp_symbols_not_a_weapon_behavior_runtime_test":True,
  "original_WarMachine_gatling_missile_or_aim_M_binding_PROVEN":False,
  "Vita_gameplay_motion_weapon_damage_or_projectile_changed":False,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G236 owner true MachO symbols",native["nsyms"],
       "actual CLARA attack",freq["Attack"],"weapon",freq["Weapon"],
       "named Attack_type0/1 found",len(named01))
 for cls,methods in sorted(byclass.items()):
  print("G236 original C++",cls,"methods",len(methods))
  for m in methods[:60]:print("G236 ORIGINAL_METHOD",m["vm"],m["method"])
 for rec in named01:print("G236 ORIGINAL_C1L1_TYPED_OBJECT",rec)
 for edge in calls[:60]:print("G236 REAL_METHOD_EDGE",edge)
 print("G236 original CLARA source Attack named ID not assumed global WeaponDB runtime index. NO VPK")
 return report

if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--ipa",required=True,type=Path)
 ap.add_argument("--out",required=True,type=Path)
 a=ap.parse_args()
 run(a.ipa,a.out)
