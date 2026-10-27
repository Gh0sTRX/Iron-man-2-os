#ifndef B24_GPU_SUIT_IM2_ADAPTER_H
#define B24_GPU_SUIT_IM2_ADAPTER_H
#include "b24_gpu_suit.h"
/* This adapter uses authentic reconstructed renderer.h IM2Model at compile
 * time, but copied GPU staging geometry is strictly aliasing safe. */
#include "renderer.h"
typedef struct {
 B24GpuSuitVertex *dynamic_vertices;
 B24GpuSuitTriangle *static_triangles;
 B24GpuSuitSource source;
 const unsigned char *atlas_source;
} B24GpuIM2Stream;
int b24_gpu_im2_stream_init(B24GpuIM2Stream *s,const IM2Model *original);
int b24_gpu_im2_stream_update(B24GpuIM2Stream *s,const IM2Model *animated);
void b24_gpu_im2_stream_free(B24GpuIM2Stream *s);
#endif
