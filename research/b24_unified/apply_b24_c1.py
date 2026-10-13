#!/usr/bin/env python3
"""Patch the reconstructed B24 game renderer with an authentic C1L1 level test pass.
Keep B24 suit/controls/HUD/flight. CPU LOD is intentionally a *temporary* real
geometry renderer; GL GPU context ownership remains unsolved. Fail on code drift.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/"work"
r=ROOT/"src/renderer.c"
s=r.read_text()
inc='#include "../b24/b24_unified/b24_c1l1_map.h"\n'
assert "b24_c1l1_map.h" not in s
s=inc+s
anchor="static void b17_world_floor(uint32_t *out,float *depth,const IM2Camera *cam){"
assert s.count(anchor)==1
extra=r"""
/* B24-C1: source-authentic C1L1 city triangles: exact 2010 BDAE vertices.
   This temporary bounded CPU pass proves integration into B24; next replace
   scene and animated armor draws with one native vitaGL/GXM renderer.
   Only draw local geometry to avoid the B17 480x272 per-pixel FPS collapse. */
static int b24_c1_scene(uint32_t *out,float *depth,const IM2Camera *cam){
    static int loaded=0;
    if(!loaded)loaded=b24_c1l1_load("maps/C1L1_environment.im2map")?1:-1;
    if(loaded!=1)return 0;
    const int limits[4]={520,780,180,210};
    int used[4]={0,0,0,0};
    const float radius=135.f;
    const float minX=cam->player_x-radius,maxX=cam->player_x+radius;
    const float minY=cam->player_y-radius,maxY=cam->player_y+radius;
    const size_t n=b24_c1l1_count();
    for(size_t i=0;i<n;i++){
        const B24C1Triangle *tri=b24_c1l1_triangle(i);
        if(!tri||tri->category>3u)continue;
        int category=(int)tri->category;
        if(used[category]>=limits[category])continue;
        float a=tri->p[0],b=tri->p[3],c=tri->p[6];
        float d=tri->p[1],e=tri->p[4],f=tri->p[7];
        if((a<minX&&b<minX&&c<minX) ||
           (a>maxX&&b>maxX&&c>maxX) ||
           (d<minY&&e<minY&&f<minY) ||
           (d>maxY&&e>maxY&&f>maxY))continue;
        /* B17 project retains original world Z-up and the armor depth sign. */
        B17Projected p0=b17_project(cam,tri->p[0],tri->p[1],tri->p[2]);
        B17Projected p1=b17_project(cam,tri->p[3],tri->p[4],tri->p[5]);
        B17Projected p2=b17_project(cam,tri->p[6],tri->p[7],tri->p[8]);
        if(!p0.ok||!p1.ok||!p2.ok)continue;
        /* Reject triangles trivially outside screen, not merely outside radius. */
        if((p0.x<0&&p1.x<0&&p2.x<0) ||
           (p0.x>=IM2_W&&p1.x>=IM2_W&&p2.x>=IM2_W) ||
           (p0.y<0&&p1.y<0&&p2.y<0) ||
           (p0.y>=IM2_H&&p1.y>=IM2_H&&p2.y>=IM2_H))continue;
        const uint32_t rgb=tri->rgb;
        uint32_t color=packrgb((int)((rgb>>16)&255u),
                               (int)((rgb>>8)&255u),
                               (int)(rgb&255u));
        b17_floor_tri(out,depth,p0,p1,p2,color);
        used[category]++;
    }
    return 1;
}
"""
s=s.replace(anchor,extra+"\n"+anchor)
needle="b17_world_floor(pixels,zbuffer,camera);"
assert s.count(needle)==1
s=s.replace(needle,"if(!b24_c1_scene(pixels,zbuffer,camera))b17_world_floor(pixels,zbuffer,camera);")
r.write_text(s)
# All original B7/B8/B13/B14/B16 native regression/preview executables which
# compile renderer.c also need the C1L1 parser linked, not only im2_beta.
cmake=ROOT/"CMakeLists.txt"
s=cmake.read_text()
assert "B24_C1L1_MAP_LINK" not in s
s+='''

# B24_C1L1_MAP_LINK: original stage source module for every renderer target.
get_property(b24c1_targets DIRECTORY PROPERTY BUILDSYSTEM_TARGETS)
foreach(_b24c1_target IN LISTS b24c1_targets)
  get_target_property(_b24c1_kind ${_b24c1_target} TYPE)
  if(_b24c1_kind STREQUAL "EXECUTABLE" OR
     _b24c1_kind STREQUAL "STATIC_LIBRARY" OR
     _b24c1_kind STREQUAL "SHARED_LIBRARY")
    target_sources(${_b24c1_target} PRIVATE
      ${CMAKE_CURRENT_SOURCE_DIR}/b24/b24_unified/b24_c1l1_map.c)
  endif()
endforeach()
'''
cmake.write_text(s)
print("B24 original C1L1 map CPU-LOD scene renderer hooked: replacing repeated tiles when map valid; fallback preserved.")
