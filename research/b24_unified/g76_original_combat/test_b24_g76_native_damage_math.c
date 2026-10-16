#include "b24_g76_original_native_damage_math.h"
#include <assert.h>
#include <stdio.h>
#include <math.h>
int main(void){
 B24G76DamageResource a={30.f,120.f};
 assert(b24_g76_native_damage_reference(&a,10.f)==B24_G76_PRIMARY_RESOURCE_HIT);
 assert(a.primary_float_at_actor_offset_0x3BC==20.f);
 assert(a.secondary_float_at_actor_offset_0x394==120.f);
 assert(b24_g76_native_damage_reference(&a,25.f)==B24_G76_PRIMARY_RESOURCE_HIT);
 assert(a.primary_float_at_actor_offset_0x3BC==0.f);
 assert(a.secondary_float_at_actor_offset_0x394==120.f); /* No within-hit overflow */
 assert(b24_g76_native_damage_reference(&a,60.f)==B24_G76_SECONDARY_RESOURCE_HIT);
 assert(a.secondary_float_at_actor_offset_0x394==60.f);
 assert(b24_g76_native_damage_reference(&a,100.f)==B24_G76_SECONDARY_RESOURCE_HIT);
 assert(a.secondary_float_at_actor_offset_0x394==0.f);
 assert(b24_g76_native_damage_reference(&a,20.f)==B24_G76_NO_HIT);
 assert(b24_g76_native_damage_reference(&a,NAN)==B24_G76_NO_HIT);
 printf("PASS G76 original ARM two-stage native Actor resource subtraction: +0x3BC then +0x394, saturation and no damage carry-over across active primary source pool; callbacks not wired.\n");
 return 0;
}
