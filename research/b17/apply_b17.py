#!/usr/bin/env python3
"""Apply reversible B17 experimental changes to freshly reconstructed private B16E work/.
Do not patch old archived overlays or installed apps. All changes originate in this file."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2] / "work"

def replace(path, old, new, count=1):
    p=ROOT/path
    s=p.read_text()
    matches=s.count(old)
    if matches != count:
        raise RuntimeError(f"{p}: needed {count} occurrences; found {matches} of {old[:110]!r}")
    p.write_text(s.replace(old,new))

# Hardware user feedback: ground WALK/RUN solely from analogue strength, no run button.
replace("src/b14_world.c",
  '(w->rush?2.2f:1.1f);',
  '(len>=.78f?2.4f:1.1f);')
replace("src/b14_pose.c",
  'if(flight_stage==2 || adv->armor==2)return B14_FLY;',
  'if(flight_stage==2)return B14_FLY;')
replace("src/b14_pose.c",
  'case B14_FLY:return get_adv(a,a->armor==2?B13_FLOAT_MOVE:B13_FLY_NORMAL);',
  'case B14_FLY:return get_adv(a,B13_FLY_NORMAL);')
# WM stage 2 uses recovered native fly .im2v (via B7 fallback), stage 3 same original
# fly with DIFFERENT temporary prototype forward lean; authentic Rush retarget pending.

def replace_once(path, old, new):
    replace(path,old,new)

# Determine authenticated mesh-point anchors by checking actual original IM2T geometry.
# In viewer they're still vertex IDs, so projection follows live skinned mesh each frame.
main=ROOT/"src/main.c"
s=main.read_text()
needle='static B8Combat range={0};'
assert s.count(needle)==1
anchors=r'''
static unsigned b17_chest_vertex=0,b17_shoulder_vertex=0;
static unsigned b17_find_anchor(const IM2Model *m,int shoulder) {
    if(!m || !m->nv)return 0;
    float minx=m->vertices[0].x,maxx=minx;
    float miny=m->vertices[0].y,maxy=miny;
    float minz=m->vertices[0].z,maxz=minz;
    for(unsigned i=1;i<m->nv;i++){
        const IM2Vertex v=m->vertices[i];
        if(v.x<minx)minx=v.x;if(v.x>maxx)maxx=v.x;
        if(v.y<miny)miny=v.y;if(v.y>maxy)maxy=v.y;
        if(v.z<minz)minz=v.z;if(v.z>maxz)maxz=v.z;
    }
    const float dx=fmaxf(.01f,maxx-minx),dy=fmaxf(.01f,maxy-miny),dz=fmaxf(.01f,maxz-minz);
    /* Best candidate surface vertex near chest arc-reactor or shoulder hardpoint.
       This IS a geometry heuristic, not a decoded original weapon socket. */
    const float wantx=shoulder?minx+dx*.79f:(minx+maxx)*.5f;
    const float wanty=miny+dy*.22f;
    const float wantz=minz+dz*(shoulder?.84f:.73f);
    float best=1e30f;unsigned which=0;
    for(unsigned i=0;i<m->nv;i++){
        const IM2Vertex v=m->vertices[i];
        float xx=(v.x-wantx)/dx,yy=(v.y-wanty)/dy,zz=(v.z-wantz)/dz;
        float metric=xx*xx*2.8f+yy*yy*.5f+zz*zz*3.f;
        if(metric<best){best=metric;which=i;}
    }
    return which;
}
static void b17_rush_lean(IM2Model *m,float radians) {
    if(!m || !m->vertices)return;
    float sn=sinf(radians),cs=cosf(radians);
    for(unsigned i=0;i<m->nv;i++) {
        float y=m->vertices[i].y,z=m->vertices[i].z-m->center_z;
        m->vertices[i].y=y*cs-z*sn;
        m->vertices[i].z=m->center_z+y*sn+z*cs;
    }
}
'''
assert s.count(needle)==1
s=s.replace(needle,needle+"\n"+anchors)
old='    if(!im2_load(&model, path))return 0;'
new='    if(!im2_load(&model, path))return 0;\n    b17_chest_vertex=b17_find_anchor(&model,0);\n    b17_shoulder_vertex=b17_find_anchor(&model,1);'
assert s.count(old)==1;s=s.replace(old,new)
# Strong stick deflection automatically activates ground run.
old='        B14Mode mode=b15_pose_pick(&motion13,world.flying,has_move,world.flight_stage,boost,landing_now,now-rush_begin);'
new='''        const int ground_run=!world.flying && world.speed>=.78f;
        B14Mode mode=b15_pose_pick(&motion13,world.flying,has_move,world.flight_stage,
                                 world.flying?boost:ground_run,landing_now,now-rush_begin);'''
assert s.count(old)==1;s=s.replace(old,new)
old='''        if(!b14_pose_tick_ex(&animator,&model,&motion,&motion13,mode,(unsigned)now,
              b16_idle_override(&attack,mode,idx))){running=0;break;}'''
new='''        const B13Clip *chosen=b16_idle_override(&attack,mode,idx);
        /* No neutral WM walk baked yet. Use REAL IronMan_run-to-WM skinned retarget
           rather than the known-bad, raised-hand Warmachine_Aim_Ground_move_F.
           This is interim locomotion, not verified original WM walking. */
        if(idx==2 && mode==B14_WALK && motion13.clips[B13_RUN].xyz)
            chosen=&motion13.clips[B13_RUN];
        if(!b14_pose_tick_ex(&animator,&model,&motion,&motion13,mode,(unsigned)now,
              chosen)){running=0;break;}
        if(idx==2 && world.flying && world.flight_stage==3)
            b17_rush_lean(&model,0.43f); /* PROTOTYPE tilt, NOT original Rush clip */'''
assert s.count(old)==1;s=s.replace(old,new)
old='''          const unsigned palm=((combat.shots&1)==0)?attack.palm_r:attack.palm_l;
          float muzzle[3];b16_model_palm(&model,&world,palm,muzzle);
          int fired=b16_combat_fire(&combat,&world,muzzle);
          if(fired>=0 && combat.mode!=B16_MELEE)
             b16_attack_begin(&attack,now,world.flying,palm==attack.palm_l,combat.mode==B16_UNIBEAM?2:combat.shots%3);
          trigger=0;'''
new='''          const unsigned palm=((combat.shots&1)==0)?attack.palm_r:attack.palm_l;
          const unsigned emitter=combat.mode==B16_UNIBEAM?b17_chest_vertex:
                                 combat.mode==B16_MISSILE?b17_shoulder_vertex:palm;
          float muzzle[3];b16_model_palm(&model,&world,emitter,muzzle);
          int fired=b16_combat_fire(&combat,&world,muzzle);
          if(fired>=0 && combat.mode==B16_REPULSOR)
              b16_attack_begin(&attack,now,world.flying,palm==attack.palm_l,combat.shots%3);
          trigger=0;'''
assert s.count(old)==1;s=s.replace(old,new)
old='''        camera.emitter_vertex=attack.hand?attack.palm_l:attack.palm_r;'''
new='''        camera.emitter_vertex=combat.mode==B16_UNIBEAM?(int)b17_chest_vertex:
              combat.mode==B16_MISSILE?(int)b17_shoulder_vertex:
              (attack.hand?(int)attack.palm_l:(int)attack.palm_r);'''
assert s.count(old)==1;s=s.replace(old,new)
old='''        const char *suffix=boost?(world.flying?" RUSH":" RUN"):"";'''
new='''        const char *suffix=world.flying?(world.flight_stage==3?" RUSH":""):
                           (ground_run?" RUN":"");'''
assert s.count(old)==1;s=s.replace(old,new)
old='''    SDL_Window *window=SDL_CreateWindow("Iron Man 2 - Combat B16",'''
new='''    SDL_Window *window=SDL_CreateWindow("Iron Man 2 - Arena B17",'''
assert s.count(old)==1;s=s.replace(old,new)
main.write_text(s)

# A truly world-anchored colored floor, with per-pixel inverse-depth comparison
# against the ORIGINAL armor rasterizer: geometry is our test environment, not
# a claim to have loaded the first mission's C1L1 geometry.
renderer=ROOT/"src/renderer.c"
s=renderer.read_text()
anchor='static void world_grid(uint32_t *pixels,const IM2Camera *cam){'
assert s.count(anchor)==1
floor=r'''
/* B17: bounded checkerboard rectangles on WORLD z=-1 plane. Every vertex
   goes through existing third-person camera projection. This is not a
   fixed-position 2-D HUD background and uses depth with the armor mesh. */
typedef struct {float x,y,iz;int ok;} B17Projected;
static B17Projected b17_project(const IM2Camera *cam,float x,float y,float z){
    B17Projected p={0};
    p.ok=world_to_screen(cam,x,y,z,&p.x,&p.y,&p.iz);
    if(!isfinite(p.x)||!isfinite(p.y)||fabsf(p.x)>3500||fabsf(p.y)>3500)p.ok=0;
    return p;
}
static void b17_floor_tri(uint32_t *out,float *depth,B17Projected a,
                          B17Projected b,B17Projected c,uint32_t col){
    if(!a.ok||!b.ok||!c.ok)return;
    float det=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y);
    if(fabsf(det)<.001f)return;
    int loX=CLAMP((int)floorf(MIN(a.x,MIN(b.x,c.x))),0,IM2_W-1);
    int hiX=CLAMP((int)ceilf(MAX(a.x,MAX(b.x,c.x))),0,IM2_W-1);
    int loY=CLAMP((int)floorf(MIN(a.y,MIN(b.y,c.y))),0,IM2_H-1);
    int hiY=CLAMP((int)ceilf(MAX(a.y,MAX(b.y,c.y))),0,IM2_H-1);
    /* Clip to gameplay space so top HUD is never hidden by the ground plane. */
    loY=MAX(loY,25);hiY=MIN(hiY,IM2_H-18);
    if(loX>hiX||loY>hiY)return;
    float inv=1.0f/det;
    for(int y=loY;y<=hiY;y++){
        for(int x=loX;x<=hiX;x++){
            float wx=x+.5f,wy=y+.5f;
            float q=((b.y-c.y)*(wx-c.x)+(c.x-b.x)*(wy-c.y))*inv;
            float r=((c.y-a.y)*(wx-c.x)+(a.x-c.x)*(wy-c.y))*inv;
            float t=1.f-q-r;
            if(q<-.0001f||r<-.0001f||t<-.0001f)continue;
            float iz=q*a.iz+r*b.iz+t*c.iz;
            size_t p=(size_t)y*IM2_W+(size_t)x;
            if(iz>depth[p]){depth[p]=iz;out[p]=col;}
        }
    }
}
static void b17_world_floor(uint32_t *out,float *depth,const IM2Camera *cam){
    const int baseX=(int)floorf(cam->player_x/2.f)*2;
    const int baseY=(int)floorf(cam->player_y/2.f)*2;
    for(int j=-5;j<=5;j++)for(int i=-5;i<=5;i++){
        float x=(float)(baseX+2*i),y=(float)(baseY+2*j);
        B17Projected a=b17_project(cam,x,y,-1.f);
        B17Projected b=b17_project(cam,x+2.f,y,-1.f);
        B17Projected c=b17_project(cam,x+2.f,y+2.f,-1.f);
        B17Projected d=b17_project(cam,x,y+2.f,-1.f);
        /* Muted cyan/steel panels with bright 4x4m positional stripes. */
        int edge=(i%4==0||j%4==0);
        uint32_t color=edge?packrgb(28,83,112):
          ((i+j)&1)?packrgb(20,59,82):packrgb(43,96,117);
        if(i==0 && j==0)color=packrgb(73,117,91);
        b17_floor_tri(out,depth,a,b,c,color);
        b17_floor_tri(out,depth,a,c,d,color);
    }
}
'''
s=s.replace(anchor,floor+'\n'+anchor)
old='''    if(camera->third_person)world_grid(pixels,camera);
    memset(zbuffer,0,sizeof(float)*IM2_W*IM2_H);'''
new='''    memset(zbuffer,0,sizeof(float)*IM2_W*IM2_H);
    if(camera->third_person){
        b17_world_floor(pixels,zbuffer,camera);
        world_grid(pixels,camera);
    }'''
assert s.count(old)==1;s=s.replace(old,new)
old='''camera->b16_active?"VITA COMBAT B16"'''
new='''camera->b16_active?"VITA ARENA B17"'''
assert s.count(old)==1;s=s.replace(old,new)
old='''            (int)camera->target_screen_y,(int)camera->target_radius,gold);'''
assert s.count(old)==1
# Don't display misleading straight repulsor tracer for missiles or melee:
old='''      if(camera->beam_time>0){'''
new='''      if(camera->beam_time>0 && camera->weapon_mode!=2 && camera->weapon_mode!=3){'''
assert s.count(old)==1;s=s.replace(old,new)
old='''          write_text(pixels,10,140,hud,packrgb(250,205,109),1);'''
new='''          write_text(pixels,10,140,hud,packrgb(250,205,109),1);
          if(camera->weapon_mode==B16_UNUSED_MELEE_CONSTANT)
              write_text(pixels,10,152,"MELEE: ORIGINAL ANIMATION NOT YET PORTED",packrgb(255,169,125),1);'''
# renderer deliberately does not include b16_action.h; avoid internal combat enum dependency
new=new.replace("B16_UNUSED_MELEE_CONSTANT","3")
assert s.count(old)==1;s=s.replace(old,new)
old='''      camera->b16_active?"L MOVE R CAM SQ ACT O FLY TRI BOOST D-UP WEAPON"'''
new='''      camera->b16_active?"L WALK/RUN R CAM SQ ACT O FLY TRI AIR BOOST"'''
assert s.count(old)==1;s=s.replace(old,new)
renderer.write_text(s)

# The historic B15 regression encoded "War Machine has NO distinct boost pose".
# B17 intentionally introduces a *temporary* lean via B14_RUSHFULL, so only
# the reconstructed B17 test expectation needs to be updated.
replace("tools/test_b15.c",
  'b15_pose_pick(&(B13Motion){.armor=2},1,1,3,1,0,650)==B14_FLY',
  'b15_pose_pick(&(B13Motion){.armor=2},1,1,3,1,0,650)==B14_RUSHFULL')

print('B17 arena source applied; original B16 ZIP, B15 VPKs, and original private IPA assets unchanged.')
