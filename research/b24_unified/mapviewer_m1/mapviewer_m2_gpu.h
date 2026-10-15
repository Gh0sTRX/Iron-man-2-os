/* C1L1 M2 GPU-RESIDENT map. ONE upload of immutable authored 2010 source buffers.
   May reduce CPU->GPU client-array remarshal; NOT guaranteed fast until real Vita profiling.
   Never applies guessed original CLARA world transforms. Diagnostic group filtering. */
#ifndef IM2_M2_STATIC_GPU_H
#define IM2_M2_STATIC_GPU_H
#include "b24_c1_gpu_mesh.h"
#include "b24_c1_gpu_uv.h"
#include "b24_c1_material_batches.h"
#include "b24_c1_2010_diffuse_bank.h"
typedef struct {
 unsigned vbo, uvbo, ebo_original, ebo_material;
 int ready, upload_failed;
 unsigned submitted_draws, submitted_triangles, submitted_original_atlas_draws;
} M2Gpu;
int m2_gpu_load(M2Gpu *gpu,const B24GpuC1Mesh *mesh,
                const B24C1UV *uv,const B24C1MaterialBatchPlan *batches);
void m2_gpu_release(M2Gpu *gpu);
int m2_gpu_draw(M2Gpu *gpu,const B24GpuC1Mesh *mesh,
               const B24C1MaterialBatchPlan *batches,
               const B24C1OriginalDiffuseBank *bank,
               int original_textures,int group_filter);
#endif
