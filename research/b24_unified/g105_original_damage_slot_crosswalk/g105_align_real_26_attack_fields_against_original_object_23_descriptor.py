#!/usr/bin/env python3
"""G105: verify 2010 C1L1 all 26 Attack instances typed 54 length-prefix
fields match ORIGINAL class110 Object descriptor order / type-shape.
Only emit candidate slot if all 26 lengths uniquely align. Do NOT
promote an inherited Object field into AttackEntity native Damage until
actual EntityData ancestry/GetParamValue property dispatch is shown.
"""
import argparse,json,collections
from pathlib import Path
NATIVE={1:1,2:4,4:4,8:4,512:4}
def run(src,out):
 db=json.loads(src.read_text())
 assert db['source_named_instances_verified']==26
 assert db['all_26_length_streams_pass'] is True
 obj=db['G103_native_Object110_full_source_local_property_list']
 assert obj[0]['source_property']=='Object'
 fields=obj[1:]
 assert len(fields)==23
 assert len([f for f in fields if f['source_property']=='Damage'])==1
 instances=db['all_26_original_named_Attack_property_size_stream_attempts']
 assert len(instances)==26
 if any(len(r['sample_source_fields'])!=54 for r in instances):
  raise ValueError('G105 requires 26 full 54 genuine source-size records')
 candidates=[]
 for offset in range(54-len(fields)+1):
  evidence=[];valid=True
  for entry in instances:
   slots=entry['sample_source_fields']
   mapping=[]
   for j,f in enumerate(fields):
    spec=slots[offset+j];tag=f['original_binary_type_tag']
    expected=NATIVE.get(tag)
    if expected is not None and spec['actual_source_data_length']!=expected:
     valid=False;break
    if expected is None and tag!=1024:
     valid=False;break
    mapping.append({'2010_class110_property_name':f['source_property'],
      '2010_native_type_tag':tag,'attack_serialized_slot_index':offset+j,
      'genuine_source_byte_length':spec['actual_source_data_length'],
      'i32_value_only_if_typed_and_four_bytes':spec['decoded_i32_only_IF_four_byte_field']})
   if not valid:break
   damage=next(e for e in mapping if e['2010_class110_property_name']=='Damage')
   evidence.append({'attack':entry['original_2010_attack'],
     'Object_Damage_field_candidate_source_slot':damage['attack_serialized_slot_index'],
     'source_i32_candidate_value':damage['i32_value_only_if_typed_and_four_bytes'],
     'original_Attack_parented_to_Object110_ACTUALLY_PROVEN':False})
  if valid and len(evidence)==26:
   candidates.append({'contiguous_class110_object_local_properties_first_serialized_slot':offset,
      'class110_original_descriptor_property_count':len(fields),
      'native_type_length_pattern_verified_for_all_26_attacks':True,
      'Damage_position_within_local_class110':next(i for i,x in enumerate(fields) if x['source_property']=='Damage'),
      'source_i32_damage_CANDIDATES_NOT_YET_GAMEPLAY_VERIFIED':evidence})
 result={'game':'original user iOS 2010 Stark Expo 26 class108 Attack',
 'all_26_attack_field_length_prefixes_truly_decoded':True,
 'class110_local_23_original_prototype_property_tag_sequence':[{'name':f['source_property'],'original_type_tag':f['original_binary_type_tag']} for f in fields],
 'testable_parent_class_property_slot_alignment_candidates':candidates,
 'candidates_with_26_of_26_exact_type_length_matching':len(candidates),
 'safe_original_AttackEntity_damage_per_26_typed_numeric_values_PROVEN':False,
 'exact_source_EntityData_inheritance_property_dispatch_PROVEN':False,
 'safe_to_enable_2010_damage_runtime':False,
 'NO_VPK':True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('G105 genuine Object110 property typed signature vs 26 x 54 originally serialized fields: valid contiguous offsets',len(candidates))
 for c in candidates:
  print('CANDIDATE native Object property prefix position',c['contiguous_class110_object_local_properties_first_serialized_slot'],
        'Damage slot',c['source_i32_damage_CANDIDATES_NOT_YET_GAMEPLAY_VERIFIED'][0]['Object_Damage_field_candidate_source_slot'])
  print('Original 26 ATTACK slot derived INT candidate values; NOT VERIFIED as Damage game values:',
     [(v['attack'],v['source_i32_candidate_value']) for v in c['source_i32_damage_CANDIDATES_NOT_YET_GAMEPLAY_VERIFIED']])
 print('G105 source crosswalk candidate analysis is separate from G104 user-test VPK, which remains immortal dummy debug-only.')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--schema',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
 q=a.parse_args();run(q.schema,q.out)
