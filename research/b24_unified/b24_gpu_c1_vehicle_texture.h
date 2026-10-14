#ifndef B24_GPU_C1_VEHICLE_TEXTURE_H
#define B24_GPU_C1_VEHICLE_TEXTURE_H
#include <stdint.h>
/* C1TX: original user-owned B12 512x512 RGBA C1L1_Vehicles atlas.
 * NOT a full-city texture solution; source PVRTC decoder is experimental.
 * Texture is uploaded once when available, never once per gameplay frame. */
int b24_gpu_c1_vehicle_atlas_open(uint32_t *texture_id,const char *path);
void b24_gpu_c1_vehicle_atlas_close(uint32_t *texture_id);
#endif
