#include "b24_camera_recenter.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
int main(void){
 B24CameraRecenter c={0};
 float o=1.5f;
 for(int i=0;i<30;i++)o=b24_camera_recenter(&c,2,1.f/60.f,0,0,o,0.f);
 assert(fabsf(o-1.5f)<1e-5f);
 for(int i=0;i<90;i++)o=b24_camera_recenter(&c,2,1.f/60.f,0,0,o,0.f);
 assert(fabsf(o)<.3f);
 o=1.8f;
 for(int i=0;i<60;i++)o=b24_camera_recenter(&c,2,1.f/60.f,.5f,0,o,0.f);
 assert(fabsf(o-1.8f)<1e-5f&&c.idle_seconds==0.f);
 for(int i=0;i<90;i++)o=b24_camera_recenter(&c,3,1.f/60.f,0,0,o,0.f);
 assert(fabsf(o)<.3f);
 o=-2.5f;
 for(int i=0;i<300;i++)o=b24_camera_recenter(&c,1,1.f/60.f,0,0,o,0.f);
 assert(fabsf(o+2.5f)<1e-5f);
 /* Wrap safe near +pi/-pi; no long revolution. */
 c.idle_seconds=2.f;o=3.11f;
 float next=b24_camera_recenter(&c,2,.016f,0,0,o,-3.11f);
 assert(fabsf(next-o)<.04f);
 uint32_t seed=0x24c1ba1u;
 for(int i=0;i<20000;i++){
  seed=seed*1664525u+1013904223u;
  float rx=(int)(seed%300u)/100.f-1.5f;
  float dt=(seed&1u)?1.f/60.f:.12f;
  int stage=(int)((seed>>16)&3u);
  o=b24_camera_recenter(&c,stage,dt,rx,0,o,2.5f);
  assert(isfinite(o));
 }
 puts("PASS B24 auto-recenter: full manual look, 0.65s delay, Stage2/RUSH only, wrapped yaw and 20k inputs");
}
