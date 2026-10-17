#!/usr/bin/env python3
"""G147 original 2010 Lua ShowTut(339,13,0) and IsTutConfirmed()
source-native call guard applied ONLY after canonical already-successful
G145/G146 true single-game / typed QTE 1456 optional Vita integration.
No synthetic tutorial success, no guessed translated text ID339, no
invented PC73 Lua control flow. Native UI logic is attached but
unresolved original font rendering/StringMgr binding => fail closed.
NO new VPK.
"""
from pathlib import Path
import shutil
HERE=Path(__file__).resolve().parent
R=HERE.parents[2]
W=R/'work'
D=W/'b24/b24_unified'
M=W/'src/main.c';CM=W/'CMakeLists.txt'
def one(s,a,z):
 if s.count(a)!=1:raise ValueError('G147 canonical G146 source drift count '+str(s.count(a))+' '+repr(a[:95]))
 return s.replace(a,z,1)
def run():
 if not M.is_file() or not CM.is_file():
  raise FileNotFoundError("G147 needs canonical G146 one-Vita C1L1 assembled sources")
 m=M.read_text();cm=CM.read_text()
 assert 'B24_G145_SOURCE_MISSION_AUDIO' in cm
 assert 'B24_G146_SOURCE_2010_QTE_1456' in cm
 assert m.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')==1
 assert m.count('b24_unified_tick(&b24_game,&b24_obs);')==1
 assert m.count('b24_g83_timeline_tick(')==1
 if 'B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE' in cm:
  raise ValueError('G147 duplicate source')
 for file in ('b24_g147_authentic_tutorial_actor.h','b24_g147_authentic_tutorial_actor.c'):
  shutil.copyfile(HERE/file,D/file)
 m=one(m,
   '#include "../b24/b24_unified/b24_g146_true_2010_QTE_actor.h"',
   '#include "../b24/b24_unified/b24_g146_true_2010_QTE_actor.h"\n#ifdef B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE\n#include "../b24/b24_unified/b24_g147_authentic_tutorial_actor.h"\n#endif')
 m=one(m,
   'static B24G146QTE g146_real_2010_actor_QTE1456;',
   'static B24G146QTE g146_real_2010_actor_QTE1456;\n#ifdef B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE\nstatic B24G147Tutorial g147_original_L1_source_tutorial;\nstatic int g147_native_Lua_PC72_queried_only=0;\nstatic int g147_native_PC72_original_result=0;\n#endif')
 m=one(m,
   ' return b24_g142_owner_source_music_call(music,e);',
   '''#ifdef B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE
 if(e->original_lua_pc==67&&e->opcode==B24_G137_CALL_SHOW_TUT){
  /* Original 2010 TextID339 must be resolved via StringMgr native
   * strIDClara2Real first. The real UI tutorial renderer and fonts
   * are NOT bound; never pass invented translation or ack the call. */
  return b24_g147_lua_ShowTut_PC67(
      &g147_original_L1_source_tutorial,e,NULL,NULL,NULL);
 }
 if(e->original_lua_pc==72&&e->opcode==B24_G137_CALL_IS_TUT_CONFIRMED){
  /* Real ARM native Lua query returns boolean; existing G137
   * event dispatcher C API cannot deliver Lua VM return values.
   * Track source semantics for diagnostics, but do not infer PC73
   * EQ branch, MissionResume, or player flight authorization. */
  g147_native_Lua_PC72_queried_only=1;
  g147_native_PC72_original_result=
    b24_g147_lua_IsTutConfirmed_native(&g147_original_L1_source_tutorial);
  return 0;
 }
#endif
 return b24_g142_owner_source_music_call(music,e);''')
 m=one(m,
   '(void)b24_g146_qte_source_init(&g146_real_2010_actor_QTE1456);',
   '''(void)b24_g146_qte_source_init(&g146_real_2010_actor_QTE1456);
#ifdef B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE
            b24_g147_tutorial_init(&g147_original_L1_source_tutorial);
#endif''')
 cm+='''
# G147 native verified original ARM ShowTut PC67 via source StringMgr,
# GamePlayUI::ShowTutorial offsets+1E38/+1E3C/+1E40 and
# IsTutConfirmed PC72 boolean (override || activeID == -1).
# Actual renderer and source StringMgr text table NOT yet bound;
# do not fake QTE id1456 success/PC73 native Lua branch.
option(B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE "Bind authentic 2010 ShowTut and IsTutConfirmed source contract in ONE G146 original Vita game" OFF)
if(B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE)
 if(NOT B24_G146_SOURCE_2010_QTE_1456)
  message(FATAL_ERROR "G147 depends on real original iOS QTE1456 source gate G146")
 endif()
 target_sources(im2_beta PRIVATE
   "b24/b24_unified/b24_g147_authentic_tutorial_actor.c")
 target_compile_definitions(im2_beta PRIVATE
   B24_G147_NATIVE_LUA_TUTORIAL_SOURCE_GATE=1)
endif()
'''
 M.write_text(m);CM.write_text(cm)
 assert not list(W.rglob('*.vpk'))
 print('G147 original native 2010 tutorial PC67 ShowTut text339 / UI mode12 and PC72 IsTutConfirmed global-or-ID-1 guard linked into canonical G146 one native game; no fake render/controller approval, NO VPK')
if __name__=='__main__':run()
