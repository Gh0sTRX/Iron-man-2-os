#!/usr/bin/env python3
"""G87 source-only integration after G75 -> G84 -> G85:
B14 physics contact feeds the ONE G83/G8 original animation selection owner.
No VPK and no alternative physics, attack or camera systems.
"""
from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
W=R/"work"
D=W/"b24/b24_unified"
GAME=W/"src/main.c"
CM=W/"CMakeLists.txt"
def rep(s,old,new,label):
 count=s.count(old)
 if count!=1:raise RuntimeError(f"G87 {label}: expected one live source match; got {count}")
 return s.replace(old,new,1)
def apply():
 if not GAME.is_file() or not CM.is_file():raise FileNotFoundError("Rebuild G75/G84/G85 first")
 main=GAME.read_text()
 cm=CM.read_text()
 for mark in ("G84_OPTIONAL_TRUE_B24_MAIN","G85_NATIVE_MARKV_629","G75_SOURCE_ONLY_GAMEPLAY_RECOVERY"):
  if mark not in main:raise RuntimeError("G87 real merged gameplay prerequisite missing: "+mark)
 if "B24_G87_REAL_TRANSITION_EVENTS" in main:raise RuntimeError("G87 already applied; no duplicate event owner")
 if main.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1:
  raise RuntimeError("G87 cannot patch duplicate or missing B14 physical owner")
 if main.count("b24_g83_timeline_tick(")!=1 or main.count("b24_g8_motion_tick_g84(")!=1:
  raise RuntimeError("G87 must preserve exactly ONE G83 timeline and G8 pose player")
 main=rep(main,"static B24G83Timeline g84_time={0};",'''static B24G83Timeline g84_time={0};
#ifdef B24_G87_REAL_TRANSITION_EVENTS
#include "../b24/b24_unified/b24_g87_transition_events.h"
static B24G87TransitionState g87_events={0};
#endif''',"single G84 timeline state")
 main=rep(main,"b24_g83_timeline_reset(&g84_time);",'''b24_g83_timeline_reset(&g84_time);
#ifdef B24_G87_REAL_TRANSITION_EVENTS
             b24_g87_transition_reset(&g87_events);
#endif''',"armor change state reset")
 main=rep(main,"g84_input.grounded_contact_verified=0;",'''#ifdef B24_G87_REAL_TRANSITION_EVENTS
          /* Physics and floor contact from the SAME G75/G68 original
             triangle world. Flight mode OFF alone proves no landing.
             Never sample made-up ground height or teleport into floors. */
          float g87_source_floor=0.f;
#ifdef B24_G75_SOURCE_CAPSULE
          g84_input.grounded_contact_verified=(!world.flying &&
               b24_g74_near_original_floor(&b24_original_walls,
                world.x,world.y,world.z,&g87_source_floor) &&
               fabsf(world.z-g87_source_floor)<=.08f);
#else
          /* Without the original source-backed floor resolver, fail closed:
             transition can be selected but landing is never invented. */
          g84_input.grounded_contact_verified=0;
#endif
          g84_input.transition=b24_g87_transition_tick(&g87_events,
               g84_input.motion,g84_input.grounded_contact_verified,0);
#else
          g84_input.grounded_contact_verified=0;
#endif''',"sourced ground-contact event injection")
 for name in ("b24_g87_transition_events.h","b24_g87_transition_events.c"):
  shutil.copyfile(HERE/name,D/name)
 cm+='''

# G87 optional source-backed, ONE-WORLD flight transition events.
# Default OFF. No release packaging permitted during source QA.
option(B24_G87_REAL_TRANSITION_EVENTS "Original C1L1 grounded flight/hover event routing" OFF)
if(B24_G87_REAL_TRANSITION_EVENTS)
 if(NOT B24_G84_ORIGINAL_MOVESET_ROUTER)
  message(FATAL_ERROR "G87 requires single original G83/G8 movement owner")
 endif()
 target_sources(im2_beta PRIVATE
  "b24/b24_unified/b24_g87_transition_events.c")
 target_compile_definitions(im2_beta PRIVATE B24_G87_REAL_TRANSITION_EVENTS=1)
endif()
'''
 assert main.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")==1
 assert main.count("b24_g83_timeline_tick(")==1
 assert main.count("b24_g8_motion_tick_g84(")==1
 assert main.count("b24_g87_transition_tick(")==1
 assert main.count("b24_g75_capsule_reconcile(")==1
 if list(W.rglob("*.vpk")):raise RuntimeError("G87 absolutely forbids any VPK")
 GAME.write_text(main)
 CM.write_text(cm)
 print("PASS G87 real G75/G84/G85 main source: same B14 world, source polygon verified landing, one G83 timeline/G8 pose, MarkVI/MarkV/WM safe, no VPK")
if __name__=="__main__":apply()
