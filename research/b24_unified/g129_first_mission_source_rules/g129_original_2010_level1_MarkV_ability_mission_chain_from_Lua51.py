#!/usr/bin/env python3
"""G129 owner 2010 iOS C1L1 original 71 Lua5.1 callbacks:
recover authentic first mission branching gates, type-linked mission names,
player MarkV idle / QTE / intro camera triggers, and ABILITY EVIDENCE.
NO blanket 'Mark V cannot fly' inference from movie or own beta.
Source 2010 original Lua static method CALLs, NOT executed native game.
No original Lua raw chunks / game assets redistributed, NO VPK.
"""
import argparse,collections,json,re
from pathlib import Path
def inspect(g26,g27,out):
 typed=json.loads(g26.read_text())
 dis=json.loads(g27.read_text())
 assert typed['source_parsed_Lua5_1_chunks']==71
 assert dis['original_native_Lua_GLOBAL_CALL_candidates']==1035
 scripts=typed['native_2010_all_original_level1_lua_callbacks']
 calls=dis['source_lua_static_CALLBACK_instructions_and_id_links']
 assert len(scripts)==len(calls)==71
 byname={row['callback_name']:row for row in scripts}
 ids={row['original_owner_node_ID']:row for row in scripts}
 assert len(byname)==71
 stage=[]
 all_functions=collections.Counter()
 exposed_calls=[]
 mission_link_names=(
   'StartMission','SetMission','EnableMission','MissionStart','MissionComplete',
   'MissionResume','MissionPause','StartNextMission','CompleteMission',
   'SetInputEnabled','SetState','ChangeState','SetPlayerState',
   'SetMovementMode','SetFlightEnabled','AllowFlight','DisableFlight',
   'EnableFlight','SetCanFly','SetCanHover','Enable','Disable','Hide','Show',
   'SetCamera','PlayAnim','CutsceneIn','CutsceneOut','PlayVoice')
 source_script_re=re.compile(r'(flying|flight|fly|rush|hover|float|suitcase|mark.?v|suit.?case|setinputenabled|mission)',re.I)
 for row in calls:
  label=row['original_callback']
  owner=byname.get(label)
  assert owner is not None
  assert row['source_owner_node']==owner['source_authored_owner_node']
  records=[]
  for event in row['original_static_global_CALL_sites']:
   fn=event['native_global_function']
   all_functions[fn]+=1
   arg=event['literal_or_statically_tracked_arguments']
   if fn not in mission_link_names and not source_script_re.search(fn):
    continue
   source_candidates=[]
   if arg and isinstance(arg[0],(float,int)) and not isinstance(arg[0],bool):
    val=arg[0]
    if float(val).is_integer() and int(val) in ids:
     item=ids[int(val)]
     source_candidates=[{'candidate_callback':item['callback_name'],
        'native_ID':int(val),'source_class':item['original_owner_native_class'],
        'link_only_if_native_API_argument_0_is_owner_ID':True}]
   records.append({'native_Lua_PC':event['source_bytecode_PC'],
       'original_native_function_name':fn,
       'typed_original_CLARA_owner_args':event['source_verified_named_entity_argument_candidates'],
       'literal_args_from_2010_Lua_static_registers':arg,
       'candidate_NPC_mission_ID_arguments_not_proven':source_candidates,
       'control_flow_branch_reachable_not_proven':True})
  strings=[q for q in owner['script_source_constant_strings'] if isinstance(q,str)]
  ability=[q for q in strings if source_script_re.search(q)]
  stage.append({'original_native_callback':label,
    'original_typed_scene_owner':owner['source_authored_owner_node'],
    'original_typed_owner_ID':owner['original_owner_node_ID'],
    'source_owner_class':owner['original_owner_native_class'],
    'original_script_constant_flight_or_mission_strings':ability[:60],
    'interesting_calls_static_NOT_execution_order':records,
    'has_direct_flight_gating_API_CALL_static':any(
      e['original_native_function_name'] in ('SetFlightEnabled','AllowFlight',
       'DisableFlight','EnableFlight','SetCanFly','SetCanHover','SetMovementMode') for e in records),
    'native_original_script_executed_on_Vita':False})
 intro=next(x for x in stage if x['original_native_callback']=='Mission000_OnStart')
 prologue=[c for c in intro['interesting_calls_static_NOT_execution_order']
     if c['native_Lua_PC']<73]
 check={(x['original_native_function_name'],
        int(x['literal_args_from_2010_Lua_static_registers'][0]))
     for x in prologue
     if x['literal_args_from_2010_Lua_static_registers'] and
       isinstance(x['literal_args_from_2010_Lua_static_registers'][0],(int,float))
       and not isinstance(x['literal_args_from_2010_Lua_static_registers'][0],bool)}
 assert {('SetState',1062),('SetCamera',1864),('SetCamera',1868)}<=check
 original_mission_callbacks=[x for x in stage if x['source_owner_class']=='Mission']
 assert len(original_mission_callbacks)==45
 all_flight_names=[fn for fn in all_functions if source_script_re.search(fn)]
 report={
  'owner_original_source':'actual Gameloft 2010 iOS level1.bclara typed 71 Lua 5.1 callback metadata',
  'original_lua_callbacks_total':71,
  'mission_class_callback_count':45,
  'original_intro_first_static_Lua_branch_PC':73,
  'original_intro_prologue_source_call_ids':[{'function':x['original_native_function_name'],
    'pc':x['native_Lua_PC'],
    'args':x['literal_args_from_2010_Lua_static_registers']}
      for x in prologue],
  'original_MarkV_first_level_can_fly_PROVEN':False,
  'original_MarkV_first_level_cannot_fly_PROVEN':False,
  'flight_unlocked_and_disabled_by_mission_source_proven':False,
  'original_native_Lua_function_names_resembling_flight_or_hover':all_flight_names,
  'original_Mission000_start_requires_idle_state_source_proven':True,
  'original_Mission000_has_scripted_QTE_camera_scene_source_proven':True,
  'statically_named_lua_functions_all_71':dict(all_functions),
  'original_callbacks_and_static_condition_call_candidates':stage,
  'Lua_native_branches_and_loops_executed_or_controlflow_reconstructed':False,
  'source_original_mission_event_dispatch_to_native_Vita_game_already_integrated':False,
  'NO_VPK':True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('G129 first-level original Lua truth:')
 print('Mission000 authored static prologue',[(x['native_Lua_PC'],x['original_native_function_name'],
       x['literal_args_from_2010_Lua_static_registers']) for x in prologue])
 print('Original 2010 native flight-related API names present',all_flight_names)
 print('Owner original Mission callback names',[x['original_native_callback'] for x in original_mission_callbacks])
 print('All 71 source script flight/hover cues',[(x['original_native_callback'],
       x['original_script_constant_flight_or_mission_strings'][:12])
       for x in stage if x['original_script_constant_flight_or_mission_strings']][:26])
 print('G129 TRUE ORIGINAL MarkV Level1 flight permission remains UNKNOWN until native actor/mission-runtime gate is recovered; no fake no-flight assumption.')
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--g26',type=Path,required=True);p.add_argument('--g27',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True);a=p.parse_args();inspect(a.g26,a.g27,a.out)
