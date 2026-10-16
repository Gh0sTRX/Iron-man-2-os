#ifndef B24_G82_ORIGINAL_COMBAT_COORDINATOR_H
#define B24_G82_ORIGINAL_COMBAT_COORDINATOR_H
#include <stdint.h>
#include "../b24_g8_melee_source_chain.h"
#include "../g76_original_combat/b24_g76_original_native_damage_math.h"
#include "../g77_original_weapon_db/b24_g77_melee_source_radius.h"
/* Source-only coordinator. The original 2010 game:
 * - has source IM2V animation durations, now in G8;
 * - has real model bounding-box half diagonal check, G77;
 * - has native Actor::Damage two-resource math, G76.
 * Authentic contact event frame and AttackEntity instance damage numbers
 * still UNKNOWN. This coordinator NEVER fabricates either of them.
 * Actual game B14 remains sole movement/physics owner; no VPK built. */
typedef struct {
 B24G8MeleeChain clip;
 unsigned bound_target_valid;
 uint32_t last_step;
 uint32_t last_contact_id;
 uint32_t last_target_id;
 unsigned accepted_hits;
 unsigned rejected_unverified_events;
} B24G82Combat;
typedef struct {
 uint32_t observed_original_event_id;
 uint32_t target_id;
 unsigned observed_original_combo_step;
 int source_contact_timing_verified; /* NEVER auto-set from clip percentage */
 int source_attack_damage_verified;  /* requires actual decoded instance */
 int actor_can_attack_verified;       /* original permissions/target check */
 float original_attack_damage;
 B24G77Bounds attacker_bounds;
 B24G77Bounds target_bounds;
 B24G77Vec3 original_attacker_world_contact;
 B24G77Vec3 original_target_world_contact;
 float original_global_melee_tolerance; /* not decoded; caller supplied */
} B24G82Contact;
void b24_g82_request_melee(B24G82Combat *state,uint32_t now_ms,int grounded,
                            int paused);
const char *b24_g82_tick(B24G82Combat *state,uint32_t now_ms);
B24G76DamageResult b24_g82_resolve_source_contact(
 B24G82Combat *state,const B24G82Contact *source_contact,
 B24G76DamageResource *target);
#endif
