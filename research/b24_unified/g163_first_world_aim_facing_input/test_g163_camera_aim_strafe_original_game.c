#include "b24_g163_aim_facing.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(void){
 /* B14 used to turn actor BACKWARDS when aiming+backpedal;
  * after a 60 Hz second actor should face reticle, not movement. */
 float h=3.14159265358979323846f;
 const float camera=0.f,dt=1.f/60.f;
 for(int n=0;n<60;n++)h=b24_g163_aim_heading(h,camera,dt,1,1);
 assert(fabsf(atan2f(sinf(h-camera),cosf(h-camera)))<.001f);
 /* Lower-level fixed camera remains fixed, the actor only rotates. */
 assert(b24_g163_aim_heading(1.f,2.f,dt,0,1)==1.f);
 assert(b24_g163_aim_heading(1.f,2.f,dt,1,0)==1.f);
 assert(b24_g163_aim_heading(1.f,2.f,dt,1,1)>1.f);
 /* Angle wrap should turn by the shortest path, not spin full 360. */
 const float nearpi=3.13f,negative=-3.13f;
 const float x=b24_g163_aim_heading(nearpi,negative,dt,1,1);
 assert(x>nearpi&&x-nearpi<.02f);
 /* Reject invalid camera telemetry and do not apply infinite turn. */
 assert(b24_g163_aim_heading(1.f,NAN,dt,1,1)==1.f);
 assert(b24_g163_aim_heading(1.f,2.f,NAN,1,1)==1.f);
 assert(b24_g163_aim_heading(1.f,2.f,-1.f,1,1)==1.f);
 const float stalled=b24_g163_aim_heading(0.f,3.f,2.f,1,1);
 assert(stalled>0.f&&stalled<3.f);
 puts("G163 PASS aim-locked actor world yaw while backpedal/strafe; camera reticle, physics, Stage2/RUSH heading preserved; C11 no VPK.");
 return 0;
}
