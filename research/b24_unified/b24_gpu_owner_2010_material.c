#include "b24_gpu_owner.h"
#include "b24_gpu_c1_2010_textured_material.h"
/* One ONLY GPU owner, no secondary SDL/vitaGL presenter or additional
   CPU simulation. This replaces the G10 diagnostic category scene draw
   only when real C1G2+C1UV+C1MA+C1MT PVR source data are loaded. */
int b24_gpu_owner_scene_original_2010(B24GpuOwner *o,
 const B24GpuC1Mesh *mesh,const B24C1UV *uv,
 const B24C1MaterialBatchPlan *plan,const B24C1OriginalDiffuseBank *bank){
 if(!o||!o->frame_open||o->pass!=0||
    !b24_gpu_c1_draw_original_2010_world(mesh,uv,plan,bank))return 0;
 o->pass=1;o->scene_draws++;
 return 1;
}
