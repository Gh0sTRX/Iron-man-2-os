#ifndef B24_G168_SOURCE_FOOT_ORIGIN_H
#define B24_G168_SOURCE_FOOT_ORIGIN_H
#include <stdint.h>
#include <stddef.h>
/* Z contract between actual Vita B14 model root and original G66C source
 * authored SUPPORT. b24_gpu_suit_matrix places original authored vertex:
 * world_v_z=world_actor_root_z - native IM2Model.center_z + native_v_z.
 * G75 grounded capsule requires FOOT Z, not MODEL-CENTER root Z.
 * Zero invented actor scale, native original IM2T rest bind min Z. */
typedef struct{
 float source_min_z,source_center_z;
 uint32_t source_vertex_count;
 int valid;
} B24G168FootOrigin;
int b24_g168_source_bind_origin(B24G168FootOrigin *a,const void *verts,
                  size_t stride,uint32_t nv,float model_center_z);
float b24_g168_actor_foot_z(const B24G168FootOrigin *a,float root_z);
float b24_g168_actor_root_z(const B24G168FootOrigin *a,float foot_z);
#endif
