#!/usr/bin/env python3
"""B24-C2 hardware feedback hotfix, modifies GENERATED work/ after B24-C1.
Fixes: 1-4FPS C1L1 CPU per-pixel overdraw, B17 banner, empty pause panel
(glyphs in b24_unified.c), missed START taps, flight manual-look auto-centre.
Uses true original C1L1 vertex coordinates. No claim of VitaGL/GPU backend.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/"work"
def replace(path,old,new,expected=1):
    p=ROOT/path; s=p.read_text()
    if s.count(old)!=expected:
        raise RuntimeError(f"B24-C2 refused {path}: {s.count(old)} matches expected {expected}: {old[:120]!r}")
    p.write_text(s.replace(old,new))
# Replace CPU-barycentric 1-pixel map polygons with bounded 4x4 diagnostic
# rasterization. This preserves original triangle *coordinates* and depth,
# though lower spatial resolution is intentionally new and temporary.
renderer=ROOT/"src/renderer.c"
s=renderer.read_text()
needle="static int b24_c1_scene(uint32_t *out,float *depth,const IM2Camera *cam){"
assert s.count(needle)==1
fast=r"""
/* B24-C2 stopgap: bounded CPU diagnostic triangles, 4x4 spatial sampling.
   The correct long-term rendering path is Vita GPU geometry with depth.
   Cap per-stage work in PIXEL BLOCK TESTS, not only triangle count. */
