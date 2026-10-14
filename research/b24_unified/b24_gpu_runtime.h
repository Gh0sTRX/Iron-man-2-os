#ifndef B24_GPU_RUNTIME_H
#define B24_GPU_RUNTIME_H
#include "b24_gpu_owner.h"
#include "b24_gpu_c1_vehicle_texture.h"
#include "b24_gpu_cpu_profile.h"
#include "b24_gpu_hud_bridge.h"
#include "b24_gpu_hud_native.h"
#include "b24_gpu_suit.h"
#include "b24_gpu_suit_im2_adapter.h"
#include "renderer.h"
typedef struct {
 B24GpuOwner owner;
 B24CpuGpuProfile profile; /* CPU thread wall only; not GPU busy */
 B24GpuC1Mesh city;
 B24C1UV city_uv;
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
