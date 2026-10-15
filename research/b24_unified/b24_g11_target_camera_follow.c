#include "b24_g11_target_camera_follow.h"
#include <math.h>
static float cl(float f,float mn,float mx){return f<mn?mn:f>mx?mx:f;}
int b24_g11_target_camera_follow(const B24G11CameraFocusInput *i,
                                  B24G11CameraFocus *o){
 if(!i||!o||!isfinite(i->orbit)||!isfinite(i->dt)||
    !isfinite(i->player_x)||!isfinite(i->player_y)||
    !isfinite(i->actor_x)||!isfinite(i->actor_y)||i->dt<0||
    i->dt>.2f)return 0;
 B24G11CameraFocus result={0};
 result.orbit=i->orbit;
 const float dx=i->actor_x-i->player_x;
 const float dy=i->actor_y-i->player_y;
 const float length=hypotf(dx,dy);
 const int close_enough=length>.2f&&length<30.f;
 const int active=!i->world_flying&&close_enough&&
    (i->lock_held||(i->melee_active&&length<9.f));
 result.focusing=active;
 result.zoom_reduction=active?.36f:0.f;
 /* Manual camera stick input takes priority over soft tracking. */
 if(active&&!i->manual_camera_input){
  const float target=atan2f(dx,dy);
  float delta=atan2f(sinf(target-i->orbit),cosf(target-i->orbit));
  result.orbit+=cl(delta,-i->dt*3.6f,i->dt*3.6f);
 }
 *o=result;
 return 1;
}
