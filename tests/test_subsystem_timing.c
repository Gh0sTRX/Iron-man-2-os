#include "b24_unified.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(void){
 B24Unified g;B24Observation obs={0};b24_unified_init(&g);
 obs.dt=.12f;b24_unified_tick(&g,&obs);
 assert(fabsf(g.observed_dt-.05f)<.000001f);
 obs.dt=.033f;b24_unified_tick(&g,&obs);
 assert(fabsf(g.observed_dt-.033f)<.000001f);
 obs.buttons=IM2_BT_START;b24_unified_tick(&g,&obs);
 assert(b24_unified_paused(&g)&&g.observed_dt==0.f);
 obs.buttons=0;b24_unified_tick(&g,&obs);
 assert(g.observed_dt==0.f);
 obs.buttons=IM2_BT_START;b24_unified_tick(&g,&obs);
 assert(!b24_unified_paused(&g)&&fabsf(g.observed_dt-.033f)<.000001f);
 puts("PASS actual unified dt observation: cap and pause/resume, no clock policy change");
 return 0;
}
