/* Independent PS Vita third-person mechanics playground. No original physics. */
#include "b14_world.h"
#include <math.h>
#include <string.h>
#define P 3.14159265358979323846f
static float cl(float x,float l,float h){return x<l?l:(x>h?h:x);}
static const float loc[3][3]={{0.f,7.f,.55f},{3.0f,10.0f,.95f},{-3.5f,13.f,1.5f}};
void b14_world_init(B14World *w){memset(w,0,sizeof(*w));w->pitch=.12f;w->head_height=1.02f;w->camera_distance=4.35f;w->cam_z=w->head_height;w->screen_x=278;w->screen_y=110;}
void b14_world_tick(B14World *w,float dt,float strafe,float forward,float lookx,float looky,float vertical){
  dt=cl(dt,0,.10f);w->orbit+=cl(lookx,-1,1)*1.9f*dt;
  /* G75_SOURCE_ONLY_CALIBRATION: widen right-stick to -52.7/+60 degrees. */
w->pitch=cl(w->pitch+cl(looky,-1,1)*1.65f*dt,-.92f,1.05f);
  float a=cl(strafe,-1,1),b=cl(forward,-1,1);float len=sqrtf(a*a+b*b);
  if(len>1.f){a/=len;b/=len;len=1.f;}
  float vx=cosf(w->orbit)*a+sinf(w->orbit)*b;
  float vy=-sinf(w->orbit)*a+cosf(w->orbit)*b;
  w->speed=len;
  /* B16 measured user feedback: Stage 1 should occupy MOST of the analogue travel.
     Hysteresis prevents animation flicker around the full-flight boundary. */
  const int was_fast=w->flight_stage>=2;
  const float normal_threshold=was_fast?.88f:.96f;
  /* Controller strength selects upright drift / horizontal flight / boost.
   * Boost only applies at strong stick deflection, not during slow hover. */
  w->flight_stage=!w->flying||len<.16f?0:(len<normal_threshold?1:(w->rush?3:2));
  if(len>.12f){
    float desired=atan2f(vx,vy);
    float delta=atan2f(sinf(desired-w->heading),cosf(desired-w->heading));
    w->heading+=cl(delta,-dt*8.f,dt*8.f);
  }
  /* G75 proposed iOS-feel flight pace, not decoded Gameloft C++.
       Keep authentic merged stage1 HOVER stage2 CRUISE stage3 RUSH.
       Existing B14 CPU main loop remains sole integrator. */
 const float speed_target=w->flying?(w->flight_stage==3?24.f:(w->flight_stage==2?12.f:4.2f)):(len>=.96f?5.2f:2.7f);
 const float smoothing=1.f-expf(-(w->flying?(w->flight_stage==3?7.f:9.f):14.f)*dt);
 w->authored_move_vx+=(vx*speed_target-w->authored_move_vx)*smoothing;
 w->authored_move_vy+=(vy*speed_target-w->authored_move_vy)*smoothing;

  /* G8 TRUE ORIGINAL 2010 C1L1 map coverage: source C1WC BDAE extents,
     not B14's independent tiny +/-20 demo arena. No fabricated wall. */
  /* G136_REAL_CITY_BOUND_B14_WORLD_SOURCE: original 2010
    67,323 G66M source vertices measured X min/max, radius inset.
    Not an original scripted mission-playable zone / suit flight gate. */
#ifdef B24_G136_SOURCE_B14_WORLD_BOUNDS
w->x=cl(w->x+w->authored_move_vx*dt,-760.6839355f,648.8437866f);
#else
w->x=cl(w->x+w->authored_move_vx*dt,-324.f,330.f);
#endif
  #ifdef B24_G136_SOURCE_B14_WORLD_BOUNDS
w->y=cl(w->y+w->authored_move_vy*dt,-773.1599487f,586.3453125f);
#else
w->y=cl(w->y+w->authored_move_vy*dt,-351.f,254.f);
#endif
  if(w->flying)
     
#ifdef B24_G75_SOURCE_CAPSULE
     /* Existing prototype hover/travel range, relative to actual takeoff
      * feet. A high/negative source floor must not force flight toward Z=0. */
     w->target_z=cl(w->target_z+vertical*6.0f*dt,
                    w->flight_base_z+.35f,w->flight_base_z+36.f);
#else
     w->target_z=cl(w->target_z+vertical*6.0f*dt,.35f,36.f);
#endif /* 33.925 original rooftop source max */
  
  else
#ifdef B24_G75_SOURCE_CAPSULE
  /* B14_WORLD_HEIGHT_SUPPORT: remain on accepted source support, or
   * continue the existing bounded descent until G75 catches a real floor.
   * Never manufacture a support plane at absolute world zero. */
  w->target_z=w->ground_supported?w->ground_z:w->z-7.f*dt;
#else
  w->target_z=0;
#endif
  w->z+=cl(w->target_z-w->z,-7.f*dt,7.f*dt);
  /* Camera follows the player in the world, not the model orbiting in place. */
  const float follow=cl(7.f*dt,0,1);
  w->cam_x+=(w->x-w->cam_x)*follow;
  w->cam_y+=(w->y-w->cam_y)*follow;
  w->cam_z+=(w->z+w->head_height-w->cam_z)*follow;
  w->cooldown=cl(w->cooldown-dt,0,2);w->beam_time=cl(w->beam_time-dt,0,2);
  if(w->completed){w->wave_timer-=dt;if(w->wave_timer<=0.f)b15_world_spawn(w);}
  b14_world_target(w);
}
void b14_world_project(const B14World *w,float x,float y,float z,float *sx,float *sy,float *scale){
  float rx=cosf(w->orbit),ry=-sinf(w->orbit),fx=sinf(w->orbit),fy=cosf(w->orbit);
  /* Camera orbits a fixed point at the suit's HEAD. Pitch changes its
   position on a sphere around that pivot, not merely its view angle. */
  const float radial=w->camera_distance*cosf(w->pitch);
  float camx=w->cam_x-fx*radial+rx*.55f;
  float camy=w->cam_y-fy*radial+ry*.55f;
  float camz=w->cam_z+w->camera_distance*sinf(w->pitch)+.07f;
  float dx=x-camx,dy=y-camy,dz=z-camz;
  float sideways=dx*rx+dy*ry;
  float depth=dx*fx+dy*fy;
  float v=depth*sinf(w->pitch)+dz*cosf(w->pitch);
  float dist=depth*cosf(w->pitch)-dz*sinf(w->pitch);
  if(dist<.15f){if(sx)*sx=-500;if(sy)*sy=-500;if(scale)*scale=0;return;}
  if(scale)*scale=350.f/dist;
  if(sx)*sx=240.f+sideways*350.f/dist;
  if(sy)*sy=100.f-v*350.f/dist;
}
void b15_world_spawn(B14World *w){
 w->hits=0;w->completed=0;w->wave_timer=0.f;w->waves++;
}
void b14_world_target(B14World *w){
  if(w->completed){w->visible=0;return;}
  int i=w->hits;if(i>2)i=2;
  float s=0;b14_world_project(w,loc[i][0],loc[i][1],loc[i][2],&w->screen_x,&w->screen_y,&s);
  w->screen_radius=cl(s*.22f,6,34);
  w->visible=s>0 && w->screen_x>=-35 && w->screen_x<515 && w->screen_y>=-35 && w->screen_y<295;
}
int b14_world_fire(B14World *w){
 if(w->cooldown>0.f)return 0;
 w->cooldown=.22f;w->beam_time=.14f;w->shots++;
 /* Never lock the shooting action after the target wave is cleared. */
 if(w->completed)return 0;
 float dx=w->screen_x-278.f,dy=w->screen_y-110.f;
 if(w->visible && dx*dx+dy*dy<(w->screen_radius+9.f)*(w->screen_radius+9.f)){
   w->hits++;w->total_hits++;if(w->hits>=3){w->completed=1;w->wave_timer=1.35f;}else b14_world_target(w);return 1;
 }
 return 0;
}

/* B14_WORLD_HEIGHT_SUPPORT: helpers only change B14 intent/contact state.
 * B14 tick remains the sole integrator; G75 alone accepts source collision.
 * .8 / .35 / 36 / 7 are existing PORT prototype values, not iOS discoveries. */
void b14_world_toggle_flight(B14World *w){
 if(!w)return;
#ifndef B24_G75_SOURCE_CAPSULE
 /* Standalone B14 still has its explicit Z=0 playground and no G75 owner. */
 w->flying=!w->flying;
 w->target_z=w->flying?fmaxf(w->target_z,.8f):0.f;
#else
 if(!w->flying){
  w->flying=1;
  w->flight_base_z=w->z;
  w->target_z=w->z+.8f;
 }else{
  w->flying=0;
  w->target_z=w->z;
 }
 w->ground_supported=0;
#endif
}
void b14_world_accept_ground_support(B14World *w,int found,float support_z){
 if(!w)return;
 w->ground_supported=!w->flying&&found&&isfinite(support_z)&&
                       fabsf(w->z-support_z)<=.0001f;
 if(w->ground_supported){
  w->ground_z=support_z;
  w->target_z=support_z;
 }
}
