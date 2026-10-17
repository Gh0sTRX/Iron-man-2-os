#!/usr/bin/env python3
"""G109 authentic original iOS 2010 ARM GetParamValue call/field flow.
No conjectural attack damage number, no IPA bytes committed, NO VPK.
Use the original 2010 owner ARM source extraction G97 artifact.
"""
import argparse,json
from pathlib import Path
NAMES=('EntityData::GetParamValue(char const*, int*)',
       'EntityData::GetParamValue(char const*, bool*)',
       'Actor::CanAttack(Actor*)',
       'Actor::TestMeleeHit',
       'ProjectileEntity::HitImpactActor',
       'MainCharacter::UpdateMeleeAttackState')
def run(inp,out):
 source=json.loads(inp.read_text())
 methods=source['original_CPP_methods']
 parsed=[]
 for prefix in NAMES:
  exact=[x for x in methods if x.get('original_symbol_found') and x['source_method'].startswith(prefix)]
  if not exact:
   if prefix.startswith('EntityData::'):raise ValueError('original native typed getter not included')
   continue
  for m in exact:
   op=m['full_bounded_original_source_opcode_metadata_NOT_machine_bytes']
   branches=m['ARM_control_flow_branch_sites']
   calls=m['real_native_calls']
   if not op or not calls:raise ValueError('not actual native 2010 ARM method data')
   callnames=[{'pc_relative_hex':v['relative_pc_hex'],
      'target_original_2010_cpp_source_symbols':v['source_original_called_symbols'],
      'branch_via_actor_virtual_dispatch_unproven':v['indirect_vtable_register_call']}
      for v in calls]
   parsed.append({'native_Cplusplus_method':m['source_method'],
    'native_arm_function_vm_address':m['original_ARM_address_hex'],
    'actual_source_encoded_arm_register_memory_reads':m['real_native_pointer_mem_accesses'],
    'original_bounded_2010_arm_control_flow_assembly':op,
    'original_2010_Cplusplus_named_direct_calls':callnames,
    'original_branch_edges':branches,
    'verified_integer_field_name_Damage_from_G98_but_not_source_instance_typed_values':True,
    'full_native_2010_gameplay_event_dispatch_reconstructed':False})
 out.parent.mkdir(parents=True,exist_ok=True)
 report={'authentic_source_2010_iOS_methods':parsed,
  'real_cpp_entitydata_int_bool_getters_found':len([x for x in parsed if x['native_Cplusplus_method'].startswith('EntityData::')]),
  'original_clara_Attack_26_Damage_numeric_values_recovered':False,
  'original_iOS_touch_event_callbacks_recovered':False,'NO_VPK':True}
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('G109 2010 owner source native actual getters and hit flow found',len(parsed))
 for m in parsed:
  print('G109 METHOD',m['native_Cplusplus_method'],m['native_arm_function_vm_address'])
  for o in m['original_bounded_2010_arm_control_flow_assembly']:
   print('G109 ARM',o['offset_hex'],o['mnemonic'],o['operand_register_or_literal'])
  for c in m['original_2010_Cplusplus_named_direct_calls']:
   print('G109 CALL',c['pc_relative_hex'],c['target_original_2010_cpp_source_symbols'],
    'virtual',c['branch_via_actor_virtual_dispatch_unproven'])
 print('G109 original exact source ARM extracted without inventing combat damage and no VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--metadata',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path);a=p.parse_args()
 run(a.metadata,a.out)
