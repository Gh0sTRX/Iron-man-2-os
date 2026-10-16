#!/usr/bin/env python3
"""G70 reverse integration: G9/B17/B24 gameplay remains main; G68 map only.
Run after G9/B24 source generation and G7/G8 B14 patches, before VitaSDK.
No new G68 main.c or G68 mission/player code is copied into working game.
"""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[3]
W=ROOT/"work"
GAME=W/"src/main.c"
RUNTIME=W/"b24/b24_unified"
REQUIRED=[
 "b24_gpu_runtime.c","b24_gpu_runtime.h","b24_unified.c",
 "b24_c1_original_collision.c","b24_gpu_owner_vitagl.c",
 "b24_gpu_hud_native.c","b24_g8_live_original_motion.c"
]
def single(code,a,b):
 if code.count(a)!=1:raise RuntimeError("G70 gameplay owner source drift: "+repr(a[:100]))
 return code.replace(a,b,1)
def apply():
 for name in REQUIRED:
  if not (RUNTIME/name).is_file():raise FileNotFoundError("Missing old G9 gameplay "+name)
 cm=W/"CMakeLists.txt"
 if not GAME.is_file() or not cm.is_file():raise RuntimeError("Restore G9 B24 work tree first")
 code=GAME.read_text()
 if "G70_REVERSE_MERGE" in code:raise RuntimeError("G70 already applied")
 code=single(code,'#include "../b24/b24_unified/b24_c1_original_collision.h"',
   '#include "../b24/b24_unified/b24_c1_original_collision.h"\n'
   '#include "../b24/b24_unified/b24_gpu_g68_collision.h" /* G70_REVERSE_MERGE */')
 code=single(code,
   'b24_c1_original_collision_load(&b24_original_walls,\n'
   '                                               "app0:maps/C1L1_original_collision.c1wc")',
   'b24_g70_g68_collision_load(&b24_original_walls,\n'
   '                             "app0:assets/G66_original_collision.g66c")')
 if "b24_gpu_runtime_draw(&b24_gpu_rt,&model,&camera,&b24_game,idx)" not in code:
  raise RuntimeError("Old B24 gameplay engine GPU loop is missing")
 if "b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)" not in code:
  raise RuntimeError("The authoritative B14 gameplay flight physics disappeared")
 # G74 exact original source non-wall walkable surface HEIGHT query.
 # Apply ONLY in initial Ground stage of existing B14 movement motor,
 # after G7 wall sweep. This is not a second physics integration loop.
 world_floor_hook="          float c1_follow=fminf(7.f*dt,1.f);"
 if code.count(world_floor_hook)!=1:
  raise RuntimeError("G74 original B24 camera reconciler drift")
 code=code.replace(world_floor_hook,'''
#ifdef B24_G74_GROUND_CONTACT
          /* G74: only snap if one original sourced floor is within
           * [-0.5,+0.45] player-foot Z. Never lift to remote sky roof.
           * Source collider has limited horizontal coverage; original
           * B14 fallback stays authoritative elsewhere. */
          if(world.flight_stage==0){
            float g74_native_floor=0.f;
            if(b24_g74_near_original_floor(&b24_original_walls,
                                          world.x,world.y,world.z,
                                          &g74_native_floor)){
              float support_delta=g74_native_floor-world.z;
              world.z=g74_native_floor;
              world.cam_z+=support_delta*fminf(7.f*dt,1.f);
            }
          }
#endif
'''+world_floor_hook,1)
 GAME.write_text(code)
 for name in ["b24_gpu_g68_city.h","b24_gpu_g68_city.c",
              "b24_gpu_g68_collision.h","b24_gpu_g68_collision.c",
              "b24_gpu_g72_sky.h","b24_gpu_g72_sky_vitagl.c",
              "b24_gpu_g72_light.h",
              "b24_gpu_g73_sky.h","b24_gpu_g73_sky_vitagl.c"]:
  shutil.copy2(ROOT/"research/b24_unified"/name,RUNTIME/name)
 world=W/"src/b14_world.c"
 legacy=world.read_text()
 if "w->x=cl(w->x+vx*velocity*dt,-270.f,273.f);" not in legacy:
  raise RuntimeError("G8 source original 2010 B14 X travel clamp drift")
 if "w->y=cl(w->y+vy*velocity*dt,-297.f,191.f);" not in legacy:
  raise RuntimeError("G8 source original 2010 B14 Y travel clamp drift")
 # G67 conservative source extent (-325,+331), (-352,+255), radius .39.
 # Broader native C1L1 G68 world while preserving old B14 actor movement,
 # no second game movement or hard reset of old stage 1/2/3.
 legacy=single(legacy,"-270.f,273.f","-324.f,330.f")
 legacy=single(legacy,"-297.f,191.f","-351.f,254.f")
 world.write_text(legacy)
 conf=cm.read_text()
 marker="# G70_REVERSE_MERGE_B24_G9_G68_WORLD_BACKEND"
 if marker in conf:raise RuntimeError("G70 CMake already patched")
 conf+="""

# G70_REVERSE_MERGE_B24_G9_G68_WORLD_BACKEND
# The old B24/B17 GAME owns all input, hud, z-armors and native weapon/flight
# logic; G68 SOURCE CITY and original G59 collision are dependency payloads.
option(B24_G68_CITY_BACKEND "Use previously tested G68 source PVR city in B24 GPU engine" OFF)
if(B24_G68_CITY_BACKEND)
 if(NOT B24_ENABLE_GPU)
   message(FATAL_ERROR "G68 city uses existing B24 VitaGL GPU owner, not SDL framebuffer")
 endif()
 target_compile_definitions(im2_beta PRIVATE B24_G68_CITY_BACKEND=1)
 # G71 EXPERIMENTAL: one opt-in runtime source-alpha reorder, G70 default
 # untouched until desktop contrast preview and hardware acceptance.
 option(B24_G71_ALPHA_PASSES "Original source 7 RGBA atlas batches separated from opaque pass" OFF)
 if(B24_G71_ALPHA_PASSES)
  target_compile_definitions(im2_beta PRIVATE B24_G71_ALPHA_PASSES=1)
 endif()
 # G72 A/B diagnostics only. G70 original remains untouched by default.
 option(B24_G72_DUSK_ATMOSPHERE "Diagnostic dusk horizon until authored sky shader recovery" OFF)
 option(B24_G72_SOURCE_LIGHTING "One-time triangle-normal baked twilight vertex color" OFF)
 option(B24_G73_REAL_SKY "Original six BRES C1L1 sky pieces with two source night atlas material candidate assignment" OFF)
 option(B24_G74_GROUND_CONTACT "Nearby sourced floor contact in original B24 ground stage only" OFF)
 if(B24_G74_GROUND_CONTACT)
  target_compile_definitions(im2_beta PRIVATE B24_G74_GROUND_CONTACT=1)
 endif()
 if(B24_G73_REAL_SKY)
  target_sources(im2_beta PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_gpu_g73_sky_vitagl.c")
  target_compile_definitions(im2_beta PRIVATE B24_G73_REAL_SKY=1)
 endif()
 option(B24_G72_DIAGNOSTIC_SKYLINE "Temporary silhouette, not original 2010 source sky" OFF)
 if(B24_G72_DUSK_ATMOSPHERE)
  target_sources(im2_beta PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_gpu_g72_sky_vitagl.c")
  target_compile_definitions(im2_beta PRIVATE B24_G72_DUSK_ATMOSPHERE=1)
  if(B24_G72_DIAGNOSTIC_SKYLINE)
   set_source_files_properties(
     "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_gpu_g72_sky_vitagl.c"
     PROPERTIES COMPILE_DEFINITIONS B24_G72_DIAGNOSTIC_SKYLINE=1)
  endif()
 endif()
 if(B24_G72_SOURCE_LIGHTING)
  target_compile_definitions(im2_beta PRIVATE B24_G72_SOURCE_LIGHTING=1)
 endif()
 target_sources(im2_beta PRIVATE
   "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_gpu_g68_city.c"
   "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_gpu_g68_collision.c")
endif()
"""
 cm.write_text(conf)
 assert "G70_REVERSE_MERGE" in GAME.read_text()
 print("PASS G70 source-only reverse merge: old B24 GPU G9 gameplay + G68 source PVR city + G59 native 1910 walls; no new physics owner / HUD loop")
if __name__=="__main__":apply()
