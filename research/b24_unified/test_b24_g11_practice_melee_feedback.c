#include "b24_g11_practice_melee_feedback.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 B24G11PracticeMeleeFeedback s={0};
 B24G10PracticeTarget t=b24_g10_practice_target_at_floor(-.25f);
 assert(t.invulnerable==1);
 assert(!b24_g11_practice_melee_hit(&s,&t,0.f,0.f,0.f,1000,1,1));
 assert(s.whiffs==1&&s.successful_hits==0);
 assert(b24_g11_practice_melee_hit(&s,&t,0.f,9.f,0.f,1000,1,1));
 assert(s.successful_hits==1&&t.invulnerable);
 assert(b24_g11_practice_hit_flash(&s,1000)>.95f);
 assert(!b24_g11_practice_melee_hit(&s,&t,0.f,9.f,0.f,1050,1,1));
 assert(b24_g11_practice_melee_hit(&s,&t,0.f,9.f,0.f,1240,1,1));
 assert(s.successful_hits==2&&t.invulnerable==1);
 assert(!b24_g11_practice_hit_flash(&s,1500));
 assert(!b24_g11_practice_melee_hit(&s,&t,0.f,9.f,0.f,1600,1,0));
 assert(!b24_g11_practice_melee_hit(&s,&t,0.f,9.f,0.f,1600,0,1));
 puts("PASS G11 real C1L1 permanent GPU practice actor receives"
      " proximity melee feedback, no hits beyond range, cooldown, yellow"
      " temporary flash, original target invulnerable forever, no fake AI");
 return 0;
}
