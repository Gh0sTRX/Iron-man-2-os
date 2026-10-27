#include "b24_g76_original_native_damage_math.h"
#include <math.h>
B24G76DamageResult b24_g76_native_damage_reference(
 B24G76DamageResource *actor,float damage){
 /* Real native:
  * vldr s15,[r0,#0x3BC]; vmov s14,r1;
  * vldr s16,[r0,#0x394]; vcmpe.f32 s15,#0;
  * vsubhi.f32 s15,s15,s14 ; vstrhi [r0,#0x3BC];
  * alternate path vsub.f32 s15,s16,s14 ; vstr [r0,#0x394].
  * Native code also dispatches status callbacks, not reproduced here.
  * Positive finite input validation is NEW API safety, not native check.
  */
 if(!actor||!isfinite(damage)||damage<=0.f||
    !isfinite(actor->primary_float_at_actor_offset_0x3BC)||
    !isfinite(actor->secondary_float_at_actor_offset_0x394))
  return B24_G76_NO_HIT;
 if(actor->primary_float_at_actor_offset_0x3BC>0.f){
  float val=actor->primary_float_at_actor_offset_0x3BC-damage;
  actor->primary_float_at_actor_offset_0x3BC=fmaxf(0.f,val);
  return B24_G76_PRIMARY_RESOURCE_HIT;
 }
 if(actor->secondary_float_at_actor_offset_0x394>0.f){
  float val=actor->secondary_float_at_actor_offset_0x394-damage;
  /* G77 native ARM vstr [r0,#0x394] is RAW subtract; it does NOT
   clamp this secondary write in Actor::Damage(float). */
  actor->secondary_float_at_actor_offset_0x394=val;
  return B24_G76_SECONDARY_RESOURCE_HIT;
 }
 return B24_G76_NO_HIT;
}
