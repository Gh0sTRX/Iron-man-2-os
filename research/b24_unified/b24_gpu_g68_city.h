#ifndef B24_G70_G68_CITY_H
#define B24_G70_G68_CITY_H
#include <stdint.h>
#include "b24_gpu_owner.h"
/* G70 scene backend ONLY. G9/B17/B24 owns input, five suits, original
 * animations, HUD, mission and CPU movement. G68 supplies source world GPU
 * geometry and original PVR atlas data. Never create another VGL context. */
#define B24_G68_BATCH_MAX 80u
#define B24_G68_TEX_MAX 48u
typedef struct {
 uint32_t first,count,tex,flags;
} B24G68Batch;
typedef struct {
 B24G68Batch batches[B24_G68_BATCH_MAX];
 uint32_t texture_ids[B24_G68_TEX_MAX];
 uint32_t vbo,vertices,batch_count,texture_count,ready;
} B24G68City;
int b24_g68_city_open(B24G68City *city,
 const char *mesh_path,const char *texture_prefix);
int b24_g68_city_draw(const B24G68City *city);
int b24_gpu_owner_scene_g68(B24GpuOwner *owner,const B24G68City *city);
void b24_g68_city_close(B24G68City *city);
#endif
