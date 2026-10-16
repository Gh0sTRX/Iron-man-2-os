#ifndef B24_GPU_RUNTIME_H
#define B24_GPU_RUNTIME_H
#include "b24_gpu_owner.h"
#ifdef B24_G68_CITY_BACKEND
#include "b24_gpu_g68_city.h"
#ifdef B24_G73_REAL_SKY
#include "b24_gpu_g73_sky.h"
#endif
#endif
#include "b24_gpu_c1_vehicle_texture.h"
#include "b24_gpu_cpu_profile.h"
#include "b24_c1_material_source.h"
#include "b24_gpu_hud_bridge.h"
#include "b24_gpu_hud_native.h"
#include "b24_gpu_suit.h"
#include "b24_gpu_suit_im2_adapter.h"
#include "renderer.h"
typedef struct {
 B24GpuOwner owner;
 B24CpuGpuProfile profile; /* CPU thread wall only; not GPU busy */
 B24GpuC1Mesh city; /* old G9 source C1 mesh, untouched in legacy mode */
#ifdef B24_G68_CITY_BACKEND
 B24G68City g68_city; /* authoritative photographed 2010 source G68 scene */
#ifdef B24_G73_REAL_SKY
 B24G73Sky original_sky;
#endif
#endif
 B24C1UV city_uv;
 B24C1MaterialSource city_material; /* original material LABELS, NOT atlases */
 uint32_t verified_vehicle_atlas; /* 0 until B12 original atlas loaded, never guessed */
 B24GpuSuit suit;
 B24GpuIM2Stream stream;
 B24GpuHudBridge hud;
 B24NativeHudGeometry native_hud; /* GPU-only shape command buffer */
 B24GpuSuitPose frame_pose;
 B24Unified *frame_game;
 uint32_t suit_rebinds,frames;
 int loaded_suit_index;
 int initialized;
} B24GpuRuntime;
/* GPU owns ONLY renderer; SDL gamepad/timer input can remain active. */
int b24_gpu_runtime_set_clock(B24GpuRuntime *r,B24GpuTicksFn fn,
                               void *ctx,double frequency_hz);
int b24_gpu_runtime_open(B24GpuRuntime *r,const char *city_file);
int b24_gpu_runtime_sync_model(B24GpuRuntime *r,const IM2Model *model,int suit_index);
int b24_gpu_runtime_draw(B24GpuRuntime *r,const IM2Model *model,
                  const IM2Camera *camera,B24Unified *game,int suit_index);
void b24_gpu_runtime_close(B24GpuRuntime *r);
#endif
