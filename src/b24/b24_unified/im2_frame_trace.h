#ifndef IM2_FRAME_TRACE_H
#define IM2_FRAME_TRACE_H
#include "b24_gpu_cpu_profile.h"
#include <stdio.h>
typedef struct {
 unsigned long long frame;
 unsigned millis;
 double raw_dt_ms,simulation_dt_ms,controls_dt_ms,animation_blend_dt_ms,cpu_frame_wall_ms;
 double phase_ms[B24P_COUNT];
 float world_x,world_y,world_z,gpu_x,gpu_y,gpu_z;
 int paused,cpu_mhz,gpu_mhz,bus_mhz,xbar_mhz;
} Im2FrameSample;
typedef struct {FILE *file;unsigned rows;int failed;} Im2FrameTrace;
int im2_frame_trace_open(Im2FrameTrace *trace,const char *path);
int im2_frame_trace_write(Im2FrameTrace *trace,const Im2FrameSample *sample);
void im2_frame_trace_clocks(Im2FrameSample *sample);
void im2_frame_trace_close(Im2FrameTrace *trace);
#endif
