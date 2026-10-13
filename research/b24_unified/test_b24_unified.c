#include "b24_unified.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define NPIX 130560
static uint32_t screen[NPIX+2];
static void frame(B24Unified *g,B24Observation *in,int n){
 for(int i=0;i<n;i++)b24_unified_tick(g,in);
}
int main(void){
 B24Unified g;
 b24_unified_init(&g);
 assert(g.controls.state==IM2_PLAYING && g.missile.phase==B23_IDLE);
 B24Observation in={0};
 in.dt=1.f/60.f;in.suit_index=0;in.target_id=-1;
 in.weapon_index=0;in.stage=1;in.left_forward=.35f;
 frame(&g,&in,90);
 assert(g.visual_root.stage==IM2_FLIGHT_HOVER);
 assert(!g.speed_fx.enabled && g.camera_base.shoulder_to_chase<.01f);
 assert(!g.thruster_out.enabled[IM2_BACK_L]);
 /* Host uses synthetic sockets, not recovered original model hardware. */
 Im2ThrusterSocket six[IM2_THRUSTER_SOCKETS]={0};
 for(int i=0;i<IM2_THRUSTER_SOCKETS;i++){
    six[i].valid=1;
    six[i].model_position=(Im2Vec3){.3f,1.f,(float)i*.1f};
    six[i].model_exhaust_direction=(Im2Vec3){0.f,-1.f,0.f};
 }
 b24_unified_set_sockets(&g,six);
 in.stage=2;in.left_forward=.99f;in.right_x=.1f;
 frame(&g,&in,120);
 for(int i=0;i<4;i++)assert(g.thruster_out.enabled[i]);
 assert(!g.thruster_out.enabled[4]&&!g.thruster_out.enabled[5]);
 assert(!g.speed_fx.enabled && g.camera_base.shoulder_to_chase>.99f);
 assert(fabsf(b24_unified_chase_distance(&g)-4.65f)<.06f);
 in.stage=3;frame(&g,&in,100);
 for(int i=0;i<6;i++)assert(g.thruster_out.enabled[i]);
 assert(g.speed_fx.enabled && g.camera_base.rush_amount>.99f);
 assert(fabsf(b24_unified_chase_distance(&g)-5.85f)<.06f);
 in.stage=2;b24_unified_tick(&g,&in);
 assert(!g.thruster_out.enabled[4]&&!g.thruster_out.enabled[5]);
 for(int i=0;i<IM2_THRUSTER_MAX_PARTICLES;i++)
   assert(!g.thruster.particles[i].active || g.thruster.particles[i].socket_id<4);
 /* Missile targeting only when weapon MISSILE and L pressed. */
 in.stage=1;in.target_visible=1;in.target_alive=1;in.target_id=4;
 in.target_distance=8.f;in.target_screen_x=278;in.target_screen_y=110;
 in.target_health_percent=-1.f;in.weapon_index=0;in.buttons=IM2_BT_L;
 frame(&g,&in,50);assert(g.missile.phase==B23_IDLE);
 in.weapon_index=2;frame(&g,&in,45);
 assert(g.missile.phase==B23_LOCKED && g.missile.target_id==4);
 in.target_visible=0;b24_unified_tick(&g,&in);
 assert(g.missile.phase==B23_IDLE);
 in.buttons=0;b24_unified_tick(&g,&in);
 in.buttons=IM2_BT_START;b24_unified_tick(&g,&in);
 assert(b24_unified_paused(&g) && g.hud.page==B22_PAUSE);
 screen[0]=0x10203040u;screen[NPIX+1]=0x11223344u;
 b24_unified_draw_overlay(&g,screen+1,480);
 assert(screen[0]==0x10203040u&&screen[NPIX+1]==0x11223344u);
 in.buttons=0;b24_unified_tick(&g,&in);
 in.buttons=IM2_BT_START;b24_unified_tick(&g,&in);
 assert(!b24_unified_paused(&g));
 /* Fuzz: one authority, no Stage2 back and no implicit missile lock. */
 uint32_t rng=0x2026b240u;
 for(int k=0;k<20000;k++){
    rng=rng*1664525u+1013904223u;
    in.stage=(int)(rng%4u);
    in.left_x=(float)((int)((rng>>8)%201u)-100)/100.f;
    in.left_forward=(float)((int)((rng>>14)%201u)-100)/100.f;
    in.weapon_index=(int)(rng%4u);
    in.buttons=(rng&8u)?IM2_BT_L:0u;
    in.target_alive=1;in.target_visible=(int)((rng>>17)&1u);
    in.target_id=in.target_visible?4:-1;
    in.dt=k%233==0?NAN:1.f/60.f;
    b24_unified_tick(&g,&in);
    assert(isfinite(g.visual_root.visual_roll_rad));
    assert(isfinite(g.camera_base.shoulder_to_chase));
    assert(in.stage==3 || (!g.thruster_out.enabled[4]&&!g.thruster_out.enabled[5]));
    assert(in.weapon_index==2 || g.missile.phase==B23_IDLE);
 }
 puts("PASS B24 unified loop: B19/B21/B22/B23 + flight camera + exact RUSH-only thrusters, visor, 20k fuzz");
 return 0;
}
