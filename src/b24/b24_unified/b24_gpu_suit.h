#ifndef B24_GPU_SUIT_H
#define B24_GPU_SUIT_H
#include <stdint.h>
/* Layout EXACTLY matches original renderer.h IM2Vertex and IM2Triangle.
   No separate animation simulation: read B14/B16-mutated model vertices
   AFTER authentic .im2v update, and draw current frame on GPU. */
typedef struct {float x,y,z,u,v;} B24GpuSuitVertex;
typedef struct {uint16_t i0,i1,i2;} B24GpuSuitTriangle;
typedef struct {
 const B24GpuSuitVertex *vertices;
 const B24GpuSuitTriangle *triangles;
 const unsigned char *texture_rgba;
 uint32_t nv,nt,tw,th;
 float center_z;
 float native_bind_min_z; /* source original suit unanimated bind minimum from im2_load */
} B24GpuSuitSource;
typedef struct {float x,y,z,heading,pitch,roll;} B24GpuSuitPose;
typedef struct {
 unsigned texture_id;
 uint32_t nv,nt,tw,th;
 int prepared;
 float *light_normals;
 unsigned char *light_rgba;
 uint32_t light_capacity; /* optional persistent experimental shading scratch */
} B24GpuSuit;
int b24_gpu_suit_validate(const B24GpuSuitSource *src);
int b24_gpu_suit_matrix(float out16[16],
    const B24GpuSuitPose *pose,float center_z);
int b24_gpu_suit_prepare(B24GpuSuit *s,const B24GpuSuitSource *src);
int b24_gpu_suit_draw(const B24GpuSuit *s,const B24GpuSuitSource *src,
                      const B24GpuSuitPose *pose);
void b24_gpu_suit_release(B24GpuSuit *s);
#endif
