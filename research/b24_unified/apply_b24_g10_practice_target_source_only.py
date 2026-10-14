#!/usr/bin/env python3
"""G10 user-requested physical Vita practice target: first C1L1 center.

Visible source grounded neon target in the *same* VitaGL frame/world, and
B23 L-held lock on any weapon when ID==910; permanently invulnerable.
No hidden enemy simulation, no invented original mission content.
Only apply after G10 true-ground and G9 full motion/GPU source bridge.
"""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[2];W=ROOT/"work"
def patch(relative,old,new):
 p=W/relative
 s=p.read_text()
 if s.count(old)!=1:raise RuntimeError(f"G10 practice target integration source drift {relative}: {s.count(old)} {old[:90]!r}")
 p.write_text(s.replace(old,new))
patch("b24/b24_unified/b24_gpu_runtime.h",
 '#include "b24_gpu_owner.h"',
 '''#include "b24_gpu_owner.h"
#include "b24_g10_practice_target.h"''')
patch("b24/b24_unified/b24_gpu_runtime.h",
 ' B24GpuC1Mesh city;',
 ' B24G10PracticeTarget practice_target; /* visible, immortal USER TEST dummy */\n B24GpuC1Mesh city;')
patch("b24/b24_unified/b24_gpu_runtime.c",
 '#include "b24_g10_original_foot_contact.h"',
 '''#include "b24_g10_original_foot_contact.h"
#include "b24_g10_practice_target.h"
#include "b24_c1_true_source_floor.h"''')
patch("b24/b24_unified/b24_gpu_runtime.c",
 ''' (void)b24_gpu_boot_trace_mark("21 C1G2_LOAD_OK");''',
 ''' (void)b24_gpu_boot_trace_mark("21 C1G2_LOAD_OK");
 /* Never invent a fake floor: original C1L1 B11 ground must actually
    contain the map-center practice object's footprint. */
 float original_practice_floor=0.f;
 if(!b24_c1_true_floor_at(&r->city,0.f,10.f,0.f,4.f,
                          &original_practice_floor))return 0;
 r->practice_target=b24_g10_practice_target_at_floor(original_practice_floor);
 if(!b24_g10_practice_target_valid(&r->practice_target))return 0;''')
patch("b24/b24_unified/b24_gpu_runtime.c",
 ''' if(!r->frames)(void)b24_gpu_boot_trace_mark("44 SCENE_DRAW_OK");''',
 ''' /* Debug target renders between original C1L1 GPU geometry and the suit
    in EXACT SAME camera/projection, no extra framebuffer swap. */
 if(!b24_g10_practice_target_draw(&r->practice_target))return 0;
 if(!r->frames)(void)b24_gpu_boot_trace_mark("44 SCENE_DRAW_OK");''')
patch("src/main.c",
 '''        b24_obs.target_health_percent=-1.f;''',
 '''#ifdef B24_GPU_ENGINE
        /* User-requested permanent C1L1 central aim-training actor.
           This does not modify original B14 mission sphere or HP/waves.
           B14 initial projection is approximate until original shared
           GPU projection is back-fed to HUD observation on next frame. */
        float target_px=-500.f,target_py=-500.f,target_scale=0.f;
        b14_world_project(&world,0.f,10.f,0.7527f,
                          &target_px,&target_py,&target_scale);
        b24_obs.target_visible=target_scale>0.f &&
              target_px>=0.f&&target_px<480.f&&
              target_py>=0.f&&target_py<272.f;
        b24_obs.target_alive=1;
        b24_obs.target_occluded=0; /* explicit practice object, no solid scenery LOS proven */
        b24_obs.target_id=B24_G10_PRACTICE_TARGET_ID;
        float distx=world.x,disty=world.y-10.f,distz=world.z-.7527f;
        b24_obs.target_distance=sqrtf(distx*distx+disty*disty+distz*distz);
        b24_obs.target_screen_x=(int)target_px;
        b24_obs.target_screen_y=(int)target_py;
        b24_obs.target_health_percent=100.f; /* immutable, no hit damage */
        b24_obs.target_world_valid=1;
        b24_obs.target_z_up=(Im2Vec3){0.f,10.f,.7527f};
#else
        b24_obs.target_health_percent=-1.f;
#endif''')
patch("src/main.c",
 '#include "../b24/b24_unified/b24_g8_live_original_motion.h"',
 '''#include "../b24/b24_unified/b24_g8_live_original_motion.h"
#include "../b24/b24_unified/b24_g10_practice_target.h"''')
patch("b24/b24_unified/b24_unified.c",
 '    int candidates=0;', '    int candidates=0;') if False else None
