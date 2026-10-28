#ifndef IM2_GAME_CAMERA_H
#define IM2_GAME_CAMERA_H
#include "renderer.h"
#include "b24_unified.h"
#include "b24_gpu_camera.h"
/* Shared current frame camera for visible world, test combat and HUD. */
int im2_game_camera(const IM2Camera *camera,const B24Unified *game,
                    B24GpuCamera *out,B24GpuCameraMatrices *matrices);
#endif
