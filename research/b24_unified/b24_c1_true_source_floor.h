#ifndef B24_C1_TRUE_SOURCE_FLOOR_H
#define B24_C1_TRUE_SOURCE_FLOOR_H
#include "b24_c1_gpu_mesh.h"
/* Original B11 -> C1G2 category-0 actual polygon floor surface, NOT C1WC wall.
   Does not invent a plane or move the player; a candidate must intersect an
   existing original 2010 GLB triangle in X/Y.  No renderer GPU readback.
   Return 1 only when original source triangle supports point; return 0 when
   no ground there. */
int b24_c1_true_floor_at(const B24GpuC1Mesh *city,
                         float x,float y,float reference_z,
                         float vertical_range,float *floor_z);
#endif
