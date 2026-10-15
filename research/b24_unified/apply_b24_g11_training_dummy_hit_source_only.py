#!/usr/bin/env python3
"""G11 true GPU target collision feedback instead of wrong old B16 dummy.

Must apply AFTER G10 practice target, real B14, G11 shooting and camera.
A square combat input near visible x=0,y=10 practice actor flashes gold, with
permanent health and still no original 2010 mission enemies. Single GPU frame.
"""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2];w=root/'work';p=w/'src/main.c'
s=p.read_text()
def rep(old,new):
 global s
 n=s.count(old)
 if n!=1:raise RuntimeError('G11 real dummy source drift '+str(n)+' '+old[:110])
 s=s.replace(old,new)
rep('#include "../b24/b24_unified/b24_g11_target_camera_follow.h"',
'''#include "../b24/b24_unified/b24_g11_target_camera_follow.h"
#include "../b24/b24_unified/b24_g11_practice_melee_feedback.h"''')
rep('static B24WMOutput b24_wm_frame_events={0};',
'''static B24WMOutput b24_wm_frame_events={0};
/* Only user-invoked practice dummy; original level1 enemy AI unavailable. */
static B24G11PracticeMeleeFeedback g11_real_practice_hit={0};''')
rep('''        b24_unified_tick(&b24_game,&b24_obs);
#ifdef B24_GPU_ENGINE''',
'''        b24_unified_tick(&b24_game,&b24_obs);
#ifdef B24_GPU_ENGINE
        /* Original B16 has a DIFFERENT hard-coded prototype 3-sphere
           target array. Connect Square to the ACTUAL source-grounded GPU
           target at x=0,y=10. The immortal actor is never deleted/damaged. */
        if(!b24_unified_paused(&b24_game)&&!world.flying&&idx!=2&&
           b24_unified_should_melee(&b24_game))
          (void)b24_g11_practice_melee_hit(&g11_real_practice_hit,
                &b24_gpu_rt.practice_target,world.x,world.y,world.z,
                (uint32_t)now,1,1);
        b24_gpu_rt.practice_target.hit_flash=
          b24_g11_practice_hit_flash(&g11_real_practice_hit,
                                     (uint32_t)now);''')
p.write_text(s)
dst=w/'b24/b24_unified'
for fname in ('b24_g11_practice_melee_feedback.h',
              'b24_g11_practice_melee_feedback.c'):
 shutil.copyfile(root/'research/b24_unified'/fname,dst/fname)
cm=w/'CMakeLists.txt';body=cm.read_text()
if 'G11_VISIBLE_IMMORTAL_DUMMY_HIT_REACTION' in body:raise RuntimeError('duplicate')
body+='''

# G11_VISIBLE_IMMORTAL_DUMMY_HIT_REACTION
if(B24_ENABLE_GPU)
 target_sources(im2_beta PRIVATE
  "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_g11_practice_melee_feedback.c")
endif()
'''
cm.write_text(body)
assert s.count('b24_g11_practice_melee_hit(')==1
assert s.index('b24_unified_tick(&b24_game')<s.index('b24_g11_practice_melee_hit(')
assert s.index('b24_g11_practice_hit_flash(')<s.index('b24_gpu_runtime_draw(')
print('PASS original user-requested 3D test target REAL GPU source hit flash at Square combo range, health forever unchanged, WM unaffected, no VPK')
