#ifndef IM2_SUIT_LIGHTING_H
#define IM2_SUIT_LIGHTING_H
#include "b24_gpu_suit.h"
#include <stddef.h>
/* Experimental existing G75 light policy evaluated on current mesh geometry.
 * Derived normals are presentation data, NOT recovered native Gameloft shading.
 * root is the exact suit draw transform; neither source mesh nor atlas changes.
 * Caller supplies persistent bounded scratch (3*capacity floats,4*capacity bytes).
 */
int im2_suit_lighting_colors(const B24GpuSuitSource *src,const float root[16],
                            float *normals,unsigned char *rgba,size_t capacity);
#endif
