#!/usr/bin/env python3
"""G279: add OPTIONAL persistent Vita CSV diagnostic to the actual G278
single Vita C1L1 renderer/collision/animation loop, not a parallel simulation.
Must run AFTER G227, G229, G277, G278. Source-only; NO VPK or moved actor.
The file is written only for first 3 rendered frames and per 120 contiguous
rendered ground frames, and flushes after each row to survive abnormal exits.
"""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = Path(__file__).resolve().parents[3]
HEADER = "b24_g279_walk_trace.h"

def one(s: str, needle: str, inserted: str, label: str) -> str:
    n = s.count(needle)
    if n != 1:
        raise ValueError(f"G279 fail closed: real Vita {label} count={n}, required 1")
    return s.replace(needle, inserted, 1)

def install(root: Path) -> None:
    work=root/"work"
    main=work/"src/main.c"
    cmake=work/"CMakeLists.txt"
    dest=work/"b24/b24_unified"/HEADER
    for p in (main,cmake,HERE/HEADER):
        if not p.is_file():
            raise FileNotFoundError("G279 actual G278 Vita game source missing: "+str(p))
    if list(work.rglob("*.vpk")):
        raise ValueError("G279 forbids any VPK packaging")
    src=main.read_text()
    cfg=cmake.read_text()
    if "B24_G279_WALK_TRACE_FILE" in src or "B24_G279_WALK_TRACE_FILE" in cfg:
        raise ValueError("G279 must never duplicate a trace file observer")
    for token in (
        "G278_INITIAL_BOOT_WORLD", "B24G229WalkWindow",
        "G277_GROUND_REJECTION_BREAKDOWN","B24_G227_WALK_ROOT_DIAGNOSTIC",
        "g278_has_native_floor","b24_g278_boot_sample_count"
    ):
        # The G278 variable name is g278_boot_sample_count (without b24);
        # check the actual real source-specific symbol below separately.
        if token=="b24_g278_boot_sample_count":
            token="g278_boot_sample_count"
        if token not in src:
            raise ValueError("G279 requires real prior source diagnostic "+token)
    for token in (
        "B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL",
        "B24_G227_WALK_ROOT_DIAGNOSTIC",
        "B24_G75_SOURCE_CAPSULE"
    ):
        if token not in cfg:
            raise ValueError("G279 G171 true-collision Vita configuration absent: "+token)
    for call in (
        "b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)",
        "b24_g75_capsule_reconcile(",
        "b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)",
        "b24_g8_motion_tick_g84("
    ):
        if src.count(call)!=1:
            raise ValueError("G279 one existing gameplay owner changed: "+call)
    src=one(src,
        '#include "../b24/b24_unified/b24_g277_real_c1l1_ground_reject_reasons.h"',
        '#include "../b24/b24_unified/b24_g277_real_c1l1_ground_reject_reasons.h"\n'
        '#ifdef B24_G279_WALK_TRACE_FILE\n'
        '#include "../b24/b24_unified/b24_g279_walk_trace.h"\n'
        '#endif',
        "existing G277 include after G227")
    src=one(src,
        "unsigned g278_boot_sample_count=0u;",
        "unsigned g278_boot_sample_count=0u;\n"
        "#ifdef B24_G279_WALK_TRACE_FILE\n"
        ' (void)b24_g279_trace_open("ux0:data/ironman2_g279_walk.csv");\n'
        "#endif",
        "one source-authored B14 boot, no spawn mutation")
    boot='''#ifdef B24_G279_WALK_TRACE_FILE
            /* Same 3 successful GPU frames captured by G278. No invented
             * mission start, root offset, floor or network source. */
            B24G279Row g279_first={0};
            g279_first.phase="BOOT";
            g279_first.frame=(unsigned)frame;
            g279_first.millis=(unsigned)now;
            g279_first.initial_x=g278_initial_b14_x;
            g279_first.initial_y=g278_initial_b14_y;
            g279_first.initial_z=g278_initial_b14_z;
            g279_first.x=world.x;g279_first.y=world.y;g279_first.z=world.z;
            g279_first.gpu_x=b24_gpu_rt.frame_pose.x;
            g279_first.gpu_y=b24_gpu_rt.frame_pose.y;
            g279_first.gpu_z=b24_gpu_rt.frame_pose.z;
            g279_first.cam_x=camera.cam_x;g279_first.cam_y=camera.cam_y;
            g279_first.stick_x=b24_g227_probe.stick_x;
            g279_first.stick_y=b24_g227_probe.stick_y;
            g279_first.wall_reject=(unsigned)g278_reject.candidate_wall_reject;
            g279_first.missing_floor=(unsigned)g278_reject.candidate_no_source_support;
            g279_first.step_reject=(unsigned)g278_reject.candidate_unsupported_step_height;
            g279_first.has_native_floor=g278_has_native_floor;
            g279_first.native_floor_z=g278_has_native_floor?g278_nearby_native_floor:0.f;
            (void)b24_g279_trace_write(&g279_first);
#endif
            ++g278_boot_sample_count;'''
    src=one(src,"++g278_boot_sample_count;",boot,
        "G278 real first successful GPU 3-frame block")
    window='''#ifdef B24_G279_WALK_TRACE_FILE
             /* G229 has a WHOLE contiguous 120 SUCCESSFUL ground
              * render-frame window. Preserve world/GPU/camera deltas,
              * verified G171 collision rejects, input and native sample.
              * Last G277 wall/no-floor/step counts are per final sweep,
              * while G229 collision_reject is over full 120-frame window. */
             const B24G277CollisionReasons g279_last=
                 b24_g277_last_collision_reasons();
             B24G279Row g279_win={0};
             g279_win.phase="WALK120";
             g279_win.frame=(unsigned)frame;
             g279_win.millis=(unsigned)now;
             g279_win.initial_x=g278_initial_b14_x;
             g279_win.initial_y=g278_initial_b14_y;
             g279_win.initial_z=g278_initial_b14_z;
             g279_win.x=world.x;g279_win.y=world.y;g279_win.z=world.z;
             g279_win.gpu_x=b24_gpu_rt.frame_pose.x;
             g279_win.gpu_y=b24_gpu_rt.frame_pose.y;
             g279_win.gpu_z=b24_gpu_rt.frame_pose.z;
             g279_win.cam_x=camera.cam_x;g279_win.cam_y=camera.cam_y;
             g279_win.stick_x=b24_g227_probe.stick_x;
             g279_win.stick_y=b24_g227_probe.stick_y;
             g279_win.b14_path=(float)b24_g229_window.b14_path_xy;
             g279_win.accepted_path=(float)b24_g229_window.resolved_path_xy;
             g279_win.active_stick=(unsigned)b24_g229_window.active_stick_frames;
             g279_win.coll_reject=(unsigned)b24_g229_window.collision_reject_frames;
             g279_win.root_mismatch=(unsigned)b24_g229_window.root_mismatch_frames;
             g279_win.wall_reject=(unsigned)g279_last.candidate_wall_reject;
             g279_win.missing_floor=(unsigned)g279_last.candidate_no_source_support;
             g279_win.step_reject=(unsigned)g279_last.candidate_unsupported_step_height;
             (void)b24_g279_trace_write(&g279_win);
#endif
             b24_g229_window_reset(&b24_g229_window);'''
    src=one(src,
       "b24_g229_window_reset(&b24_g229_window);",window,
       "one true 120 rendered ground-frame G229 window conclusion")
    cfg+='''
# G279 optional small persistent walk evidence ONLY, no extra gameplay owner:
# available on future Vita hardware as ux0:data/ironman2_g279_walk.csv
# Original 2010 collision + movement untouched. Disabled by default.
option(B24_G279_WALK_TRACE_FILE "Write first 3 rendered boot and 120-frame real grounded C1L1 movement CSV to ux0:data, diagnostic only" OFF)
if(B24_G279_WALK_TRACE_FILE)
 if(NOT B24_G227_WALK_ROOT_DIAGNOSTIC OR
    NOT B24_G171_STRICT_SCULPTURE_NO_VISUAL_INFERRED_WALL OR
    NOT B24_G75_SOURCE_CAPSULE)
  message(FATAL_ERROR "G279 requires same strict real Vita source G171/G227 diagnostic")
 endif()
 target_compile_definitions(im2_beta PRIVATE B24_G279_WALK_TRACE_FILE=1)
endif()
'''
    for call in (
        "b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)",
        "b24_g75_capsule_reconcile(",
        "b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)",
        "b24_g8_motion_tick_g84("
    ):
        if src.count(call)!=1:
            raise ValueError("G279 duplicated/removed a live game owner: "+call)
    if src.count("b24_g279_trace_write(")!=2 or src.count("b24_g279_trace_open(")!=1:
        raise ValueError("G279 not exactly two real recording phases and one file")
    if list(work.rglob("*.vpk")):
        raise ValueError("G279 never produces a package")
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(HERE/HEADER,dest)
    main.write_text(src)
    cmake.write_text(cfg)
    print("G279 installed optional Vita persistent genuine B14/G75/G8/GPU/camera first-3-frame + 120-render-ground-window trace, NO VPK")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=DEFAULT_ROOT)
    args=p.parse_args()
    install(args.root)
