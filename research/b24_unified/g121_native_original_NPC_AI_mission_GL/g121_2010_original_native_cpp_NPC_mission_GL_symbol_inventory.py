#!/usr/bin/env python3
"""G121 user 2010 iOS Iron Man 2 original Mach-O actual C++ NPC mission
and render lighting symbol/relative source ABI inventory. This is a
PROVENANCE step to select authentic 2010 engine methods for C port,
not a made-up NPC AI or exact shader parity claim. No VPK or game bits.
"""
import argparse,bisect,collections,json,re,subprocess,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'g76_original_combat'))
from g76_2010_native_arm_combat_method_provenance import parse_macho
import capstone
KEYS={
 'NPC_AI':re.compile(r'(NPC|Enemy|ActorManager|AIManager|Damage|OnHit|Death|Kill|StateMachine|Brain|Target)',re.I),
 'MISSION_SPAWN':re.compile(r'(Mission|Level|Trigger|Spawn|Wave|Script|Lua|Scenario|Checkpoint|Objective|EventManager|GameState)',re.I),
 'VISUAL_GLES':re.compile(r'(Render|Light|Sun|Sky|Material|Shader|Texture|OpenGL|GlState|Alpha|Blend|Camera|Draw|Scene)',re.I)
}
def inspect(ipa,out):
 if ipa.stat().st_size!=248613763:raise ValueError('original user 2010 iOS IPA required')
 with zipfile.ZipFile(ipa) as z:ex=z.read('Payload/IronMan2.app/IronMan2')
 m=parse_macho(ex)
 names=[x[0] for x in m['entries']]
 dem=subprocess.run(['c++filt'],input='\n'.join(names)+'\n',
     capture_output=True,text=True,check=True).stdout.splitlines()
 if len(dem)!=len(names):raise ValueError('native 2010 owner C++ source symbol count mismatch')
 all_syms=sorted(zip(m['entries'],dem),key=lambda q:q[0][1]&~1)
 ordered=sorted(set(x[0][1]&~1 for x in all_syms))
 secs=[s for s in m['sections'] if s[3]=='__text']
 source={k:[] for k in KEYS}
 for row,name in all_syms:
  address=row[1]&~1
  sec=next((s for s in secs if s[0]<=address<s[0]+s[1]),None)
  if sec is None:continue
  categories=[key for key,rx in KEYS.items() if rx.search(name)]
  if not categories:continue
  pos=bisect.bisect_right(ordered,address)
  nxt=ordered[pos] if pos<len(ordered) else sec[0]+sec[1]
  size=max(0,min(nxt-address,sec[0]+sec[1]-address))
  for cat in categories:
   source[cat].append({'original_2010_cpp_symbol':name,
     'source_native_ARM_or_thumb_address':hex(address),
     'original_native_symbol_byte_span_until_next':size,
     'native_is_thumb':bool(row[1]&1)})
 # Exact on-device function bodies, not method name implies behavior.
 targets={
  'CNPC':re.compile(r'^(CNPC|NPC)::(Update|OnHit|Damage|Die|Attack|Move|Initialize|Reset)',re.I),
  'ActorManager':re.compile(r'^ActorManager::',re.I),
  'MISSION':re.compile(r'^(Mission|MissionManager|Level|LevelManager|EventManager|Trigger)',re.I),
  'VISUAL':re.compile(r'^(RenderManager|SceneRenderer|Material|Lighting|Sun|Sky|TextureManager)::',re.I)}
 probes=[]
 cs_arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 cs_thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 for cs in (cs_arm,cs_thumb):cs.detail=True
 for row,name in all_syms:
  if len(probes)>=170:break
  family=next((cat for cat,rx in targets.items() if rx.search(name)),None)
  if family is None:continue
  address=row[1]&~1
  sec=next((s for s in secs if s[0]<=address<s[0]+s[1]),None)
  if sec is None:continue
  idx=bisect.bisect_right(ordered,address)
  nxt=ordered[idx] if idx<len(ordered) else sec[0]+sec[1]
  size=min(1024,nxt-address,sec[0]+sec[1]-address)
  if size<12:continue
  off=sec[2]+address-sec[0]
  instructions=list((cs_thumb if row[1]&1 else cs_arm).disasm(ex[off:off+size],address))
  bl=[]
  for ins in instructions:
   if ins.mnemonic in ('bl','blx'):
    bl.append({'original_callsite_relative_bytes':hex(ins.address-address),
      'original_ARM_call_text':ins.op_str[:70]})
  probes.append({'category':family,'original_cpp_source_symbol':name,
    'original_native_ARM_addr':hex(address),
    'bounded_source_instruction_count':len(instructions),
    'native_source_calls_bounded':bl[:64],
    'real_native_full_behavior_ported_to_vita':False})
 result={
  'origin':'owner user supplied original Gameloft 2010 ARM executable symbol table',
  'NPC_AI_original_named_source_methods':source['NPC_AI'],
  'MISSION_SPAWN_original_named_source_methods':source['MISSION_SPAWN'],
  'VISUAL_GLES_original_named_source_methods':source['VISUAL_GLES'],
  'exact_original_named_CPP_bounded_call_probes':probes,
  'real_NPC_AI_state_machine_integrated_into_B24':False,
  'real_original_mission_wave_script_integrated':False,
  'real_original_iOS_glBlend_light_fixed_function_reproduced':False,
  'ORIGINAL_ARM_IPA_binary_committed':False,'VPK_generated':False}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G121_REAL_2010_NATIVE_NPC_MISSION_RENDER_CPLUSPLUS_SOURCE_SYMBOLS_ONLY.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 print('G121 genuine native 2010 CPP NPC AI',len(source['NPC_AI']),'mission',len(source['MISSION_SPAWN']),
   'visual GLES',len(source['VISUAL_GLES']),'bounded signature call-probes',len(probes))
 for cat,items in source.items():
  print('G121 ORIGINAL',cat,'first 30 source methods:',
    [(x['original_2010_cpp_symbol'],x['source_native_ARM_or_thumb_address']) for x in items[:30]])
 print('G121 AI/renderer functions are real original 2010 names only, no invented runtime behavior or VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path);a=p.parse_args()
 inspect(a.ipa,a.out)
