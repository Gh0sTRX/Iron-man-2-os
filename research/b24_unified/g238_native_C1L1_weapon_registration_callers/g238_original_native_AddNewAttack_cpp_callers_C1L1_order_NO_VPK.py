#!/usr/bin/env python3
"""G238 genuine original Iron Man 2 (2010) Mach-O direct callers of
WeaponDB::AddNewAttackEntity / AddNewWeapon / AddNewWeaponAccessory.
Compare with *file-order* of original typed C1L1 entities; DO NOT infer
global runtime array index from object naming or serialization order.
ARM/Thumb-aware direct call scanning with exact original C++ labels,
no source byte/code/assets redistribution or PS Vita gameplay mutation.
"""
from __future__ import annotations
import argparse,bisect,collections,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM, ARM_INS_BL, ARM_INS_BLX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"g76_original_combat"))
sys.path.insert(0,str(ROOT))
from g76_2010_native_arm_combat_method_provenance import parse_macho
from b24_owner_pack_extract import decode,get_exact
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize

EXPECTED_IPA_BYTES=248613763
EXPECTED_MACHO_BYTES=7480208
TARGETS={
 0xab894:"WeaponDB::AddNewAttackEntity(EntityData*)",
 0xabbd4:"WeaponDB::AddNewWeaponAccessory(EntityData*)",
 0xabf14:"WeaponDB::AddNewWeapon(EntityData*)",
 0xb27e4:"WeaponMgr::InitWeaponData(EntityData*, Entity3D*, int)",
}
def audit(ipa:Path,out:Path,g237:Path|None)->dict:
 if ipa.stat().st_size!=EXPECTED_IPA_BYTES:raise ValueError("not owner's exact original 2010 IPA")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip() is not None:raise ValueError("original IPA fails CRC")
  exe=z.read("Payload/IronMan2.app/IronMan2")
  packed=z.read("Payload/IronMan2.app/clev")
 if len(exe)!=EXPECTED_MACHO_BYTES:raise ValueError("wrong original 2010 Mach-O size")
 native=parse_macho(exe)
 entries=native["entries"]
 dem=subprocess.run(["c++filt"],input="\n".join(x[0] for x in entries)+"\n",
       text=True,capture_output=True,check=True).stdout.splitlines()
 if len(entries)!=len(dem) or native["nsyms"]!=65500:
  raise ValueError("genuine original 2010 symbol table not matched")
 byaddress=collections.defaultdict(set)
 modes=collections.defaultdict(set)
 for row,sym in zip(entries,dem):
  addr=row[1]&~1
  byaddress[addr].add(sym)
  modes[addr].add("thumb" if row[1]&1 else "arm")
 for addr,name in TARGETS.items():
  if name not in byaddress.get(addr,()):
   raise ValueError(f"original 2010 native target C++ symbol drift {addr:#x}")
 text_sections=sorted((s for s in native["sections"] if s[3]=="__text"))
 starts=sorted(addr for addr in byaddress if any(
  sec[0]<=addr<sec[0]+sec[1] for sec in text_sections))
 if len(starts)<5000:raise ValueError("native __text symbol coverage unavailable")
 decoder_arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 decoder_thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 for decoder in (decoder_arm,decoder_thumb):decoder.detail=True
 callsites=collections.defaultdict(list)
 checked=0
 decode_limited=0
 unknown_isa=0
 # All original native __text methods, not just a guessed "loader" list.
 for i,addr in enumerate(starts):
  sec=next((s for s in text_sections if s[0]<=addr<s[0]+s[1]),None)
  if sec is None:continue
  limit=(starts[i+1] if i+1<len(starts) else sec[0]+sec[1])
  limit=min(limit,sec[0]+sec[1])
  length=min(limit-addr,65536)
  if length<4:continue
  if limit-addr>65536:decode_limited+=1
  choices=modes[addr]
  if len(choices)!=1:
   unknown_isa+=1
   continue
  ofs=sec[2]+addr-sec[0]
  if ofs<0 or ofs+length>len(exe):
   raise ValueError("native original iOS __text mapped bounds invalid")
  decoder=decoder_thumb if "thumb" in choices else decoder_arm
  checked+=1
  for ins in decoder.disasm(exe[ofs:ofs+length],addr):
   if ins.id not in (ARM_INS_BL,ARM_INS_BLX) or not ins.operands:
    continue
   p=ins.operands[0]
   if p.type!=ARM_OP_IMM:continue
   dst=p.imm&~1
   if dst not in TARGETS:continue
   callsites[dst].append({
    "real_original_cpp_caller_entry_VM":hex(addr),
    "real_original_cpp_caller_names":sorted(byaddress.get(addr,()))[:8],
    "real_original_ARM_or_THUMB":next(iter(choices)),
    "genuine_iOS_2010_direct_callsite_VM":hex(ins.address),
    "real_original_cpp_target_VM":hex(dst),
    "real_original_cpp_target_name":TARGETS[dst],
    "call_alone_not_proof_of_live_original_Level1_order":True
   })
 src=get_exact(packed,decode(packed,".bclara"),"level1.bclara")
 scene=summarize(src)
 rows=[r for r in scene["source_2010_typed_class_instances"]
       if r["original_class_name"] in ("Attack","Weapon","WeaponAccessory")]
 counts=collections.Counter(r["original_class_name"] for r in rows)
 if counts["Attack"]!=26 or counts["Weapon"]!=13:
  raise ValueError("actual original level1 typed instance inventory drift")
 ordered=[{
  "original_binary_name_offset":row["original_name_offset"],
  "original_scene_ID":row["original_numeric_name_id"],
  "original_typed_cpp_class":row["original_class_name"],
  "original_scene_instance_name":row["original_name"],
  "source_file_order_only_NOT_runtime_AddNew_array_index":True
 } for row in sorted(rows,key=lambda q:q["original_name_offset"])]
 named=[x for x in ordered if x["original_scene_instance_name"] in (
   "Attack_type0","Attack_type1","Attack_WM_Missile","Attack_F22_missile")]
 if g237:
  previous=json.loads(g237.read_text())
  if not previous["source_three_independent_native_arrays_proven"] or len(
      previous["separate_attack_weapon_accessory_native_memory_layout"])!=3:
   raise ValueError("G238 requires real G237 original native array provenance")
 report={
  "origin":"G238 native original 2010 owner iOS Mach-O with 65500 original named symbols and C1L1 classed serialized object source",
  "original_source_macho_sha256":hashlib.sha256(exe).hexdigest(),
  "authentic_native_methods_scanned":checked,
  "source_native_inconsistent_arm_thumb_symbol_entries_skipped":unknown_isa,
  "native_source_bounded_over_64KB_methods":decode_limited,
  "original_native_WeaponDB_and_WeaponMgr_loader_exact_symbols":{
    hex(addr):label for addr,label in TARGETS.items()},
  "actual_original_2010_direct_BL_BLX_callers_of_loader_methods":{
    hex(addr):callsites[addr] for addr in TARGETS},
  "source_direct_native_loader_calls_found_total":sum(map(len,callsites.values())),
  "original_C1L1_file_order_of_typed_attack_weapon_accessory_instances":ordered,
  "original_named_attack_type0_type1_missile_source_instance_rows":named,
  "original_source_class_instance_counts":dict(counts),
  "original_C1L1_disk_serialization_order_eq_actual_native_WeaponDB_registration_order_PROVEN":False,
  "original_WeaponDB_index_0_maps_to_Attack_type0_PROVEN":False,
  "original_WeaponDB_index_1_maps_to_Attack_type1_PROVEN":False,
  "all_native_callers_including_indirect_virtual_calls_exhaustive":False,
  "real_original_level1_runtime_registration_order_observed":False,
  "original_WarMachine_missile_gatling_gesture_mapping_PROVEN":False,
  "Vita_suit_world_physics_weapon_damage_or_animation_changed":False,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G238 ORIGINAL native source functions checked",checked,
   "64KB-bound skips",decode_limited,"mixed ISA skipped",unknown_isa)
 for addr,target in TARGETS.items():
  print("G238 2010 EXACT native C++",hex(addr),target,
    "direct source caller count",len(callsites[addr]))
  for row in callsites[addr][:30]:print("G238 ORIGINAL C++ SOURCE CALLER",row)
 print("G238 TRUE source C1L1 file-ordered typed objects",len(ordered),dict(counts))
 for row in named:print("G238 actual serialized typed named entity",row)
 print("G238 PASS genuine original native loader C++ caller scan; runtime DB index order NOT GUESSED; NO VPK")
 return report

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g237",type=Path)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 audit(a.ipa,a.out,a.g237)
