#!/usr/bin/env python3
"""G278: first-3 real rendered Vita frames source-grounded boot trace.
Compare B14 world initial XYZ with first actual Vita world/camera/GPU actor
XYZ and original G66C near-floor Z. Installed strictly AFTER G277.
No player teleport, inferred source boot Z, collision removal, new VPK.
"""
from __future__ import annotations
import argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
def exactly_once(s:str,old:str,new:str,label:str)->str:
 n=s.count(old)
 if n!=1:raise ValueError(f"G278 original live C1L1 {label} code site count={n}, expected 1")
 return s.replace(old,new,1)

def patch(root:Path):
 work=root/"work";m=work/"src/main.c";cm=work/"CMakeLists.txt"
 if not m.is_file() or not cm.is_file():raise FileNotFoundError("G278 requires actual reconstructed PS Vita game")
 if list(work.rglob("*.vpk")):raise ValueError("G278 not a VPK packaging workflow")
 code=m.read_text();cfg=cm.read_text()
 for key in ("B24_G227_WALK_ROOT_DIAGNOSTIC","B24G229WalkWindow","G277_GROUND_REJECTION_BREAKDOWN"):
  if key not in code:raise ValueError("G278 requires proven G227/G229/G277 diagnostic "+key)
 for key in ("B24_G75_SOURCE_CAPSULE","B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL"):
  if key not in cfg:raise ValueError("G278 genuine C1L1 G75/G171 missing "+key)
 if "G278_INITIAL_BOOT_WORLD" in code or "g278_boot_sample_count" in code:
  raise ValueError("G278 cannot patch source twice")
 if code.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1:
  raise ValueError("G278 sole B14 gameplay owner missing")
 if code.count("b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)")!=1:
  raise ValueError("G278 sole native GPU world actor source missing")
 if "b24_original_walls" not in code:
  raise ValueError("G278 actual originally sourced G66C city variable missing")
 boot="B14World world; b14_world_init(&world);world.head_height=b15_suit_head(&model);world.cam_z=world.head_height;"
 code=exactly_once(code,boot,
  boot+"\n#ifdef B24_G227_WALK_ROOT_DIAGNOSTIC\n"
  " /* G278: original Vita reconstructed port B14 initial source world,\n"
  "  * NOT proof of original 2010 iOS first-story mission spawn. */\n"
  " const float g278_initial_b14_x=world.x,g278_initial_b14_y=world.y,g278_initial_b14_z=world.z;\n"
  " unsigned g278_boot_sample_count=0u;\n"
  "#endif",
  "initial true B14 reconstructed world state")
 place="b24_g227_probe.frame_num=(uint32_t)frame;"
 extras='''b24_g227_probe.frame_num=(uint32_t)frame;
          /* G278 FIRST 3 ACTUAL SUCCESSFULLY RENDERED Vita frames.
           * G75 loaded real G66C original collision; unlike G276
           * source-authored local coordinates, this observes WORLD
           * coordinates of the actual reconstructed Vita runtime.
           * Three samples expose early Mission000 camera/state changes
           * without modifying player's velocity/spawn/weapon/animation.
           */
          if(g278_boot_sample_count<3u){
            float g278_nearby_native_floor=0.f;
            const unsigned g278_has_native_floor =
                (unsigned)(b24_original_walls.ready &&
                b24_g74_near_original_floor(&b24_original_walls,
                   world.x,world.y,world.z,&g278_nearby_native_floor));
            const B24G277CollisionReasons g278_reject=b24_g277_last_collision_reasons();
            SDL_Log("G278_INITIAL_BOOT_WORLD render_sample=%u rendered_frame=%u "
              "B14_initial=(%.5f,%.5f,%.5f) resolved_WORLD=(%.5f,%.5f,%.5f) "
              "original_G66C_ready=%u near_native_floor=%u native_floor_Zup=%.5f "
              "GPU_actor=(%.5f,%.5f,%.5f) camera_player=(%.5f,%.5f,%.5f) "
              "grounded=%u flight_stage=%d original_wall_reject=%u "
              "missing_floor_reject=%u step_height_reject=%u accepted_substeps=%u "
              "original_2010_iOS_story_spawn_unverified=YES",
              g278_boot_sample_count,(unsigned)frame,
              g278_initial_b14_x,g278_initial_b14_y,g278_initial_b14_z,
              world.x,world.y,world.z,
              (unsigned)b24_original_walls.ready,g278_has_native_floor,
              g278_nearby_native_floor,
              b24_gpu_rt.frame_pose.x,b24_gpu_rt.frame_pose.y,
              b24_gpu_rt.frame_pose.z,
              camera.player_x,camera.player_y,camera.player_z,
              (unsigned)!world.flying,(int)world.flight_stage,
              (unsigned)g278_reject.candidate_wall_reject,
              (unsigned)g278_reject.candidate_no_source_support,
              (unsigned)g278_reject.candidate_unsupported_step_height,
              (unsigned)g278_reject.candidate_accepted);
            ++g278_boot_sample_count;
          }'''
 code=exactly_once(code,place,extras,"successfully rendered C1L1 GPU frame source prior to G229")
 if code.count("G278_INITIAL_BOOT_WORLD")!=1 or code.count("g278_boot_sample_count")!=4:
  raise ValueError("G278 source inserted once but boot sampling/trace count changed")
 if code.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1:
  raise ValueError("G278 duplicated world integration")
 if code.count("b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)")!=1:
  raise ValueError("G278 duplicated GPU renderer")
 if code.count("b24_g75_capsule_reconcile(")!=1:raise ValueError("G278 changed original G75 caller")
 if list(work.rglob("*.vpk")):raise ValueError("G278 generates no VPK")
 m.write_text(code)
 print("G278 PASS source-only REAL Vita first three rendered-world boot/G66C-floor/GPU camera telemetry installed; no actor input or world motion changed, NO VPK")

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--root",type=Path,default=ROOT)
 a=p.parse_args();patch(a.root)
