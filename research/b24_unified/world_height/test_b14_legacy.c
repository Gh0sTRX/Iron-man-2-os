/* The standalone no-G75 B14 playground must retain its explicit Z=0 floor. */
#include "b14_world.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(void){
 B14World w;b14_world_init(&w);
 for(unsigned i=0;i<120;i++)b14_world_tick(&w,1.f/60.f,0,0,0,0,0);
 assert(w.z==0.f && w.target_z==0.f);
 b14_world_toggle_flight(&w);
 assert(w.flying && fabsf(w.target_z-.8f)<.0001f);
 for(unsigned i=0;i<120;i++)b14_world_tick(&w,1.f/60.f,0,0,0,0,0);
 assert(fabsf(w.z-.8f)<.0001f);
 b14_world_toggle_flight(&w);
 assert(!w.flying && w.target_z==0.f);
 for(unsigned i=0;i<120;i++)b14_world_tick(&w,1.f/60.f,0,0,0,0,0);
 assert(w.z==0.f);
 puts("PASS no-G75 standalone B14 retains explicit playground zero floor");
 return 0;
}
