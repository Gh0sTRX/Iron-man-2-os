#include "b24_g103_verified_original_actor_attack_classification.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
int main(void){
 assert(b24_g103_can_attack_proven_native_classes(0,2)==B24_G103_ORIGINAL_PERMISSION_DENIED);
 assert(b24_g103_can_attack_proven_native_classes(0,3)==B24_G103_ORIGINAL_PERMISSION_ALLOWED);
 assert(b24_g103_can_attack_proven_native_classes(0,4)==B24_G103_ORIGINAL_PERMISSION_UNKNOWN);
 assert(b24_g103_can_attack_proven_native_classes(0,0)==B24_G103_ORIGINAL_PERMISSION_ALLOWED);
 assert(b24_g103_can_attack_proven_native_classes(0,1)==B24_G103_ORIGINAL_PERMISSION_ALLOWED);
 assert(b24_g103_can_attack_proven_native_classes(0,5)==B24_G103_ORIGINAL_PERMISSION_ALLOWED);
 assert(b24_g103_can_attack_proven_native_classes(0,-1)==B24_G103_ORIGINAL_PERMISSION_ALLOWED);
 assert(b24_g103_can_attack_proven_native_classes(1,2)==B24_G103_ORIGINAL_PERMISSION_UNKNOWN);
 assert(b24_g103_can_attack_proven_native_classes(1,4)==B24_G103_ORIGINAL_PERMISSION_UNKNOWN);
 assert(b24_g103_can_attack_proven_native_classes(2,3)==B24_G103_ORIGINAL_PERMISSION_DENIED);
 assert(b24_g103_can_attack_proven_native_classes(-1,3)==B24_G103_ORIGINAL_PERMISSION_DENIED);
 assert(b24_g103_can_attack_proven_native_classes(INT32_MAX,INT32_MIN)==B24_G103_ORIGINAL_PERMISSION_DENIED);
 puts("PASS G103 exact original 2010 Actor::CanAttack ARM source type0 known-case truth table, target virtual type4 and attacker type1 UNKNOWN; real original hit permissions not enabled without actual native actor type. NO VPK.");
 return 0;
}
