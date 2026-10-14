#!/usr/bin/env python3
"""Wire G8 304-original motion stream into CURRENT G8 B14/B16/VitaGL frame flow.

Run ONLY after the exact G8 source reconstruction and G8 original bounds patch.
Source-only extension: deliberately DOES NOT create/modify G8 VPK artifact.
Missing source bank files fall back to unchanged original 59 IM2V animations.
No second world state, no new render owner, no invented bone animation.
"""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/"work"
P=WORK/"src/main.c"
s=P.read_text()
def rep(old,new):
 global s
 n=s.count(old)
 if n!=1:raise RuntimeError("G8 motion hook drift: %s matches: %s"%(n,old[:150]))
 s=s.replace(old,new)
rep('#include "../b24/b24_unified/b24_gpu_runtime.h"',
'''#include "../b24/b24_unified/b24_gpu_runtime.h"
#include "../b24/b24_unified/b24_g8_live_original_motion.h"''')
rep("static B24GpuRuntime b24_gpu_rt={0};",
'''static B24GpuRuntime b24_gpu_rt={0};
/* One source animation state/stream for the already-authoritative B14 body.
   G8 renderer remains the SAME real VitaGL owner. */
static B24G8LiveOriginalMotion b24_original_motion={0};''')
rep('''          if(fired>=0 && combat.mode==B16_REPULSOR && !attack.attack_active)
              b16_attack_begin(&attack,now,world.flying,0,0);''',
'''          if(fired>=0 && combat.mode==B16_REPULSOR && !attack.attack_active){
              b16_attack_begin(&attack,now,world.flying,0,0);
#ifdef B24_GPU_ENGINE
              /* Trigger on REAL accepted shot. Source _Att begins NEXT tick.
                 Existing B16 is fallback when exact IM2V is absent. */
              b24_g8_motion_repulsor_trigger(&b24_original_motion,(uint32_t)now);
#endif
          }''')
rep("        b16_apply_attack(&attack,&model,now);",
'''#ifdef B24_GPU_ENGINE
        /* B14 has already computed SINGLE authoritative world pose and B13
           59-bank fallback. Only source-compatible Mark VI / War Machine
           get genuine streamed 2010 motion; failure leaves fallback intact.
           IMPORTANT: do this BEFORE B16 right-palm-only repulsor blending,
           never replace the original B16 attack mask/muzzle direction. */
        if(!b24_unified_paused(&b24_game)){
          const B24MotionStage original_stage=
              !world.flying?(landing_now?B24M_LAND:
                        ground_run?B24M_RUN:has_move?B24M_WALK:B24M_IDLE):
              (world.flight_stage>=3?B24M_RUSH:
               world.flight_stage==2?B24M_CRUISE:
               has_move?B24M_DRIFT:B24M_HOVER);
          if(!b24_g8_motion_tick(&b24_original_motion,
                "app0:animations",
                model.vertices,sizeof(IM2Vertex),model.nv,idx,
                original_stage,move_x,move_y,(uint32_t)now)){
             running=0;break;
          }
        }
#endif
#ifdef B24_GPU_ENGINE
        /* Real full-body 2010 directional _Att must NOT be overdrawn by B16
           upper-arm overlay. If exact source absent B16 remains fallback. */
        if(b24_g8_motion_whole_body_fire(&b24_original_motion))
          attack.attack_active=0;
#endif
        b16_apply_attack(&attack,&model,now);''')
rep("    b24_gpu_runtime_close(&b24_gpu_rt);",
'''    b24_g8_motion_release(&b24_original_motion);
    b24_gpu_runtime_close(&b24_gpu_rt);''')
P.write_text(s)
out=WORK/"b24/b24_unified"
for name in ("b24_g8_live_original_motion.c",
             "b24_g8_live_original_motion.h",
             "b24_original_im2v_stream.c","b24_original_im2v_stream.h",
             "b24_hover_pose_blend.c","b24_hover_pose_blend.h"):
 shutil.copyfile(ROOT/"research/b24_unified"/name,out/name)
CMAKE=WORK/"CMakeLists.txt"
cm=CMAKE.read_text()
marker="# G8_HOST_SOURCE_ORIGINAL_304_MOTION_SINGLE_OWNER"
if marker in cm:raise RuntimeError("motion hook already applied")
cm+='''
# G8_HOST_SOURCE_ORIGINAL_304_MOTION_SINGLE_OWNER
# Opt-in original source pose stream only on the already selected GPU gameplay.
# Existing 59 B13/B16 clips are retained as a known-good fallback.
if(B24_ENABLE_GPU)
 target_sources(im2_beta PRIVATE
   "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_g8_live_original_motion.c"
   "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_original_im2v_stream.c"
   "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_hover_pose_blend.c")
endif()
'''
CMAKE.write_text(cm)
assert s.index("b14_pose_tick_ex(")<s.index("b24_g8_motion_tick(")<s.index("b16_apply_attack(&attack,&model,now)")
assert s.index("b16_apply_attack(&attack,&model,now)")<s.index("b24_gpu_runtime_draw(")
print("PASS G8 source-only real B14 -> original 304 streaming -> B16 right arm -> GPU draw single world/render owner. No VPK; files must be staged separately.")
