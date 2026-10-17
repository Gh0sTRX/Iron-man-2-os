#include "b24_g163_aim_facing.h"
#include <math.h>
float b24_g163_aim_heading(float heading,float orbit,float dt,
                          int aim_pressed,int ground_or_hover){
 if(!isfinite(heading)||!isfinite(orbit)||!isfinite(dt))
  return heading;
 if(!aim_pressed||!ground_or_hover)return heading;
 if(dt<0.f)return heading;
 if(dt>.05f)dt=.05f;
 /* B14 source has heading=atan2(vx,vy) in orbit-relative movement.
  * During iOS-style over-shoulder aiming the camera reticle remains
  * straight ahead and locomotion becomes backwards/left/right strafe;
  * never rotate the actor toward its movement vector in this state.
  * Wrap shortest route around ±PI, preserving world axes and roll. */
 const float diff=atan2f(sinf(orbit-heading),cosf(orbit-heading));
 const float blend=1.f-expf(-22.f*dt);
 return heading+diff*blend;
}
