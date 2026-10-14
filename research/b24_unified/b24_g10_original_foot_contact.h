#ifndef B24_G10_ORIGINAL_FOOT_CONTACT_H
#define B24_G10_ORIGINAL_FOOT_CONTACT_H
#include "b24_c1_gpu_mesh.h"
#include "renderer.h"
/* G10 VISUAL-only recovery from real 2010 C1L1 source ground mesh:
   projects bottom of authentic animated armor to original ground triangles.
   Does not replace B14 CPU gravity or fake a floor when no triangle exists.
   Authoritative B14 position and existing original C1WC XY walls unchanged.
   Returns 1 when a REAL supporting ground face was found. */
int b24_g10_foot_visual_source_offset(const B24GpuC1Mesh *city,
                                       const IM2Model *m,const IM2Camera *cam,
                                       float *z_offset);
#endif