# Main B24 original B23 lock computes aim cosine from wrong noncenter reticle;
# G10 test target uses real centered 240x136 aiming while old enemies untouched.
patch("b24/b24_unified/b24_unified.c",
 '''        float delta_x=(float)obs->target_screen_x-278.f;
        float delta_y=(float)obs->target_screen_y-110.f;''',
 '''        const int practice=(obs->target_id==B24_G10_PRACTICE_TARGET_ID);
        float delta_x=(float)obs->target_screen_x-
                       (practice?240.f:278.f);
        float delta_y=(float)obs->target_screen_y-
                       (practice?136.f:110.f);''')
patch("b24/b24_unified/b24_unified.c",
 '#include "b24_unified.h"',
 '''#include "b24_unified.h"
#include "b24_g10_practice_target.h"''')
# B23 target lock formerly limited to missile, allows explicitly marked
# DEBUG target for any selected weapon, L held. Normal iOS lock unchanged.
patch("b24/b23_missile_lock/b23_missile_lock.c",
 '    if(weapon!=B23_MISSILE || !held){clear_target(s);return;}',
 '''    int practice=0;
#ifdef B24_G10_PRACTICE_LOCK
    for(size_t i=0;targets&&i<count;i++)
       if(targets[i].id==B24_G10_PRACTICE_TARGET_ID)practice=1;
#endif
    if((weapon!=B23_MISSILE && !practice) || !held){
        clear_target(s);return;
    }''')
patch("b24/b23_missile_lock/b23_missile_lock.c",
 '#include "b23_missile_lock.h"',
 '''#include "b23_missile_lock.h"
#ifdef B24_G10_PRACTICE_LOCK
#include "b24_g10_practice_target.h"
#endif''')
patch("b24/b23_missile_lock/b23_missile_lock.c",
 'if(!s || s->phase==B23_IDLE || s->weapon!=B23_MISSILE || !s->lock_button_held)return 0.f;',
 '''if(!s || s->phase==B23_IDLE || !s->lock_button_held)return 0.f;
#ifndef B24_G10_PRACTICE_LOCK
 if(s->weapon!=B23_MISSILE)return 0.f;
#else
 if(s->weapon!=B23_MISSILE && s->target_id!=B24_G10_PRACTICE_TARGET_ID)return 0.f;
#endif''')
patch("b24/b24_unified/b24_gpu_hud_native.c",
 ''' if(ui->page!=B22_GAME||!s||s->weapon!=B23_MISSILE||
   !s->lock_button_held||s->phase==B23_IDLE||s->target_id<0)return;''',
 ''' if(ui->page!=B22_GAME||!s||
   !(s->weapon==B23_MISSILE||s->target_id==B24_G10_PRACTICE_TARGET_ID)||
   !s->lock_button_held||s->phase==B23_IDLE||s->target_id<0)return;''')
patch("b24/b24_unified/b24_gpu_hud_native.c",
 '#include "b24_gpu_hud_native.h"',
 '''#include "b24_gpu_hud_native.h"
#include "b24_g10_practice_target.h"''')
out=W/"b24/b24_unified"
for f in ("b24_g10_practice_target.h","b24_g10_practice_target.c",
          "b24_g10_practice_target_vitagl.c"):
 shutil.copyfile(ROOT/"research/b24_unified"/f,out/f)
# Original B23 headers are nested in historical module location, appended
# G10 patch include find via common GPU B24 include path.
for relative in ("b24/b23_missile_lock/b23_missile_lock.c",):
 p=W/relative
 if not p.exists():raise RuntimeError("G10 B23 physical original path drift")
cm=W/"CMakeLists.txt";s=cm.read_text()
s+='''

# G10_VISIBLE_SOURCE_GROUND_C1L1_LOCKABLE_IMMORTAL_USER_TEST_ACTOR
if(B24_ENABLE_GPU)
 target_compile_definitions(im2_beta PRIVATE B24_G10_PRACTICE_LOCK=1)
 target_sources(im2_beta PRIVATE
   "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_g10_practice_target.c"
   "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_g10_practice_target_vitagl.c")
endif()
'''
cm.write_text(s)
print("PASS G10 actual original C1L1 center wireframe training target VitaGL visible + B23 L-lock all weapons; source-only, invulnerable, no invented iOS enemy")
