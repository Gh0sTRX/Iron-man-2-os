#!/usr/bin/env python3
"""G92 opt-in REAL B24 Vita native single-main static INDESTRUCTIBLE dummy.
Run AFTER G75 G84 G85 G87 owner-original source assembly. Place once on
genuine source-backed G68/G75 collision floor; render within existing B24
VitaGL frame; an input-proximity gold flash is DIAGNOSTIC feedback ONLY.
Reuses REAL previous G10 & G11 source C (not invented NPC).
No original hit frame, numerical damage, AI or weapon event invented.
OFF by default. NEVER a new VPK.
"""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[3]
W=ROOT/'work';D=W/'b24/b24_unified'
M=W/'src/main.c';H=D/'b24_gpu_runtime.h'
R=D/'b24_gpu_runtime.c';CM=W/'CMakeLists.txt'
def once(s,a,b,location):
 n=s.count(a)
 if n!=1:raise ValueError('G92 source drift '+location+' matched='+str(n)+' expected '+repr(a[:75]))
 return s.replace(a,b,1)
def apply():
 for p in (M,H,R,CM):
  if not p.is_file():raise FileNotFoundError('G92 requires built G75/G84/G85/G87 physical game: '+str(p))
 main=M.read_text();header=H.read_text();runtime=R.read_text();cm=CM.read_text()
 for expect in ('G84_OPTIONAL_TRUE_B24_MAIN','B24_G85_NATIVE_MARKV_629','B24_G87_REAL_TRANSITION_EVENTS'):
  if expect not in main:raise ValueError('G92 source precondition missing: '+expect)
 if 'G92_STATIC_DUMMY_SOURCE_IN_SINGLE_MAIN' in main:
  raise ValueError('G92 may only patch physical main ONCE')
 if main.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')!=1:
  raise ValueError('G92 cannot create a second physical movement owner')
 if main.count('b24_g8_motion_repulsor_trigger(')!=1 or main.count('b24_g8_motion_melee_trigger(')!=1:
  raise ValueError('G92 cannot duplicate an original 2010 weapon event')
 if main.count('b24_g83_timeline_tick(')!=1:
  raise ValueError('G92 requires ONLY ONE authored movement timeline')
 # Include once inside protected GPU runtime (owned by original B24).
 header=once(header,'#include "b24_gpu_owner.h"',
   '#include "b24_gpu_owner.h"\n#ifdef B24_G92_STATIC_DUMMY_SOURCE_PREVIEW\n#include "b24_g10_practice_target.h"\n#endif','runtime header')
 header=once(header,' B24GpuC1Mesh city;',
   '''#ifdef B24_G92_STATIC_DUMMY_SOURCE_PREVIEW
 B24G10PracticeTarget g92_practice_dummy;
#endif
 B24GpuC1Mesh city;''','runtime data model')
 # Runtime include layout changed with the G68 backend; append a safe guarded
 # include instead of coupling the debug actor to legacy G10 contact code.
 if '#include "b24_g10_practice_target.h"' in runtime:
  raise ValueError('G92 target declaration already present in renderer')
 runtime='#ifdef B24_G92_STATIC_DUMMY_SOURCE_PREVIEW\n#include "b24_g10_practice_target.h"\n#endif\n'+runtime
 # Render only AFTER the existing original C1L1 GPU city and before next HUD.
 # In an uninitialized source world do not conjure a dummy in the void.
 runtime=once(runtime,' if(!r->frames)(void)b24_gpu_boot_trace_mark("44 SCENE_DRAW_OK");',
   '''#ifdef B24_G92_STATIC_DUMMY_SOURCE_PREVIEW
 /* The source G75 collision sampler must have explicitly found authentic
  * G68 ground before the G10 practice target can become visible. */
 if(b24_g10_practice_target_valid(&r->g92_practice_dummy))
  (void)b24_g10_practice_target_draw(&r->g92_practice_dummy);
#endif
 if(!r->frames)(void)b24_gpu_boot_trace_mark("44 SCENE_DRAW_OK");''',
   'original one scene pass city to player target')
 main=once(main,'#include "../b24/b24_unified/b24_g75_source_capsule.h"',
   '''#include "../b24/b24_unified/b24_g75_source_capsule.h"
#ifdef B24_G92_STATIC_DUMMY_SOURCE_PREVIEW
#include "../b24/b24_unified/b24_g10_practice_target.h"
#include "../b24/b24_unified/b24_g11_practice_melee_feedback.h"
/* G92_STATIC_DUMMY_SOURCE_IN_SINGLE_MAIN */
static B24G11PracticeMeleeFeedback g92_debug_feedback={0};
static int g92_debug_floor_found=0;
/* Shared accepted source G8 combat edge; diagnostic never polls it twice. */
static unsigned g92_debug_accepted_melee_edge=0;
#endif''','main include')
 anchor='''        b24_unified_tick(&b24_game,&b24_obs);
#ifdef B24_GPU_ENGINE'''
 change='''        b24_unified_tick(&b24_game,&b24_obs);
#ifdef B24_G92_STATIC_DUMMY_SOURCE_PREVIEW
        /* Exactly ONE debug target; initially invalid until ORIGINAL 2010
           G68 collision surface proves placement. Never fake an invisible
           support plane. Fixed for the remainder of this test session. */
        if(!g92_debug_floor_found && b24_original_walls.ready){
          const float xx[]={0.f,world.x,world.x+5.f,world.x-5.f};
          const float yy[]={10.f,world.y+5.f,world.y,world.y};
          for(unsigned candidate=0;candidate<4;candidate++){
            float zfloor=0.f;
            if(!b24_g75_floor_crossed(&b24_original_walls,
                  xx[candidate],yy[candidate],world.z+2.f,
                  world.z-5.f,&zfloor))continue;
            B24G10PracticeTarget demo=b24_g10_practice_target_at_floor(zfloor);
            demo.x=xx[candidate];demo.y=yy[candidate];
            if(!b24_g10_practice_target_valid(&demo))continue;
            b24_gpu_rt.g92_practice_dummy=demo;
            g92_debug_floor_found=1;
            break;
          }
        }
        if(g92_debug_floor_found &&
           !b24_unified_paused(&b24_game)&&!world.flying&&
           (idx==0||idx==4)&&g92_debug_accepted_melee_edge){
           (void)b24_g11_practice_melee_hit(&g92_debug_feedback,
             &b24_gpu_rt.g92_practice_dummy,
             world.x,world.y,world.z,(uint32_t)now,1,1);
        }
        if(g92_debug_floor_found)
          b24_gpu_rt.g92_practice_dummy.hit_flash=
            b24_g11_practice_hit_flash(&g92_debug_feedback,(uint32_t)now);
        g92_debug_accepted_melee_edge=0; /* one consumed debug latch */
        /* ORIGINAL HP/mission data/weapon fire events remain untouched. */
#endif
#ifdef B24_GPU_ENGINE'''
 main=once(main,anchor,change,'original actual single game loop post tick')

 # G93: older G92 polled b24_unified_should_melee TWICE and might lose
 # the authentic accepted game input edge. Capture the actual one G8
 # melee acceptance and consume it once in the same/next frame.
 import re
 call_pattern=r'(?m)^(?P<indent>[ \t]*)b24_g8_motion_melee_trigger\((?P<args>[^;\n]*)\);'
 matches=list(re.finditer(call_pattern,main))
 if len(matches)!=1:
  raise ValueError('G93 requires 1 real B24 G8 melee call, got '+str(len(matches)))
 found=matches[0]
 indent=found.group('indent')
 native_call=found.group(0).strip()
 replacement=(indent+'{\n'+indent+' '+native_call+'\n'
   +indent+'#ifdef B24_G92_STATIC_DUMMY_SOURCE_PREVIEW\n'
   +indent+' g92_debug_accepted_melee_edge=1;\n'
   +indent+'#endif\n'+indent+'}')
 main=main[:found.start()]+replacement+main[found.end():]
 assert main.count('b24_g8_motion_melee_trigger(')==1
 # G85's MarkV opt-in has TWO mutually-exclusive compile branches with
 # identical source input condition; only ONE is live in the G92 ARM build.
 # The dummy must NEVER add a third should_melee poll.
 assert main.count('b24_unified_should_melee(&b24_game)')==2
 assert 'g92_debug_accepted_melee_edge' in main
 assert main.count('g92_debug_accepted_melee_edge=1;')==1
 for name in ('b24_g10_practice_target.h','b24_g10_practice_target.c',
              'b24_g10_practice_target_vitagl.c',
              'b24_g11_practice_melee_feedback.h',
              'b24_g11_practice_melee_feedback.c'):
  shutil.copyfile(ROOT/'research/b24_unified'/name,D/name)
 cm+='''
# G92 user-approved source-only one immortal target in the actual B24 G68 game.
# No second B14 tick, NO original iOS enemy AI, no original hit active frames.
option(B24_G92_STATIC_DUMMY_SOURCE_PREVIEW "Source floor-grounded training dummy, never real NPC" OFF)
if(B24_G92_STATIC_DUMMY_SOURCE_PREVIEW)
 if(NOT B24_ENABLE_GPU OR NOT B24_G75_SOURCE_CAPSULE OR NOT B24_G87_REAL_TRANSITION_EVENTS OR NOT B24_G85_NATIVE_MARKV_629)
  message(FATAL_ERROR "G92 requires source-only genuine G68/G75/G85/G87 GPU stage")
 endif()
 target_compile_definitions(im2_beta PRIVATE B24_G92_STATIC_DUMMY_SOURCE_PREVIEW=1)
 target_sources(im2_beta PRIVATE
  "b24/b24_unified/b24_g10_practice_target.c"
  "b24/b24_unified/b24_g10_practice_target_vitagl.c"
  "b24/b24_unified/b24_g11_practice_melee_feedback.c")
endif()
'''
 for path,txt in ((M,main),(H,header),(R,runtime),(CM,cm)):
  path.write_text(txt)
 assert not list(W.rglob('*.vpk'))
 assert main.count('b24_g11_practice_melee_hit(')==1
 assert main.count('b24_g75_floor_crossed(')==1
 assert main.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')==1
 print('PASS G92 real Vita G75/G84/G85/G87 single main: SOURCE 2010 floor grounded static immortal dummy + original G10 visible mesh and G11 debug-only hit flash; 1 B14+G8+G83 owner, default OFF, NO VPK')
if __name__=='__main__':apply()
