#!/usr/bin/env python3
"""G137 read real USER ORIGINAL 2010 G27 mission .bclara decoded
metadata, generate exact first prebranch action[] source to native Vita C.
This is source-authentic Lua GETGLOBAL/CALL argument provenance.
Only PC<73 (G135 exact first conditional EQ) is straight-line.
Refuse unrecognized names/bad args instead of fake 'mission complete'.
Owner game IPA/raw bytecode not redistributed and NO VPK.
"""
import argparse,json,re
from pathlib import Path
ENUM={'MissionPause':'MISSION_PAUSE','Show':'SHOW','Hide':'HIDE',
      'Enable':'ENABLE','Disable':'DISABLE','SetState':'SETSTATE',
      'SetInputEnabled':'SETINPUT','PlayVoice':'PLAYVOICE',
      'SetCamera':'SETCAMERA','PauseMusic':'PAUSE_MUSIC',
      'HideUI':'HIDE_UI','BlackScreenOn':'BLACK_SCREEN_ON',
      'PlayMusic':'PLAY_MUSIC','ShowTut':'SHOW_TUT',
      'IsTutConfirmed':'IS_TUT_CONFIRMED'}
def run(source,out):
 d=json.loads(source.read_text())
 assert d['original_native_Lua_GLOBAL_CALL_candidates']==1035
 rows=d['source_lua_static_CALLBACK_instructions_and_id_links']
 assert len(rows)==71
 intro=next(x for x in rows if x['original_callback']=='Mission000_OnStart')
 events=[x for x in intro['original_static_global_CALL_sites']
         if x['source_bytecode_PC']<73]
 assert len(events)==24, 'Original iOS 2010 Mission000 prebranch 24 native Lua API call sites'
 seen=set();lines=[]
 for e in sorted(events,key=lambda x:x['source_bytecode_PC']):
  pc=e['source_bytecode_PC'];name=e['native_global_function']
  args=e['literal_or_statically_tracked_arguments']
  if pc in seen:raise ValueError('G137 duplicate opcode event')
  seen.add(pc)
  if name not in ENUM:raise ValueError('G137 unresolved original authored prebranch Lua native API '+name)
  a0=args[0] if args else 0
  a1=args[1] if len(args)>1 else 0
  a2=args[2] if len(args)>2 else 0
  if not isinstance(a2,(int,float)) or isinstance(a2,bool) or not float(a2).is_integer():
   raise ValueError('G137 original native Lua third argument not exactly numeric '+repr((pc,name,a2)))

  if isinstance(a0,bool) or not isinstance(a0,(int,float)) or (a0 and not float(a0).is_integer()):
   raise ValueError('G137 original Lua arg0 not owner scene identifier '+str((pc,name,a0)))
  if isinstance(a1,str) and not re.fullmatch(r'[A-Za-z_]{1,24}',a1):
   raise ValueError('G137 Lua original string unsafe')
  if a1 is None or isinstance(a1,bool):
   numeric1=0;bool1=int(bool(a1));string1='0'
  elif isinstance(a1,(int,float)) and not isinstance(a1,bool):
   if not float(a1).is_integer():raise ValueError('G137 source arg1 is not native integral')
   numeric1=int(a1);bool1=bool(numeric1);string1='0'
  elif isinstance(a1,str):
   numeric1=0;bool1=0;string1=json.dumps(a1)
  else:raise ValueError('G137 untyped original Lua source arg1')
  lines.append(' { %d, B24_G137_CALL_%s, %d, %d, %d, %s, %d, 1 },'%
   (pc,ENUM[name],int(a0),numeric1,int(a2),string1,int(bool1)))
 actual={(e['source_bytecode_PC'],e['native_global_function']):e for e in events}
 for pc,name,arg0 in ((1,'MissionPause',None),(6,'Show',1456),(34,'SetState',1062),
                       (43,'Hide',1062),(50,'SetInputEnabled',14),(70,'PlayVoice',320)):
  e=actual.get((pc,name))
  if e is None:raise ValueError('G137 missing source opcode '+str((pc,name)))
  if arg0 is not None and int(e['literal_or_statically_tracked_arguments'][0])!=arg0:
   raise ValueError('G137 owner original scene ID mismatch '+str((pc,name)))
 if actual[(34,'SetState')]['literal_or_statically_tracked_arguments'][1]!='idle':
  raise ValueError('G137 actual original MarkV intro idle enum mismatch')
 if actual[(50,'SetInputEnabled')]['literal_or_statically_tracked_arguments'][1] is not False:
  raise ValueError('G137 native Input14 action not false')
 out.parent.mkdir(parents=True,exist_ok=True)
 code='''/* AUTO-GENERATED FROM OWNER ORIGINAL 2010 Level1 Lua actual CALL opcodes.
 * First branch at Lua PC73. DO NOT run PC914/927/935 without source VM.
 * Real owner scripts not committed or redistributed. NO VPK.
 */
#include "b24_g137_source_mission000_intro.h"
const B24G137Event b24_g137_source_lua_events[]={
'''+ '\n'.join(lines)+'''
};
const uint32_t b24_g137_source_lua_event_count=
 sizeof(b24_g137_source_lua_events)/sizeof(b24_g137_source_lua_events[0]);
'''
 out.write_text(code)
 print('G137 original 2010 Mission000 authentic first straight-line PC1..70 source callbacks',len(lines))
 for line in lines:print(line)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--g27',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 run(a.g27,a.out)
