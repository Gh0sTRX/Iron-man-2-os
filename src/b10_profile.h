#ifndef B10_PROFILE_H
#define B10_PROFILE_H
#include <math.h>
#include <stdint.h>
typedef struct {
 float motion_ms, cpu_ms, upload_ms, copy_ms, present_ms;
 uint32_t samples;
} B10Profiler;
static inline float b10_ema(float prev, float next, uint32_t samples) {
    if(!isfinite(next) || next < 0 || next > 2000.0f) return prev;
    return samples==0?next:prev*0.88f+next*0.12f;
}
static inline void b10_record(B10Profiler *p,float motion,float cpu,float upload,float copy,float present){
 uint32_t samples=p->samples;
 p->motion_ms=b10_ema(p->motion_ms,motion,samples);
 p->cpu_ms=b10_ema(p->cpu_ms,cpu,samples);
 p->upload_ms=b10_ema(p->upload_ms,upload,samples);
 p->copy_ms=b10_ema(p->copy_ms,copy,samples);
 p->present_ms=b10_ema(p->present_ms,present,samples);
 if(p->samples<1000000) p->samples++;
}
#endif
