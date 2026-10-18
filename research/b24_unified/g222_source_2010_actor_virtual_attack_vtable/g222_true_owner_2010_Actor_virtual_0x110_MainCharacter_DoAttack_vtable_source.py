#!/usr/bin/env python3
"""G222 verify exact original iOS 2010 32-bit ARM C++ virtual actor
callback target from Actor::UpdateStateAttack:
    [vptr+0x110](AttackType, StateTrack[GetEvent()].third_u32).
Owner 2010 ARM code G221 already PROVES registers/arguments.
Now find ORIGINAL MainCharacter/Actor/Whiplash vtable symbol/slot
and compare original pointer to MainCharacter::DoAttack(int,int).

Original Itanium ABI stores vtable[-2,-1] RTTI and offset-to-top;
source vptr commonly starts at vtable+8; probe +0x110 around
C++ symbol without claiming pointer identity until exactly matched.
No raw proprietary table pointers beyond names and addresses published,
no Vita hit/damage/time guess and no VPK.
"""
from __future__ import annotations
import argparse,collections,json,struct,subprocess,zipfile
from pathlib import Path
sysdummy=0
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
OWNER_BYTES=248613763
def run(ipa:Path,out:Path):
 if ipa.stat().st_size!=OWNER_BYTES:raise ValueError("need true original 2010 iOS game owner IPA")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("2010 iOS original ZIP checksum fail")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("not the authentic original 2010 ARM MachO executable")
 orig=parse_macho(exe)
 dems=subprocess.run(["c++filt"],input="\n".join(x[0] for x in orig["entries"])+"\n",
                     check=True,text=True,capture_output=True).stdout.splitlines()
 if len(dems)!=len(orig["entries"]):raise ValueError("native C++ demangling symbol count drift")
 symbols=collections.defaultdict(set)
 for rec,name in zip(orig["entries"],dems):symbols[rec[1]&~1].add(name)
 target_symbol="MainCharacter::DoAttack(int, int)"
 original_attack_addrs=sorted([addr for addr,n in symbols.items() if target_symbol in n])
 if original_attack_addrs!=[0xf64f8]:
  raise ValueError("MainCharacter original C++ DoAttack 0xf64f8 symbol original owner drift "+str(original_attack_addrs))
 desired=(
  "vtable for MainCharacter",
  "vtable for Actor",
  "vtable for CNPC",
  "vtable for WhiplashNPC")
 lookup=[]
 for name in desired:
  found=[addr for addr,names in symbols.items() if name in names]
  if len(found)>1:raise ValueError("native 2010 duplicate vtable source "+name)
  if not found:
   lookup.append({"source_original_vtable_Cpp":name,"source_original_owner_vtable_vm":None,"source_vtable_absent_symbol":True})
   continue
  addr=found[0];section=next((sec for sec in orig["sections"] if sec[0]<=addr<sec[0]+sec[1]),None)
  if section is None:
   lookup.append({"source_original_vtable_Cpp":name,"source_original_owner_vtable_vm":hex(addr),
     "source_vtable_section_absent":True})
   continue
  ptrs=[]
  for offset in (0x100,0x104,0x108,0x10c,0x110,0x114,0x118,0x11c,0x120):
   pos=addr+offset
   if pos>=section[0]+section[1]:continue
   binpos=section[2]+pos-section[0]
   val=struct.unpack_from("<I",exe,binpos)[0]
   raw_addr=val&~1
   ptrs.append({"original_vtable_byte_offset_from_symbol":offset,
     "original_owner_2010_unrelocated_u32_pointer_VM":hex(val),
     "exact_original_cpp_target_at_pointer":sorted(symbols.get(raw_addr,()))[:4],
     "source_target_exact_MainCharacter_DoAttack_0xF64F8":raw_addr==0xf64f8})
  lookup.append({"source_original_vtable_Cpp":name,"source_original_owner_vtable_vm":hex(addr),
    "source_vtable_section":section[3],
    "source_original_2010_Itanium_vptr_plus_0x110_relative_symbol_offset_0x118":True,
    "source_original_table_window":ptrs})
  print("G222 original 2010 C++",name,"VM",hex(addr),"section",section[3],flush=True)
  for p in ptrs:
   print("G222 owner vtable source slot",name,p,flush=True)
 # The 0x110 native vcall may select MainCharacter::DoAttack or an
 # overridden wrapper. Source calls remain proven regardless. Assert
 # only if the slot resolves by direct original binary pointer.
 mc=next(x for x in lookup if x["source_original_vtable_Cpp"]=="vtable for MainCharacter")
 mcslot=next((q for q in mc.get("source_original_table_window",[])
  if q["original_vtable_byte_offset_from_symbol"]==0x118),None)
 confirmed=bool(mcslot and mcslot["source_target_exact_MainCharacter_DoAttack_0xF64F8"])
 report={
  "source":"G222 original user's 2010 Iron Man 2 ARM MachO native Itanium Actor/MainCharacter virtual C++ method vtable original bytes",
  "source_native_owner_DoAttack_VM":"0xf64f8",
  "original_arm_Actor_UpdateStateAttack_virtual_offset_from_vptr":272,
  "source_2010_true_original_Itanium_Cpp_vtables":lookup,
  "source_2010_MainCharacter_vptr_0x110_exact_method_is_MainCharacter_DoAttack_PROVEN":confirmed,
  "source_original_vcall_method_identity_OTHER_players_or_enemy_PROVEN":False,
  "source_original_virtual_method_attack_damage_hitframe_proven":False,
  "source_real_2010_StateTrack_third_u32_payload_meaning_WeaponDB_missile_or_hitframe_PROVEN":False,
  "G218_live_Vita_gameplay_or_B16_changed":False,
  "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G222 native owner 2010 MainCharacter vptr +0x110 EXACT original DoAttack match",confirmed)
 print("G222 source actor third-u32 flow known, original event field semantics and actual Vita combat unchanged; no VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 run(a.ipa,a.out)
