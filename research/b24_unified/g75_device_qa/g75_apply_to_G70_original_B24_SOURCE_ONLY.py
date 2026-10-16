#!/usr/bin/env python3
"""G75 optional source-only integration into a G70-authored work tree.
No VPK output, no VitaSDK build. Reuse the EXISTING B14 gameplay once
and replace ONLY post-tick collision reconciliation / 3D camera pace.
Requires completed G70 merge. Fail-closed on ABI/call-site drift.
"""
from pathlib import Path
import subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[3]
W=ROOT/"work"
GAME=W/"src/main.c"
CM=W/"CMakeLists.txt"
DST=W/"b24/b24_unified"
HERE=Path(__file__).resolve().parent
def exactly_once(text,old,new,what):
 count=text.count(old)
 if count!=1:raise RuntimeError("G75 mismatched "+what+" source statements "+str(count))
 return text.replace(old,new,1)
def main():
 if not GAME.exists() or not CM.exists() or not DST.exists():
  raise RuntimeError("First restore and run working old B24 G70 source merge in work/")
 code=GAME.read_text();cm=CM.read_text()
 if "G75_SOURCE_ONLY_GAMEPLAY_RECOVERY" in code or "G75_SOURCE_ONLY_GAMEPLAY_RECOVERY" in cm:
  raise RuntimeError("Already patched, do not stack duplicate flight/capsule owners")
 mandatory=[
    "#include \"../b24/b24_unified/b24_gpu_g68_collision.h\"",
    "b24_g70_g68_collision_load(&b24_original_walls",
    "b24_c1_original_collision_resolve(&b24_original_walls",
    "b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)",
    "float c1_follow=fminf(7.f*dt,1.f);"
 ]
 for mark in mandatory:
  if code.count(mark)!=1:raise RuntimeError("G75 original sole B14 owner changed: "+mark)
 code=exactly_once(code,
  '#include "../b24/b24_unified/b24_gpu_g68_collision.h"',
  '#include "../b24/b24_unified/b24_gpu_g68_collision.h"\n'
  '#include "../b24/b24_unified/b24_g75_source_capsule.h"\n'
  '/* G75_SOURCE_ONLY_GAMEPLAY_RECOVERY */',
  'one B14 actor/source triangle capsule import')
 legacy='''          if(!b24_c1_original_collision_resolve(&b24_original_walls,
              old_c1x,old_c1y,old_c1z,world.z,.35f,&world.x,&world.y)){
              running=0;break;
          }'''
 new='''#ifdef B24_G75_SOURCE_CAPSULE
          /* G75 original G67-style source 3-plane capsule + floor delta.
             The B14 world tick above remains the ONE gameplay integrator. */
          const float b75_proposed_z=world.z;
          float b75_x=world.x,b75_y=world.y,b75_z=world.z;
          if(!b24_g75_capsule_reconcile(&b24_original_walls,
                 old_c1x,old_c1y,old_c1z,
                 b75_x,b75_y,b75_z,
                 !world.flying,.35f,2.24f,&b75_x,&b75_y,&b75_z)){
             running=0;break;
          }
          world.x=b75_x;world.y=b75_y;world.z=b75_z;
          world.cam_z+=(world.z-b75_proposed_z)*fminf(7.f*dt,1.f);
#else
'''+legacy+'''
#endif'''
 code=exactly_once(code,legacy,new,"post-physics original wall owner")
 # Do not apply both G74 and G75 floor-snapping post-filters.
 marker="#ifdef B24_G74_GROUND_CONTACT"
 if code.count(marker)!=1:raise RuntimeError("G75 G74 native floor block changed")
 code=code.replace(marker,
    "#if defined(B24_G74_GROUND_CONTACT) && !defined(B24_G75_SOURCE_CAPSULE)",1)
 for fn in ["b24_g75_source_capsule.h","b24_g75_source_capsule.c",
            "b24_g75_original_sun_lighting_candidate.h"]:
  shutil.copyfile(HERE/fn,DST/fn)
 cm+='''

# G75_SOURCE_ONLY_GAMEPLAY_RECOVERY — optional next Vita beta ONLY.
option(B24_G75_SOURCE_CAPSULE "3-plane source G67 capsule + original G74 ground platform" OFF)
option(B24_G75_ORIGINAL_SUN_LIGHTING_CANDIDATE "Four genuine G30 Sun source placements, speculative color/falloff" OFF)
if(B24_G75_SOURCE_CAPSULE)
 if(NOT B24_ENABLE_GPU)
  message(FATAL_ERROR "G75 requires existing B24 GPU collision owner")
 endif()
 target_sources(im2_beta PRIVATE
  "${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_g75_source_capsule.c")
 target_compile_definitions(im2_beta PRIVATE B24_G75_SOURCE_CAPSULE=1)
endif()
if(B24_G75_ORIGINAL_SUN_LIGHTING_CANDIDATE)
 target_compile_definitions(im2_beta PRIVATE B24_G75_ORIGINAL_SUN_LIGHTING_CANDIDATE=1)
endif()
'''
 # Check complete source invariants before replacing current files.
 assert code.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')==1
 assert code.count('b24_g75_capsule_reconcile(')==1
 assert '#ifdef B24_G75_SOURCE_CAPSULE' in code
 assert 'b24_unified_tick(&b24_game' in code
 subprocess.run([sys.executable,str(HERE/"g75_patch_b14_camera_and_flight_SOURCE_ONLY.py"),
   "--b14-source-dir",str(W/"src")],check=True)
 GAME.write_text(code)
 CM.write_text(cm)
 print("PASS G75 source-only integration prepared: old B24 gameplay + optional 3-plane G68 collision and source Sun lighting, B14 flight+camera pace calibrated, no VPK")
if __name__=="__main__":main()
