#include "b24_g82_original_combat_coordinator.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static B24G82Contact fixture(void){
 B24G82Contact c={0};
 c.observed_original_event_id=109;
 c.target_id=8;
 c.observed_original_combo_step=1;
 c.original_attack_damage=12.f;
 c.attacker_bounds=(B24G77Bounds){{0,0,0},{2,2,2}};
 c.target_bounds=c.attacker_bounds;
 c.original_attacker_world_contact=(B24G77Vec3){0,0,0};
 c.original_target_world_contact=(B24G77Vec3){2,0,0};
 c.original_global_melee_tolerance=0.f;
 return c;
}
int main(void){
 B24G82Combat state={0};
 B24G76DamageResource enemy={20.f,50.f};
 B24G82Contact c=fixture();
 /* Without native combat evidence, original 2010 clips do NOT damage. */
 assert(!b24_g82_tick(&state,1000));
 b24_g82_request_melee(&state,1000,0,0);
 assert(state.clip.phase==0);
 b24_g82_request_melee(&state,1000,1,1);
 assert(state.clip.phase==0);
 b24_g82_request_melee(&state,1000,1,0);
 assert(strcmp(b24_g82_tick(&state,1010),
          "ironman_ironman_ground_combo_1")==0);
 assert(b24_g82_resolve_source_contact(&state,&c,&enemy)==B24_G76_NO_HIT);
 assert(enemy.primary_float_at_actor_offset_0x3BC==20.f);
 assert(state.rejected_unverified_events==1);
 /* The following 3 flags/model data are TEST FIXTURES, NOT original
  * 2010 observed hit frames or source damage; only wiring exercised. */
 c.source_contact_timing_verified=1;c.source_attack_damage_verified=1;
 c.actor_can_attack_verified=1;
 assert(b24_g82_resolve_source_contact(&state,&c,&enemy)==B24_G76_PRIMARY_RESOURCE_HIT);
 assert(enemy.primary_float_at_actor_offset_0x3BC==8.f);
 assert(b24_g82_resolve_source_contact(&state,&c,&enemy)==B24_G76_NO_HIT);
 assert(enemy.primary_float_at_actor_offset_0x3BC==8.f);
 c.original_target_world_contact.x=99.f;
 c.observed_original_event_id++;
 assert(b24_g82_resolve_source_contact(&state,&c,&enemy)==B24_G76_NO_HIT);
 c.original_target_world_contact.x=2.f;
 b24_g82_request_melee(&state,1011,1,0);
 assert(strcmp(b24_g82_tick(&state,1266),
          "ironman_ironman_ground_combo_2")==0);
 c.observed_original_combo_step=2;
 c.observed_original_event_id++;
 assert(b24_g82_resolve_source_contact(&state,&c,&enemy)==B24_G76_PRIMARY_RESOURCE_HIT);
 assert(enemy.primary_float_at_actor_offset_0x3BC==0.f);
 assert(enemy.secondary_float_at_actor_offset_0x394==50.f);
 b24_g82_request_melee(&state,1270,1,0);
 assert(strcmp(b24_g82_tick(&state,1566),
          "ironman_ironman_ground_combo_3")==0);
 c.observed_original_combo_step=3;
 c.observed_original_event_id++;
 assert(b24_g82_resolve_source_contact(&state,&c,&enemy)==B24_G76_SECONDARY_RESOURCE_HIT);
 assert(enemy.secondary_float_at_actor_offset_0x394==38.f);
 assert(!b24_g82_tick(&state,2066));
 assert(state.accepted_hits==3);
 assert(b24_g82_resolve_source_contact(&state,&c,&enemy)==B24_G76_NO_HIT);
 puts("PASS G82 original source clip 266/300/500ms + G77 model-radius + G76 two-resource hit arithmetic chained; NO native hit-window assumption, only synthetic verified-signal API fixture, NO VPK");
 return 0;
}
