#!/usr/bin/env python3
"""G137 integrate verified iOS 2010 Mission000 OnStart original Lua first
linear prefix PC<73 (mission pause, QTE scene, Deco, idle actor, input14)
into already assembled ONE Vita game main under opt-in source flag.
IMPORTANT: only MissionPause scoped state is currently ACTUALLY bound;
2010 PauseMusic PC3 is first unbound native action; QTE PC6 and
Deco/Camera engine callbacks remain unavailable. Fail closed at PC3.
No fake autoplay PC914/927 and no invented flight unlock/mission resume.
This is a live hooked, source-ID-correct in-game dispatcher, not a complete
Lua VM or implemented original mission. No VPK.
"""
from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[3];W=R/'work'
D=W/'b24/b24_unified';M=W/'src/main.c';CM=W/'CMakeLists.txt'
HERE=Path(__file__).resolve().parent
def one(text,old,new):
 if text.count(old)!=1:raise ValueError("G137 source main anchor drift "+str(text.count(old))+" "+repr(old[:70]))
 return text.replace(old,new,1)
def patch():
 if not M.is_file() or not CM.is_file():
  raise FileNotFoundError("G137 real G136B source complete required")
 main=M.read_text();cm=CM.read_text()
 assert main.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')==1
 assert main.count('b24_unified_tick(&b24_game,&b24_obs);')==1
 assert main.count('b24_g83_timeline_tick(')==1
 assert 'B24_G136_SOURCE_B14_WORLD_BOUNDS' in cm
 if 'B24_G137_MISSION000_REAL_SOURCE_EVENTS' in cm:raise ValueError('duplicate source mission')
 generated=D/'b24_g137_mission000_owner_original_generated.c'
 if not generated.is_file():raise ValueError('Original G27 source intro event generator must run first')
 for name in ('b24_g137_source_mission000_intro.h','b24_g137_source_mission000_intro.c'):
  shutil.copyfile(HERE/name,D/name)
 # The original 2010 MissionPause flag is modeled in G137 action state.
 # Unknown actual QTE/Deco, Show/Hide scene bindings MUST return false;
 # never start the game paused and unresumable due to a dummy QTE timer.
 include='''#include "../b24/b24_unified/b24_g137_source_mission000_intro.h"
/* G137 native original 2010 level1 Lua Mission000OnStart SOURCE EVENTS:
 * on first real game tick, dispatch authentic linear first branch.
 * MissionPause is scoped to scripted task journal; player physics is
 * untouched until real QTE scene object and valid original input actions
 * have native bindings (so existing practice viewer stays testable). */
#ifdef B24_G137_MISSION000_REAL_SOURCE_EVENTS
static B24G137Mission000 g137_real_source_Mission000;
static int g137_real_source_initialized=0;
static int g137_real_scene_MissionPause_only(void *ctx,const B24G137Event *e){
 (void)ctx;
 /* Request is original source. No invented scene entity/QTE binding.
  * Actual mission task paused state tracked by dispatch state, not B14
  * gameplay global pause; original MissionPause != freeze entire game. */
 return e&&e->opcode==B24_G137_CALL_MISSION_PAUSE;
}
#endif
'''
 # Put include after header includes before functions using stable anchor. 
 anchor='#include "../b24/b24_unified/b24_g75_source_capsule.h"' 
 main=one(main,anchor,anchor+'\n#ifdef B24_G137_MISSION000_REAL_SOURCE_EVENTS\n'+include+'#endif') 
 action='''        b24_unified_tick(&b24_game,&b24_obs);
#ifdef B24_G137_MISSION000_REAL_SOURCE_EVENTS
        if(!g137_real_source_initialized){
          g137_real_source_initialized=1;
          if(b24_g137_mission000_init(&g137_real_source_Mission000))
            (void)b24_g137_mission000_dispatch_verified_prefix(
               &g137_real_source_Mission000,
               g137_real_scene_MissionPause_only,NULL);
        }
        /* PauseMusic at PC3 and QTE ID1456 Show at PC6 lack a bound
         * native scene/audio API: retain first unsupported source PC and
         * do not fabricate camera/Deco visibility, MarkV flight rights,
         * PC914/927 UI unlock or MissionResume PC935. */
#endif
''' 
 main=one(main,'        b24_unified_tick(&b24_game,&b24_obs);',action) 
 cm+='''

# G137 first actual original 2010 native Mission000 source intro events
# for PC<73 linked into EXISTING player/physics main. OFF by default.
# PauseMusic is first unavailable native binding at PC3; never skip it
# just to display QTE ID1456 at PC6.
option(B24_G137_MISSION000_REAL_SOURCE_EVENTS "Link source-proven 2010 Level1 Mission000 prefirst branch events into real game, fail-closed native audio/QTE, not original full Lua VM" OFF)
if(B24_G137_MISSION000_REAL_SOURCE_EVENTS)
 if(NOT B24_G136_SOURCE_B14_WORLD_BOUNDS OR NOT B24_G127_ORIGINAL_STATESMGR_SOURCE)
  message(FATAL_ERROR "G137 full original Mission000 needs current one G136B source world and G127 class runtime")
 endif()
 target_compile_definitions(im2_beta PRIVATE B24_G137_MISSION000_REAL_SOURCE_EVENTS=1)
 target_sources(im2_beta PRIVATE
  "b24/b24_unified/b24_g137_source_mission000_intro.c"
  "b24/b24_unified/b24_g137_mission000_owner_original_generated.c")
endif()
'''
 M.write_text(main);CM.write_text(cm)
 assert not list(W.rglob('*.vpk'))
 print("G137 owner REAL 2010 Level1 Lua native Mission000 PC1 MissionPause bound inside actual B24 main; source PauseMusic unbound PC3 (QTE Show PC6 likewise) remains blocked, no invented NPC/camera/no fake first flight unlock/mission resume, NO VPK")
if __name__=='__main__':patch()
