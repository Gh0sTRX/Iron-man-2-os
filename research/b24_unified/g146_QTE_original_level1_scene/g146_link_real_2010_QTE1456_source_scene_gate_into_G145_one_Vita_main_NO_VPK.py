#!/usr/bin/env python3
"""G146 source-authentic typed InteractiveObj_QTE ID1456 class94 and
original position into same real G145 Vita C game, WITHOUT INVENTING
a fake QTE texture/button/gameplay completion. Original first Lua
Mission000 PC6 Show(1456) is recorded pending; ACK only after actual
2010 QTE UI scene renderer callback eventually exists. NO VPK.
"""
from pathlib import Path
import shutil
HERE=Path(__file__).resolve().parent
R=HERE.parents[2];W=R/'work';D=W/'b24/b24_unified'
M=W/'src/main.c';CM=W/'CMakeLists.txt'
def once(s,old,new):
 if s.count(old)!=1:raise ValueError("G146 source drift "+str(s.count(old))+" "+old[:75])
 return s.replace(old,new,1)
def run():
 if not M.is_file() or not CM.is_file():raise FileNotFoundError("G146 needs one G145 gameplay source first")
 main=M.read_text();cm=CM.read_text()
 assert 'B24_G145_SOURCE_MISSION_AUDIO' in cm
 assert main.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")==1
 assert main.count("b24_unified_tick(&b24_game,&b24_obs);")==1
 assert main.count("b24_g83_timeline_tick(")==1
 if 'B24_G146_SOURCE_2010_QTE_1456' in cm:raise ValueError("duplicate")
 for name in ('b24_g146_true_2010_QTE_actor.h','b24_g146_true_2010_QTE_actor.c'):
  shutil.copyfile(HERE/name,D/name)
 main=once(main,
  '#include "../b24/b24_unified/b24_g144_source_audio_channels.h"',
  '#include "../b24/b24_unified/b24_g144_source_audio_channels.h"\n#ifdef B24_G146_SOURCE_2010_QTE_1456\n#include "../b24/b24_unified/b24_g146_true_2010_QTE_actor.h"\n#endif')
 main=once(main,
  'static B24G144NativeAudio g145_original_vita_channels;',
  'static B24G144NativeAudio g145_original_vita_channels;\n#ifdef B24_G146_SOURCE_2010_QTE_1456\nstatic B24G146QTE g146_real_2010_actor_QTE1456;\n#endif')
 main=once(main,
  ' return b24_g142_owner_source_music_call(music,e);',
  '''#ifdef B24_G146_SOURCE_2010_QTE_1456
 if(e->original_lua_pc==6&&e->opcode==B24_G137_CALL_SHOW)
  return b24_g146_qte_show_source_Lua_PC6(
    &g146_real_2010_actor_QTE1456,e,NULL,NULL);
 /* Actual QTE widget renderer has NOT been linked yet, so PC6 must
  * remain blocked. This stores exact sourced actor visibility request. */
#endif
 return b24_g142_owner_source_music_call(music,e);''')
 main=once(main,
   '            b24_g144_source_audio_init(&g145_original_vita_channels);',
   '''            b24_g144_source_audio_init(&g145_original_vita_channels);
#ifdef B24_G146_SOURCE_2010_QTE_1456
            (void)b24_g146_qte_source_init(&g146_real_2010_actor_QTE1456);
#endif''')
 cm+='''
# G146 map actual 2010 first mission PC6 Show(1456) to its REAL
# class94 original InteractiveObj + source child1458 local XYZ/Quat.
# NO fabricated Vita QTE renderer or fictitious user success.
option(B24_G146_SOURCE_2010_QTE_1456 "Native typed original 2010 InteractiveObj QTE ID1456 scene source and Lua PC6 Show demand in G145 game" OFF)
if(B24_G146_SOURCE_2010_QTE_1456)
 if(NOT B24_G145_SOURCE_MISSION_AUDIO)
  message(FATAL_ERROR "G146 source-original first QTE requires G145 original mission/audio main")
 endif()
 target_sources(im2_beta PRIVATE
   "b24/b24_unified/b24_g146_true_2010_QTE_actor.c")
 target_compile_definitions(im2_beta PRIVATE B24_G146_SOURCE_2010_QTE_1456=1)
endif()
'''
 M.write_text(main);CM.write_text(cm)
 if list(W.rglob('*.vpk')):raise RuntimeError('NO NEW VPK')
 print('G146 owner typed 2010 Level1 original InteractiveObj_QTE ID1456 class94 in ONE B14 G145 game source at real native PC6 Show, no fake QTE scene completion, no VPK.')
if __name__=='__main__':run()
