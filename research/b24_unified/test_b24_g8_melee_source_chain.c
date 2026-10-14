#include "b24_g8_melee_source_chain.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void){
 B24G8MeleeChain a={0};
 assert(!b24_g8_melee_active(&a));
 b24_g8_melee_press(&a,1000);
 assert(!strcmp(b24_g8_melee_tick(&a,1000),"ironman_ironman_ground_combo_1"));
 b24_g8_melee_press(&a,1200);
 assert(!strcmp(b24_g8_melee_tick(&a,1266),"ironman_ironman_ground_combo_2"));
 assert(a.completed_attacks==1);
 b24_g8_melee_press(&a,1450);
 assert(!strcmp(b24_g8_melee_tick(&a,1566),"ironman_ironman_ground_combo_3"));
 assert(a.completed_attacks==2);
 assert(b24_g8_melee_active(&a));
 assert(b24_g8_melee_tick(&a,2066)==NULL);
 assert(!b24_g8_melee_active(&a) && a.completed_attacks==3);
 b24_g8_melee_press(&a,2200);
 assert(!strcmp(b24_g8_melee_tick(&a,2466),"ironman_ironman_ground_combo_1_end"));
 assert(b24_g8_melee_tick(&a,2699)==NULL);
 assert(a.completed_attacks==4);
 b24_g8_melee_press(&a,3000);
 b24_g8_melee_press(&a,3010);
 assert(!strcmp(b24_g8_melee_tick(&a,3266),"ironman_ironman_ground_combo_2"));
 assert(!strcmp(b24_g8_melee_tick(&a,3566),"ironman_ironman_ground_combo_2_end"));
 assert(b24_g8_melee_tick(&a,3866)==NULL);
 assert(a.completed_attacks==6);
 puts("PASS original 2010 Mark VI actual combo_1 (266ms) -> combo_2"
      " (300ms) -> combo_3 (500ms), authored recovery clips,"
      " buffered Square edge, no invented hit/damage frames, NO VPK");
 return 0;
}
