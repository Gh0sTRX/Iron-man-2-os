#!/usr/bin/env python3
"""G237 verify source-native original 2010 WeaponDB owns THREE distinct
32-bit arrays and that AddNew* methods use capacity/count+1.
Only original G236 source opcode metadata. NO runtime insertion order
or guessing that C1L1 Attack_type0 == WeaponDB attack array[0].
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

PROOF={
 "Attack":{
  "vm":"0xab894","owner":"WeaponDB::AddNewAttackEntity(EntityData*)",
  "object_cpp_ctor":"0xa9784","ptr":0x30,"capacity":0x34,"count":0x38,
  "source_loadcount":"0xab8cc","source_loadcapacity":"0xab8d0","source_countplus1":"0xab8d4"},
 "WeaponAccessory":{
  "vm":"0xabbd4","owner":"WeaponDB::AddNewWeaponAccessory(EntityData*)",
  "object_cpp_ctor":"0xc0a40","ptr":0x18,"capacity":0x1c,"count":0x20,
  "source_loadcount":"0xabc0c","source_loadcapacity":"0xabc10","source_countplus1":"0xabc14"},
 "Weapon":{
  "vm":"0xabf14","owner":"WeaponDB::AddNewWeapon(EntityData*)",
  "object_cpp_ctor":"0xc1710","ptr":0x0,"capacity":0x4,"count":0x8,
  "source_loadcount":"0xabf4c","source_loadcapacity":"0xabf50","source_countplus1":"0xabf54"}
}
def run(g236:Path,out:Path):
 d=json.loads(g236.read_text())
 if d["original_native_Cpp_symbol_total"]<60000 or (
      d["original_C1L1_2010_typed_attack_count"],
      d["original_C1L1_2010_typed_weapon_count"])!=(26,13):
  raise ValueError("G237 original G236 source auth invalid")
 windows=d.get("G237_original_2010_native_loader_opcode_source_windows")
 if not isinstance(windows,dict) or len(windows)!=4:
  raise ValueError("G237 requires actual G236 logged native AddNew* original opcode windows")
 rows=[]
 for cls,expect in PROOF.items():
  q=windows.get(expect["vm"])
  if q is None or q["native_original_cpp_method"]!=expect["owner"]:
   raise ValueError(f"G237 genuine original 2010 C++ {cls} missing")
  ops={x["vm"]:(x["mnemonic"],x["args"]) for x in q["bounded_authentic_2010_ARM_ops"]}
  if len(ops)<60:raise ValueError("native C++ method window truncated")
  must={
    expect["source_loadcount"]:("ldr",f"r6, [r8, #{expect['count']:#x}]".replace("#0x0]","#0]")),
    expect["source_countplus1"]:("add","r2, r6, #1"),
    expect["vm"]:("push","{r4, r5, r6, r7, lr}"),
  }
  # Capstone formats offset #8 as #8 (decimal) and >= 10 as #0x10;
  # compare parsed integer displacement instead of human text formatting.
  for addr,(mn,arg) in must.items():
   if addr==expect["source_loadcount"]:
    x=ops.get(addr)
    if x is None or x[0]!="ldr" or not x[1].startswith("r6, [r8,"):
      raise ValueError(f"G237 true {cls} native count LDR missing @{addr}")
    actual=int(x[1].split("#",1)[1].rstrip("]"),0)
    if actual!=expect["count"]:raise ValueError(f"G237 count offset drift {cls} {actual}")
   elif ops.get(addr)!=(mn,arg):
    raise ValueError(f"G237 true native {cls} drift @{addr}: {ops.get(addr)} != {(mn,arg)}")
  cap=ops.get(expect["source_loadcapacity"])
  if not cap or cap[0]!="ldr" or not cap[1].startswith("sl, [r8,"):
    raise ValueError("G237 true capacity source disappeared "+cls)
  actualcap=int(cap[1].split("#",1)[1].rstrip("]"),0)
  if actualcap!=expect["capacity"]:raise ValueError("G237 cap offset changed "+cls)
  ctor=[{"vm":addr,"source_ARM":list(v)} for addr,v in ops.items()
       if v==("bl",f"#{expect['object_cpp_ctor']}")]
  if len(ctor)!=1:raise ValueError("G237 original typed constructor not unambiguously called "+cls)
  pointer_use=[{"vm":addr,"opcode":mn,"args":arg} for addr,(mn,arg) in ops.items()
   if mn.startswith(("ldr","str")) and (
    arg.endswith(", [r8]") and expect["ptr"]==0 or
    f"[r8, #{expect['ptr']:#x}]" in arg or
    f"[r8, #{expect['ptr']}]" in arg)]
  if not pointer_use:raise ValueError("G237 original array pointer field never accessed "+cls)
  count_stores=[]
  for vm,(mn,arg) in ops.items():
   if not mn.startswith("str") or "[r8" not in arg:continue
   if expect["count"]==0:continue
   try:offset=int(arg.split("#",1)[1].rstrip("]"),0)
   except (ValueError,IndexError):continue
   if offset==expect["count"]:count_stores.append({"vm":vm,"ARM":mn+" "+arg})
  rows.append({
   "original_type":cls,"native_AddNew_CPP_method":q["native_original_cpp_method"],
   "source_native_AddNew_VM":expect["vm"],
   "original_native_32bit_pointer_array_offset":hex(expect["ptr"]),
   "original_native_capacity_field_offset":hex(expect["capacity"]),
   "original_native_count_field_offset":hex(expect["count"]),
   "original_native_2010_count_before_add_VM":expect["source_loadcount"],
   "original_native_2010_count_plus_one_VM":expect["source_countplus1"],
   "original_native_object_constructor_direct_BL_sites":ctor,
   "source_original_pointer_array_field_uses":pointer_use[:10],
   "original_native_count_field_writes_in_bounded_window":count_stores,
   "structural_count_plus_one_and_capacity_check_proven":True,
   "source_all_runtime_insertions_into_WeaponDB_from_C1L1_in_order_proven":False,
  })
 result={
  "origin":"G237 from G236 original owner iOS 2010 authentic 65500 named MachO symbol/opcodes",
  "source_three_independent_native_arrays_proven":True,
  "separate_attack_weapon_accessory_native_memory_layout":rows,
  "source_WeaponDB_append_count_plus_one_present":True,
  "original_runtime_registered_attack_names_to_index_0_1_proven":False,
  "original_WeaponDB_index_0_1_is_Attack_type0_1_proven":False,
  "original_iOS_G218_selection_weapon_damage_or_attack_frame_proven":False,
  "Vita_gameplay_modified":False,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 for row in rows:print("G237 SOURCE-TRUE NATIVE ARRAY",row)
 print("G237 PASS read-only source 3 native WeaponDB independent pointer/cap/count arrays and count+1, no scene runtime index mapping; NO VPK")
 return result
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--g236",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 x=p.parse_args()
 run(x.g236,x.out)
