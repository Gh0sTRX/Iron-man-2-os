/* G88: defensive multi-target contact evidence ledger regression.
 * This test deliberately supplies synthetic 1.0f DAMAGE and flags only to
 * exercise existing G82 safe API. It does NOT reveal original 2010 hit
 * frames/damage, or authorize real Vita enemy hits. NO VPK.
 */
#include "../g82_original_combat/b24_g82_original_combat_coordinator.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static B24G82Contact test_contact(unsigned event_id,unsigned target_id,
                                  unsigned combo_step){
 B24G82Contact c={0};
 c.observed_original_event_id=event_id;
 c.target_id=target_id;
 c.observed_original_combo_step=combo_step;
 c.original_attack_damage=1.f; /* UNIT TEST FIXTURE, NOT GAME DATA */
 c.attacker_bounds=(B24G77Bounds){{0.f,0.f,0.f},{2.f,2.f,2.f}};
 c.target_bounds=c.attacker_bounds;
 c.original_attacker_world_contact=(B24G77Vec3){0.f,0.f,0.f};
 c.original_target_world_contact=(B24G77Vec3){1.f,0.f,0.f};
 c.original_global_melee_tolerance=0.f; /* fixture */
 return c;
}
int main(void){
 B24G82Combat c={0};
 B24G76DamageResource a={100.f,100.f},b={100.f,100.f};
 B24G82Contact hit=test_contact(700,111,1);
 b24_g82_request_melee(&c,100,1,0);
 assert(b24_g82_tick(&c,101));
 /* Missing original 2010 frame/damage/permission proof: absolutely NO HIT */
 assert(b24_g82_resolve_source_contact(&c,&hit,&a)==B24_G76_NO_HIT);
 assert(a.primary_float_at_actor_offset_0x3BC==100.f);
 hit.source_contact_timing_verified=1;
 hit.source_attack_damage_verified=1;
 hit.actor_can_attack_verified=1;
 assert(b24_g82_resolve_source_contact(&c,&hit,&a)==B24_G76_PRIMARY_RESOURCE_HIT);
 assert(a.primary_float_at_actor_offset_0x3BC==99.f);
 /* Interleaving separate target B may be independently accepted. */
 hit.target_id=222;
 assert(b24_g82_resolve_source_contact(&c,&hit,&b)==B24_G76_PRIMARY_RESOURCE_HIT);
 assert(b.primary_float_at_actor_offset_0x3BC==99.f);
 /* Repeated source event 700+A was the G82 bug: last tuple was 700+B. */
 hit.target_id=111;
 assert(b24_g82_resolve_source_contact(&c,&hit,&a)==B24_G76_NO_HIT);
 assert(a.primary_float_at_actor_offset_0x3BC==99.f);
 assert(c.g88_duplicates_rejected==1);
 /* Unit contact with a separately supplied verified event ID is distinct.
  * This fixture is NOT a statement that the source game has a new frame. */
 hit.observed_original_event_id=701;
 assert(b24_g82_resolve_source_contact(&c,&hit,&a)==B24_G76_PRIMARY_RESOURCE_HIT);
 assert(a.primary_float_at_actor_offset_0x3BC==98.f);
 assert(c.g88_verified_contact_count==3u);
 /* One attack phase can contain up to 32 distinct verified contact pairs.
  * Full ledger fails closed, never evicts old A and permits another hit. */
 for(unsigned i=3;i<B24_G88_MAX_VERIFIED_CONTACTS_PER_COMBO_PHASE;i++){
  hit.observed_original_event_id=702u+i;
  hit.target_id=1000u+i;
  assert(b24_g82_resolve_source_contact(&c,&hit,&a)==B24_G76_PRIMARY_RESOURCE_HIT);
 }
 assert(c.g88_verified_contact_count==B24_G88_MAX_VERIFIED_CONTACTS_PER_COMBO_PHASE);
 const float last=a.primary_float_at_actor_offset_0x3BC;
 hit.observed_original_event_id=900u;
 hit.target_id=900u;
 assert(b24_g82_resolve_source_contact(&c,&hit,&a)==B24_G76_NO_HIT);
 assert(a.primary_float_at_actor_offset_0x3BC==last);
 assert(c.g88_capacity_rejected==1);
 hit.observed_original_event_id=700u;
 hit.target_id=111u;
 assert(b24_g82_resolve_source_contact(&c,&hit,&a)==B24_G76_NO_HIT);
 assert(c.g88_duplicates_rejected==2);
 /* Genuine authored source clip step 1 -> 2 at 266 ms:
  * clear ONLY previous phase ledger; old target can receive a separate
  * independent, source-verified event in step 2. */
 b24_g82_request_melee(&c,120,1,0);
 assert(b24_g82_tick(&c,366));
 assert(c.clip.phase==2u);
 assert(c.g88_verified_contact_count==0u);
 hit=test_contact(700u,111u,2u);
 hit.source_contact_timing_verified=1;
 hit.source_attack_damage_verified=1;
 hit.actor_can_attack_verified=1;
 assert(b24_g82_resolve_source_contact(&c,&hit,&a)==B24_G76_PRIMARY_RESOURCE_HIT);
 assert(c.g88_verified_contact_count==1u);
 /* Never accept event from the previous original phase. */
 hit.observed_original_combo_step=1u;
 assert(b24_g82_resolve_source_contact(&c,&hit,&a)==B24_G76_NO_HIT);
 puts("PASS G88 source-safe G82 C11: unverified hit suppressed, A-B-A duplicate fixed, finite per-phase source pair ledger, capacity fail-closed, 266ms phase reset; no invented original hit frames/damage, NO VPK");
 return 0;
}