static void b24_c1_tri_fast(uint32_t *pixels,float *depth,
        B17Projected a,B17Projected b,B17Projected c,
        uint32_t color,int *remaining){
    if(!remaining||*remaining<=0||!a.ok||!b.ok||!c.ok)return;
    float det=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y);
    if(!isfinite(det)||fabsf(det)<0.001f)return;
    int minx=CLAMP((int)floorf(MIN(a.x,MIN(b.x,c.x))),0,IM2_W-1);
    int maxx=CLAMP((int)ceilf(MAX(a.x,MAX(b.x,c.x))),0,IM2_W-1);
    int miny=CLAMP((int)floorf(MIN(a.y,MIN(b.y,c.y))),25,IM2_H-22);
    int maxy=CLAMP((int)ceilf(MAX(a.y,MAX(b.y,c.y))),25,IM2_H-22);
    if(minx>maxx||miny>maxy)return;
    /* Fixed align: continuous tiles where adjacent triangles meet. */
    minx=(minx/4)*4;
    miny=(miny/4)*4;
    const float inv=1.f/det;
    for(int y=miny;y<=maxy && *remaining>0;y+=4){
        for(int x=minx;x<=maxx && *remaining>0;x+=4){
            --*remaining;
            float px=(float)x+2.f,py=(float)y+2.f;
            float q=((b.y-c.y)*(px-c.x)+(c.x-b.x)*(py-c.y))*inv;
            float r=((c.y-a.y)*(px-c.x)+(a.x-c.x)*(py-c.y))*inv;
            float t=1.f-q-r;
            if(q<-.0001f||r<-.0001f||t<-.0001f)continue;
            float z=q*a.iz+r*b.iz+t*c.iz;
            for(int yy=y;yy<y+4 && yy<=maxy && yy<IM2_H;yy++){
                for(int xx=x;xx<x+4 && xx<=maxx && xx<IM2_W;xx++){
                    size_t k=(size_t)yy*IM2_W+(size_t)xx;
                    if(z>depth[k]){depth[k]=z;pixels[k]=color;}
                }
            }
        }
    }
}
"""
s=s.replace(needle,fast+"\n"+needle)
s=s.replace("const int limits[4]={520,780,180,210};",
            "const int limits[4]={65,180,60,60};\n    int sample_budget[4]={6200,9000,1800,1400};")
s=s.replace("b17_floor_tri(out,depth,p0,p1,p2,color);",
            "b24_c1_tri_fast(out,depth,p0,p1,p2,color,&sample_budget[category]);")
old="if(!b24_c1_scene(pixels,zbuffer,camera))b17_world_floor(pixels,zbuffer,camera);"
assert s.count(old)==1
# On load failure do NOT silently go back to the costly B17 CPU checkerboard.
# Diagnostic old floor was measured at 235-839ms on physical Vita by user.
s=s.replace(old,'''int b24_map_ok=b24_c1_scene(pixels,zbuffer,camera);
        /* On-screen diagnostic: distinguishes missing app0: asset from camera culling. */
        write_text(pixels,337,181,b24_map_ok?"C1L1 READY":"C1L1 FAIL",
                   b24_map_ok?packrgb(120,230,168):packrgb(255,108,89),1);''')
assert s.count("VITA ARENA B17")>=1
# Original B17 grid overlay would overpaint the real Chapter1 geometry.
assert s.count("world_grid(pixels,camera);")==1
s=s.replace("world_grid(pixels,camera);","/* Original C1L1 environment, no B17 grid lines. */")
s=s.replace("VITA ARENA B17","B24 C1L1 TEST")
s=s.replace("MELEE: ORIGINAL ANIMATION NOT YET PORTED","MELEE COMBO CLIPS FOUND - NOT BAKED")
renderer.write_text(s)

# Real B14 orbit is the only on-screen camera authority; B22 camera remains
# advisory. Only after right-stick release in Stage2/RUSH should view recenter.
main=ROOT/"src/main.c"
s=main.read_text()
include='#include "../b24/b24_unified/b24_unified.h"'
assert s.count(include)==1
s=s.replace(include,include+'\n#include "../b24/b24_unified/b24_camera_recenter.h"')
seed='static B24Unified b24_game={0};'
assert s.count(seed)==1
s=s.replace(seed,seed+'\nstatic B24CameraRecenter b24_camera_follow={0};\nstatic uint32_t b24_input_latched=0;')
old='b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend);\n          b16_combat_tick(&combat,&world,dt);'
new='''b14_world_tick(&world,dt,move_x,move_y,turn,look,ascend);
          world.orbit=b24_camera_recenter(&b24_camera_follow,
              world.flying?world.flight_stage:0,dt,
              turn,look,world.orbit,world.heading);
          b14_world_target(&world);
          b16_combat_tick(&combat,&world,dt);'''
assert s.count(old)==1
s=s.replace(old,new)
# Preserve short START down events between long (>200ms) Vita rendering frames.
mark='''if(e.cbutton.button==SDL_CONTROLLER_BUTTON_START)running=0;'''
# B24 adapter replaces this with a line comment, so use event start matching.
mark='''/* B24: START toggles pause in unified controls. */'''
assert s.count(mark)==1
s=s.replace(mark,'''/* START is event-latched so a quick press can't be lost at low FPS. */
                b24_input_latched|=IM2_BT_START;''')
mark='''        world.camera_distance=clip(world.camera_distance-zoom*dt*1.8f,2.8f,6.4f);'''
assert s.count(mark)==1
s=s.replace(mark,'''        b24_buttons|=b24_input_latched;
        b24_input_latched=0;
'''+mark)
# Skip expensive world raster and pose updates during pause. The last valid
# framebuffer is retained, then a newly labeled pause UI overlays it.
old='im2_render(pixels,zbuffer,&model,&camera,label,frame++);\n        b24_unified_draw_overlay(&b24_game,pixels,IM2_W);'
new='''if(!b24_unified_paused(&b24_game))
            im2_render(pixels,zbuffer,&model,&camera,label,frame++);
        b24_unified_draw_overlay(&b24_game,pixels,IM2_W);'''
assert s.count(old)==1
s=s.replace(old,new)
needle='if(!b14_pose_tick_ex('
assert s.count(needle)==1
s=s.replace(needle,'if(!b24_unified_paused(&b24_game) && !b14_pose_tick_ex(')
s=s.replace('if(idx==2 && world.flying && world.flight_stage==3)',
            'if(!b24_unified_paused(&b24_game) && idx==2 && world.flying && world.flight_stage==3)')
main.write_text(s)
print("B24-C2 patched: app0:map, 4x4 CPU scene raster budgets, B24 banner, readable pause UI, START event latching, rear-follow camera.")
