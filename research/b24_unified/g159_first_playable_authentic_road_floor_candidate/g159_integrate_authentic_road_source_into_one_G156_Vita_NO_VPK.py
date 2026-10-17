#!/usr/bin/env python3
"""G159 source-authentic c1l1_road ORIGINAL material candidate inside G75.

This is an opt-in PORT COLLISION POLICY, not proven 2010 native gameplay
solidness. Takes real named G66M batch12 vertices, preserves original G66C
faces and G156 exact source wall sweep. B14 is sole gameplay tick.
"""
from pathlib import Path
import shutil
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
W=ROOT/"work"
D=W/"b24/b24_unified"
C=D/"b24_g75_source_capsule.c"
CM=W/"CMakeLists.txt"
M=W/"src/main.c"
def once(s,a,b):
    count=s.count(a)
    if count!=1:
        raise ValueError("G159 source G75 previous C1L1 gameplay anchor drift "
                         +str(count)+" "+repr(a[:120]))
    return s.replace(a,b,1)

def apply():
    for p in (C,CM,M):
        if not p.is_file():raise FileNotFoundError("G159 requires assembled G156 native game: "+str(p))
    c=C.read_text()
    cm=CM.read_text()
    main=M.read_text()
    if "G159_SOURCE_ROAD_CANDIDATE" in c or "B24_G159_ROAD_FLOOR_CANDIDATE" in cm:
        raise ValueError("G159 cannot be layered twice")
    for flag in ("B24_G156_CONTINUOUS_TRI_CONTACT","B24_G75_SOURCE_CAPSULE",
                 "B24_G108_SOURCE_VISUAL_WALLS","B24_G136_SOURCE_B14_WORLD_BOUNDS"):
        if flag not in cm:raise ValueError("G159 missing true source first-level collision: "+flag)
    for x in ("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)",
              "b24_unified_tick(&b24_game,&b24_obs);",
              "b24_g83_timeline_tick("):
        if main.count(x)!=1:raise ValueError("G159 duplicate main gameplay owner "+x)
    if "G134_LIMIT_LONG_FRAME_DISPLACEMENT" not in c:
        raise ValueError("G159 missing source-safe G134 swept wall test")
    if c.count("b24_g74_near_original_floor(")!=2:
        raise ValueError("G159 native floor sites need two exact G75 gameplay calls")
    c=once(c,'#include "b24_g156_exact_vertical_triangle_contact.h"',
    '''#include "b24_g156_exact_vertical_triangle_contact.h"
#ifdef B24_G159_ROAD_FLOOR_CANDIDATE
#include "b24_g159_real_source_road.h"
/* G159_SOURCE_ROAD_CANDIDATE uses actual original 2010 atlas12 triangles.
   SOURCE-authentic vertices, EXPERIMENTAL PORT ground policy only. */
static B24G159Road g159_source_road={0};
static int g159_attempted_road_load=0;
#endif''')
    # G75 original descending-floor native result is preserved; a road
    # surface must actually be crossed, never snap up to distant roof.
    c=once(c,
''' if(found)*floor_z=best;
 return found;
}
int b24_g75_capsule_reconcile''',
'''#ifdef B24_G159_ROAD_FLOOR_CANDIDATE
 /* Source road MAY be higher than the original G66C collision proxy.
  * Existing genuine native G66C faces always remain loaded unchanged. */
 float source_road_z=0.f;
 if(b24_g159_road_crossed(&g159_source_road,x,y,z_before,z_after,
                          &source_road_z) &&
    (!found||source_road_z>best)){
  found=1;best=source_road_z;
 }
#endif
 if(found)*floor_z=best;
 return found;
}
#ifdef B24_G159_ROAD_FLOOR_CANDIDATE
static int g159_authoritative_first_native_then_source_road(
 const B24C1OriginalCollision *world,float x,float y,float z,float *h){
 /* Never override a genuine G66C source support at this foot height. */
 if(b24_g74_near_original_floor(world,x,y,z,h))return 1;
 return b24_g159_road_near(&g159_source_road,x,y,z,h);
}
#else
#define g159_authoritative_first_native_then_source_road b24_g74_near_original_floor
#endif
int b24_g75_capsule_reconcile''')
    c=once(c,
''' if(!g108_attempted_load){
  g108_attempted_load=1;
  (void)b24_g108_grid_load(&g108_source_steep_walls,
       "app0:assets/G66_city.g66m",world);
 }
#endif''',
''' if(!g108_attempted_load){
  g108_attempted_load=1;
  (void)b24_g108_grid_load(&g108_source_steep_walls,
       "app0:assets/G66_city.g66m",world);
 }
#endif
#ifdef B24_G159_ROAD_FLOOR_CANDIDATE
 /* Load the genuine road source once, same G66 GPU already loaded.
  * On missing/corrupt assets, preserve G75 native 1910 behavior.
  * No guessed constant Z and no second world movement tick. */
 if(!g159_attempted_road_load){
  g159_attempted_road_load=1;
  (void)b24_g159_road_open(&g159_source_road,
       "app0:assets/G66_city.g66m");
 }
#endif''')
    c=once(c,
      "if(!b24_g74_near_original_floor(world,nx,ny,z,&h))continue;",
      "if(!g159_authoritative_first_native_then_source_road(world,nx,ny,z,&h))continue;")
    c=once(c,
      "if(!b24_g74_near_original_floor(world,x,y,z,&original_support))",
      "if(!g159_authoritative_first_native_then_source_road(world,x,y,z,&original_support))")
    for name in ("b24_g159_real_source_road.c","b24_g159_real_source_road.h"):
        shutil.copyfile(HERE/name,D/name)
    cm+="""
# G159: opt-in original iOS road ("c1l1_road.tga") surface-only
# material-authoring candidate when original G66C lacks support at actual
# source road height. NOT the verified original iOS native solidity rule.
option(B24_G159_ROAD_FLOOR_CANDIDATE "Experimental one B14 original c1l1_road material-source ground support in G75 (authored solidity unproven)" OFF)
if(B24_G159_ROAD_FLOOR_CANDIDATE)
 if(NOT B24_G75_SOURCE_CAPSULE OR NOT B24_G108_SOURCE_VISUAL_WALLS
     OR NOT B24_G156_CONTINUOUS_TRI_CONTACT
     OR NOT B24_G136_SOURCE_B14_WORLD_BOUNDS)
  message(FATAL_ERROR "G159 genuine C1L1 road candidate requires single B14/G75 source collision, G108, G136 and G156")
 endif()
 target_sources(im2_beta PRIVATE
   "b24/b24_unified/b24_g159_real_source_road.c")
 target_compile_definitions(im2_beta PRIVATE
   B24_G159_ROAD_FLOOR_CANDIDATE=1)
endif()
"""
    C.write_text(c)
    CM.write_text(cm)
    if c.count("g159_authoritative_first_native_then_source_road(")!=4:
        raise ValueError("G159 unexpected bypass of real source G75 native floor")
    if list(W.rglob("*.vpk")):raise ValueError("G159 no VPK policy")
    print("G159 installed true original G66 road atlas12 source floor candidate in existing ONE B14/G75 source native engine; G156/G134 unchanged, NO VPK")
if __name__=="__main__":apply()
