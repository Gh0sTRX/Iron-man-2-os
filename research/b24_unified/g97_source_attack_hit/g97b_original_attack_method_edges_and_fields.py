#!/usr/bin/env python3
"""G97B derive exact original C++ native attack method call graph and
source object field read/write from G97 original user-owned IPA metadata.
Cannot independently prove serialized typed attack numeric values, specific
hitframe semantics or a playable enemy. Metadata and shortest call paths.
"""
import json,argparse,collections,re
from pathlib import Path
FOCUS=[
 'AttackEntity::LoadFromFile',
 'AttackEntity::DoAttack',
 'AttackEntity::DoProjectileAttack',
 'ProjectileEntity::HitImpactActor',
 'ProjectileEntity::UpdateCollisions',
 'ProjectileEntity::DoSplashDamage',
 'WeaponDB::AddNewAttackEntity',
 'Actor::Damage',
 'Actor::TestMeleeHit',
 'CNPC::OnHit',
 'MainCharacter::UpdateMeleeAttackState',
 'MainCharacter::UpdateComboAttackAction',
]
FAMILY=re.compile('Attack|Damage|Collision|Melee|Hit|Projectile|EntityData|Weapon|Actor|Effect|Hur|Shield|Health|State',re.I)
def run(source,out):
 doc=json.loads(source.read_text())
 if not doc['NO_VPK'] or doc['WEAPON_DB_SERIALIZED_DATA_ACTUALLY_TYPED']:
  raise ValueError('G97B needs authentic source metadata with unknown typed WeaponDB')
 methods=[x for x in doc['original_CPP_methods'] if x.get('original_symbol_found')]
 byaddr={x['original_ARM_address_hex']:x for x in methods}
 relevant=[]
 for m in methods:
  if not any(m['source_method'].startswith(x) for x in FOCUS):continue
  calls=m['real_native_calls']
  known=[]
  for c in calls:
   names=c['source_original_called_symbols']
   known.append({'source_offset':c['relative_pc_hex'],
      'native_method_address':c['source_original_called_address_hex'],
      'direct_original_callee':names,
      'is_combat_or_entitydata_related':any(FAMILY.search(n) for n in names),
      'indirect_virtual_call_without_type_proof':c['indirect_vtable_register_call']})
  field_count=collections.Counter(
   (z['operation'],z['offset_hex']) for z in m['real_native_pointer_mem_accesses'])
  highlights=[{'opcode':op,'original_field_offset':off,'observed_instruction_count':n}
   for (op,off),n in field_count.most_common(70)]
  relevant.append({'method':m['source_method'],
    'native_addr':m['original_ARM_address_hex'],
    'native_opcode_count':m['original_decoded_instruction_count'],
    'all_real_native_direct_calls':known,
    'actual_native_memory_access_profile':highlights,
    'source_known_Actor_resource_or_combo_accesses':
      m['2010_source_combo_and_actor_resource_field_accesses'],
    'genuine_serialized_property_name_for_offsets_unverified':True})
 if not any(x['method'].startswith('AttackEntity::LoadFromFile') for x in relevant):
  raise ValueError('No original source AttackEntity::LoadFromFile')
 out.parent.mkdir(parents=True,exist_ok=True)
 report={'original_iOS_2010_combat_call_flow_source_only':relevant,
    'native_method_count_source_scanned':len(methods),
    'exact_melee_attack_damage_float_values_proven':False,
    'exact_attack_window_frame_start_end_proven':False,
    'original_source_PSVita_AI_NPC_damage_integrated':False,
    'never_treat_raw_mem_offset_as_named_Damage_field_without_type_proof':True,
    'never_treat_virtual_call_name_as_semantic_without_dispatch_proof':True,
    'NO_VPK':True}
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS G97B exact 2010 source method flow',len(relevant),
       'no invented source attack damage/hitwindow')
 for row in relevant:
  print('SOURCE_METHOD',row['method'],'native',row['native_addr'],'code instructions',row['native_opcode_count'])
  for x in row['all_real_native_direct_calls']:
   if x['direct_original_callee']:
    print('  CALL',x['source_offset'],x['native_method_address'],
         ' '.join(x['direct_original_callee'][:3]))
   elif x['indirect_virtual_call_without_type_proof']:
    print('  CALL',x['source_offset'],'VIRTUAL register target unknown')
  print('  FIELDS',row['actual_native_memory_access_profile'][:20])
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--metadata',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();run(a.metadata,a.out)
