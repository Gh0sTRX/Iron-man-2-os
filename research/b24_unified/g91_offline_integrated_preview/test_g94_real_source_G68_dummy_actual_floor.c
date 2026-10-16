/* G94. Test EXACT native G92 static dummy placement against real owner
 * G68 1910 original 2010 collision source faces. No authored fake floor.
 * This is a HOST hardware-independent source world placement smoke.
 */
#include "../b24_gpu_g68_collision.h"
#include "../g75_device_qa/b24_g75_source_capsule.h"
#include "../b24_g10_practice_target.h"
#include "../b24_g11_practice_melee_feedback.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
int main(int argc,char **argv) {
 if(argc!=2)return 2;
 B24C1OriginalCollision world={0};
 assert(b24_g70_g68_collision_load(&world,argv[1]));
 assert(world.ready && world.count==1910 && world.wall_count==1690);
 /* G92's exact intended initial real G75 B14 world candidate: 0,0 at
  * source ground 0.072501 rather than typed CLARA unverified spawn Z25. */
 const float px=0.f,py=0.f,pz=.072501f;
 const float xx[]={0.f,px,px+5.f,px-5.f};
 const float yy[]={10.f,py+5.f,py,py};
 B24G10PracticeTarget dummy={0};
 int found=0;
 for(unsigned c=0;c<4;c++){
   float ground=-10.f;
   if(!b24_g75_floor_crossed(&world,xx[c],yy[c],
                             pz+2.f,pz-5.f,&ground))continue;
   B24G10PracticeTarget candidate=b24_g10_practice_target_at_floor(ground);
   candidate.x=xx[c];candidate.y=yy[c];
   if(!b24_g10_practice_target_valid(&candidate))continue;
   dummy=candidate;found=1;break;
 }
 assert(found && "G92 real native game could NEVER spawn user test target");
 assert(dummy.invulnerable && b24_g10_practice_target_valid(&dummy));
 float surface=-123.f;
 assert(b24_g75_floor_crossed(&world,dummy.x,dummy.y,
             dummy.z+1.f,dummy.z-2.f,&surface));
 assert(fabsf((dummy.z-1.f)-surface)<.004f);
 /* Source-backed collision check does not silently relabel DEBUG hits as
  * original iOS actor.damage, and the dummy is never destructible. */
 B24G11PracticeMeleeFeedback feedback={0};
 assert(!b24_g11_practice_melee_hit(&feedback,&dummy,
       dummy.x,dummy.y,dummy.z-1.f,100u,0,1));
 assert(b24_g11_practice_melee_hit(&feedback,&dummy,
       dummy.x,dummy.y,dummy.z-1.f,110u,1,1));
 assert(feedback.successful_hits==1u && dummy.invulnerable==1);
 printf("PASS G94 real 2010 G68 1910 source triangles verified G92 dummy 3D floor=%f at x=%.3f y=%.3f z=%.3f; ORIGINAL_DAMAGE_DISABLED, NO VPK\n",
         surface,dummy.x,dummy.y,dummy.z);
 b24_c1_original_collision_free(&world);
 return 0;
}
