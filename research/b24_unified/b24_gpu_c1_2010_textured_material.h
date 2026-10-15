#ifndef B24_GPU_C1_2010_TEXTURED_MATERIAL_H
#define B24_GPU_C1_2010_TEXTURED_MATERIAL_H
#include "b24_c1_gpu_mesh.h"
#include "b24_c1_gpu_uv.h"
#include "b24_c1_material_batches.h"
#include "b24_c1_2010_diffuse_bank.h"
/* Draw ORIGINAL 2010 source 22919 triangles ONCE in same VitaGL frame.
   Per-BRES material bucket (group,material-ID) selects authentic shader
   property source atlas, not name/ordinal texture guesses.
   Ground, buildings, cars have 100% source UV candidate coverage.
   Lights stay color-only until per-mesh 2284 UV-less triangles segregated.
   An unavailable source C1TX texture remains original colored geometry. */
int b24_gpu_c1_draw_original_2010_world(const B24GpuC1Mesh *scene,
 const B24C1UV *uv,const B24C1MaterialBatchPlan *batches,
 const B24C1OriginalDiffuseBank *bank);
#endif
