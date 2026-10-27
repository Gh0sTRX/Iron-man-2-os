/* Real reconstructed B14 + G75 + G159/G160/G171 integration, host only.
 * Original source geometry is supplied at runtime. Translated copies below
 * are explicitly synthetic reference-frame tests, never original spawns. */
#include "b14_world.h"
#include "b24_g75_source_capsule.h"
#include "b24_gpu_g68_collision.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static B14World world;
static int landing_now;
static unsigned landing_started;
static int b24_game;
static float last_proposed_z;
enum {SDL_CONTROLLER_BUTTON_B=1};
typedef struct {struct {int button;} cbutton;} SDL_Event;
static int b24_unified_paused(const int *paused){return *paused;}
static unsigned SDL_GetTicks(void){return 1234u;}
static void circle(int paused){
 SDL_Event e={{SDL_CONTROLLER_BUTTON_B}};
 b24_game=paused;
 /* Generated from the ACTUAL guarded SDL event in work/src/main.c. */
#include "actual_circle_event.inc"
}

static void support(B24C1OriginalCollision *city){
#ifdef B14_WORLD_HEIGHT_SUPPORT
 float h=0.f;
 int found=!world.flying&&b24_g75_support_at(city,world.x,world.y,world.z,&h);
 b14_world_accept_ground_support(&world,found,h);
#else
 (void)city;
#endif
}

static void tick(B24C1OriginalCollision *city,float dt,float x,float y,float vertical){
 const float ox=world.x,oy=world.y,oz=world.z;
 b14_world_tick(&world,dt,x,y,0,0,vertical);
 const float px=world.x,py=world.y,pz=world.z;
 last_proposed_z=pz;
 float ax=world.x,ay=world.y,az=world.z;
 assert(b24_g75_capsule_reconcile(city,ox,oy,oz,ax,ay,az,
     !world.flying,.35f,2.24f,&ax,&ay,&az));
 world.x=ax;world.y=ay;world.z=az;
 const float follow=fminf(7.f*dt,1.f);
 world.cam_x+=(ax-px)*follow;
 world.cam_y+=(ay-py)*follow;
 world.cam_z+=(az-pz)*follow;
 support(city);
 assert(isfinite(world.x)&&isfinite(world.y)&&isfinite(world.z));
 assert(isfinite(world.cam_x)&&isfinite(world.cam_y)&&isfinite(world.cam_z));
}

static void init_at(B24C1OriginalCollision *city,float x,float y,float z){
 b14_world_init(&world);
 world.x=x;world.y=y;world.z=z;world.target_z=z;
 world.cam_x=x;world.cam_y=y;world.cam_z=z+world.head_height;
 float ax=x,ay=y,az=z;
 assert(b24_g75_capsule_reconcile(city,x,y,z,x,y,z,1,.35f,2.24f,&ax,&ay,&az));
 assert(fabsf(az-z)<.05f);
 world.x=ax;world.y=ay;world.z=az;
 support(city);
}

static void takeoff_regression(B24C1OriginalCollision *city,float z){
 init_at(city,-160.f,-160.f,z);
 const float start=world.z;
 /* Same state as a preceding grounded frame, not a helpful hand-set target. */
 tick(city,1.f/60.f,0,0,0);
 circle(0);
 assert(world.flying && !landing_now && landing_started==1234u);
 const float before=world.z;
 tick(city,1.f/60.f,0,0,0);
 printf("takeoff source floor=%.6f before=%.6f target=%.6f B14_proposal=%.6f G75_resolved=%.6f\n",
        start,before,world.target_z,last_proposed_z,world.z);fflush(stdout);
 assert(world.z>before); /* Old Z=2.6937 -> 2.577033: failed takeoff. */
}

static void landing_regression(B24C1OriginalCollision *city){
 init_at(city,-160.f,-160.f,2.6937f);
 const float floor=world.z;
 world.z=floor+.8f;world.target_z=0.f;
 support(city);
 for(unsigned i=0;i<480;i++)tick(city,1.f/120.f,0,0,0);
 printf("landing source floor=%.6f resolved=%.6f gap=%.6f\n",
        floor,world.z,world.z-floor);fflush(stdout);
 assert(fabsf(world.z-floor)<.001f);
}

#ifdef B14_WORLD_HEIGHT_SUPPORT
static unsigned cases;
static void stationary_cycle(B24C1OriginalCollision *city,float z,float dt){
 init_at(city,-160.f,-160.f,z);
 const float floor=world.z;
 assert(world.ground_supported);
 for(unsigned n=0;n<10;n++){
  circle(0);
  const float launch=world.flight_base_z;
  assert(fabsf(launch-floor)<.0001f);
  for(unsigned i=0;i<(unsigned)ceilf(2.f/dt);i++)tick(city,dt,0,0,0);
  assert(fabsf(world.z-(launch+.8f))<.001f);
  assert(!world.ground_supported);
  B14World before=world;
  const int old_landing=landing_now;
  const unsigned old_time=landing_started;
  circle(1);
  assert(memcmp(&world,&before,sizeof(world))==0);
  assert(landing_now==old_landing&&landing_started==old_time);
  circle(0);
  assert(!world.flying && landing_now);
  for(unsigned i=0;i<(unsigned)ceilf(3.f/dt);i++)tick(city,dt,0,0,0);
  if(!world.ground_supported)fprintf(stderr,
      "landing failure dt=%.8f cycle=%u floor=%.8f feet=%.8f target=%.8f\n",
      dt,n,floor,world.z,world.target_z);
  assert(world.ground_supported);
  assert(fabsf(world.z-floor)<.001f);
  assert(fabsf(world.cam_z-(floor+world.head_height))<.002f);
  before=world;circle(1);
  assert(memcmp(&world,&before,sizeof(world))==0);
 }
 cases++;
}

