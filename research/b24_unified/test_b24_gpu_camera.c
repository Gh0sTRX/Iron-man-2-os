#include "b24_gpu_camera.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
int main(void){
 B24GpuCamera c={{0,-12,6},{0,2,2},{0,0,1},72.f,960.f/544.f,.15f,2400.f};
 B24GpuCameraMatrices m={0};float x=0,y=0,z=0;
 assert(b24_gpu_camera_matrices(&c,&m));
 assert(b24_gpu_world_to_screen(&m,c.target,960,544,&x,&y,&z));
 assert(fabsf(x-480.f)<.01f&&fabsf(y-272.f)<.01f);
 assert(!b24_gpu_world_to_screen(&m,(B24GpuVec3){0,-30,6},960,544,&x,&y,&z));
 assert(b24_gpu_world_to_screen(&m,(B24GpuVec3){2,2,2},960,544,&x,&y,&z));
 assert(x>480.f);
 B24GpuCamera shoulder=c;
 assert(b24_gpu_camera_apply_shoulder(&shoulder,1.f,0.f,1.05f));
 assert(b24_gpu_camera_matrices(&shoulder,&m));
 assert(b24_gpu_world_to_screen(&m,c.target,960,544,&x,&y,&z));
 assert(x<430.f&&x>250.f); /* avatar left in hover */
 assert(b24_gpu_camera_matrices(&c,&m));
 assert(b24_gpu_world_to_screen(&m,c.target,960,544,&x,&y,&z));
 assert(fabsf(x-480.f)<.01f); /* avatar center in cruise */
 assert(!b24_gpu_camera_apply_shoulder(&shoulder,0.f,0.f,1.f));
 assert(b24_gpu_world_to_screen(&m,(B24GpuVec3){0,2,4},960,544,&x,&y,&z));
 assert(y<272.f);
 B24GpuCamera invalid=c;invalid.target=invalid.eye;
 assert(!b24_gpu_camera_matrices(&invalid,&m));
 invalid=c;invalid.world_up=(B24GpuVec3){0,0,0};
 assert(!b24_gpu_camera_matrices(&invalid,&m));
 uint32_t rng=0xB24C2026u;
 for(int i=0;i<20000;i++){
  rng=1664525u*rng+1013904223u;
  float angle=(float)(rng%6283u)*.001f;
  c.eye=(B24GpuVec3){sinf(angle)*10.f,cosf(angle)*10.f,2.f+(float)(rng%5u)};
  c.target=(B24GpuVec3){0,0,2};
  assert(b24_gpu_camera_matrices(&c,&m));
  assert(b24_gpu_world_to_screen(&m,c.target,960,544,&x,&y,&z));
  assert(fabsf(x-480.f)<.1f&&fabsf(y-272.f)<.1f);
 }
 puts("PASS B24 GPU camera: original Z-up, 960x544 center, axes & depth, 20k random views");
 return 0;
}
