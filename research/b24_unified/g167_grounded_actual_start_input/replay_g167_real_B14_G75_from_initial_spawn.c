#include "b14_world.h"
#include "b24_g75_source_capsule.h"
#include "b24_gpu_g68_collision.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>

/* C11 test the ORIGINAL deployed G161 B14 tick movement and real G75
 * source post-tick reconcile, not just injecting fake proposed XY.
 * Source 2010 G66C/G66M remains authoritative; G161 B14 homebrew
 * init=0,0,0 is NOT native story entry, diagnosing actual device bug.
 * Run 120 real 60Hz game ticks with identical left-stick input.
 */
typedef struct{float x0,y0,z0, x1,y1,z1;unsigned proposed,accepted;} G167;
static G167 replay(const B24C1OriginalCollision *source,
                   float x,float y,float z,int flying,float strafe,float forward){
 B14World w;
 b14_world_init(&w);
 w.x=x;w.y=y;w.z=z;w.target_z=z;w.cam_x=x;w.cam_y=y;
 w.cam_z=z+w.head_height;w.flying=flying;
 G167 v={x,y,z,0,0,0,0,0};
 for(int frame=0;frame<120;frame++){
  const float beforex=w.x,beforey=w.y,beforez=w.z;
  b14_world_tick(&w,1.f/60.f,strafe,forward,0.f,0.f,0.f);
  if(hypotf(w.x-beforex,w.y-beforey)>.001f)v.proposed++;
  float px=w.x,py=w.y,pz=w.z;
  assert(b24_g75_capsule_reconcile(source,beforex,beforey,beforez,
     w.x,w.y,w.z,!w.flying,.35f,2.24f,&px,&py,&pz));
  w.x=px;w.y=py;w.z=pz;
  if(hypotf(w.x-beforex,w.y-beforey)>.001f)v.accepted++;
  if(frame==0||frame==1||frame==10||frame==119){
   printf("G167 real B14 frame=%3d flying=%d forward=%.2f proposed=(%.4f,%.4f) resolved=(%.4f,%.4f,%.4f) original_before=(%.4f,%.4f,%.4f)\n",
         frame,flying,forward,
         px,py,w.x,w.y,w.z,beforex,beforey,beforez);
  }
 }
 v.x1=w.x;v.y1=w.y;v.z1=w.z;return v;
}
int main(int argc,char**argv){
 if(argc!=2)return 2;
 B24C1OriginalCollision w={0};
 assert(b24_g70_g68_collision_load(&w,argv[1]));
 G167 a=replay(&w,0.f,0.f,0.f,0,0.f,1.f);
 G167 b=replay(&w,0.f,0.f,0.f,1,0.f,1.f);
 G167 c=replay(&w,-160.f,-160.f,2.6937f,0,0.f,.55f);
 G167 d=replay(&w,-160.f,-160.f,2.6937f,1,0.f,.55f);
 G167 e=replay(&w,-1.319f,-6.747f,.0725f,0,0.f,.55f);
 printf("G167 REAL ONE B14 G75 initial (0,0,0) ground accepted=%u/%u XY change=%.4f versus flight %u/%u change=%.4f; real road elevated ground %u/%u, flight %u/%u; nearby CLARA-local-source XY ground %u/%u\n",
   a.accepted,a.proposed,hypotf(a.x1-a.x0,a.y1-a.y0),
   b.accepted,b.proposed,hypotf(b.x1-b.x0,b.y1-b.y0),
   c.accepted,c.proposed,d.accepted,d.proposed,
   e.accepted,e.proposed);
 b24_c1_original_collision_free(&w);
 puts("G167 actual B14 real input -> G75 original source city physics diagnostic complete; no fake story spawn/height, NO VPK");
 return 0;
}
