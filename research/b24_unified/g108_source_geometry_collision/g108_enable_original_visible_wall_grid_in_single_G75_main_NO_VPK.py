#!/usr/bin/env python3
"""G108 additive source-original G66M steep wall broadphase inside ONE old
B14 / G75 original-world capsule, never a second physics tick.
Run AFTER G75/G84/G85/G87/G92 / optional G106; NO VPK.
Diagnostic opt-in: actual *rendered 2010 source* faces do not by
themselves prove they were physically solid in the original iOS game.
"""
from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[3]
W=R/'work';D=W/'b24/b24_unified';M=W/'src/main.c';CM=W/'CMakeLists.txt'
HERE=Path(__file__).resolve().parent
def one(txt,old,new):
 if txt.count(old)!=1:
  raise ValueError('G108 refusing out-of-date B14 G75 source anchor count '+str(txt.count(old))+' '+repr(old[:90]))
 return txt.replace(old,new,1)
def install():
 for file in (M,CM,D/'b24_g75_source_capsule.c'):
  if not file.is_file():raise FileNotFoundError('Rebuild G75/G84/G85/G87/G92 first '+str(file))
 m=M.read_text();cm=CM.read_text()
 p=D/'b24_g75_source_capsule.c';code=p.read_text()
 if 'G108_SUPPLEMENT_AUTHORED_RENDER_GEOMETRY' in code:raise ValueError('already G108')
 for expected in ('G84_OPTIONAL_TRUE_B24_MAIN','G85_NATIVE_MARKV_629',
                  'G92_STATIC_DUMMY_SOURCE_IN_SINGLE_MAIN'):
  if expected not in m:raise ValueError('No authoritative combined 2010 old single game '+expected)
 if m.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')!=1:
  raise ValueError('G108 does not permit second B14 movement owner')
 code=one(code,'#include "b24_gpu_g68_collision.h"',
  '''#include "b24_gpu_g68_collision.h"
#ifdef B24_G108_SOURCE_VISUAL_WALLS
#include "b24_g108_visible_original_wall_grid.h"
/* G108_SUPPLEMENT_AUTHORED_RENDER_GEOMETRY */
static B24G108Grid g108_source_steep_walls={0};
static int g108_attempted_load=0;
#endif''')
 code=one(code,''' }
 return 1;
}
static int triangle_z''',''' }
#ifdef B24_G108_SOURCE_VISUAL_WALLS
 /* Real 2010 render-source walls supplement original G68 1,910-source
  * authored collider inside the SAME G75 swept-capsule test. Never
  * duplicate movement, update the world, or fabricate a contact event. */
 if(!b24_g108_grid_clear(&g108_source_steep_walls,x,y,feet,r,height))
  return 0;
#endif
 return 1;
}
static int triangle_z''')
 code=one(code,''' /* G67's sub-22cm wall and floor tests adapted to old B14 as a POST-tick
  * source collision resolver. Game still calls only ONE B14 motion tick. */''','''#ifdef B24_G108_SOURCE_VISUAL_WALLS
 /* Load once from the SAME authored original G66 city asset that the
  * existing VitaGL GPU has already loaded. First capsule call only.
  * If source asset cannot load, preserve *baseline* 1,910 faces; do not
  * invent a fake fallback map or crash the entire gameplay main. */
 if(!g108_attempted_load){
  g108_attempted_load=1;
  (void)b24_g108_grid_load(&g108_source_steep_walls,
       "app0:assets/G66_city.g66m",world);
 }
#endif
 /* G67's sub-22cm wall and floor tests adapted to old B14 as a POST-tick
  * source collision resolver. Game still calls only ONE B14 motion tick. */''')
 cm+='''
# G108 independent optional VPK-free fix to source city penetration:
# preserve G68 original 1910 faces; supplement missing original visible
# opaque steep wall source geometry in spatial CSR indexed source grid.
# This is a conservative *source-geometry collision candidate*, NOT
# proof of the original iOS CollisionEntity solidity/material property.
option(B24_G108_SOURCE_VISUAL_WALLS "Use source visual 2010 city opaque steep faces to supplement G75 one-player wall sweep" OFF)
if(B24_G108_SOURCE_VISUAL_WALLS)
 if(NOT B24_G75_SOURCE_CAPSULE OR NOT B24_G68_CITY_BACKEND)
  message(FATAL_ERROR "G108 source city wall supplement requires SAME G75 original collision and G68 visual world")
 endif()
 target_sources(im2_beta PRIVATE
  "b24/b24_unified/b24_g108_visible_original_wall_grid.c")
 target_compile_definitions(im2_beta PRIVATE B24_G108_SOURCE_VISUAL_WALLS=1)
endif()
'''
 for file in ('b24_g108_visible_original_wall_grid.h','b24_g108_visible_original_wall_grid.c'):
  shutil.copyfile(HERE/file,D/file)
 p.write_text(code);CM.write_text(cm)
 assert code.count('b24_g108_grid_clear(')==1
 assert code.count('b24_g108_grid_load(')==1
 assert m.count('b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)')==1
 assert not list(W.rglob('*.vpk')),'G108 must never package a new VPK'
 print('G108 real source visual 2010 supplemental wall grid integrated with ONE G75/B14 physics without generating VPK')
if __name__=='__main__':install()
