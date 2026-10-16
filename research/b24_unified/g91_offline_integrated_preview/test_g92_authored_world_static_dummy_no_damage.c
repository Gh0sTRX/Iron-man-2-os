/* G92 real existing G10/G11 C original integration diagnostic. Explicitly
 * NOT actual iOS hitframes; simulated proximity flashes cannot change HP. */
#include "../b24_g10_practice_target.h"
#include "../b24_g11_practice_melee_feedback.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 B24G10PracticeTarget dummy=b24_g10_practice_target_at_floor(.072501f);
 assert(b24_g10_practice_target_valid(&dummy));
 assert(dummy.x==0.f&&dummy.y==10.f&&dummy.invulnerable==1);
 const float z=dummy.z-1.f;
 B24G11PracticeMeleeFeedback effect={0};
 /* diagnostic is grounded-only, held / fly does not create melee damage */
 assert(!b24_g11_practice_melee_hit(&effect,&dummy,0.f,9.f,z,1000,0,1));
 assert(!b24_g11_practice_melee_hit(&effect,&dummy,0.f,9.f,z,1000,1,0));
 assert(!b24_g11_practice_melee_hit(&effect,&dummy,0.f,0.f,z,1000,1,1));
 assert(effect.whiffs==1&&effect.successful_hits==0);
 assert(b24_g11_practice_melee_hit(&effect,&dummy,0.f,9.f,z,1010,1,1));
 assert(effect.successful_hits==1&&b24_g11_practice_hit_flash(&effect,1010)>0.f);
 /* Closely repeated user input must not multiply debug contacts. */
 assert(!b24_g11_practice_melee_hit(&effect,&dummy,0.f,9.f,z,1015,1,1));
 assert(b24_g11_practice_hit_flash(&effect,1500)==0.f);
 assert(b24_g11_practice_melee_hit(&effect,&dummy,0.f,9.f,z,1501,1,1));
 assert(effect.successful_hits==2);
 assert(dummy.invulnerable==1 && dummy.radius==.46f && dummy.z==z+1.f);
 assert(b24_g10_practice_target_valid(&dummy));
 puts("PASS G92 actual original source B24 G10+G11 diagnostic immortal 3D target and melee-range feedback; no original hit frame or enemy damage claimed. NO VPK.");
 return 0;
}
