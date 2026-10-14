#include "b24_g10_original_foot_contact.h"
#include "b24_c1_true_source_floor.h"
#include <math.h>
int b24_g10_foot_visual_source_offset(const B24GpuC1Mesh *city,
                                       const IM2Model *m,const IM2Camera *cam,
                                       float *offset){
 if(!city||!m||!cam||!offset||!m->vertices||m->nv<3||m->nv>16000||
    !isfinite(m->center_z)||!isfinite(cam->player_x)||
    !isfinite(cam->player_y)||!isfinite(cam->player_z)||
    cam->flying)return 0;
 float bottom=INFINITY;
 for(size_t i=0;i<m->nv;i++){
  float v=m->vertices[i].z;
  if(!isfinite(v))return 0;
  if(v<bottom)bottom=v;
 }
 /* Original GPU armor translation = player_z-center_z.
    Exact lowest source geometry in this frame lies HERE in world-space. */
 const float sole_world_z=cam->player_z-m->center_z+bottom;
 float surface=0.f;
 if(!b24_c1_true_floor_at(city,cam->player_x,cam->player_y,
                          sole_world_z,4.f,&surface))return 0;
 /* User G9 photos show legs under flat ground because target_z=0.
    Snap visuals ONLY to a REAL original ground triangle's Z. This must
    not force fly/hovers and does not add invisible collision surfaces. */
 const float shift=surface+.025f-sole_world_z;
 if(!isfinite(shift)||fabsf(shift)>2.5f)return 0;
 *offset=shift;
 return 1;
}
