#include "b24_g75_source_capsule.h"
#include "b24_gpu_g68_collision.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
/* Genuine original 2010 G66 city and G66C native collider, now test
 * the integrated G75 singleton after optional G159 source road patch.
 * Requires app0:assets/G66_city.g66m linked inside CI working directory.
 * Only C11 host evidence, not Vita physical console. */
int main(int argc,char **argv){
 if(argc!=2)return 2;
 B24C1OriginalCollision w={0};
 assert(b24_g70_g68_collision_load(&w,argv[1]));
 float x=-160.f,y=-160.f,z=2.6937f;
 assert(b24_g75_capsule_reconcile(&w,-160.f,-160.f,2.6937f,
     -159.96f,-160.f,2.6937f,1,.35f,2.24f,&x,&y,&z));
 printf("G159 real G75 capsule road source candidate move: xy=(%.4f,%.4f) height=%.4f\n",x,y,z);
 /* One original source road triangle must be valid floor at original Z;
  * do not allow collapse 2.6212 below the rendered road. */
 assert(fabsf(z-2.6937f)<.05f);
 assert(x>=-160.f && x<=-159.95f);
 /* The same world original native G66C low support stays unchanged. */
 float b_x=-160.f,b_y=-160.f,b_z=.0725f;
 assert(b24_g75_capsule_reconcile(&w,-160.f,-160.f,.0725f,
      -159.96f,-160.f,.0725f,1,.35f,2.24f,
      &b_x,&b_y,&b_z));
 assert(fabsf(b_z-.0725f)<.03f);
 /* No original authored support far outside the real map. */
 float support=777.f;
 assert(!b24_g74_near_original_floor(&w,10000.f,10000.f,2.6937f,&support));
 assert(support==777.f);
 printf("G159 native G75 one-game original road candidate PASS: roadZ=%.4f nativeZ=%.4f and B14 position move %.4f. No invented collision source / no VPK\n",z,b_z,x);
 b24_c1_original_collision_free(&w);
 return 0;
}
