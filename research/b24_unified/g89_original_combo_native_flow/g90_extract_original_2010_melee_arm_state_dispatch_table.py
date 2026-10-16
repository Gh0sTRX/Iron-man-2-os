#!/usr/bin/env python3
"""G90: exact 2010 iOS native ARM UpdateMeleeAttackState 0..12 branch dispatch
from G89 source-verified disassembly. Identifies code targets, NOT real
2010 iPhone touch input conditions, attack animation hit timings, or a
13-attack moveset. No native machine code/audio/VPK exported.
"""
import argparse,json
from pathlib import Path

OWNER='MainCharacter::UpdateMeleeAttackState()'
def main(source,out):
 db=json.loads(source.read_text())
 methods=[x for x in db['other_original_methods_referencing_combo_step_or_melee_call']
          if x['source_symbol']==OWNER]
 if len(methods)!=1:raise ValueError('G90 source must contain original UpdateMeleeAttackState')
 m=methods[0]
 if m['native_address_hex']!='0xf1de4':
  raise ValueError('2010 iOS source address changed')
 allread=[e for e in m['combo_0x824_accesses'] if e['operation']=='read']
 allwrite=[e for e in m['combo_0x824_accesses'] if e['operation']=='write']
 if len(allread)!=4 or len(allwrite)!=12:
  raise ValueError('2010 native source 0x824 read/write counts changed')
 witness=None
 for e in allread:
  ctx=e['nearby_ordered_native_instructions']
  asmap={int(x['offset_hex'],16):x for x in ctx}
  if 0x78 in asmap and 0x7c in asmap:
   witness=asmap
   break
 if not witness:
  raise ValueError('original ARM 2010 13-way jump source context absent')
 expect=((0x78,'cmp','r0, #0xc'),
         (0x7c,'addls','pc, pc, r0, lsl #2'),
         (0x80,'b','#0xf1e1c'))
 for offset,mnemonic,operand in expect:
  x=witness.get(offset)
  if x is None or x['mnemonic']!=mnemonic or x['operands']!=operand:
   raise ValueError('original 2010 exact native jump table guard differs at '+hex(offset))
 branches={int(x['offset_hex'],16):x for x in m['conditional_or_jump_edges']}
 targets=[]
 for state in range(13):
  table_offset=0x84+4*state
  ins=branches.get(table_offset)
  if not ins or ins['mnemonic']!='b' or not ins['immediate_target_in_same_bounded_function']:
   raise ValueError('source 2010 ARM switch jump target missing at '+hex(table_offset))
  dest=int(ins['immediate_target_relative_hex'],16)
  if dest<0 or dest>=m['function_bounded_bytes']:
   raise ValueError('original 2010 ARM branch target invalid')
  targets.append({'original_native_melee_internal_state_id':state,
    'original_ARM_dispatch_branch_instruction_address_hex':hex(0xf1de4+table_offset),
    'target_original_ARM_address_hex':hex(0xf1de4+dest),
    'target_offset_relative_to_original_function_hex':hex(dest),
    'is_attack_animation_name_known':False,
    'is_hit_frame_semantic_known':False})
 assert len(targets)==13
 report={'source':'real 2010 user-owned iOS v1.0.0 ARM Mach-O',
 'function':OWNER,'exact_native_start_hex':'0xf1de4',
 'native_state_var_object_byte_offset_hex':'0x824',
 'original_13_way_switch_dispatch_verified':True,
 'state_upper_bound_immediate_source':12,
 'default_out_of_range_relative_target_hex':'0x38',
 'arm_program_counter_pipeline_rule':'ARM-state PC at ADDLS = opcode_address + 8, hence index zero begins +0x84',
 'source_state_id_to_original_ARM_branch_target':targets,
 'original_13_internal_states_are_13_distinct_playable_combos':False,
 'original_combat_hit_start_end_frames_verified':False,
 'original_weapon_damage_numeric_verified':False,
 'source_authorized_gameplay_event_dispatch_active':False,
 'original_2010_host_PSvita_source_not_the_same_binaries':True,
 'NO_VPK':True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS G90 REAL original 2010 ARM 13 native state IDs -> 13 source branch targets; no fake combos or damage; NO VPK')
 for row in targets:
  print('NATIVE STATE',row['original_native_melee_internal_state_id'],
   'ARM slot',row['original_ARM_dispatch_branch_instruction_address_hex'],
   'target',row['target_original_ARM_address_hex'])
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--g89-json',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();main(a.g89_json,a.out)
