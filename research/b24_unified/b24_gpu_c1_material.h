#ifndef B24_GPU_C1_MATERIAL_H
#define B24_GPU_C1_MATERIAL_H
#include "b24_c1_gpu_mesh.h"
#include "b24_c1_gpu_uv.h"
#include <stdint.h>
/* Render four original C1L1 categories. Only the 22 car meshes have a
 * separately B12-validated atlas association. All other original
 * material->diffuse and lightmap bindings remain unresolved.
 *
 * vehicle_atlas=0 => no made-up texture, color-only 2010 mesh fallback.
 * vertex streams are NOT CPU rasterized into a full-screen image.
 */
int b24_gpu_c1_draw_material(const B24GpuC1Mesh *scene,
                             const B24C1UV *original_uv,
                             uint32_t vehicle_atlas);
#endif
