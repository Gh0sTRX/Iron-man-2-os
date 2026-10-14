#ifndef B24_GPU_OWNER_H
#define B24_GPU_OWNER_H
#include "b24_gpu_camera.h"
#include "b24_c1_gpu_mesh.h"
#include "b24_c1_gpu_uv.h"
/* One graphical owner: SDL Renderer and vitaGL GPU presenter cannot coexist.
 * This is B24 engine source, not a standalone game/demo. Real gameplay path
 * must transfer 5 original IM2T/IM2V armors and HUD into this owner.
 */
typedef int (*B24GpuDrawCallback)(void *userdata);
typedef struct {
 int initialized,frame_open,pass;
 unsigned frames_presented,scene_draws,armor_draws,hud_draws;
} B24GpuOwner;
int b24_gpu_owner_init(B24GpuOwner *owner,int sdl_renderer_exists);
int b24_gpu_owner_begin(B24GpuOwner *owner,const B24GpuCameraMatrices *cam);
int b24_gpu_owner_scene(B24GpuOwner *owner,const B24GpuC1Mesh *scene);
int b24_gpu_owner_scene_material(B24GpuOwner *owner,const B24GpuC1Mesh *scene,
  const B24C1UV *original_uv,uint32_t verified_vehicle_atlas);
int b24_gpu_owner_armor(B24GpuOwner *owner,B24GpuDrawCallback draw,void *user);
int b24_gpu_owner_hud(B24GpuOwner *owner,B24GpuDrawCallback draw,void *user);
int b24_gpu_owner_present(B24GpuOwner *owner);
#endif
