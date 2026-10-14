#include "b24_wm_original_marker_g8_world.h"
#include <math.h>

static int finite3(const float p[3]){
 return p&&isfinite(p[0])&&isfinite(p[1])&&isfinite(p[2]);
}
static int actor_valid(const B24WMG8ActorPose *a){
 return a&&isfinite(a->player_x)&&isfinite(a->player_y)&&
   isfinite(a->player_z)&&isfinite(a->player_heading)&&
   isfinite(a->model_center_z)&&isfinite(a->hover_bob);
}
int b24_wm_g8_marker_world_point(const B24WMG8ActorPose *a,
                                const float p[3],float out[3]){
 if(!actor_valid(a)||!finite3(p)||!out)return 0;
 const float hx=cosf(a->player_heading),hy=sinf(a->player_heading);
 /* Exact current G8 renderer.c:420–428 body / camera transformation.
    World is Z-UP; this is NOT GXM texture coordinate space. */
 const float x=a->player_x-p[0]*hx-p[1]*hy;
 const float y=a->player_y+p[0]*hy-p[1]*hx;
 const float z=p[2]-a->model_center_z+a->player_z+a->hover_bob;
 if(!isfinite(x)||!isfinite(y)||!isfinite(z))return 0;
 out[0]=x;out[1]=y;out[2]=z;
 return 1;
}
int b24_wm_g8_marker_world_direction(const B24WMG8ActorPose *a,
                                    const float direction[3],float out[3]){
 if(!actor_valid(a)||!finite3(direction)||!out)return 0;
 const float hx=cosf(a->player_heading),hy=sinf(a->player_heading);
 float x=-direction[0]*hx-direction[1]*hy;
 float y=direction[0]*hy-direction[1]*hx;
 float z=direction[2];
 float sq=x*x+y*y+z*z;
 if(!isfinite(sq)||sq<1e-12f)return 0;
 const float inv=1.f/sqrtf(sq);
 x*=inv;y*=inv;z*=inv;
 if(!isfinite(x)||!isfinite(y)||!isfinite(z))return 0;
 out[0]=x;out[1]=y;out[2]=z;
 return 1;
}
int b24_wm_g8_source_gun03_marker_world(const B24WMG8ActorPose *a,
                                       const float source[6][16],
                                       float tip[3],float axis[3]){
 if(!a||!source||!tip||!axis)return 0;
 float source_tip[3],source_axis[3],world_tip[3],world_axis[3];
 if(!b24_wm_gun_original_marker_axis(source,source_tip,source_axis)||
    !b24_wm_g8_marker_world_point(a,source_tip,world_tip)||
    !b24_wm_g8_marker_world_direction(a,source_axis,world_axis))return 0;
 for(int k=0;k<3;k++){tip[k]=world_tip[k];axis[k]=world_axis[k];}
 return 1;
}
