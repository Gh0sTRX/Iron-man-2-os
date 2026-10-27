#ifndef B24_C1_MATERIAL_BATCHES_H
#define B24_C1_MATERIAL_BATCHES_H
#include "b24_c1_gpu_mesh.h"
#include "b24_c1_material_source.h"
#include <stdint.h>

/* CPU-once material bucket preparation for the SAME B24 original Z-up city.
   Reorders only triangle INDEX REFERENCES. Vertices, original face winding,
   file-qualified material identity and every original triangle are preserved.
   This is an authenticated material draw schedule, NOT a diffuse atlas link.
   No GPU context, VPK, or texture guesses. */
#define B24_C1_MAX_MATERIAL_BUCKETS (B24_GPU_C1_BATCHES*B24_C1_MAT_NLABEL)
typedef struct {
 uint32_t group,material_id,first_index,index_count;
} B24C1MaterialBucket;
typedef struct {
 uint16_t *indices;
 B24C1MaterialBucket buckets[B24_C1_MAX_MATERIAL_BUCKETS];
 uint32_t nbuckets,index_count;
 int ready;
} B24C1MaterialBatchPlan;
int b24_c1_material_batches_build(B24C1MaterialBatchPlan *dst,
                                  const B24GpuC1Mesh *scene,
                                  const B24C1MaterialSource *src);
void b24_c1_material_batches_free(B24C1MaterialBatchPlan *dst);
#endif
