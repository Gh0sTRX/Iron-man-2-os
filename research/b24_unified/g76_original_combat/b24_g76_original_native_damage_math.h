#ifndef B24_G76_ORIGINAL_NATIVE_DAMAGE_MATH_H
#define B24_G76_ORIGINAL_NATIVE_DAMAGE_MATH_H
/* Original 2010 iOS ARM Actor::Damage(float) bounded instruction translated
 * to an isolated PURE mathematical reference. Offsets and subtraction order
 * AUTHENTIC, exact typed field names not yet proven (e.g. shield vs HP).
 * No attack permissions, reaction, SFX, callbacks or B24 gameplay wiring.
 * Not connected to VPK. */
typedef struct {
 float primary_float_at_actor_offset_0x3BC;
 float secondary_float_at_actor_offset_0x394;
} B24G76DamageResource;
typedef enum {
 B24_G76_NO_HIT=0,B24_G76_PRIMARY_RESOURCE_HIT=1,
 B24_G76_SECONDARY_RESOURCE_HIT=2
} B24G76DamageResult;
/* This exact deterministic pure core reproduces the two native float
 * subtraction branches when input is positive finite. It does NOT map
 * original current/max or native dispatch virtual functions. */
B24G76DamageResult b24_g76_native_damage_reference(
 B24G76DamageResource *actor,float source_damage_amount);
#endif
