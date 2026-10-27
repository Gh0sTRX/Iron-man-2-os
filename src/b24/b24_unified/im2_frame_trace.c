#include "im2_frame_trace.h"
#include <math.h>
#include <string.h>
#ifdef __vita__
#include <psp2/power.h>
#endif
/* CPU wall/submission timings, never GPU busy or a hardware FPS claim.
 * Bounded 4096 rows, first three frames then every 60th rendered frame.
 * Diagnostic failure must never stop gameplay. Buffered writes, periodic flush. */
int im2_frame_trace_open(Im2FrameTrace *t,const char *path){
 if(!t||!path||!*path||t->file)return 0;
 memset(t,0,sizeof(*t));t->file=fopen(path,"w");
 if(!t->file){t->failed=1;return 0;}
 if(fputs("schema,frame,ms,raw_dt_ms,simulation_dt_ms,controls_dt_ms,animation_blend_dt_ms,"
          "cpu_frame_wall_ms,stream_ms,camera_ms,scene_submit_ms,suit_submit_ms,"
          "hud_submit_ms,swap_wall_ms,world_x,world_y,world_z,gpu_x,gpu_y,gpu_z,"
          "paused,cpu_mhz,gpu_mhz,bus_mhz,xbar_mhz,gpu_busy_available\n",t->file)<0){
  t->failed=1;im2_frame_trace_close(t);return 0;
 }
 return 1;
}
void im2_frame_trace_close(Im2FrameTrace *t){
 if(t&&t->file){if(fclose(t->file))t->failed=1;t->file=NULL;}
}
int im2_frame_trace_write(Im2FrameTrace *t,const Im2FrameSample *s){
 if(!t||!t->file||!s)return 0;
 if(t->rows>=4096 || (s->frame>=3 && s->frame%60!=0))return 1;
 const double values[]={s->raw_dt_ms,s->simulation_dt_ms,s->controls_dt_ms,
  s->animation_blend_dt_ms,s->cpu_frame_wall_ms,s->world_x,s->world_y,s->world_z,
  s->gpu_x,s->gpu_y,s->gpu_z};
 for(unsigned i=0;i<sizeof(values)/sizeof(values[0]);i++)if(!isfinite(values[i]))return 0;
 for(unsigned i=0;i<B24P_COUNT;i++)if(!isfinite(s->phase_ms[i])||s->phase_ms[i]<0)return 0;
 if(s->raw_dt_ms<0||s->simulation_dt_ms<0||s->controls_dt_ms<0||
    s->animation_blend_dt_ms<0||s->cpu_frame_wall_ms<0)return 0;
 int ok=fprintf(t->file,"1,%llu,%u,%.6f,%.6f,%.6f,%.6f,%.6f,"
  "%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,"
  "%d,%d,%d,%d,%d,0\n",s->frame,s->millis,s->raw_dt_ms,s->simulation_dt_ms,
  s->controls_dt_ms,s->animation_blend_dt_ms,s->cpu_frame_wall_ms,
  s->phase_ms[0],s->phase_ms[1],s->phase_ms[2],s->phase_ms[3],s->phase_ms[4],s->phase_ms[5],
  (double)s->world_x,(double)s->world_y,(double)s->world_z,
  (double)s->gpu_x,(double)s->gpu_y,(double)s->gpu_z,
  s->paused,s->cpu_mhz,s->gpu_mhz,s->bus_mhz,s->xbar_mhz)>=0;
 t->rows++;
 if(ok&&(t->rows<=3 || t->rows%32==0))ok=fflush(t->file)==0;
 if(!ok){t->failed=1;im2_frame_trace_close(t);}
 return ok;
}
void im2_frame_trace_clocks(Im2FrameSample *s){
 if(!s)return;
#ifdef __vita__
 s->cpu_mhz=scePowerGetArmClockFrequency();
 s->gpu_mhz=scePowerGetGpuClockFrequency();
 s->bus_mhz=scePowerGetBusClockFrequency();
 s->xbar_mhz=scePowerGetGpuXbarClockFrequency();
#else
 s->cpu_mhz=s->gpu_mhz=s->bus_mhz=s->xbar_mhz=-1;
#endif
}
