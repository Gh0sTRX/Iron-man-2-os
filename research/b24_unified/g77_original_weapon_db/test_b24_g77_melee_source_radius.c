#include "b24_g77_melee_source_radius.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(void){
 B24G77Bounds a={{0,0,0},{2,2,2}};
 B24G77Bounds b={{0,0,0},{2,2,2}};
 float radius=b24_g77_original_model_radius(&a);
 assert(fabsf(radius-1.7320508f)<.00001f);
 assert(b24_g77_original_melee_broadphase(&a,&b,(B24G77Vec3){0,0,0},
   (B24G77Vec3){3,0,0},0.f)==1);
 assert(b24_g77_original_melee_broadphase(&a,&b,(B24G77Vec3){0,0,0},
   (B24G77Vec3){3.5f,0,0},0.f)==0);
 assert(b24_g77_original_melee_broadphase(&a,&b,(B24G77Vec3){0,0,0},
   (B24G77Vec3){3.5f,0,0},.1f)==1);
 assert(b24_g77_original_melee_broadphase(&a,&b,(B24G77Vec3){0,0,0},
   (B24G77Vec3){3.5f,0,0},NAN)==0);
 puts("PASS G77 genuine ARM 0x3F000000 melee half-BBox-3D diagonal radius and threshold compare host source");
 return 0;
}
