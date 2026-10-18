#!/usr/bin/env python3
"""G193 original Iron Man 2 (iOS, 2010), source-proven UniBeam
native dummy group key 14 -> Dummy_Chest, 33 -> Dummy_Foot_L.

Proof is 5 independently captured ORIGINAL 2010 native ARM sources:
 G179 real DoAttack(14/33)->DoUniBeamAttack argument forwarding,
 G191 real Game::DoInitInLogo Create(34)+34 actual names,
 G192 DummiesTableAdd saves name to [base+old_count*4] and increments,
 G184 CollectDummies enumerates same global table r6 from 0,
 G185 CollectDummies accesses scene registry using SAME r6,
 plus G192 SceneImpl::GetDummy group index r1 (14/33) with child0.
Not proof that Vita's particle muzzle/VFX transform or damage already works.
Not a generated missile/beam/arm move-set or VPK.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def index(entries):
 return {int(i["vm"],16):(i["mnemonic"],i["args"]) for i in entries}
def require(mapping,addr,mn,args):
 received=mapping.get(addr)
 if received!=(mn,args):raise ValueError(f"original source ARM provenance mismatch {addr:#x}: {received} != {(mn,args)}")

def run(g179,g191,g192,g184,g185,out):
 a=json.loads(g179.read_text())
 b=json.loads(g191.read_text())
 c=json.loads(g192.read_text())
 d=json.loads(g184.read_text())
 e=json.loads(g185.read_text())
 for x in (a,b,c,d,e):
  if x.get("NO_VPK") is not True:raise ValueError("Original 2010 source CI provenance not intact")
 if a["original_DoAttack_to_UniBeam_arg0_native_integer_values"]!=[14,14,33]:
  raise ValueError("Original UniBeam actual native argument values changed")
 if a["original_UniBeam_WeaponDB_Attack_index_proven"]!=4:
  raise ValueError("Source original WeaponDB index4 provenance changed")
 names=b["source_original_registration_order_and_strings"]
 if len(names)!=34 or b["native_original_DummiesTableCreate_integer_argument_proven"]!=34:
  raise ValueError("Must use exactly original 2010 native Create(34)")
 if any(i["source_startup_CALL_order_zero_based"]!=k or
        not i["native_call_register_arg0_proven_constant"] or
        not i["source_original_dummy_string"] for k,i in enumerate(names)):
  raise ValueError("All 34 original ARM native direct name args MUST be valid & ordered")
 if b["source_original_Add_native_call_count"]!=34:raise ValueError("Not original Game::DoInitInLogo()")
 if names[14]["source_original_dummy_string"]!="Dummy_Chest":
  raise ValueError("Real owner 2010 dummy #14 source drift")
 if names[33]["source_original_dummy_string"]!="Dummy_Foot_L":
  raise ValueError("Real owner 2010 dummy #33 source drift")
 add=index(c["native_real_methods"]["DummiesTableAdd"]["source_original_ARM_instructions"])
 for vm,mn,args in (
  (0x641c4,"mov","fp, r0"),
  (0x641d0,"ldr","r8, [r1, #8]"), # old count = index
  (0x641e8,"add","sl, r8, #1"), # new count
  (0x641fc,"str","sl, [r5, #8]"),
  (0x643d4,"lsl","r5, r8, #2"), # write offset oldCount*4
  (0x643e0,"str","sl, [r4, #8]"),
  (0x6440c,"mov","r0, fp"), # original source input name
  (0x64410,"bl","#0x471170"), # original copy string
  (0x64414,"str","r0, [r6]"), # new copied name at old_count
  (0x64418,"mov","r0, r8") # return old index
 ):
  require(add,vm,mn,args)
 collect=index([{"vm":x["VM"],"mnemonic":x["opcode"],"args":x["args"]}
  for x in d["original_native_collect_loop_ARM_context_no_binary_bytes"]])
 for vm,mn,args in (
  (0x62f94,"ldr","fp, [r1, #8]"), # total named patterns
  (0x62fb0,"ldr","ip, [r5]"), # actual source name array
  (0x62fb8,"mov","r6, #0"), # start at zero
  (0x62fbc,"ldr","r1, [ip]"), # pattern[0]
  (0x62fc0,"bl","#0x73e84"), # stristr(nodeName,pattern)
  (0x62fd0,"add","r6, r6, #1"),
  (0x62ff8,"ldr","r1, [r2, r6, lsl #2]"),
  (0x63014,"ldr","r1, [lr, r6, lsl #2]"),
  (0x63054,"ldr","r1, [lr, r6, lsl #2]"),
  (0x630c0,"cmp","fp, r6")
 ):
  require(collect,vm,mn,args)
 scene=index([{"vm":x["VM"],"mnemonic":x["mnemonic"],"args":x["args"]}
  for x in e["original_registration_opcode_rows_not_binary"]])
 for vm,mn,args in (
  (0x63230,"ldr","r5, [r8, #0x278]"),
  (0x63234,"ldr","r4, [r5, r6, lsl #2]"), # same r6 goes to the scene group
  (0x6370c,"str","r0, [r5, r6, lsl #2]")
 ):
  require(scene,vm,mn,args)
 lookup=index(c["native_real_methods"]["SceneImpl_GetDummy"]["source_original_ARM_instructions"])
 for vm,mn,args in (
  (0x61724,"ldr","r3, [r0, #0x278]"),
  (0x61728,"ldr","r3, [r3, r1, lsl #2]"), # original UniBeam 14/33
  (0x6173c,"ldr","r1, [r3, #8]"),
  (0x61740,"cmp","r1, r2"),
  (0x61748,"ldr","r0, [r3]"),
  (0x6174c,"ldr","r0, [r0, r2, lsl #2]") # original child 0
 ):
  require(lookup,vm,mn,args)
 report={
  "provenance":"G179+G191+G192+G184+G185 ORIGINAL source native 2010 ARM instruction source chain",
  "verified_native_2010_Unibeam_WeaponDB_attack_index":4,
  "original_DoAttack_to_UniBeam_dummy_args":[14,14,33],
  "original_native_scene_group14_named_source_key":"Dummy_Chest",
  "original_native_scene_group33_named_source_key":"Dummy_Foot_L",
  "native_original_source_name_mapping_PROVEN":True,
  "native_original_group_element_index":0,
  "authored_original_34_named_dummy_groups_order":[x["source_original_dummy_string"] for x in names],
  "original_DummiesTableAdd_preserves_order_and_returns_old_index_proven":True,
  "original_CollectDummies_uses_same_group_idx_as_GetDummy_proven":True,
  "original_mapped_group_presence_in_specific_markV_or_markVI_rig_PROVEN":False,
  "original_real_game_branch_33_fires_which_unibeam_variant_PROVEN":False,
  "Vita_port_3D_dummy_transform_mapped_and_active":False,
  "Vita_actual_muzzle_firing_from_chest_or_foot_proven":False,
  "Vita_weapon_damage_hit_events_changed":False,
  "user_PS_Vita_physical_device_test_passed_for_new_mapping":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G193 ORIGINAL 2010 NATIVE SOURCE verified: UniBeam source WeaponDB index 4; native group 14 -> Dummy_Chest, 33 -> Dummy_Foot_L")
 print("G193 ARM proves startup 34 source strings indexed append order -> CollectDummies r6 group -> GetDummy r1 group, first node r2=0")
 print("G193 NO Vita beam emitter or damage movement changes, no VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for arg in ("g179","g191","g192","g184","g185","out"):
  p.add_argument("--"+arg,required=True,type=Path)
 a=p.parse_args()
 run(a.g179,a.g191,a.g192,a.g184,a.g185,a.out)
