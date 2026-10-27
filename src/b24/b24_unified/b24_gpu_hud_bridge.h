#ifndef B24_GPU_HUD_BRIDGE_H
#define B24_GPU_HUD_BRIDGE_H
#include <stdint.h>
#include "b24_unified.h"
/* Intermediate HUD: GPU-owned SCREEN, only low-cost 2D overlay is rasterized
   in RAM until native GL vector text is implemented. This is NOT CPU scene
   raster/SDL_UpdateTexture and it never owns/presents a second framebuffer. */
typedef struct {
 uint32_t texture;
 uint32_t *rgb_canvas; /* 480x272 packed RGB, original B22/B23 UI */
 unsigned char *rgba_canvas;
 unsigned frames,texture_uploads;
 int prepared;
} B24GpuHudBridge;
int b24_gpu_hud_bridge_prepare(B24GpuHudBridge *h);
int b24_gpu_hud_bridge_draw(B24GpuHudBridge *h,B24Unified *game);
void b24_gpu_hud_bridge_release(B24GpuHudBridge *h);
#endif
