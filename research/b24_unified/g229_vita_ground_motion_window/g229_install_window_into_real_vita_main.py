#!/usr/bin/env python3
"""G229: install read-only temporal QA AFTER G227 into the SAME Vita main.
No physics/camera/animation/weapon edits, no VPK generation.
Strict anchors fail closed. Optional B24_G227_WALK_ROOT_DIAGNOSTIC=ON.
"""
from pathlib import Path
import argparse
import shutil

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = Path(__file__).resolve().parents[3]
HEADER = "b24_g229_ground_trajectory_window.h"


def replace_one(text: str, original: str, changed: str, label: str) -> str:
    n = text.count(original)
    if n != 1:
        raise ValueError(f"G229 cannot patch {label}: expected exactly 1 anchor, found {n}")
    return text.replace(original, changed, 1)


def run(root: Path) -> None:
    main = root / "work/src/main.c"
    cmake = root / "work/CMakeLists.txt"
    dst = root / "work/b24/b24_unified" / HEADER
    for path in (main, cmake, HERE / HEADER):
        if not path.is_file():
            raise FileNotFoundError(f"G229 missing source: {path}")
    original = main.read_text()
    cm = cmake.read_text()
    if "B24_G227_WALK_ROOT_DIAGNOSTIC" not in original or "B24_G227_WALK_ROOT_DIAGNOSTIC" not in cm:
        raise ValueError("G229 requires installed opt-in G227 QA and CMake gate")
    if "B24G229WalkWindow" in original or "b24_g229_window_push" in original:
        raise ValueError("G229 already installed; no duplicate frame observers")
    for name in ("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)",
                 "b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)",
                 "b24_g227_qa_classify(&b24_g227_probe)"):
        if original.count(name) != 1:
            raise ValueError("G229 invalid B14/GPU/G227 original single-owner: " + name)
    if list((root / "work").rglob("*.vpk")):
        raise ValueError("G229 is NO-VPK, abort if work contains a VPK")
    changed = replace_one(original,
        '#include "../b24/b24_unified/b24_g227_vita_ground_world_render_probe.h"',
        '#include "../b24/b24_unified/b24_g227_vita_ground_world_render_probe.h"\n'
        '#include "../b24/b24_unified/b24_g229_ground_trajectory_window.h"',
        "G227 instrument header")
    changed = replace_one(changed,
        'B24G227GroundProbe b24_g227_probe={0}; /* one read-only snapshot per game frame */',
        'B24G227GroundProbe b24_g227_probe={0}; /* one read-only snapshot per game frame */\n'
        ' B24G229WalkWindow b24_g229_window={0}; /* diagnostic only; no actor mutation */',
        "G227 read-only snapshot declaration")
    changed = replace_one(changed,
        'b24_g227_probe.frame_num=(uint32_t)frame;',
        '''b24_g227_probe.frame_num=(uint32_t)frame;
          /* G229: compare 120 consecutive successful rendered ground frames.
           * 'now' is SDL_GetTicks() captured this frame by original main.
           * Camera.cam_x/y is POSITION; no landmark projection inference. */
          if(b24_g229_window_push(&b24_g229_window,&b24_g227_probe,(uint32_t)now)){
             const B24G229WindowVerdict vw=b24_g229_window_classify(&b24_g229_window);
             const float dwx=b24_g229_window.last_world_x-b24_g229_window.first_world_x;
             const float dwy=b24_g229_window.last_world_y-b24_g229_window.first_world_y;
             const float dcx=b24_g229_window.last_camera_x-b24_g229_window.first_camera_x;
             const float dcy=b24_g229_window.last_camera_y-b24_g229_window.first_camera_y;
             SDL_Log("G229_WALK_WINDOW source-only verdict=%s frames=%u elapsed_ms=%u "
                  "active_stick=%u B14_idle=%u collision_reject=%u GPU_root_mismatch=%u "
                  "B14_path=%.4f accepted_world_path=%.4f max_GPU_error=%.4f "
                  "world_displacement=(%.4f,%.4f) camera_position_displacement=(%.4f,%.4f) "
                  "G8_missing_frames=%u Zup_first_last=(%.4f,%.4f) "
                  "Zup_min_max=(%.4f,%.4f) GPU_actor_Zup_last=%.4f",
                  b24_g229_window_verdict_name(vw),
                  (unsigned)b24_g229_window.samples,
                  (unsigned)(b24_g229_window.last_tick_ms-b24_g229_window.first_tick_ms),
                  (unsigned)b24_g229_window.active_stick_frames,
                  (unsigned)b24_g229_window.b14_idle_frames,
                  (unsigned)b24_g229_window.collision_reject_frames,
                  (unsigned)b24_g229_window.root_mismatch_frames,
                  b24_g229_window.b14_path_xy,b24_g229_window.resolved_path_xy,
                  b24_g229_window.max_gpu_root_error,dwx,dwy,dcx,dcy,
                  (unsigned)b24_g229_window.missing_original_clip_frames,
                  b24_g229_window.first_world_z,b24_g229_window.last_world_z,
                  b24_g229_window.min_world_z,b24_g229_window.max_world_z,
                  b24_g227_probe.gpu_actor_world_z);
             b24_g229_window_reset(&b24_g229_window);
          }''',
        "G227 successful GPU-frame sample")
    for name in ("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)",
                 "b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)",
                 "b24_g227_qa_classify(&b24_g227_probe)"):
        if changed.count(name) != 1:
            raise ValueError("G229 changed the one-owner count: " + name)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HERE / HEADER, dst)
    main.write_text(changed)
    print("G229 installed read-only 120-successive-render-frame B14/collision/GPU/camera-position motion window. NO VPK.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    run(args.root)
