#!/usr/bin/env python3
"""G89B: inspect exact original native combo state predicate/reset/update
instruction evidence from G89's SOURCE-owned ARM metadata. No IPA needed,
no arbitrary animation/frame guesses, no VPK or gameplay unlock.
"""
import argparse,collections,json,re
from pathlib import Path
PREDICATES=(
 'MainCharacter::IsInMeleeAttackState()',
 'MainCharacter::IsInMeleeAttackEndState()',
 'MainCharacter::IsInMeleeAttackSlideState() const',
 'MainCharacter::ResetMeleeAttackState()',
 'MainCharacter::UpdateMeleeAttackState()',
)
def inspect(source,destination):
 db=json.loads(source.read_text())
 names={x['source_symbol']:x for x in
       db['other_original_methods_referencing_combo_step_or_melee_call']}
 methods={name:names.get(name) for name in PREDICATES}
 if any(x is None for x in methods.values()):
  raise ValueError('original native reset/update/predicate +0x824 names missing: '+
   str([k for k,v in methods.items() if v is None]))
 start=db['exact_source_method_bounded_instruction_flow']['MainCharacter::StartMeleeAttack(float)']
 writes=[e for e in start['combo_0x824_accesses'] if e['operation']=='write']
 reads=[e for e in start['combo_0x824_accesses'] if e['operation']=='read']
 if len(writes)!=2 or len(reads)!=1:
  raise ValueError('2010 native StartMelee expected exactly 2 writes and 1 read')
 update=methods['MainCharacter::UpdateMeleeAttackState()']
 if len(update['combo_0x824_accesses'])!=16:
  raise ValueError('2010 native UpdateMeleeAttackState 16 field access instruction count drift')
 def compact(e):
  ctx=e['nearby_ordered_native_instructions']
  at=next((i for i,x in enumerate(ctx)
           if x['offset_hex']==e['offset_hex']),None)
  if at is None:raise ValueError('native instruction window offset mismatch')
  last=ctx[max(0,at-5):at]
  after=ctx[at+1:at+8]
  pre_cmp=[x for x in last if x['mnemonic'].startswith(('cmp','tst','vcmpe'))]
  post_br=[x for x in after if x['mnemonic'].startswith(('b','cb'))]
  return {'native_source_instruction_pc':e['source_pc_hex'],
   'source_instruction_exact':e['original_ARM_insn'],
   '2010_native_field_access_kind':e['operation'],
   'last_5_native_instructions':last,
   'next_7_native_instructions':after,
   'preceding_cmp_or_test_in_window':pre_cmp,
   'subsequent_native_branch_in_window':post_br,
   'no_asserted_attack_time_or_input':True}
 # G89 C11 reference is only allowed if every predicate matches
 # the exact ORIGINAL native read/compare/conditional-result sequence.
 def original_after(name):
  rows=methods[name]['combo_0x824_accesses']
  if len(rows)!=1:raise ValueError('native 2010 predicate expected one +0x824 read/write: '+name)
  evidence=compact(rows[0])
  return [(x['mnemonic'],x['operands']) for x in evidence['next_7_native_instructions']]
 exact={
  'MainCharacter::IsInMeleeAttackState()':[
   ('sub','r0, r1, #2'),('cmp','r0, #0xa'),('movhi','r0, #0'),('movls','r0, #1')],
  'MainCharacter::IsInMeleeAttackEndState()':[
   ('sub','r0, r1, #9'),('cmp','r0, #3'),('movhi','r0, #0'),('movls','r0, #1')],
  'MainCharacter::IsInMeleeAttackSlideState() const':[
   ('cmp','r0, #1'),('movne','r0, #0'),('moveq','r0, #1')],
 }
 for name,want in exact.items():
  got=original_after(name)
  if got[:len(want)]!=want:
   raise ValueError('REAL ORIGINAL 2010 ARM melee predicate changed: '+name+str(got))
 reset=methods['MainCharacter::ResetMeleeAttackState()']['combo_0x824_accesses']
 reset_ctx=compact(reset[0])
 if reset_ctx['last_5_native_instructions'][-1]['mnemonic']!='mov' or \
    reset_ctx['last_5_native_instructions'][-1]['operands']!='r3, #0' or \
    reset_ctx['next_7_native_instructions'][0]['mnemonic']!='str' or \
    reset_ctx['next_7_native_instructions'][0]['operands']!='r3, [r0, #0x828]':
  raise ValueError('Original iOS reset did not zero both +0x824 and +0x828')
 scenes={key:{
   'original_cpp_name':key,
   'native_start_address':val['native_address_hex'],
   'original_0x824_field_ops':[compact(x) for x in val['combo_0x824_accesses']],
   'access_kinds':dict(collections.Counter(x['operation'] for x in val['combo_0x824_accesses'])),
   'conditional_source_edges':len(val['conditional_or_jump_edges']),
   'direct_and_indirect_source_calls':val['direct_and_register_calls']}
  for key,val in methods.items()}
 start_context=[compact(x) for x in start['combo_0x824_accesses']]
 # The following is a real compare and indexed reference in one source
 # instruction neighborhood, NOT proof of 13 playable attack animations.
 native_instr={(x['offset_hex'],x['mnemonic'],x['operands'])
   for e in start['combo_0x824_accesses']
   for x in e['nearby_ordered_native_instructions']}
 bound=any(x[1]=='cmp' and x[2]=='r3, #0xc' for x in native_instr)
 indexed=any(x[1]=='ldr' and '[r1, r3, lsl #2]' in x[2] for x in native_instr)
 if not (bound and indexed):
  raise ValueError('2010 original 0..12 indexed branch context evidence drifted')
 assert any(x['source_instruction_exact']['mnemonic'].startswith('str') for x in start_context)
 report={'original_2010_native_Cplusplus':True,
  'original_StartMeleeAttack_0x824_actual_source_reads':len(reads),
  'original_StartMeleeAttack_0x824_actual_source_writes':len(writes),
  'original_UpdateMeleeAttackState_0x824_instruction_accesses':16,
  'original_StartMeleeAttack_native_source_bounded_index_compared_to_12':bound,
  'original_StartMeleeAttack_native_source_32bit_indexed_lookup_after_compare':indexed,
  'all_3_native_melee_classification_predicates_exact_ARM_asserted':True,
  'native_reset_0x824_and_0x828_zero_exact_ARM_asserted':True,
  '2010_native_classification_truth_table':{
    'slide':[1],'attack_state_inclusive_range':[2,12],
    'ending_state_inclusive_range':[9,12]},
  'index_0_through_12_IS_NOT_a_proven_gameplay_attack_count':True,
  'actual_original_reset_and_predicate_functions':scenes,
  'original_start_melee_source_field_flow':start_context,
  'original_contact_hit_active_frame_time_proven':False,
  'original_2010_damage_per_attack_numeric_proven':False,
  'fully_emulated_original_combo_13_state_logic_on_Vita':False,
  'no_VPK':True}
 destination.parent.mkdir(parents=True,exist_ok=True)
 destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS G89B original ARM 2 Start writes, 1 Start read and 16 native UpdateMeleeAttackState accesses; indexed source 0xC compare, NOT 13 proved attack combos')
 for name,record in scenes.items():
  print('NATIVE METHOD',name,'pc',record['native_start_address'],
        '0x824',record['access_kinds'],'branches',record['conditional_source_edges'])
  for v in record['original_0x824_field_ops']:
   x=v['source_instruction_exact']
   print(' FIELD',v['2010_native_field_access_kind'],v['native_source_instruction_pc'],
         x['mnemonic'],x['operands'])
   for inst in v['last_5_native_instructions']:
    print('   BEFORE',inst['offset_hex'],inst['mnemonic'],inst['operands'])
   for inst in v['next_7_native_instructions']:
    print('   AFTER',inst['offset_hex'],inst['mnemonic'],inst['operands'])
 print('G89B native genuine read/write sites only. No source-authorized damage/animation hit frame.')
if __name__=='__main__':
 ap=argparse.ArgumentParser()
 ap.add_argument('--g89-json',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 opts=ap.parse_args()
 inspect(opts.g89_json,opts.out)
