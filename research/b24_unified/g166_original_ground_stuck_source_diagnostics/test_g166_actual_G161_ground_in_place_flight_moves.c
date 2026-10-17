#include "b24_g75_source_capsule.h"
#include "b24_gpu_g68_collision.h"
#include "b24_g159_real_source_road.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
/* G166: diagnostic of ACTUAL G161/G165 source gameplay ONLY. No proxy
 * movement, fabricated geometry, fake floors or Vita FPS inference.
 * G161 player reports ground animation advances but B14 location does
 * not move; flight moves. Exact original G66C + 2010 G66M assets.
 * Compare identical proposed original-source XY delta and native B14
 * floor height in grounded=1 vs airborne=0. Report failures by
 * actual source coordinates, do NOT hide them by increasing speed.
 */
static void eval(const B24C1OriginalCollision *w,float x,float y,float z,
                 float dx,float dy, int *ground_moved,int *air_moved){
 float gx=x,gy=y,gz=z,ax=x,ay=y,az=z;
 assert(b24_g75_capsule_reconcile(w,x,y,z,x+dx,y+dy,z,
     1,.35f,2.24f,&gx,&gy,&gz));
 assert(b24_g75_capsule_reconcile(w,x,y,z,x+dx,y+dy,z,
     0,.35f,2.24f,&ax,&ay,&az));
 *ground_moved=hypotf(gx-x,gy-y)>.001f;
 *air_moved=hypotf(ax-x,ay-y)>.001f;
}
int main(int argc,char **argv){
 if(argc!=2)return 2;
 B24C1OriginalCollision w={0};
 B24G159Road road={0};
 assert(b24_g159_road_open(&road,"app0:assets/G66_city.g66m"));
 assert(b24_g70_g68_collision_load(&w,argv[1]));
 assert(w.count==1910u&&w.wall_count==1690u);
 int grounded_samples=0,blocked_ground=0,air_ok_ground_blocked=0;
 int blocked_air=0,show=0;
 float z;
 const float xs[]={0.f,-1.319f,-160.f,-120.f,-80.f,-40.f,40.f,80.f,120.f,160.f};
 const float ys[]={0.f,-6.747f,-160.f,-120.f,-80.f,-40.f,40.f,80.f,120.f,160.f};
 for(unsigned i=0;i<sizeof(xs)/sizeof(xs[0]);i++){
  for(unsigned j=0;j<sizeof(ys)/sizeof(ys[0]);j++){
   for(int level=0;level<4;level++){
    const float target=level==0?0.0725f:level==1?2.6937f:
                       level==2?2.82955f:6.673064f;
    /* Start only on ACTUAL original native G66C support unless
     * G159 true source road confirms this starting road level. */
    float native=0.f;
    if(b24_g74_near_original_floor(&w,xs[i],ys[j],target,&native))
      z=native;
    else if(b24_g159_road_near(&road,xs[i],ys[j],target,&z))
      { /* Verified actual road polygon under this XY, not guessed height. */ }
    else continue;
    int ground=0,air=0;
    eval(&w,xs[i],ys[j],z,.12f,0.f,&ground,&air);
    grounded_samples++;
    blocked_ground+=!ground;blocked_air+=!air;
    if(!ground&&air){
     air_ok_ground_blocked++;
     if(show++<16)printf("G166 2010 sample ground STUCK air MOVES XY=(%.3f,%.3f) supportZ=%.5f native=%d\n",
                      xs[i],ys[j],z,
                      b24_g74_near_original_floor(&w,xs[i],ys[j],z,&native));
    }
   }
  }
 }
 /* Stable long-running individual point check from the already
  * source-tested G159 actual original road ground. */
 int roadg=0,roada=0;
 eval(&w,-160.f,-160.f,2.6937f,.12f,0.f,&roadg,&roada);
 printf("G166 original C1L1 G161 exact single G75 native physics: %d original source support/road probes, %d ground-motion blocked, %d airborne blocked, %d source cases WALK STUCK but FLIGHT MOVES; G159 authenticated road(-160,-160,2.6937) grounded move=%d air move=%d\n",
 grounded_samples,blocked_ground,blocked_air,air_ok_ground_blocked,roadg,roada);
 assert(grounded_samples>0);
 b24_g159_road_close(&road);
 b24_c1_original_collision_free(&w);
 puts("G166 DIAGNOSTIC COMPLETE: this reports original authored G66 source 2010 ground vs flight, no invented walk-speed correction and NO VPK");
 return 0;
}
