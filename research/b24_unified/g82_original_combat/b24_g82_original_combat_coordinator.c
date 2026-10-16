#include "b24_g82_original_combat_coordinator.h"
#include <math.h>
#include <stddef.h>
void b24_g82_request_melee(B24G82Combat *state,uint32_t now,
 int grounded,int paused){
 if(!state||!grounded||paused)return;
 b24_g8_melee_press(&state->clip,now);
}
const char *b24_g82_tick(B24G82Combat *state,uint32_t now){
 if(!state)return NULL;
 unsigned was=state->clip.phase;
 const char *next=b24_g8_melee_tick(&state->clip,now);
 if(was!=state->clip.phase){
  /* an event in combo_1 must not apply after step advances to combo_2 */
  state->bound_target_valid=0;
  state->last_step=state->clip.phase;
  /* G88: old events are never reused across original authored combo
   * boundaries (266/300/500ms). Clear on EVERY phase transition. */
  state->g88_verified_contact_count=0;
 }
 return next;
}
B24G76DamageResult b24_g82_resolve_source_contact(
 B24G82Combat *state,const B24G82Contact *event,
 B24G76DamageResource *target){
 if(!state||!event||!target)return B24_G76_NO_HIT;
 /* Every game-damaging event must come from an ORIGINAL observed hit
  * timing+validated AttackEntity value+2010 attack permission.
  * Until touchHLE/native game confirms all three, no synthetic hits.
  * The unit test passes flagged SIMULATED values solely for API QA. */
 if(!event->source_contact_timing_verified||
    !event->source_attack_damage_verified||
    !event->actor_can_attack_verified||
    !isfinite(event->original_attack_damage)||
    event->original_attack_damage<=0.f||
    !isfinite(event->original_global_melee_tolerance)||
    event->original_global_melee_tolerance<0.f){
  state->rejected_unverified_events++;
  return B24_G76_NO_HIT;
 }
 const unsigned step=state->clip.phase;
 if(step<1||step>3||event->observed_original_combo_step!=step)
  return B24_G76_NO_HIT;
 /* G88: preserve all accepted pairs for THIS ORIGINAL animation
  * phase. The old single last-contact tuple allowed A->B->A duplicate
  * damage during one attack event. Never infer a new 2010 hit from a
  * changed target, from animation elapsed time, or from this guard. */
 for(unsigned i=0;i<state->g88_verified_contact_count;i++){
  if(state->g88_verified_event_ids[i]==event->observed_original_event_id &&
     state->g88_verified_target_ids[i]==event->target_id){
   state->g88_duplicates_rejected++;
   return B24_G76_NO_HIT;
  }
 }
 /* When the bounded ledger fills, reject all further contacts in the
  * current phase. Evicting old pairs would allow re-hitting a target. */
 if(state->g88_verified_contact_count>=
    B24_G88_MAX_VERIFIED_CONTACTS_PER_COMBO_PHASE){
  state->g88_capacity_rejected++;
  return B24_G76_NO_HIT;
 }
 if(!b24_g77_original_melee_broadphase(
   &event->attacker_bounds,&event->target_bounds,
   event->original_attacker_world_contact,
   event->original_target_world_contact,event->original_global_melee_tolerance))
  return B24_G76_NO_HIT;
 B24G76DamageResult result=b24_g76_native_damage_reference(
   target,event->original_attack_damage);
 if(result!=B24_G76_NO_HIT){
  state->bound_target_valid=1;
  state->last_step=step;
  state->last_contact_id=event->observed_original_event_id;
  state->last_target_id=event->target_id;
  unsigned idx=state->g88_verified_contact_count++;
  state->g88_verified_event_ids[idx]=event->observed_original_event_id;
  state->g88_verified_target_ids[idx]=event->target_id;
  state->accepted_hits++;
 }
 return result;
}
