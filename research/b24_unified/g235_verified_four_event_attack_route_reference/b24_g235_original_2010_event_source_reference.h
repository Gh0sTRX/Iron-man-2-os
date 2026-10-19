/* G235: source-only 2010 iOS DoAttack event callsite metadata.
 * Proven by original ARM 0xF6A30 native r8[0..3] (outer AttackType 0
 * directly, AttackType 1/18 via conditional paths),
 * G233 real MachO C++ symbols, G234 exact 2010 immediate arg writes.
 * This is NOT a new Vita weapon/animation/touch input controller:
 * name-based G218 clip->state match is NOT actual 2010 live state proof.
 * Never generate damage, bullets, missiles or effects with this header.
 */
#ifndef B24_G235_SOURCE_EVENT_ROUTE_REFERENCE_H
#define B24_G235_SOURCE_EVENT_ROUTE_REFERENCE_H
#include <stdint.h>
#include "../g197_source2010_attack_dispatch/b24_g197_original_2010_attack_dispatch_reference.h"
typedef enum {
  B24_G235_UNKNOWN=0,
  B24_G235_ORIGINAL_GETWEAPON_SLOT0_DB_ATTACK0=1,
  B24_G235_ORIGINAL_GETASSISTANT_SLOT0_DB_ATTACK1=2,
  B24_G235_ORIGINAL_UNIBEAM_CHEST_GROUP14=3,
  B24_G235_ORIGINAL_UNIBEAM_FOOTL_GROUP33=4
} B24G235OriginalSourcePath;
typedef struct {
  B24G235OriginalSourcePath candidate_source_path;
  uint32_t source_native_ARM_event_branch_start;
  uint32_t original_get_weapon_or_assistant_Cpp_VM;
  uint32_t original_weapon_db_attack_index_or_UNKNOWN;
  uint32_t original_unibeam_actor_dummy_group_or_ZERO;
  uint8_t original_ARM_source_proven;
  uint8_t original_runtime_selected_state_proven;
  uint8_t original_controller_or_gameplay_effect_proven;
} B24G235EventReference;
static inline B24G235EventReference b24_g235_original_source_event(
    uint32_t original_AttackType,uint32_t original_event_third_u32) {
 B24G235EventReference a={0};
 /* Outer source index 0 directly selects 0xF6A30. Native selectors 1/18
  * share 0xF6930 and may reach this secondary switch conditionally.
  * Other AttackType values must not use this 4-way source map.
  * No assertion that this StateData is currently SELECTED in Vita. */
 const uint32_t upper=b24_g197_original_source_attack_entry(original_AttackType)
     .original_ARM_branch_target_VM;
 if(upper!=0xF6A30u && upper!=0xF6930u)return a;
 switch(original_event_third_u32){
 case 0u:
   a.candidate_source_path=B24_G235_ORIGINAL_GETWEAPON_SLOT0_DB_ATTACK0;
   a.source_native_ARM_event_branch_start=0xF6C60u;
   a.original_get_weapon_or_assistant_Cpp_VM=0xB1F14u;
   a.original_weapon_db_attack_index_or_UNKNOWN=0u;
   break;
 case 1u:
   a.candidate_source_path=B24_G235_ORIGINAL_GETASSISTANT_SLOT0_DB_ATTACK1;
   a.source_native_ARM_event_branch_start=0xF6CE0u;
   a.original_get_weapon_or_assistant_Cpp_VM=0xB1D2Cu;
   a.original_weapon_db_attack_index_or_UNKNOWN=1u;
   break;
 case 2u:
   a.candidate_source_path=B24_G235_ORIGINAL_UNIBEAM_CHEST_GROUP14;
   a.source_native_ARM_event_branch_start=0xF6D58u;
   a.original_weapon_db_attack_index_or_UNKNOWN=UINT32_MAX;
   a.original_unibeam_actor_dummy_group_or_ZERO=14u;
   break;
 case 3u:
   a.candidate_source_path=B24_G235_ORIGINAL_UNIBEAM_FOOTL_GROUP33;
   a.source_native_ARM_event_branch_start=0xF6D98u;
   a.original_weapon_db_attack_index_or_UNKNOWN=UINT32_MAX;
   a.original_unibeam_actor_dummy_group_or_ZERO=33u;
   break;
 default:return a;
 }
 a.original_ARM_source_proven=1u;
 /* Do NOT change either flag until the original 2010 native branch
  * predicates & actual iOS state/control/weapon runtime are validated. */
 a.original_runtime_selected_state_proven=0u;
 a.original_controller_or_gameplay_effect_proven=0u;
 return a;
}
#endif
