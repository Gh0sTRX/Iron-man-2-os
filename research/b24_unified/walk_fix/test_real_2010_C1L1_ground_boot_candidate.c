#include "vita_source_walkable_boot_fix.h"
#include "b24_g75_source_capsule.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
static unsigned eight(const B24C1OriginalCollision *c,float x,float y,float z) {
 static const float d[8][2]={{1,0},{-1,0},{0,1},{0,-1},
   {.70710678f,.70710678f},{-.70710678f,.70710678f},
   {.70710678f,-.70710678f},{-.70710678f,-.70710678f}};
 unsigned good=0;
 for(unsigned i=0;i<8;i++){
  const float nx=x+.08f*d[i][0],ny=y+.08f*d[i][1];
  float ox=nx,oy=ny,oz=z;
  assert(b24_g75_capsule_reconcile(c,x,y,z,nx,ny,z,1,.35f,2.24f,&ox,&oy,&oz));
  if(hypotf(ox-x,oy-y)>.001f)++good;
 }
 return good;
}
int main(int argc,char**argv){
 if(argc!=2)return 2;
 B24C1OriginalCollision orig={0};
 assert(b24_g70_g68_collision_load(&orig,argv[1]));
 assert(orig.ready&&orig.count==1910u&&orig.wall_count==1690u);
 const unsigned unsupported_before=eight(&orig,0,0,0);
 Im2VitaGroundBootCandidate fixed={0};
 assert(im2_vita_source_walkable_boot(&orig,0,0,0,&fixed));
 assert(isfinite(fixed.x)&&isfinite(fixed.y)&&isfinite(fixed.z));
 const unsigned improved=eight(&orig,fixed.x,fixed.y,fixed.z);
 assert(fixed.accepted_directions==improved);
 assert(improved>=6u);
 fprintf(stderr,"WALK_DIAGNOSTIC: real default B14=(0,0,0) old permitted=%u/8, candidate (%.4f,%.4f,%.4f) permitted=%u/8\\n",unsupported_before,fixed.x,fixed.y,fixed.z,improved);
 /* If origin already passes authentic G75 wall/floor, a spawn relocation
  * is NOT the cause or the solution. Explicitly diagnose, do not move it. */
 if(unsupported_before<6u)assert(improved>unsupported_before);
 float true_floor=0.f;
 assert(b24_g74_near_original_floor(&orig,fixed.x,fixed.y,fixed.z,&true_floor));
 assert(fabsf(true_floor-fixed.z)<.005f);
 const Im2VitaGroundBootCandidate frozen=fixed;
 Im2VitaGroundBootCandidate unset={0};
 assert(!im2_vita_source_walkable_boot(NULL,0,0,0,&unset));
 assert(unset.accepted_directions==0);
 assert(fixed.x==frozen.x&&fixed.y==frozen.y&&fixed.z==frozen.z);
 printf("REAL_C1L1_VITA_GROUND_BOOT: old_B14_origin=(0,0,0) permitted=%u/8, source_face_based_start=(%.5f,%.5f,%.5f) permitted=%u/8 original_native_floor=%.5f, checked_authored_faces=%u\n",
  unsupported_before,fixed.x,fixed.y,fixed.z,improved,true_floor,fixed.source_floor_candidates);
 puts("Walk-focused TEST PASS: sourced G66C candidate available for diagnostic Vita boot, not genuine 2010 iOS MainCharacter spawn. No VPK.");
 b24_c1_original_collision_free(&orig);
 return 0;
}
