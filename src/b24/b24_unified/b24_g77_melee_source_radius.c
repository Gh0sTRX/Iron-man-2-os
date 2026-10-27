#include "b24_g77_melee_source_radius.h"
#include <math.h>
static int finite3(B24G77Vec3 p){
 return isfinite(p.x)&&isfinite(p.y)&&isfinite(p.z);
}
static float diagonal_length(B24G77Vec3 a,B24G77Vec3 b){
 float x=a.x-b.x,y=a.y-b.y,z=a.z-b.z;
 return sqrtf(x*x+y*y+z*z);
}
float b24_g77_original_model_radius(const B24G77Bounds *bounds){
 if(!bounds||!finite3(bounds->min)||!finite3(bounds->max))return NAN;
 /* 2010 native source ARM vldr s16 from literal 0x3f000000 = .5 */
 return diagonal_length(bounds->max,bounds->min)*.5f;
}
int b24_g77_original_melee_broadphase(const B24G77Bounds *attacker,
 const B24G77Bounds *target,B24G77Vec3 a,B24G77Vec3 b,float global_tolerance){
 /* The original ARM takes two object-space bbox diagonals and a world-
  * space 3D separation from two virtual model callbacks; their EXACT
  * selection remains to be mapped. Both world points and the native global
  * epsilon are caller supplied. No fabricated hit time/damage applied.
  * Source ARM returns !(distance > threshold) for this broadphase. */
 float ra=b24_g77_original_model_radius(attacker);
 float rb=b24_g77_original_model_radius(target);
 if(!isfinite(ra)||!isfinite(rb)||!finite3(a)||!finite3(b)||
    !isfinite(global_tolerance)||global_tolerance<0.f)return 0;
 float distance=diagonal_length(a,b);
 return isfinite(distance)&&distance<=ra+rb+global_tolerance;
}
