/* Source support authority only: synthetic plates plus optional original road.
 * No original spawn, native solidity, controller or hardware claim. */
#include "b14_world.h"
#include "b24_g75_source_capsule.h"
#include "b24_gpu_g68_collision.h"
#include "b24_g159_real_source_road.h"
#include "b24_g87_transition_events.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static int contact(const B24C1OriginalCollision *city,float x,float y,float z,int flying){
 B14World world={0};world.x=x;world.y=y;world.z=z;world.flying=flying;
 B24C1OriginalCollision b24_original_walls=*city;B24G83Input g84_input={0};
 #include "actual_ground_contact.inc"
 return g84_input.grounded_contact_verified;
}
static void plate(float z){
 B24C1OriginalCollisionFace f={0};const float triangle[]={-10,-10,z,10,-10,z,0,10,z};
 memcpy(f.xyz,triangle,sizeof(triangle));f.minx=f.miny=-10;f.maxx=f.maxy=10;f.minz=f.maxz=z;
 B24C1OriginalCollision city={0};city.ready=1;city.count=1;city.faces=&f;
 assert(contact(&city,0,0,z,0));assert(!contact(&city,0,0,z,1));
 assert(!contact(&city,0,0,z+.04f,0));assert(!contact(&city,0,0,z-.04f,0));
 B24G87TransitionState events={0};
 assert(b24_g87_transition_tick(&events,B24G83_FLIGHT,0,0)==B24G83_EVENT_NONE);
 assert(b24_g87_transition_tick(&events,B24G83_GROUND,contact(&city,0,0,z+.04f,0),0)==B24G83_EVENT_NONE);
 assert(events.pending_landing);
 assert(b24_g87_transition_tick(&events,B24G83_GROUND,contact(&city,0,0,z,0),0)==B24G83_EVENT_FLY_TO_GROUND);
 assert(b24_g87_transition_tick(&events,B24G83_GROUND,contact(&city,0,0,z,0),0)==B24G83_EVENT_NONE);
}
static void original(const char *path,const char *mesh){
 B24C1OriginalCollision city={0};B24G159Road road={0};
 assert(b24_g70_g68_collision_load(&city,path));assert(b24_g159_road_open(&road,mesh));
 unsigned checked=0;
 for(unsigned i=0;i<road.count;i++){
  const float *p=road.faces[i].p;
  const float x=(p[0]+p[3]+p[6])/3.f,y=(p[1]+p[4]+p[7])/3.f,z=(p[2]+p[5]+p[8])/3.f;
  float a=x,b=y,c=z;
  assert(b24_g75_capsule_reconcile(&city,x,y,z,x,y,z,1,.35f,2.24f,&a,&b,&c));
  float h=0,unused=0;
  if(!b24_g75_support_at(&city,x,y,z,&h)||b24_g74_near_original_floor(&city,x,y,z,&unused))continue;
  assert(contact(&city,x,y,z,0));assert(!contact(&city,x,y,z,1));
  checked++;
 }
 assert(checked>20);printf("PASS %u original road-only supports agree with current G75 authority; no native-solidness/spawn claim\n",checked);
 b24_g159_road_close(&road);b24_c1_original_collision_free(&city);
}
int main(int argc,char **argv){
 if(argc==3){original(argv[1],argv[2]);return 0;}assert(argc==1);
 const float heights[]={-40,0,40,200};for(unsigned i=0;i<4;i++)plate(heights[i]);
 puts("PASS canonical contact query: no 4cm early landing, no below-floor/airborne contact; one transition on support");
 return 0;
}
