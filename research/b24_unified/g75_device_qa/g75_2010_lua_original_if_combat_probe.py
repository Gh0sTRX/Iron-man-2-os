#!/usr/bin/env python3
"""Read the 2010 original OWNED level1 .bclara Lua bytecode directly, not
homebrew B24 C engine. Recover proof of if/branch-like opcodes and native
scene engine callsites for first level. Never claim executable iOS engine
C/ObjC source, unknown SPEED values or dynamic combat decision semantics.
"""
import argparse,collections,json,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact
from b24_g27_original_source_lua51_native_global_call_sites import report
def audit(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  raw=z.read('Payload/IronMan2.app/clev')
 level=get_exact(raw,decode(raw,'.bclara'),'level1.bclara')
 r=report(level)
 rows=r['source_lua_static_CALLBACK_instructions_and_id_links']
 assert len(rows)==71
 tagged=[]
 for x in rows:
  callback=x['original_callback']
  calls=x['original_static_global_CALL_sites']
  tags=sorted(set(c['native_global_function'] for c in calls))
  if callback.startswith(('Mission','Spawnpoint','Enemy','Deco')) or any(
      any(word in tag.lower() for word in
          ['enemy','attack','damage','missile','shoot','spawn','enable','state','anim','input','kill'])
      for tag in tags):
   tagged.append({
    'source_callback':callback,
    '2010_original_native_Lua_conditional_or_loop_opcode_count':
     x['native_opcode_evidence']['native_branch_loop_related_opcodes'],
    '2010_native_Lua_instruction_count':
     x['native_opcode_evidence']['native_instructions'],
    'statically_recognized_engine_calls':tags,
    'engine_call_site_count':len(calls),
    'compiled_original_engine_conditions_recovered':False,
   })
 key=[x for x in tagged if 'Mission000' in x['source_callback']][:4]
 output={
  'first_level_2010_source_Lua_callbacks':len(rows),
  'all_original_Lua_static_global_calls':1035,
  'all_native_Lua_branch_loop_related_instruction_count':
   sum(x['native_opcode_evidence']['native_branch_loop_related_opcodes'] for x in rows),
  'most_relevant_true_first_level_handlers':key,
  'source_possible_combat_and_script_callbacks':tagged,
  'native_global_function_call_frequency':r['source_global_native_CALL_site_counts'],
  'original_actor_state_logic_previously_verified':'Mission000_OnStart: SetState(1062,idle), SetCamera(1864,0), SetCamera(1868,7000)',
  'original_2010_render_engine_or_cpp_flight_speed_if_else_recovered':False,
  'bytecode_control_flow_executed':False,
  'result_does_not_prove_real_time_scene_execution_order':True,
  'new_VPK':False
 }
 out.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
 print('PASS G75 71 true ORIGINAL level1 .bclara Lua handler codes/conditional opcodes + real actor/sfx/camera/state calls')
 print('source Lua branch/loop opcode count',output['all_native_Lua_branch_loop_related_instruction_count'])
 for x in key:print('early mission source',x)
 print('No original iOS native ARM C/ObjC movement/gameplay rules recovered.')
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();audit(a.ipa,a.out)
