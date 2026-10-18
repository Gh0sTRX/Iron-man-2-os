#!/usr/bin/env python3
"""G227 instrument ORIGINAL reassembled real Vita C1L1 gameplay main.
Original 2010 world source G66C collision + actual B14->GPU root
gets observed, no code path can change world/camera/G8/attack.
Does NOT presume a Vita walk bug is fixed or has the source iOS speed.
After G218 installed. No VPK. Strict 1:1 anchors or fail closed.
"""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[3]
MAIN=ROOT/"work/src/main.c"
CM=ROOT/"work/CMakeLists.txt"
OUT=ROOT/"work/b24/b24_unified"
HERE=Path(__file__).resolve().parent
HEADER="b24_g227_vita_ground_world_render_probe.h"
def one(s,a,b,label):
 if s.count(a)!=1:
  raise ValueError(f"G227 real single-main source {label} anchor wrong count={s.count(a)}")
 return s.replace(a,b,1)
def run():
 for f in (MAIN,CM,HERE/HEADER,OUT/"b24_g218_live_authentic_2010_state_observer.h"):
  if not f.is_file():raise FileNotFoundError("original current Vita single-main required "+str(f))
 m=MAIN.read_text();cm=CM.read_text()
 if "B24_G227_WALK_ROOT_DIAGNOSTIC" in m or "B24_G227_WALK_ROOT_DIAGNOSTIC" in cm:
  raise ValueError("G227 source QA already installed once; never double probe")
 for original in (
  "b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)",
  "camera.player_x=world.x;camera.player_y=world.y;camera.player_z=world.z;",
  "b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)",
  "b24_g218_observe_actually_loaded_G8_clip("):
  if m.count(original)!=1:
   raise ValueError("original game world/camera/G8 source no longer single-owner: "+original)
 m=one(m,
  '#include "../b24/b24_unified/b24_g218_live_authentic_2010_state_observer.h"',
  '#include "../b24/b24_unified/b24_g218_live_authentic_2010_state_observer.h"\n'
  '#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC\n'
  '#include "../b24/b24_unified/b24_g227_vita_ground_world_render_probe.h"\n'
  '#endif',
  "G218 original real source include after G83/G8")
 m=one(m,
  "B14World world; b14_world_init(&world);world.head_height=b15_suit_head(&model);world.cam_z=world.head_height;",
  "B14World world; b14_world_init(&world);world.head_height=b15_suit_head(&model);world.cam_z=world.head_height;\n"
  "#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC\n"
  " B24G227GroundProbe b24_g227_probe={0}; /* one read-only snapshot per game frame */\n"
  "#endif",
  "B14 source world initialization")
 m=one(m,
  "Uint32 now=SDL_GetTicks();float raw_dt=(now-last)*0.001f;last=now;",
  "Uint32 now=SDL_GetTicks();float raw_dt=(now-last)*0.001f;last=now;\n"
  "#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC\n"
  " b24_g227_probe=(B24G227GroundProbe){0}; /* pause, fail or missing input never reuse stale frame */\n"
  "#endif",
  "single SDL frame start")
 m=one(m,
  "b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend);",
  "b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend);\n"
  "#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC\n"
  " b24_g227_probe.old_world_x=old_c1x;\n"
  " b24_g227_probe.old_world_y=old_c1y;\n"
  " b24_g227_probe.proposed_world_x=world.x;\n"
  " b24_g227_probe.proposed_world_y=world.y;\n"
  " b24_g227_probe.stick_x=move_x;\n"
  " b24_g227_probe.stick_y=move_y;\n"
  " b24_g227_probe.flying=(uint8_t)world.flying;\n"
  " b24_g227_probe.recorded=1;\n"
  "#endif",
  "actual B14 tick and temporary world original XY proposals")
 # The assembled G9/G171 main has historically varied one-space
 # indentation around the same real GPU rendering call. Match precisely
 # its B24 single render statement and failure branch by syntax, never
 # depend on a particular whitespace convention. Fail closed on >1.
 import re
 pattern=r'if\(!b24_gpu_runtime_draw\(&b24_gpu_rt,&model,&camera,&b24_game,idx\)\)\{\s*running=0;break;\s*\}'
 matches=list(re.finditer(pattern,m))
 if len(matches)!=1:
  raise ValueError("G227 original game GPU frame source anchor needs exactly 1 actual successful frame path, found "+str(len(matches)))
 new=matches[0].group(0)+'''
#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC
          /* TRUE GPU root AFTER render, vs resolved original 2010 G66C
           * collision/world, vs follow camera target. This does not
           * draw another frame or change player's movement. Logging
           * every 120 frames (not every tick); original 2010 weapon
           * and animation semantics remain completely untouched. */
          b24_g227_probe.resolved_world_x=world.x;
          b24_g227_probe.resolved_world_y=world.y;
          b24_g227_probe.gpu_actor_world_x=b24_gpu_rt.frame_pose.x;
          b24_g227_probe.gpu_actor_world_y=b24_gpu_rt.frame_pose.y;
          b24_g227_probe.camera_target_x=camera.cam_x;
          b24_g227_probe.camera_target_y=camera.cam_y;
          b24_g227_probe.original_G8_clip_loaded=
             (uint8_t)(b24_original_motion.active&&!b24_original_motion.missing);
          b24_g227_probe.original_G8_source_clip_missing=
             (uint8_t)b24_original_motion.missing;
          b24_g227_probe.frame_num=(uint32_t)frame;
          if((frame%120u)==0u){
             const B24G227WalkVerdict verdict=
                b24_g227_qa_classify(&b24_g227_probe);
             SDL_Log("G227_WALK_ROOT source-only verdict=%s "
                 "stick=(%.3f,%.3f) world_pre=(%.4f,%.4f) "
                 "B14_proposal=(%.4f,%.4f) native_collision_resolved=(%.4f,%.4f) "
                 "GPU_ACTOR=(%.4f,%.4f) camera_TARGET=(%.4f,%.4f) "
                 "G8_original_loaded=%u G8_missing=%u original_clip=%s",
               b24_g227_walk_verdict_name(verdict),
               b24_g227_probe.stick_x,b24_g227_probe.stick_y,
               b24_g227_probe.old_world_x,b24_g227_probe.old_world_y,
               b24_g227_probe.proposed_world_x,b24_g227_probe.proposed_world_y,
               b24_g227_probe.resolved_world_x,b24_g227_probe.resolved_world_y,
               b24_g227_probe.gpu_actor_world_x,b24_g227_probe.gpu_actor_world_y,
               b24_g227_probe.camera_target_x,b24_g227_probe.camera_target_y,
               (unsigned)b24_g227_probe.original_G8_clip_loaded,
               (unsigned)b24_g227_probe.original_G8_source_clip_missing,
               b24_original_motion.selected);
          }
#endif'''
 m=m[:matches[0].start()]+new+m[matches[0].end():]
 cm+='''
# G227 optional source-only actual Vita grounded-motion root telemetry:
# one B14 physics proposal vs original authored G66C collision accepted
# displacement vs GPU armor world position vs chase-camera target.
# Never write physical world transform, add 2nd physics owner, VPK.
option(B24_G227_WALK_ROOT_DIAGNOSTIC "Read-only original C1L1 grounded walking input B14 collision GPU camera QA logger" OFF)
if(B24_G227_WALK_ROOT_DIAGNOSTIC)
 if(NOT B24_GPU_ENGINE OR NOT B24_G218_SOURCE_STATE_OBSERVER)
  message(FATAL_ERROR "G227 requires single existing VitaGL G218/G83/G8 original actor and native world")
 endif()
 target_compile_definitions(im2_beta PRIVATE B24_G227_WALK_ROOT_DIAGNOSTIC=1)
endif()
'''
 if m.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1:
  raise ValueError("G227 accidentally duplicated B14 original world integrator")
 if m.count("b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)")!=1:
  raise ValueError("G227 accidentally duplicated GPU Vita swap")
 if m.count("b24_g8_motion_tick_g84(")!=1:
  raise ValueError("G227 accidentally duplicated G8 source animation")
 if m.count("b16_combat_fire(&combat,&world,muzzle)")!=1:
  raise ValueError("G227 accidentally duplicated B16 accepted fire")
 if list((ROOT/"work").rglob("*.vpk")):raise ValueError("G227 forbids any VPK")
 shutil.copyfile(HERE/HEADER,OUT/HEADER)
 MAIN.write_text(m);CM.write_text(cm)
 print("G227 PASS read-only actual Vita B14 to original C1L1 collision to G8 to exact rendered GPU actor and chase camera line-level QA installed, physics/weapon untouched NO VPK")
if __name__=="__main__":
 run()
