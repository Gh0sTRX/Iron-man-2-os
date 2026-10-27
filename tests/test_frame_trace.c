#include "im2_frame_trace.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static uint64_t fake_tick(void *ctx){uint64_t *n=ctx;*n+=1000;return *n;}
int main(int argc,char **argv){
 assert(argc==2);
 B24CpuGpuProfile p={0};uint64_t ticks=0;
 assert(b24_gpu_profile_set_clock(&p,fake_tick,&ticks,1000000));
 b24_gpu_profile_begin(&p);
 for(unsigned i=0;i<B24P_COUNT;i++)b24_gpu_profile_phase(&p,(B24CpuGpuPhase)i);
 assert(p.frames==1 && !p.actual_gpu_timing_available);
 for(unsigned i=0;i<B24P_COUNT;i++)assert(p.last_ms[i]==1.0);
 Im2FrameTrace t={0};
 assert(!im2_frame_trace_open(&t,"/this/im2/path/does/not/exist"));
 assert(im2_frame_trace_open(&t,argv[1]));
 Im2FrameSample s={0};s.raw_dt_ms=120;s.simulation_dt_ms=90;s.controls_dt_ms=50;
 s.animation_blend_dt_ms=120;s.cpu_frame_wall_ms=6.0;
 for(unsigned i=0;i<B24P_COUNT;i++)s.phase_ms[i]=p.last_ms[i];
 im2_frame_trace_clocks(&s);assert(s.cpu_mhz==-1&&s.gpu_mhz==-1);
 s.world_z=-4.0f;s.gpu_z=-4.0f;
 s.raw_dt_ms=NAN;assert(!im2_frame_trace_write(&t,&s));assert(t.rows==0);
 s.raw_dt_ms=120;
 for(unsigned i=0;i<500000;i++){s.frame=i;assert(im2_frame_trace_write(&t,&s));}
 assert(t.rows==4096);
 im2_frame_trace_close(&t);
 FILE *f=fopen(argv[1],"r");assert(f);char line[2048];
 assert(fgets(line,sizeof(line),f));assert(strstr(line,"animation_blend_dt_ms"));
 unsigned count=0;
 while(fgets(line,sizeof(line),f)){
  unsigned commas=0;for(const char *q=line;*q;q++)commas+=*q==',';
  assert(commas==25);assert(strstr(line,"120.000000,90.000000,50.000000,120.000000"));
  count++;
 }
 fclose(f);assert(count==4096);
 assert(!im2_frame_trace_write(&t,&s));
 puts("PASS bounded CSV: actual phase clock, distinct dt inputs, unknown GPU busy, cadence and cap");
 return 0;
}
