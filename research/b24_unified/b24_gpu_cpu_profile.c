#include "b24_gpu_cpu_profile.h"
#include <math.h>
#include <stddef.h>
#include <string.h>
int b24_gpu_profile_set_clock(B24CpuGpuProfile *p,B24GpuTicksFn cb,
                                void *userdata,double hz){
 if(!p||!cb||!isfinite(hz)||hz<100.f||hz>1.e15)return 0;
 memset(p,0,sizeof(*p));
 p->ticks=cb;p->userdata=userdata;
 p->frequency_hz=hz;p->enabled=1;
 p->actual_gpu_timing_available=0;
 return 1;
}
void b24_gpu_profile_begin(B24CpuGpuProfile *p){
 if(!p||!p->enabled||!p->ticks)return;
 p->previous_tick=p->ticks(p->userdata);
 memset(p->last_ms,0,sizeof(p->last_ms));
 p->frame_open=1;p->next_phase=0;
}
void b24_gpu_profile_phase(B24CpuGpuProfile *p,B24CpuGpuPhase phase){
 if(!p||!p->enabled||!p->frame_open||
    phase<0||phase>=B24P_COUNT||phase!=p->next_phase)return;
 const uint64_t now=p->ticks(p->userdata);
 double delta=now>=p->previous_tick ?
   (double)(now-p->previous_tick)*1000.0/p->frequency_hz : 0.0;
 if(!isfinite(delta)||delta<0.0||delta>30000.0)delta=0.0;
 p->previous_tick=now;
 p->last_ms[(int)phase]=delta;
 p->max_ms[(int)phase]=fmax(p->max_ms[(int)phase],delta);
 if(p->frames==0)p->average_ms[(int)phase]=delta;
 else p->average_ms[(int)phase]=p->average_ms[(int)phase]*.92+delta*.08;
 p->next_phase++;
 if(p->next_phase==B24P_COUNT){
   p->frame_open=0;p->frames++;
 }
}
