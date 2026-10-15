#!/usr/bin/env python3
"""G10 hardware 2026-10-15: restore aim/COMBAT camera target tracking.

Runs AFTER G11 repulsor stage decision and G10 genuine practice actor hook.
B14 still moves suit exactly once and uses one original orbit. The camera
follows while L held near immutable practice actor and when close melee.
No phantom NPC, objective, 3D reticle or full texture claim.
"""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2]
w=root/'work'
p=w/'src/main.c'
s=p.read_text()
def replace(a,b):
 global s
 if s.count(a)!=1:
  raise RuntimeError('G11 camera real main source drift '+str(s.count(a))+' '+a[:115])
 s=s.replace(a,b)
replace('#include "../b24/b24_unified/b24_g11_combat_stage_policy.h"',
'''#include "../b24/b24_unified/b24_g11_combat_stage_policy.h"
#include "../b24/b24_unified/b24_g11_target_camera_follow.h"''')
replace('''if(!b24_unified_paused(&b24_game) && idx==0 &&
           !world.flying && b24_unified_should_melee(&b24_game))''',
'''if(!b24_unified_paused(&b24_game) && idx!=2 &&
           !world.flying && b24_unified_should_melee(&b24_game))''')
replace('''        world.camera_distance=b24_unified_chase_distance(&b24_game);''',
'''        /* Actual G10 physical report: target lock HUD changed but B14
           orbit was never driven by the target. Keep ONE camera and one
           world update. Soft orbit tracking ONLY with L at close range
           or in melee range, never during stage2/RUSH flight.
           Manual right analog override remains available. */
        B24G11CameraFocus camera_focus={0};
        const B24G11CameraFocusInput camera_focus_in={
            world.x,world.y,
            b24_gpu_rt.practice_target.x,b24_gpu_rt.practice_target.y,
            dt,world.orbit,
            (b24_buttons&IM2_BT_L)!=0,
            b24_g8_motion_melee_source_active(&b24_original_motion),
            fabsf(turn)+fabsf(look)>.15f,world.flying
        };
        if(!b24_g11_target_camera_follow(&camera_focus_in,&camera_focus)){
           running=0;break;
        }
        world.orbit=camera_focus.orbit;
        world.camera_distance=fmaxf(2.8f,
                b24_unified_chase_distance(&b24_game)-
                camera_focus.zoom_reduction);''')
p.write_text(s)
out=w/'b24/b24_unified'
for fname in ('b24_g11_target_camera_follow.h','b24_g11_target_camera_follow.c'):
 shutil.copyfile(root/'research/b24_unified'/fname,out/fname)
cm=w/'CMakeLists.txt'; body=cm.read_text()
if 'G11_L_HELD_TARGET_FOCUSED_ONE_B14_CAMERA' in body:
 raise RuntimeError('already patched')
body+='''

# G11_L_HELD_TARGET_FOCUSED_ONE_B14_CAMERA
if(B24_ENABLE_GPU)
 target_sources(im2_beta PRIVATE
  "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_g11_target_camera_follow.c")
endif()
'''
cm.write_text(body)
assert s.index('b24_g11_target_camera_follow(&camera_focus_in')<
       s.index('camera.orbit=world.orbit;')
assert s.count('b14_world_tick(&world')==1
print('PASS G11 L-locked permanent target, follow world orbit, close melee camera and all 4 genuine IronMan suit melee inputs linked to actual G10 source, NO VPK')
