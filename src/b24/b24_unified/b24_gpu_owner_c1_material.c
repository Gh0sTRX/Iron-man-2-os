#include "b24_gpu_owner.h"
#include "b24_gpu_c1_material.h"
/* Same GPU context and single-frame pass order as legacy GPU owner.
 * Only original B12-verified vehicle atlas can be enabled. No atlas means
 * source-authentic geometry with explicit diagnostic per-category color. */
int b24_gpu_owner_scene_material(B24GpuOwner *o,const B24GpuC1Mesh *scene,
                                 const B24C1UV *original_uv,
                                 uint32_t vehicle_atlas){
 if(!o||!o->frame_open||o->pass!=0||!scene)return 0;
 if(!b24_gpu_c1_draw_material(scene,original_uv,vehicle_atlas))return 0;
 o->pass=1;o->scene_draws++;
 return 1;
}
