#!/usr/bin/env python3
"""G77B: exact native WeaponDB index table and Actor::TestMeleeHit radius scale.
2010 source IPA read-only. No original code/assets exported; verified targeted
ARM instructions and authored literal data only. No proprietary VPK output.
"""
from __future__ import annotations
import argparse,subprocess,json,struct,math,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_MEM,ARM_OP_REG,ARM_REG_PC
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'g76_original_combat'))
from g76_2010_native_arm_combat_method_provenance import parse_macho

TARGET=('Actor::TestMeleeHit(Actor*)','WeaponDB::GetAttackEntityByIndex(int)',
        'WeaponDB::FindWeaponEntityById(int)','WeaponDB::GetInstance()',
        'MainCharacter::GetCurrentMeleeAttackStep() const',
        'Actor::CanBeHurt(Actor*)','Actor::Damage(float)')
def main(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  raw=z.read('Payload/IronMan2.app/IronMan2')
 parsed=parse_macho(raw)
 syms=parsed['entries']
 dem=subprocess.run(['c++filt'],input='\n'.join(x[0] for x in syms)+'\n',
                     capture_output=True,text=True,check=True).stdout.splitlines()
 if len(dem)!=len(syms):raise ValueError('demangler names mismatch')
 exact={}
 for row,name in zip(syms,dem):
  if name in TARGET and row[1]:
   if name in exact and exact[name][1]!=row[1]:raise ValueError('multiple native C++ same method addresses')
   exact[name]=row
 if not ('Actor::TestMeleeHit(Actor*)' in exact and 'WeaponDB::GetAttackEntityByIndex(int)' in exact):
  raise ValueError('2010 native expected Actor/WeaponDB method absent')
 segments=[]
 for addr,sz,off,sn,seg in parsed['sections']:
  if sn=='__text':segments.append((addr,sz,off))
 def section_offset(virtual):
  a=virtual&~1
  for vm,sz,off in segments:
   if vm<=a<vm+sz:
    ofs=off+a-vm
    if ofs>=len(raw):raise ValueError('file is truncated')
    return ofs
  raise ValueError('expected 2010 ARM text location not mapped')
 decoder=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 decoder.detail=True
 results={}
 for name in TARGET:
  if name not in exact:continue
  row=exact[name];addr=row[1]&~1
  if row[1]&1: raise ValueError('target instruction needs thumb-aware mode')
  size=0x180 if name.startswith('Actor::TestMeleeHit') else 0x60
  inst=list(decoder.disasm(raw[section_offset(addr):section_offset(addr)+size],addr))
  results[name]={'native_address_hex':hex(addr),
                 'entry_instructions':[
                   {'pc_rel':hex(i.address-addr),'operation':i.mnemonic,
                    'arguments':i.op_str} for i in inst[:35]]}
  if name=='Actor::TestMeleeHit(Actor*)':
   at=addr+0x20
   start=next((i for i in inst if i.address==at),None)
   if not start or start.mnemonic!='vldr' or len(start.operands)<2:
    raise ValueError('original native melee factor instruction changed')
   op=start.operands[1]
   if op.type!=ARM_OP_MEM or op.mem.base!=ARM_REG_PC:
    raise ValueError('not original native PC-relative factor')
   literal=((start.address+8)&~3)+op.mem.disp
   factor=struct.unpack_from('<f',raw,section_offset(literal))[0]
   if not math.isfinite(factor) or not .001<factor<100:raise ValueError('unknown native melee extent factor')
   results[name]['source_original_bbox_extent_scale_literal']={
     'pc_relative_source_literal_address':hex(literal),
     'original_raw_float32':factor,
     'source_assembly':'vldr s16,[pc,#0x110] and 2× bbox extent norms',
     'caller_melee_distance_check_via_model_bbox':True,
     'not_hit_animation_frame_or_damage_strength':True}
  if name=='WeaponDB::GetAttackEntityByIndex(int)':
   target_ops={'+0x10':'ldr r3, [r0, #0x38]', '+0x1c':'ldr r0, [r0, #0x30]',
               '+0x20':'ldr r0, [r0, r1, lsl #2]'}
   for ofs,check in target_ops.items():
    match=next((i for i in inst if i.address==addr+int(ofs,16)),None)
    if not match or (match.mnemonic+' '+match.op_str)!=check:
     raise ValueError('real original native WeaponDB array lookup differs '+ofs)
   results[name]['native_data_structure']={
    'native_offset_attack_entry_ptr_array':hex(0x30),
    'native_offset_attack_entry_count':hex(0x38),
    'index_stride_bytes':4,
    'native_return_for_out_of_bounds':'NULL',
    'actual_weapon_power_stat_recovered':False}
 result={'origin':'original unencrypted Gameloft 2010 iOS ARM Mach-O read-only',
         'exact_target_methods':results,
         'native_melee_model_bbox_scale_verified':'Actor::TestMeleeHit(Actor*)' in results,
         'native_weapon_array_layout_verified':'WeaponDB::GetAttackEntityByIndex(int)' in results,
         'damage_numbers_recovered':False,'no_VPK':True}
 from g78_source_ARM_attack_projectile_EntityData_property_keys import source as g78_property_audit
 g78_property_audit(ipa,out)
 from g78b_original_all_resource_attack_config_provenance import probe as g78_resource_scan
 g78_resource_scan(ipa,out)
 from g78c_native_source_bclara_weapon_data_value_context import run as g78_clara_values
 g78_clara_values(ipa,out)
 from g78d_native_class_attack_instance_inventory import audit as g78_real_instances
 g78_real_instances(ipa,out)
 from g79_original_26_attack_13_weapon_native_field_probe import scan as g79_weapon_instances
 g79_weapon_instances(ipa,out)
 from g80_original_CLARA_weapon_schema_to_26_attack_property_tags import audit as g80_real_2010_property_tags
 g80_real_2010_property_tags(ipa,out)
 g78_proof=json.loads((out/'G78_NATIVE_ORIGINAL_ATTACK_DAMAGE_EntityData_PROPERTY_MEMBER_MAP.json').read_text())
 result['exact_target_methods']['G78_original_AttackEntity_ProjectileEntity_2010_loader']=g78_proof['original_WeaponDB_AttackEntity_and_ProjectileEntity_source_typed_field_loader']
 result['exact_target_methods']['G78_original_2010_resource_archive_names']={'filenames':g78_proof['2010_app_top_level_resource_filename_candidates_without_encoded_content']}
 g78_assets=json.loads((out/'G78B_REAL_2010_ALL_CONTAINER_ATTACK_DAMAGE_SOURCE_LOCATOR.json').read_text())
 g80_data=json.loads((out/'G80_REAL_ORIGINAL_C1L1_WEAPON_DAMAGE_CLASS_PROPERTY_TAG_CROSSWALK.json').read_text())
 result['exact_target_methods']['G80_real_2010_attack_property_field_tags']={
    'source_attacks_schema':g80_data['authentic_class108_Attack_and_107_Weapon_schema'],
    'real_per_attack_tag_value_candidates':g80_data['26_attack_and_13_weapon_original_instance_tag_candidates']
 }
 g79_instances=json.loads((out/'G79_C1L1_26_ATTACK_13_WEAPON_ORIGINAL_INSTANCE_BINARY_FIELD_PROBE.json').read_text())
 result['exact_target_methods']['G79_true_attack_and_weapon_instance_binary_windows']={
  'original_attack_Weapon_template_headers':g79_instances['original_template_attack_weapon_class_data'],
  'original_2010_actual_26_attack_13_weapon_instance_source_windows':g79_instances['actual_binary_instance_payloads']
 }
 g78_instances=json.loads((out/'G78D_ORIGINAL_2010_CLASS_SCHEMA_WEAPON_VS_REAL_INSTANCE.json').read_text())
 result['exact_target_methods']['G78D_authentic_weapon_scene_instance_inventory']={
 'genuine_combat_relevant_native_schema_classes':g78_instances['genuine_combat_relevant_native_schema_classes'],
 'genuine_combat_relevant_typed_native_scene_instances':g78_instances['genuine_combat_relevant_typed_native_scene_instances']}
 g78_clara=json.loads((out/'G78C_NATIVE_CLEV_BCLARA_WEAPON_FIELD_VALUE_OR_TEMPLATE_CONTEXT.json').read_text())
 result['exact_target_methods']['G78C_original_2010_clev_schema_vs_value_locations']={
   'authentic_source_scene_record_count':g78_clara['authentic_original_iOS_2010_clev_BCLARA_record_count'],
   'per_original_scene_BCLARA_keyword_context':g78_clara['per_original_scene_BCLARA_keyword_context']
 }
 result['exact_target_methods']['G78B_authentic_2010_game_asset_config_locations']={
   'largest_original_app_resources':g78_assets['largest_original_app_resources'][:45],
   'source_property_name_location_hits':g78_assets['original_property_name_location_hits']
 }
 out.mkdir(parents=True,exist_ok=True)
 (out/'G77B_ORIGINAL_ARM_MELEE_BOUNDING_RADIUS_AND_WEAPON_DB_LAYOUT.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PASS G77B original native WeaponDB array source +0x30/+0x38 and original model melee geometric scalar',
       results['Actor::TestMeleeHit(Actor*)']['source_original_bbox_extent_scale_literal']['original_raw_float32'])
 print('No original attack damage or contact frame inferred')
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();main(a.ipa,a.out)
