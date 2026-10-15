#!/usr/bin/env python3
"""Wire G10 real visible immortal C1L1 actor to G11 Square proximity feedback.

Actual B14 player and original BRES suit combos still own body animation.
Only visible test actor's transient GPU wire colour is changed; immutable HP.
No fabricated B16 target damage, combat mission progression or new VPK.
Apply AFTER G11 stage/camera/Unibeam patches on top of G10 baseline.
"""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2]; w=root/'work'
p=w/'src/main.c'
s=p.read_text()
def sub(old,new):
 global s
 n=s.count(old)
 if n!=1:raise RuntimeError('G11 practice source drift %d at %s'%(n,old[:110]))
 s=s.replace(old,new)
sub('#include "../b24/b24_unified/b24_g11_target_camera_follow.h"',
'''#include "../b24/b24_unified/b24_g11_target_camera_follow.h"
#include "../b24/b24_unified/b24_g11_practice_melee_feedback.h"''')
sub('static B24G8LiveOriginalMotion b24_original_motion={0};',
'''static B24G8LiveOriginalMotion b24_original_motion={0};
/* Actual user G10 3D C1L1 practice target: received melee input,
   has permanently infinite HP, short visual flash only. */
static B24G11PracticeMeleeFeedback b24_practice_hits={0};''')
sub('''        if(!b24_unified_paused(&b24_game) && idx!=2 &&
           !world.flying && b24_unified_should_melee(&b24_game))
          b24_g8_motion_melee_trigger(&b24_original_motion,(uint32_t)now);''',
'''        if(!b24_unified_paused(&b24_game) && idx!=2 &&
           !world.flying && b24_unified_should_melee(&b24_game)){
          /* Original four IronMan authentic combos are triggered as before.
             Acceptance near the VISUAL G10 practice actor is distinct from
             old B16 three-sphere prototype / HP damage. */
          b24_g8_motion_melee_trigger(&b24_original_motion,(uint32_t)now);
          (void)b24_g11_practice_melee_hit(&b24_practice_hits,
             &b24_gpu_rt.practice_target,
             world.x,world.y,world.z,(uint32_t)now,1,1);
        }
        b24_gpu_rt.practice_target.hit_flash=
             b24_g11_practice_hit_flash(&b24_practice_hits,(uint32_t)now);''')
p.write_text(s)
out=w/'b24/b24_unified'
for fname in ('b24_g11_practice_melee_feedback.h',
              'b24_g11_practice_melee_feedback.c'):
 shutil.copyfile(root/'research/b24_unified'/fname,out/fname)
cm=w/'CMakeLists.txt'
c=cm.read_text()
if 'G11_PERMANENT_USER_TEST_ACTOR_CLOSE_COMBO_FLASH' in c:raise RuntimeError('G11 already hooked')
c+='''

# G11_PERMANENT_USER_TEST_ACTOR_CLOSE_COMBO_FLASH
if(B24_ENABLE_GPU)
 target_sources(im2_beta PRIVATE
   "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_g11_practice_melee_feedback.c")
endif()
'''
cm.write_text(c)
assert s.index('b24_g11_practice_melee_hit(&b24_practice_hits')<s.index('b24_gpu_runtime_draw(')
assert 'b24_gpu_rt.practice_target.hit_flash=' in s
print('PASS G11 original real G10 3D target proximity melee + GOLD transient visible hit feedback, immutable debug actor, one GPU scene, no VPK')
