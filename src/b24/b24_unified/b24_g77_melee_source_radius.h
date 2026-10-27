#ifndef B24_G77_MELEE_SOURCE_RADIUS_H
#define B24_G77_MELEE_SOURCE_RADIUS_H
/* Source: ORIGINAL 2010 ARM Actor::TestMeleeHit(Actor*) at 0x000DFD94.
 * PC-relative vldr s16 at +0x20 takes float32 at +0x138, decoded from
 * raw 0x3F000000 (0.5f, not a code instruction).
 * Verified source ARM normalizes bbox 3D diagonal length (vsqrt) then
 * multiplies it by this factor, once per each model.
 * Original global tolerance value/actor virtual endpoints not mapped.
 * This pure source-only mathematical primitive is NOT live gameplay/VPK. */
typedef struct {float x,y,z;} B24G77Vec3;
typedef struct {B24G77Vec3 min,max;} B24G77Bounds;
float b24_g77_original_model_radius(const B24G77Bounds *bounds);
int b24_g77_original_melee_broadphase(const B24G77Bounds *attacker,
 const B24G77Bounds *target,
 B24G77Vec3 original_melee_endpoint_a,
 B24G77Vec3 original_melee_endpoint_b,
 float decoded_later_global_tolerance);
#endif
