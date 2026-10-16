#!/usr/bin/env python3
"""True 2010 level1 Lua5.1 attack enabling data, conditional instruction
neighborhoods. Source-only static forensics; no native engine execution.
Correct Lua5.1 opcodes: 22 JMP,23 EQ,24 LT,25 LE,26 TEST,27 TESTSET,
31 FORLOOP,32 FORPREP,33 TFORLOOP. 34 SETLIST and 35 CLOSE ARE NOT
conditional opcodes. Previous G27 broader 177 includes those other ops.
"""
import argparse,collections,json,re,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode,get_exact
from b24_g27_original_source_lua51_native_global_call_sites import NativeLua,HEADER,report
OP=['MOVE','LOADK','LOADBOOL','LOADNIL','GETUPVAL','GETGLOBAL',
'GETTABLE','SETGLOBAL','SETUPVAL','SETTABLE','NEWTABLE','SELF',
'ADD','SUB','MUL','DIV','MOD','POW','UNM','NOT','LEN','CONCAT',
'JMP','EQ','LT','LE','TEST','TESTSET','CALL','TAILCALL','RETURN',
'FORLOOP','FORPREP','TFORLOOP','SETLIST','CLOSE','CLOSURE','VARARG']
BRANCH={22,23,24,25,26,27,31,32,33}
def insn(word,pc):
 op=word&63
 A=(word>>6)&255;B=(word>>23)&511;C=(word>>14)&511
 sx=((word>>14)&262143)-131071
 return {'PC':pc,'opcode':OP[op] if op<len(OP) else 'UNKNOWN',
  'a':A,'b':B,'c':C,'sBx':sx if op in {22,31,32} else None,
  'is_conditional_or_loop':op in BRANCH}
def examine(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  bank=z.read('Payload/IronMan2.app/clev')
 data=get_exact(bank,decode(bank,'.bclara'),'level1.bclara')
 original=report(data)
 byname={x['original_callback']:x for x in original['source_lua_static_CALLBACK_instructions_and_id_links']}
 scripts={}
 for m in re.finditer(re.escape(HEADER[:5]),data):
  p=NativeLua(data,m.start())
  if p.fetch(12)!=HEADER:raise ValueError('wrong 2010 Lua header')
  root=p.function()
  label=root['native_constants'][0]
  function=root['original_child_functions'][0] if root['original_child_functions'] else root
  scripts[label]=function
 assert len(scripts)==len(byname)==71
 calls=[]
 for name,record in byname.items():
  code=scripts[name]['native_function_code']
  for item in record['original_static_global_CALL_sites']:
   if item['native_global_function'] not in ('SetAttackTypeEnabled','SetInputEnabled','KillSpawnpointEnemy','PlayAnim','SetState'):continue
   pc=item['source_bytecode_PC']
   lo=max(0,pc-12)
   hi=min(len(code),pc+3)
   vicinity=[insn(code[i],i) for i in range(lo,hi)]
   nearest=[x for x in vicinity if x['is_conditional_or_loop']]
   calls.append({
    'real_original_script':name,
    'source_call':item['native_global_function'],
    'source_pc':pc,
    'source_register_traced_parameters':item['literal_or_statically_tracked_arguments'],
    'static_condition_like_instr_within_12_before':nearest,
    'opcode_window':vicinity,
    'does_NOT_prove_condition_guards_this_call':True
   })
 ct=collections.Counter(x['source_call'] for x in calls)
 raw_branch_count=sum(sum((w&63) in BRANCH for w in f['native_function_code']) for f in scripts.values())
 result={
 'source_owner_original_lua_function_count':71,
 'all_original_static_calls':1035,
 'true_Lua_5_1_branch_and_loop_opcodes_in_71_callback_bodies':raw_branch_count,
 'caution_prior_177_G27_source_count_includes_nonspecial_SETLIST_CLOSE':True,
 'SetAttackTypeEnabled_call_count':ct['SetAttackTypeEnabled'],
 'SetInputEnabled_call_count':ct['SetInputEnabled'],
 'attack_and_input_source_calls_with_instruction_context':calls,
 'original_2010_source_conditional_truth_table_or_game_engine_formula_verified':False,
 'native_iOS_combat_executable_code_reverse_engineered':False,
 'source_only_no_VPK':True}
 assert ct['SetAttackTypeEnabled']==12
 out.write_text(json.dumps(result,indent=2,ensure_ascii=False,default=str)+'\n')
 print('PASS G75 genuine 2010 SetAttackTypeEnabled calls',ct['SetAttackTypeEnabled'],
       'real Lua5.1 conditional opcodes',raw_branch_count,
       'not previously overcounted G27 177')
 for item in calls:
  if item['source_call']=='SetAttackTypeEnabled':
   print(item['real_original_script'],'PC',item['source_pc'],
      'parameters',item['source_register_traced_parameters'],
      'nearby_if_opcode_count',len(item['static_condition_like_instr_within_12_before']))
 print('Source-only, exact original if-guards and C++ engine combat values remain unproven')
if __name__=='__main__':
 a=argparse.ArgumentParser()
 a.add_argument('--ipa',required=True,type=Path)
 a.add_argument('--out',required=True,type=Path)
 q=a.parse_args();examine(q.ipa,q.out)
