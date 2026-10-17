#!/usr/bin/env python3
"""Opt-in source road CSR speedup in exact G159 original B14/G75 game.
Run AFTER G159 road patch, G156/G134 original wall corrections.
Existing G159 baseline source is not overwritten in Git; this patch works
on one assembled Vita game's transient work tree. NO new VPK.
"""
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
R=HERE.parents[2]
W=R/"work"
D=W/"b24/b24_unified"
C=D/"b24_g159_real_source_road.c"
H=D/"b24_g159_real_source_road.h"
CM=W/"CMakeLists.txt"
M=W/"src/main.c"

def one(s,old,new):
    n=s.count(old)
    if n!=1:raise ValueError(f"G160 source anchor drift count={n}: {old[:90]!r}")
    return s.replace(old,new,1)

def apply():
    for p in (C,H,CM,M):
        if not p.is_file():raise FileNotFoundError("G160 requires G159 assembled first: "+str(p))
    code=C.read_text()
    cm=CM.read_text()
    main=M.read_text()
    header=H.read_text()
    if "B24_G160_ROAD_SPATIAL_INDEX" in cm:
        raise ValueError("G160 optimization already installed")
    for x in ("B24_G159_ROAD_FLOOR_CANDIDATE","B24_G156_CONTINUOUS_TRI_CONTACT",
              "B24_G75_SOURCE_CAPSULE","B24_G108_SOURCE_VISUAL_WALLS"):
        if x not in cm:raise ValueError("G160 source G159 full game missing "+x)
    if not all(x in header for x in ("cell_offsets","cell_face_ids","spatial_index_ready")):
        raise ValueError("G160 original G159 struct ABI missing spatial index fields")
    for x in ("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)",
              "b24_unified_tick(&b24_game,&b24_obs);","b24_g83_timeline_tick("):
        if main.count(x)!=1:raise ValueError("G160 refuses second gameplay tick "+x)
    for name in ("b24_g160_original_road_spatial.h","b24_g160_original_road_spatial.c"):
        shutil.copyfile(HERE/name,D/name)
    code=one(code,'#include "b24_g159_real_source_road.h"',
      '#include "b24_g159_real_source_road.h"\n'
      '#ifdef B24_G160_ROAD_SPATIAL_INDEX\n'
      '#include "b24_g160_original_road_spatial.h"\n'
      '#endif')
    code=one(code,''' free(r->faces);
 memset(r,0,sizeof(*r));''',
      ''' free(r->faces);
#ifdef B24_G160_ROAD_SPATIAL_INDEX
 b24_g160_index_close(r);
#endif
 memset(r,0,sizeof(*r));''')
    code=one(code,''' tmp.ready=1;
 *r=tmp;''',
      '''#ifdef B24_G160_ROAD_SPATIAL_INDEX
 /* Bounded precomputed CSR, not a solidity rule. If it cannot be built
  * due to memory/scene size, original G159 full scan remains exact. */
 (void)b24_g160_index_build(&tmp);
#endif
 tmp.ready=1;
 *r=tmp;''')
    old=''' int found=0;float best=-100000.f;
 for(uint32_t i=0;i<r->count;i++){
  const B24G159RoadFace *f=&r->faces[i];'''
    new='''#ifdef B24_G160_ROAD_SPATIAL_INDEX
 uint32_t begin=0,end=0;
 if(!b24_g160_index_query(r,x,y,&begin,&end))return 0;
#else
 const uint32_t begin=0,end=r->count;
#endif
 int found=0;float best=-100000.f;
 for(uint32_t k=begin;k<end;k++){
#ifdef B24_G160_ROAD_SPATIAL_INDEX
  const uint32_t i=r->spatial_index_ready?r->cell_face_ids[k]:k;
#else
  const uint32_t i=k;
#endif
  const B24G159RoadFace *f=&r->faces[i];'''
    if code.count(old)!=2:raise ValueError("G160 must optimize exactly near & crossed, not other physics sites")
    code=code.replace(old,new)
    cm+='''

# G160 SOURCE ORIGINAL ROAD PERF: optional CSR spatial index for the
# same G159 original iOS atlas12/c1l1_road authored triangles.
# It does not change material source solidity or add a gameplay owner.
option(B24_G160_ROAD_SPATIAL_INDEX "Precompute bounded CSR XY candidates for G159 original source road ground" OFF)
if(B24_G160_ROAD_SPATIAL_INDEX)
 if(NOT B24_G159_ROAD_FLOOR_CANDIDATE OR
    NOT B24_G75_SOURCE_CAPSULE OR
    NOT B24_G156_CONTINUOUS_TRI_CONTACT)
  message(FATAL_ERROR "G160 requires genuine source G159/G75/G156 single Vita road gameplay")
 endif()
 target_sources(im2_beta PRIVATE
  "b24/b24_unified/b24_g160_original_road_spatial.c")
 target_compile_definitions(im2_beta PRIVATE
  B24_G160_ROAD_SPATIAL_INDEX=1)
endif()
'''
    C.write_text(code)
    CM.write_text(cm)
    if code.count('b24_g160_index_query(')!=2:
        raise ValueError("G160 incomplete old vs new query paths")
    if code.count('b24_g160_index_build(')!=1:
        raise ValueError("G160 index not built once at source asset load")
    if list(W.rglob("*.vpk")):raise ValueError("No VPK packaging during G160")
    print("G160 installed single G75 source road CSR spatial broadphase: full-scan OOM fallback, two original near/crossed callbacks, 1 native B14 tick, NO VPK")

if __name__=="__main__":apply()
