#include "im2_game_camera.h"
#include "b24_g164_camera_sky_framing.h"
#include <math.h>
int im2_game_camera(const IM2Camera *c,const B24Unified *g,B24GpuCamera *out,B24GpuCameraMatrices *matrices){
 if(!c||!g||!out||!matrices)return 0;
 float a=c->orbit, cp=cosf(c->pitch),sp=sinf(c->pitch);
 float fd=c->camera_distance;
#ifdef B24_G164_HERO_CAMERA_FRAMING
 /* ONLY perspective, G161 MarkV original sourced 2.2355 unit model and
  * original world collision G75/G66C coordinates remain BIT-IDENTICAL.
  * Stage2/RUSH centered chase uses previous 72deg/distance. Ground and
  * upright hover blend slightly closer when shoulder mode is active. */
 float g164_fov=72.f,g164_distance_multiplier=1.f;
 if(!b24_g164_camera_framing(
      1.f-g->camera_base.shoulder_to_chase,
      &g164_distance_multiplier,&g164_fov))return 0;
 fd*=g164_distance_multiplier;
#endif
 if(!isfinite(a)||!isfinite(cp)||!isfinite(sp)||
    !isfinite(fd)||fd<.1f)return 0;
 float fx=sinf(a),fy=cosf(a),rx=cosf(a),ry=-sinf(a);
 B24GpuCamera cam={
  {c->cam_x-fx*fd*cp,
   c->cam_y-fy*fd*cp,
   c->cam_z+fd*sp},
  {c->cam_x,c->cam_y,c->cam_z},
  {0,0,1},
#ifdef B24_G164_HERO_CAMERA_FRAMING
  g164_fov,960.f/544.f,.15f,2600.f
#else
  72.f,960.f/544.f,.15f,2600.f
#endif
 };
 /* Centered gun reticle but avatar left in GROUND/HOVER. B22 camera_base
    carries the already-smoothed transition toward centered CRUISE/RUSH. */
 float shoulder=1.f-g->camera_base.shoulder_to_chase;
 if(!isfinite(shoulder))return 0;
 if(shoulder<0.f)shoulder=0.f;
 if(shoulder>1.f)shoulder=1.f;
 if(!b24_gpu_camera_apply_shoulder(&cam,rx,ry,1.05f*shoulder))return 0;
 *out=cam;
 if(!b24_gpu_camera_matrices(&cam,matrices))return 0;
 return 1;
}
