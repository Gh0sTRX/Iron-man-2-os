#ifndef B24_G82_ORIGINAL_COMBAT_COORDINATOR_H
#define B24_G82_ORIGINAL_COMBAT_COORDINATOR_H
#include <stdint.h>
#include "b24_g8_melee_source_chain.h"
#include "b24_g76_original_native_damage_math.h"
#include "b24_g77_melee_source_radius.h"
#ifdef B24_G111_NATIVE_SOURCE_GATES
#include "b24_g111_original_source_entitydata_and_combat_permission.h"
#endif
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
 /* G88 defensive source-event dedup: previous implementation remembered
  * ONLY the last target/event pair; A -> B -> A duplicated A's damage.
  * Keep ALL observed accepted event/target pairs in a bounded combo phase.
  * Saturation FAILS CLOSED, never evicts a previous pair and re-hits.
  * This is our Vita integration guard, NOT original iOS contact semantics. */
#define B24_G88_MAX_VERIFIED_CONTACTS_PER_COMBO_PHASE 32u
 unsigned g88_verified_contact_count;
 uint32_t g88_verified_event_ids[B24_G88_MAX_VERIFIED_CONTACTS_PER_COMBO_PHASE];
 uint32_t g88_verified_target_ids[B24_G88_MAX_VERIFIED_CONTACTS_PER_COMBO_PHASE];
 unsigned g88_duplicates_rejected;
 unsigned g88_capacity_rejected;
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
#ifdef B24_G111_NATIVE_SOURCE_GATES
 /* 2010 Actor native input and EntityData names MUST actually originate
  * from original scene/AI; zero-value default is always UNVERIFIED.
  * Old B14 dummy never supplies this; its flash remains DEBUG only. */
 const B24G111OriginalEntityData *original_2010_attack_entitydata;
 int original_actor_fields_0x2b8_verified;
 int32_t original_attacker_actor_field_0x2b8;
 int32_t original_target_actor_field_0x2b8;
 int original_melee_state_field_0x824_verified;
 uint32_t original_melee_state_field_0x824;
#endif
} B24G82Contact;
void b24_g82_request_melee(B24G82Combat *state,uint32_t now_ms,int grounded,
                            int paused);
const char *b24_g82_tick(B24G82Combat *state,uint32_t now_ms);
B24G76DamageResult b24_g82_resolve_source_contact(
 B24G82Combat *state,const B24G82Contact *source_contact,
 B24G76DamageResource *target);
#endif
