#!/usr/bin/env python3
"""G163 target source actual G161 G75/G83/G8 ONE actor gameplay, no VPK.
G162 source inspection confirmed B14 movement always sets w->heading =
atan2(vx,vy) even if L aim pressed. Correct after B14 only for ground/hover.
Do not modify source-model scale, original gameloft assets or mission spawn.
"""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[3]
W=ROOT/"work"
P=W/"src/main.c"
CM=W/"CMakeLists.txt"
D=W/"b24/b24_unified"
HERE=Path(__file__).resolve().parent
def once(s,a,b):
    if s.count(a)!=1:
        raise ValueError(f"G163 source owner anchor drift {s.count(a)} {a[:85]!r}")
    return s.replace(a,b,1)
def patch():
    for p in (P,CM,D/"b24_g83_unified_movement_aim.c"):
        if not p.is_file():raise FileNotFoundError(str(p))
    s=P.read_text();cm=CM.read_text()
    if "B24_G163_CAMERA_AIM_FACING" in cm:raise ValueError("G163 duplicate source")
    if s.count("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)")!=1:
        raise ValueError("G163 rejects missing or duplicate B14 integrator")
    if s.count("b24_g83_timeline_tick(")!=1:raise ValueError("G163 must leave G83 alone")
    if "B24_G85_NATIVE_MARKV_629" not in cm:raise ValueError("G163 needs original source animations")
    if "B24_G160_ROAD_SPATIAL_INDEX" not in cm:raise ValueError("G163 must preserve G160")
    inc='#include "../b24/b24_unified/b24_g75_source_capsule.h"'
    s=once(s,inc,inc+'\n#ifdef B24_G163_CAMERA_AIM_FACING\n'
        '#include "../b24/b24_unified/b24_g163_aim_facing.h"\n#endif')
    anchor='''          b14_world_target(&world);
          b16_combat_tick(&combat,&world,dt);'''
    replacement='''#ifdef B24_G163_CAMERA_AIM_FACING
          /* G163 one current B14 actor and G83 original clip owner.
           * Current prototype L+repulsor aim prevents rotating away
           * toward move vector when strafing or backpedalling. Movement
           * delta, camera position, crosshair and Stage2/RUSH remain
           * untouched. Device source G161 reported actor turned backward. */
          world.heading=b24_g163_aim_heading(
              world.heading,world.orbit,dt,
              (b24_buttons&IM2_BT_L)&&combat.mode==B16_REPULSOR,
              !world.flying||world.flight_stage<=1);
#endif
          b14_world_target(&world);
          b16_combat_tick(&combat,&world,dt);'''
    s=once(s,anchor,replacement)
    cm+="""
# G163: experimental B14 heading lock toward camera while original source
# G83 ground/hover directional aim animations strafe; native iOS input
# semantics still not proven, no new root motion/physics/camera.
option(B24_G163_CAMERA_AIM_FACING "Keep MarkV actor facing crosshair when L+repulsor aim and move side/back in original source C1L1" OFF)
if(B24_G163_CAMERA_AIM_FACING)
 if(NOT B24_G84_ORIGINAL_MOVESET_ROUTER OR NOT B24_G85_NATIVE_MARKV_629)
  message(FATAL_ERROR "G163 requires one B14/G83/G85 source movement actor")
 endif()
 target_sources(im2_beta PRIVATE "b24/b24_unified/b24_g163_aim_facing.c")
 target_compile_definitions(im2_beta PRIVATE B24_G163_CAMERA_AIM_FACING=1)
endif()
"""
    for name in ("b24_g163_aim_facing.h","b24_g163_aim_facing.c"):
        shutil.copyfile(HERE/name,D/name)
    if s.count("b24_g163_aim_heading(")!=1:raise ValueError("G163 must use exactly one heading correction")
    P.write_text(s);CM.write_text(cm)
    if list(W.rglob("*.vpk")):raise ValueError("G163 no new install while feedback fixes incomplete")
    print("G163 actual G161 main patched: one B14 move, one G83/G8 original animation, aim direction camera-locked for ground/hover only; no VPK")
if __name__=="__main__":patch()
