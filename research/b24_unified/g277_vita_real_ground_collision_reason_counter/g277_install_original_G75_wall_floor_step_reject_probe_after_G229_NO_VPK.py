#!/usr/bin/env python3
"""G277 REAL B14/G75 Vita game: report WHICH real C1L1-ground rejection
(wall vs absent nearby authored floor vs excessive .35/.45 step). Modify
ONLY the optional G227 probe, NOT physics decisions, object transforms,
collision walls, animation routing, GPU draw or game release VPK.
Run AFTER g227/g229 source assembly. Fail closed on source drift.
"""
from pathlib import Path
import argparse,shutil
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
HDR="b24_g277_real_c1l1_ground_reject_reasons.h"
def one(s,old,new,label):
 n=s.count(old)
 if n!=1:raise ValueError(f"G277 REAL Vita grounded source {label} anchor count={n}")
 return s.replace(old,new,1)
def patch(root:Path):
 w=root/"work";src=w/"b24/b24_unified/b24_g75_source_capsule.c";m=w/"src/main.c"
 cm=w/"CMakeLists.txt"
 for p in (src,m,cm,HERE/HDR):
  if not p.is_file():raise FileNotFoundError("G277 actual G171 Vita game source needed: "+str(p))
 if list(w.rglob("*.vpk")):raise ValueError("G277 NO VPK means NO VPK")
 c=src.read_text();main=m.read_text();cfg=cm.read_text()
 if "G277_GROUND_REJECTION_BREAKDOWN" in c or "G277_GROUND_REJECTION_BREAKDOWN" in main:
  raise ValueError("G277 must not be installed twice")
 for token in ("B24_G227_WALK_ROOT_DIAGNOSTIC","B24G229WalkWindow"):
  if token not in main:raise ValueError("G277 must follow real G227/G229")
 for token in ("B24_G159_ROAD_FLOOR_CANDIDATE","B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL"):
  if token not in cfg:raise ValueError("G277 old source original G159/G171 not proven: "+token)
 if main.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1:
  raise ValueError("G277 one original real B14 gameplay integrator required")
 if main.count("b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)")!=1:
  raise ValueError("G277 one actual original C1L1 GPU draw required")
 c=one(c,'#include "b24_g75_source_capsule.h"',
       '#include "b24_g75_source_capsule.h"\n'
       '#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC\n'
       '#include "b24_g277_real_c1l1_ground_reject_reasons.h"\n'
       '/* G277_GROUND_REJECTION_BREAKDOWN observational only */\n'
       'static B24G277CollisionReasons g277_last={0};\n'
       'B24G277CollisionReasons b24_g277_last_collision_reasons(void){return g277_last;}\n'
       '#endif',
       "real G75 public source header")
 c=one(c,
  " float dx=x1-x0,dy=y1-y0,dz=z1-z0;",
  "#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC\n"
  " g277_last=(B24G277CollisionReasons){0};\n"
  "#endif\n"
  " float dx=x1-x0,dy=y1-y0,dz=z1-z0;",
  "original same G75 sweep entry")
 c=one(c," for(int k=0;k<steps;k++){",
  "#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC\n"
  " g277_last.sweep_substeps=(uint32_t)steps;\n"
  "#endif\n"
  " for(int k=0;k<steps;k++){",
  "one real swept original triangle steps")
 c=one(c,"   if(!wall_clear(world,nx,ny,nextz,radius,height))continue;",
  "   if(!wall_clear(world,nx,ny,nextz,radius,height)){\n"
  "#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC\n"
  "    ++g277_last.candidate_wall_reject;\n"
  "#endif\n"
  "    continue;\n   }",
  "authored 2010 G66C/G108 wall candidate rejection")
 c=one(c,"     if(!g159_authoritative_first_native_then_source_road(world,nx,ny,z,&h))continue;",
  "     if(!g159_authoritative_first_native_then_source_road(world,nx,ny,z,&h)){\n"
  "#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC\n"
  "      ++g277_last.candidate_no_source_support;\n"
  "#endif\n"
  "      continue;\n     }",
  "genuine G66C floor first and experimental source road fallback absent")
 c=one(c,"     if(h<z-.35f||h>z+.45f)continue;",
  "     if(h<z-.35f||h>z+.45f){\n"
  "#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC\n"
  "      ++g277_last.candidate_unsupported_step_height;\n"
  "#endif\n"
  "      continue;\n     }",
  "source floor support present but tall step rejection")
 c=one(c,"   x=nx;y=ny;\n   accepted=1.f;break;",
  "   x=nx;y=ny;\n"
  "#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC\n"
  "   ++g277_last.candidate_accepted;\n"
  "#endif\n"
  "   accepted=1.f;break;",
  "only real G75 accepted ground or air candidate")
 main=one(main,
  '#include "../b24/b24_unified/b24_g227_vita_ground_world_render_probe.h"',
  '#include "../b24/b24_unified/b24_g227_vita_ground_world_render_probe.h"\n'
  '#include "../b24/b24_unified/b24_g277_real_c1l1_ground_reject_reasons.h"',
  "G227 existing real main source diagnostic header")
 main=one(main,
  "b24_g227_probe.frame_num=(uint32_t)frame;",
  "b24_g227_probe.frame_num=(uint32_t)frame;\n"
  "          /* G277: same real successful GPU frame, latest authentic\n"
  "           * B14 -> G75 candidate wall/source floor/step verdict.\n"
  "           * Every 120 frames only; counts are per most recent sweep. */\n"
  "          if((frame%120u)==0u){\n"
  "            const B24G277CollisionReasons g277=b24_g277_last_collision_reasons();\n"
  "            SDL_Log(\"G277_GROUND_REJECTION_BREAKDOWN original C1L1 \"\n"
  "              \"wall_reject=%u missing_floor=%u step_height_reject=%u \"\n"
  "              \"accepted=%u sweep_substeps=%u \"\n"
  "              \"world_Zup=%.4f actorGPU_Zup=%.4f grounded=%u\",\n"
  "              (unsigned)g277.candidate_wall_reject,\n"
  "              (unsigned)g277.candidate_no_source_support,\n"
  "              (unsigned)g277.candidate_unsupported_step_height,\n"
  "              (unsigned)g277.candidate_accepted,\n"
  "              (unsigned)g277.sweep_substeps,\n"
  "              b24_g227_probe.resolved_world_z,\n"
  "              b24_g227_probe.gpu_actor_world_z,\n"
  "              (unsigned)!world.flying);\n"
  "          }",
  "actual Vita GPU rendered frame and G227 probe")
 if c.count("b24_g75_capsule_reconcile(")!=1 or main.count("b24_g75_capsule_reconcile(")!=1:
  raise ValueError("G277 never duplicate original gameplay G75")
 if main.count("G277_GROUND_REJECTION_BREAKDOWN")!=1:raise ValueError("G277 one debug log per 120 only")
 if list(w.rglob("*.vpk")):raise ValueError("G277 cannot build package")
 shutil.copyfile(HERE/HDR,w/"b24/b24_unified"/HDR)
 src.write_text(c);m.write_text(main)
 print("G277 PASS observational only real Vita original source G75 wall vs no-floor vs step-height rejection after G229; NO gameplay movement changes, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--root",type=Path,default=ROOT)
 args=p.parse_args();patch(args.root)
