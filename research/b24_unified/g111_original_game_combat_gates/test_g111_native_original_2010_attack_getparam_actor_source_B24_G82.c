/* G111 verifies exact original 2010 ARM source API rules with SYNTHETIC
 * fixture data: no original CLARA AttackEntity Damage integer claims.
 * Explicitly compiled into actual G82 contact/damage pipeline, not an
 * isolated parallel combat motor. Strict fake-contact rejection.
 */
#include "b24_g82_original_combat_coordinator.h"
#include "b24_g111_original_source_entitydata_and_combat_permission.h"
#include "b24_g103_verified_original_actor_attack_classification.h"
#include "b24_g89_real_2010_melee_state_predicates.h"
#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
int main(void){
 const int32_t damage=12;
 const uint8_t billboard=1;
 const uint8_t invalid[2]={11,0};
 B24G111OriginalProperty props[]={
  {"Damage",&damage,4u},
  {"UseBillboardForTail",&billboard,1u},
  {"BadLength",invalid,2u},
  {"damage",invalid,2u} /* original strcasecmp: FIRST matching key wins */
 };
 B24G111OriginalEntityData entity={props,4,1,1};
 int32_t n=-19;
 assert(b24_g111_native_original_get_int(&entity,"damage",&n)&&n==12);
 assert(b24_g111_native_original_get_int(&entity,"DAMAGE",&n)&&n==12);
 assert(!b24_g111_native_original_get_int(&entity,"Unknown",&n));
 assert(!b24_g111_native_original_get_int(&entity,"BadLength",&n));
 assert(n==12); /* failure must not mutate destination */
 uint8_t truth=0;
 assert(b24_g111_native_original_get_bool(&entity,"uSEbILLBOARDfORtAIL",&truth)&&truth==1);
 assert(!b24_g111_native_original_get_bool(&entity,"Damage",&truth));
 entity.names_from_original_class_schema_verified=0;
 assert(!b24_g111_native_original_get_int(&entity,"Damage",&n));
 entity.names_from_original_class_schema_verified=1;
 entity.values_from_original_typed_entitydata_verified=0;
 assert(!b24_g111_native_original_get_int(&entity,"Damage",&n));
 entity.values_from_original_typed_entitydata_verified=1;
 assert(b24_g111_native_source_attack_permission_and_damage(&entity,1,0,3,1,2,&n));
 assert(n==12);
 assert(!b24_g111_native_source_attack_permission_and_damage(&entity,0,0,3,1,2,&n));
 assert(!b24_g111_native_source_attack_permission_and_damage(&entity,1,0,2,1,2,&n));
 assert(!b24_g111_native_source_attack_permission_and_damage(&entity,1,0,4,1,2,&n));
 assert(!b24_g111_native_source_attack_permission_and_damage(&entity,1,1,3,1,2,&n));
 assert(!b24_g111_native_source_attack_permission_and_damage(&entity,1,0,3,0,2,&n));
 assert(!b24_g111_native_source_attack_permission_and_damage(&entity,1,0,3,1,1,&n));
 assert(!b24_g111_native_source_attack_permission_and_damage(&entity,1,0,3,1,13,&n));
 B24G82Combat engine={0};
 B24G76DamageResource target={20.f,50.f};
 B24G82Contact event={0};
 event.observed_original_event_id=109;
 event.target_id=8;
 event.observed_original_combo_step=1;
 event.source_contact_timing_verified=1; /* synthetic fixture only! */
 event.source_attack_damage_verified=1;
 event.actor_can_attack_verified=1;
 event.original_attack_damage=12.f;
 event.attacker_bounds=(B24G77Bounds){{0,0,0},{2,2,2}};
 event.target_bounds=event.attacker_bounds;
 event.original_attacker_world_contact=(B24G77Vec3){0,0,0};
 event.original_target_world_contact=(B24G77Vec3){2,0,0};
 event.original_global_melee_tolerance=0.f;
 b24_g82_request_melee(&engine,1000u,1,0);
 assert(b24_g82_tick(&engine,1010u));
 /* These original native/source typed provenance values are ABSENT in
  * actual G104/G106 dummy. No damage, despite old fixture flags. */
 assert(b24_g82_resolve_source_contact(&engine,&event,&target)==B24_G76_NO_HIT);
 assert(target.primary_float_at_actor_offset_0x3BC==20.f);
 event.original_2010_attack_entitydata=&entity;
 event.original_actor_fields_0x2b8_verified=1;
 event.original_attacker_actor_field_0x2b8=0;
 event.original_target_actor_field_0x2b8=2; /* native category DENIED */
 event.original_melee_state_field_0x824_verified=1;
 event.original_melee_state_field_0x824=2;
 assert(b24_g82_resolve_source_contact(&engine,&event,&target)==B24_G76_NO_HIT);
 assert(target.primary_float_at_actor_offset_0x3BC==20.f);
 event.original_target_actor_field_0x2b8=3;
 assert(b24_g82_resolve_source_contact(&engine,&event,&target)==B24_G76_PRIMARY_RESOURCE_HIT);
 assert(target.primary_float_at_actor_offset_0x3BC==8.f);
 assert(b24_g82_resolve_source_contact(&engine,&event,&target)==B24_G76_NO_HIT);
 assert(engine.g88_duplicates_rejected==1);
 event.original_attack_damage=27.f;
 event.observed_original_event_id++;
 assert(b24_g82_resolve_source_contact(&engine,&event,&target)==B24_G76_NO_HIT);
 assert(target.primary_float_at_actor_offset_0x3BC==8.f);
 puts("PASS G111 EXACT original 2010 EntityData imported strcasecmp+memcpy typed getter, Actor::CanAttack native categories 0/2/3/4, melee+0x824 native state, real G82 CONTACT DAMAGE engine fail closed on unproven source, old source damage duplicates safe. Synthetic fixture is NOT original 2010 Attack damage. NO VPK.");
 return 0;
}
