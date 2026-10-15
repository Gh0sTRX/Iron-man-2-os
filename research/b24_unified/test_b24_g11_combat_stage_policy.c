#include "b24_g11_combat_stage_policy.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(void){
 B24G11CombatDecision d={0};
 B24G11CombatInput a={.9f,.95f,1,1,0,0,0};
 assert(b24_g11_combat_stage_policy(&a,&d));
 assert(d.allow_repulsor&&d.allow_unibeam&&d.allow_missile);
 assert(!d.boost&&d.force_walk&&hypotf(d.move_x,d.move_y)<=.821f);
 a=(B24G11CombatInput){.9f,.96f,1,1,0,1,1};
 assert(b24_g11_combat_stage_policy(&a,&d));
 assert(d.allow_repulsor&&d.force_stage1&&!d.boost);
 assert(hypotf(d.move_x,d.move_y)<=.821f);
 a=(B24G11CombatInput){.9f,.95f,1,1,0,1,2};
 assert(b24_g11_combat_stage_policy(&a,&d));
 assert(!d.allow_repulsor&&!d.allow_unibeam&&!d.allow_missile);
 assert(d.boost&&!d.force_stage1&&d.move_x==.9f);
 a.prior_flight_stage=3;
 assert(b24_g11_combat_stage_policy(&a,&d));
 assert(!d.allow_repulsor&&d.boost);
 a.trigger=0;
 assert(b24_g11_combat_stage_policy(&a,&d));
 assert(!d.allow_repulsor&&d.boost);
 a=(B24G11CombatInput){.22f,.4f,0,1,0,1,1};
 assert(b24_g11_combat_stage_policy(&a,&d));
 assert(d.move_x==.22f&&d.move_y==.4f&&d.allow_repulsor);
 assert(b24_g11_stage_allows_hand_attack(1,1));
 assert(!b24_g11_stage_allows_hand_attack(1,2));
 assert(!b24_g11_stage_allows_hand_attack(1,3));
 assert(b24_g11_stage_allows_hand_attack(0,0));
 a.move_x=NAN;assert(!b24_g11_combat_stage_policy(&a,&d));
 puts("PASS G11 G10 real stage decision: R->walk, no sprint,"
      " Stage1 hover R keeps stage1, Stage2/RUSH R ignored,"
      " move free again at release, old flight unchanged, WM not suit-blocked");
 return 0;
}