static void range_and_support(B24C1OriginalCollision *city,float z){
 init_at(city,-160.f,-160.f,z);
 float h=777.f;
 assert(b24_g75_support_at(city,world.x,world.y,world.z,&h));
 const float floor=world.z;
 h=777.f;
 assert(!b24_g75_support_at(city,world.x,world.y,world.z+.1f,&h));
 assert(h==777.f); /* Nearby is not accepted support. */
 assert(!b24_g75_support_at(NULL,0,0,0,&h));
 assert(!b24_g75_support_at(city,NAN,0,0,&h));
 circle(0);
 const float base=world.flight_base_z;
 world.target_z=base-100.f;
 b14_world_tick(&world,1.f/60.f,0,0,0,0,-1.f);
 assert(fabsf(world.target_z-(base+.35f))<.0001f);
 world.target_z=base+100.f;
 b14_world_tick(&world,1.f/60.f,0,0,0,0,1.f);
 assert(fabsf(world.target_z-(base+36.f))<.0001f);
 assert(world.flight_base_z==base);
 b14_world_accept_ground_support(&world,1,world.z);
 assert(!world.ground_supported); /* Flight is not grounded by proximity. */
 /* Descend from ABOVE the last takeoff level to a lower actual surface.
  * Landing must not stop at the takeoff datum or at absolute world zero. */
 world.z=floor+10.f;world.target_z=world.z;
 world.cam_z=world.z+world.head_height;
 world.flight_base_z=floor+8.f;
 circle(0);
 for(unsigned i=0;i<240;i++)tick(city,1.f/60.f,0,0,0);
 assert(world.ground_supported);
 assert(fabsf(world.z-floor)<.001f);
 /* Reject a fabricated support acknowledgment; continue bounded descent. */
 world.z=floor+4.f;
 b14_world_accept_ground_support(&world,1,floor);
 assert(!world.ground_supported);
 const float before=world.z;
 b14_world_tick(&world,.09f,0,0,0,0,0);
 assert(world.z<before && fabsf(world.z-before)<=7.f*.09f+.0001f);
 cases++;
}

static void movement_cycle(B24C1OriginalCollision *city){
 init_at(city,-160.f,-160.f,2.6937f);
 const float y=world.y;
 for(unsigned i=0;i<120;i++)tick(city,1.f/60.f,0,1,0);
 assert(world.y>y+5.f && world.ground_supported);
 const float floor=world.z;
 circle(0);
 for(unsigned i=0;i<60;i++)tick(city,1.f/60.f,0,0,0);
 float before=world.y;
 for(unsigned i=0;i<60;i++)tick(city,1.f/60.f,0,1,0);
 const float cruise=world.y-before;
 assert(world.flight_stage==2 && cruise>5.f);
 world.rush=1;before=world.y;
 for(unsigned i=0;i<60;i++)tick(city,1.f/60.f,0,1,0);
 const float rush=world.y-before;
 assert(world.flight_stage==3 && rush>cruise);
 assert(fabsf(world.z-(floor+.8f))<.01f);
 world.rush=0;
 for(unsigned i=0;i<60;i++)tick(city,1.f/60.f,0,0,0);
 circle(0);
 for(unsigned i=0;i<180;i++)tick(city,1.f/60.f,0,0,0);
 assert(world.ground_supported);
 printf("real source walk/cruise/rush/landing: cruise=%.4f rush=%.4f endZ=%.6f\n",
        cruise,rush,world.z);
 cases++;
}
#endif

int main(int argc,char **argv){
 if(argc!=3)return 2;
 B24C1OriginalCollision city={0};
 assert(b24_g70_g68_collision_load(&city,argv[1]));
 assert(city.count==1910u && city.wall_count==1690u && city.faces[715].wall);
 const int translated=strcmp(argv[2],"translated")==0;
 if(strcmp(argv[2],"baseline-landing")==0){
  landing_regression(&city);b24_c1_original_collision_free(&city);return 0;
 }
 if(!translated)takeoff_regression(&city,2.6937f);
#ifdef B14_WORLD_HEIGHT_SUPPORT
 if(translated){
  /* Synthetic metamorphic copy of ORIGINAL native triangles. No original
   * source is modified; optional visual/road assets intentionally absent. */
  const float shift[]={-40.f,40.f,200.f};float old_shift=0.f;
  for(unsigned j=0;j<3;j++){
   const float delta=shift[j]-old_shift;old_shift=shift[j];
   for(unsigned i=0;i<city.count;i++){
    for(unsigned v=0;v<3;v++)city.faces[i].xyz[v*3+2]+=delta;
    city.faces[i].minz+=delta;city.faces[i].maxz+=delta;
   }
   stationary_cycle(&city,.0725f+shift[j],1.f/60.f);
   range_and_support(&city,.0725f+shift[j]);
  }
 }else{
  landing_regression(&city);
  const float rates[]={1.f/120.f,1.f/60.f,1.f/30.f,1.f/15.f,.09f};
  for(unsigned i=0;i<5;i++){
   stationary_cycle(&city,2.6937f,rates[i]);
   stationary_cycle(&city,.0725f,rates[i]);
  }
  range_and_support(&city,2.6937f);
  movement_cycle(&city);
 }
 printf("PASS world-height integration: %u scenario groups; %s; no device/VPK claim\n",
        cases,translated?"SYNTHETIC shifted native geometry":"ORIGINAL unmodified geometry");
#endif
 b24_c1_original_collision_free(&city);
 return 0;
}
