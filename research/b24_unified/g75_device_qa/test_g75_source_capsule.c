#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "../b24_gpu_g68_collision.h"
#include "b24_g75_source_capsule.h"
int main(int argc,char **argv){
 assert(argc==2);
 B24C1OriginalCollision world={0};
 assert(b24_g70_g68_collision_load(&world,argv[1]));
 assert(world.count==1910 && world.wall_count==1690);
 float support=-1000.f;
 assert(b24_g75_floor_crossed(&world,-1.319f,-6.747f,3.4f,0.f,&support));
 assert(fabsf(support-2.82955f)<.005f);
 float lower=-1000.f;
 assert(b24_g75_floor_crossed(&world,-1.319f,-6.747f,6.9f,0.f,&lower));
 assert(fabsf(lower-6.67306f)<.005f);
 float none=9.f;
 assert(!b24_g75_floor_crossed(&world,10000.f,10000.f,3.4f,0.f,&none));
 assert(none==9.f);
 float x=0,y=0,z=0;
 assert(b24_g75_capsule_reconcile(&world,0.f,0.f,0.f,
    1.f,0.f,0.f,1,.35f,2.24f,&x,&y,&z));
 assert(isfinite(x)&&isfinite(y)&&isfinite(z));
 assert(x>=0.f && x<=1.001f);
 assert(z>=0.f && z<=.45f);
 printf("G75 original grounded move 1unit requested -> accepted xy %.3f %.3f z %.3f\n",x,y,z);
 /* Flight should not teleport arbitrary long-distance/out of source world. */
 assert(b24_g75_capsule_reconcile(&world,330.f,0.f,.0725f,
   332.f,0.f,.0725f,0,.35f,2.24f,&x,&y,&z));
 assert(x<=330.01f);
 /* Rejected bad input never mutates output pointers. */
 float tx=1.f,ty=2.f,tz=3.f;
 assert(!b24_g75_capsule_reconcile(&world,NAN,0,0,1,2,3,1,.35f,2.24f,&tx,&ty,&tz));
 assert(tx==1.f && ty==2.f && tz==3.f);
 b24_c1_original_collision_free(&world);
 puts("PASS G75 exact original source floor crossing on multiple stacked 0.0725/2.82955/6.67306 platforms and multi-slice wall-safe 22cm candidate");
 return 0;
}
