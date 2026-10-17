#!/usr/bin/env python3
"""G156 geometry fix in original 2010 first-level ONE B14/G75 gameplay.
Opt-in patch after G153 reassembles original source.
 * Original authored 1910 G66C wall faces preserved.
 * Supplemental source-visible opaque steep G66M candidates preserved.
 * G75/G108 test true 3D triangles for vertical-cylinder collision over
   FULL overlapping foot/head range instead of exactly 3 Z slices.
 * No second physics tick, no fabricated solidity rules, no new VPK.
"""
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
R=HERE.parents[2]
W=R/"work"
D=W/"b24/b24_unified"
G75=D/"b24_g75_source_capsule.c"
G108=D/"b24_g108_visible_original_wall_grid.c"
M=W/"src/main.c"
CM=W/"CMakeLists.txt"

def one(s,old,new,where):
    count=s.count(old)
    if count!=1:
        raise ValueError("G156 source drift "+where+" expected 1 found "+str(count)+" :"+repr(old[:80]))
    return s.replace(old,new,1)

def apply():
    for p in (G75,G108,M,CM):
        if not p.is_file():
            raise FileNotFoundError("G156 requires authentic full G153 one-game assembly: "+str(p))
    a=G75.read_text()
    b=G108.read_text()
    main=M.read_text()
    cm=CM.read_text()
    if "B24_G156_CONTINUOUS_TRI_CONTACT" in cm:
        raise ValueError("G156 patch already installed")
    for flag in ("B24_G75_SOURCE_CAPSULE","B24_G108_SOURCE_VISUAL_WALLS",
                 "B24_G137_MISSION000_REAL_SOURCE_EVENTS",
                 "B24_G153_REAL_SOURCE_MISSION_RETRY_LOOP"):
        if flag not in cm:
            raise ValueError("G156 requires source-authentic single gameplay: "+flag)
    for name in ("b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend)",
                 "b24_unified_tick(&b24_game,&b24_obs);",
                 "b24_g83_timeline_tick("):
        if main.count(name)!=1:
            raise ValueError("G156 refuses duplicate/missing original game owner: "+name)
    if "G134_LIMIT_LONG_FRAME_DISPLACEMENT" not in a:
        raise ValueError("G156 requires already source-safe G134 long-frame movement")
    if "b24_g108_grid_clear(" not in a:
        raise ValueError("G156 original G108 wall supplement was not loaded")
    header=HERE/"b24_g156_exact_vertical_triangle_contact.h"
    if not header.is_file():
        raise FileNotFoundError("G156 exact triangle source missing")
    shutil.copyfile(header,D/header.name)
    # Unused three-slice helper is removed, keeping existing bounded circle
    # and floor/horizontal logic exactly as original G75.
    a=one(a,
       '#include "b24_gpu_g68_collision.h"',
       '#include "b24_gpu_g68_collision.h"\n#include "b24_g156_exact_vertical_triangle_contact.h"',
       "g75_include")
    start="typedef struct{float x,y;} V;"
    end="static int wall_clear("
    if a.count(start)!=1 or a.count(end)!=1:
        raise ValueError("G156 original 3-slice G75 helpers drift")
    i=a.index(start)
    j=a.index(end)
    if j<=i or "static int slice(" not in a[i:j]:
        raise ValueError("G156 G75 removed helper is not original 3-slice")
    a=a[:i]+"""static float fmax2(float a,float b){return a>b?a:b;}
static int finite3(float x,float y,float z){
 return isfinite(x)&&isfinite(y)&&isfinite(z)&&
  fabsf(x)<100000.f&&fabsf(y)<100000.f&&fabsf(z)<100000.f;
}
"""+a[j:]
    old="""  float lo=fmax2(f->minz,feet+.005f);
  float hi=fmin2(f->maxz,feet+height-.005f);
  if(hi<lo)continue;
  float planes[3]={lo,.5f*(lo+hi),hi};
  for(int k=0;k<3;k++){
   V a,b;
   if(slice(f,planes[k],&a,&b) &&
      dist_seg2((V){x,y},a,b)<r*r)return 0;
  }"""
    new="""  /* G156 CONTINUOUS TRUE SOURCE WALL: no missed between-slice
   * contact; exact Z-clipped authored triangle vs upright XY capsule.
   * Source face is already marked wall by existing original native
   * G68 triangle orientation policy. No new solidity inferred. */
  if(b24_g156_exact_vertical_triangle_contact(
       f->xyz,x,y,feet,r,height))return 0;"""
    a=one(a,old,new,"g75_native_wall")
    b=one(b,
       '#include "b24_g108_visible_original_wall_grid.h"',
       '#include "b24_g108_visible_original_wall_grid.h"\n#include "b24_g156_exact_vertical_triangle_contact.h"',
       "g108_include")
    start="typedef struct {float x,y;} Vec;"
    end="int b24_g108_grid_clear("
    if b.count(start)!=1 or b.count(end)!=1:
        raise ValueError("G156 original 3-slice G108 helpers drift")
    i=b.index(start)
    j=b.index(end)
    if j<=i or "static int wall_slice(" not in b[i:j]:
        raise ValueError("G156 original G108 wall helper moved")
    b=b[:i]+b[j:]
    old="""  const float lo=fmaxf(w->minz,footz+.005f);
  const float hi=fminf(w->maxz,footz+height-.005f);
  if(hi<lo)continue;
  const float z[3]={lo,.5f*(lo+hi),hi};
  for(int j=0;j<3;j++){
   Vec a,b;
   if(wall_slice(w,z[j],&a,&b)&&
      distance_segment2((Vec){x,y},a,b)<radius*radius)return 0;
  }"""
    new="""  /* G156 exact full overlapping height of original opaque source
   * candidate; material/source admission policy remains G108-only. */
  if(b24_g156_exact_vertical_triangle_contact(
       w->p,x,y,footz,radius,height))return 0;"""
    b=one(b,old,new,"g108_supplement_wall")
    cm+="""
# G156 source-only replace 3-height collision misses by exact Z clipping
# inside the same G75 and G108 wall tests. No new source face/solidity,
# movement owner, GPU path, game tick or VPK.
option(B24_G156_CONTINUOUS_TRI_CONTACT "Continuous Z-clipped sourced triangle/capsule collision in native and visual-source walls" OFF)
# This source transform is unconditional once explicitly installed; if OFF,
# reject the build instead of silently running the replacement algorithm.
if(NOT B24_G156_CONTINUOUS_TRI_CONTACT)
 message(FATAL_ERROR "G156 source files already patched: explicitly set B24_G156_CONTINUOUS_TRI_CONTACT=ON or rebuild the unmodified G153 source tree")
endif()
if(B24_G156_CONTINUOUS_TRI_CONTACT)
 if(NOT B24_G108_SOURCE_VISUAL_WALLS OR NOT B24_G75_SOURCE_CAPSULE)
  message(FATAL_ERROR "G156 requires single original G75 and G108 collision")
 endif()
 target_compile_definitions(im2_beta PRIVATE B24_G156_CONTINUOUS_TRI_CONTACT=1)
endif()
"""
    # Above patch requires B24_G134... only source marker; no CMake gate.
    G75.write_text(a)
    G108.write_text(b)
    CM.write_text(cm)
    for needle in ("b24_g156_exact_vertical_triangle_contact(",):
        if a.count(needle)!=1 or b.count(needle)!=1:
            raise ValueError("G156 source callbacks are not single path")
    if list(W.rglob("*.vpk")):
        raise RuntimeError("G156 forbids new VPK")
    print("G156 PASS one Vita B14 G75/G108 real original triangle continuous Z collision; no 3-slice miss; NO VPK")

if __name__=="__main__":
    apply()
