#include "b24_gpu_cpu_profile.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdint.h>
typedef struct {uint64_t value,step;} Clock;
static uint64_t clock_fn(void *ctx){
 Clock *c=(Clock *)ctx;c->value+=c->step;return c->value;
}
int main(void){
 B24CpuGpuProfile p={0};
 Clock c={0,1000};
 assert(!b24_gpu_profile_set_clock(NULL,clock_fn,&c,1.e6));
 assert(!b24_gpu_profile_set_clock(&p,NULL,&c,1.e6));
 assert(!b24_gpu_profile_set_clock(&p,clock_fn,&c,NAN));
 assert(b24_gpu_profile_set_clock(&p,clock_fn,&c,1.e6));
 assert(!p.actual_gpu_timing_available);
 for(int i=0;i<120;i++){
  b24_gpu_profile_begin(&p);
  assert(p.frames==(uint64_t)i);
  b24_gpu_profile_phase(&p,B24P_SCENE_CALLS);
  assert(p.next_phase==0); /* can't mislabel phases */
  for(int j=0;j<B24P_COUNT;j++){
    if(j==B24P_SWAP_WALL)c.step=16000; /* vblank WAIT, not GPU busy */
    else c.step=1000;
    b24_gpu_profile_phase(&p,(B24CpuGpuPhase)j);
    if(j!=B24P_SWAP_WALL)assert(fabs(p.last_ms[j]-1.)<.001);
  }
  assert(fabs(p.last_ms[B24P_SWAP_WALL]-16.)<.001);
  c.step=1000;
 }
 assert(p.frames==120);
 assert(!p.frame_open);
 assert(p.average_ms[B24P_HUD_CALLS]>.99);
 assert(p.max_ms[B24P_SWAP_WALL]==16.);
 assert(p.actual_gpu_timing_available==0);
 assert(p.last_ms[B24P_MODEL_STREAM]==1.);
 /* Non-monotonic clocks don't produce negative spikes. */
 b24_gpu_profile_begin(&p);
 c.value=5;
 b24_gpu_profile_phase(&p,B24P_MODEL_STREAM);
 assert(p.last_ms[B24P_MODEL_STREAM]==0.);
 printf("PASS B24 CPU/GPU profile: 120 frames, stage ordering, 6 CPU wall phases, VSync wall NOT GPU execution, invalid/rollback clocks\n");
 return 0;
}
