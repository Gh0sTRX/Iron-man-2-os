#!/usr/bin/env python3
"""G135 actual original 2010 Lua 5.1 32-bit float level1 Mission000 control
flow. Replaces incorrect 'flat 1035 statically found CALLs equals execution'.
Analyze per opcode real Lua 5.1 conditional / unconditional jumps and
the path to 14,false -> 2,true -> 6,true source UI actions. NO Lua execution,
no invented player flight permission / cutscene scheduler, NO VPK.
"""
import argparse,collections,json,re,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode,get_exact
from b24_g27_original_source_lua51_native_global_call_sites import NativeLua,HEADER,report as g27report
OPCODES=['MOVE','LOADK','LOADBOOL','LOADNIL','GETUPVAL','GETGLOBAL',
'GETTABLE','SETGLOBAL','SETUPVAL','SETTABLE','NEWTABLE','SELF',
'ADD','SUB','MUL','DIV','MOD','POW','UNM','NOT','LEN','CONCAT',
'JMP','EQ','LT','LE','TEST','TESTSET','CALL','TAILCALL','RETURN',
'FORLOOP','FORPREP','TFORLOOP','SETLIST','CLOSE','CLOSURE','VARARG']
def flow(code):
 n=len(code);succ=[[] for _ in code]
 for pc,word in enumerate(code):
  op=word&63; a=(word>>6)&255; c=(word>>14)&511
  bx=(word>>14)&262143; sbx=bx-131071
  if op>=len(OPCODES):raise ValueError('2010 genuine Lua5.1 unknown opcode '+str(op))
  nx=pc+1
  if op==22:to=[pc+1+sbx]
  elif op==31:to=[pc+1,pc+1+sbx]
  elif op==32:to=[pc+1+sbx]
  elif op in (23,24,25,26,27,33):to=[pc+1,pc+2]
  elif op==2 and c:to=[pc+2]
  elif op in (29,30):to=[]
  elif op==34 and c==0:to=[pc+2] # Lua 5.1 SetList extension word
  else:to=[nx]
  if any(t<0 or t>n for t in to):
   raise ValueError('Native Lua 5.1 control-flow target outside owner function '+str((pc,to,n)))
  succ[pc]=[t for t in dict.fromkeys(to) if t<n]
 graph=collections.defaultdict(list)
 for a,links in enumerate(succ):
  for dst in links:graph[dst].append(a)
 visited={0};todo=[0]
 while todo:
  k=todo.pop()
  for v in succ[k]:
   if v not in visited:visited.add(v);todo.append(v)
 dom=[set(range(n)) for _ in code];dom[0]={0}
 for _ in range(n+2):
  modified=0
  for i in range(1,n):
   if i not in visited:continue
   incoming=[p for p in graph[i] if p in visited]
   d=({i}|set.intersection(*(dom[p] for p in incoming))) if incoming else {i}
   if d!=dom[i]:dom[i]=d;modified+=1
  if modified==0:break
 else:raise ValueError('Original Lua CFG dominators convergence failed')
 return succ,visited,dom
def run(ipa,out):
 if ipa.stat().st_size!=248613763:raise ValueError('user-authored 2010 owner exact IPA only')
 with zipfile.ZipFile(ipa) as z:
  raw=get_exact(z.read("Payload/IronMan2.app/clev"),
    decode(z.read("Payload/IronMan2.app/clev"),".bclara"),"level1.bclara")
 rows=g27report(raw)
 orig=next(r for r in rows['source_lua_static_CALLBACK_instructions_and_id_links'] if r['original_callback']=='Mission000_OnStart')
 p=NativeLua(raw,orig['original_source_callback_offset'])
 assert p.fetch(12)==HEADER
 node=p.function();fn=node['original_child_functions'][0]
 code=fn['native_function_code']
 succ,reachable,dom=flow(code)
 calls={x['source_bytecode_PC']:x for x in orig['original_static_global_CALL_sites']}
 required={
  50:('SetInputEnabled',[14.0,False]),
  914:('SetInputEnabled',[2.0,True]),
  927:('SetInputEnabled',[6.0,True]),
  935:('MissionResume',[])}
 for pc,(name,args) in required.items():
  q=calls.get(pc)
  if not q or q['native_global_function']!=name or q['literal_or_statically_tracked_arguments']!=args:
   raise ValueError(f"authentic Mission000 Lua PC{pc} previous source claim invalid")
 important=[]
 for pc in sorted(calls):
  entry=calls[pc]
  if entry['native_global_function'] not in ('SetInputEnabled','MissionPause','MissionResume',
    'SetState','SetCamera','PlayAnim','PlayVoice','Show','Hide','Enable','Disable',
    'CutsceneIn','CutsceneOut','Wait'):continue
  important.append({'2010_native_Lua_PC':pc,
   'original_script_callable_name':entry['native_global_function'],
   'original_statistically_tracked_args':entry['literal_or_statically_tracked_arguments'],
   'reachable_according_to_branch_overapproximation':pc in reachable,
   'must_run_on_all_paths_TO_all_script_exits':False,
   'native_Lua_dynamic_branch_actually_executed':False})
 condition=[
 {'pc':pc,'2010_original_Lua_op':OPCODES[word&63],
   'possible_successor_original_Lua_PCs':succ[pc],
   'dominates_input14_PC50':pc in dom[50],
   'dominates_input2_PC914':pc in dom[914],
   'dominates_input6_PC927':pc in dom[927]}
 for pc,word in enumerate(code) if (word&63) in (22,23,24,25,26,27,31,32,33)]
 report={'original_2010_source':'level1.bclara Mission000_OnStart actual 2010 float32 Lua5.1 function opcodes',
  'original_native_Lua_instructions':len(code),
  'source_2010_entry_op_pc':0,
  'source_original_branch_conditional_and_jump_sites':condition,
  '2010_source_branch_reachable_instruction_count_overapproximation':len(reachable),
  'original_intro_input_control_actions_and_camera_static_PCs':important,
  'PC50_to_PC914_has_dynamic_predicates':any(50<c['pc']<914 and c['2010_original_Lua_op'] in ('JMP','EQ','LT','LE','TEST','TESTSET','FORLOOP','FORPREP','TFORLOOP') for c in condition),
  'original_Mission000_callback_called_live_on_iOS_runtime_now':False,
  'MarkV_flight_allowed_or_forbidden_by_genuine_Level1_native_CPP_unknown':True,
  'Lua_script_execution_or_native_2010_game_event_engine_recreated':False,
  'no_new_VPK':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G135_REAL_ORIGINAL_MISSION000_LUA51_CFG_INPUT14_2_6_MISSIONRESUME_SOURCE_ONLY.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 print('G135 actual 2010 Mission000 source length',len(code),
       'branch instructions',len(condition),'overapprox reachable',len(reachable))
 for pc in required:
  print('G135 native source UI action',pc,required[pc], 'path-reachable',pc in reachable,
   'dominators-nearby',sorted(k for k in dom[pc] if k>40)[-22:])
 print('G135 Mission000 first 35 original branches:')
 for row in condition[:35]:print(row)
 print('G135 source-only original game callback control flow, NO flight guess/NO VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.ipa,a.out)
