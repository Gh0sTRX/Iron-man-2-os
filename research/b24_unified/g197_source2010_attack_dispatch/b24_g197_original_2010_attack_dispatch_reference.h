#ifndef B24_G197_ORIGINAL_2010_ATTACK_DISPATCH_REFERENCE_H
#define B24_G197_ORIGINAL_2010_ATTACK_DISPATCH_REFERENCE_H
/* Source-authenticated ORIGINAL iOS Iron Man 2 (2010) ARM
 * MainCharacter::DoAttack(int,int) at 0x000F64F8:
 * 0xF6524 CMP r5,#25
 * 0xF6528 ADDLS pc,pc,r5,LSL #2
 * Out of range executes default B @ 0xF652C -> 0xF6598.
 * 26 native ARM B entries 0xF6530..0xF6594, one per index.
 *
 * THIS TABLE IS READ-ONLY SOURCE REFERENCE, NOT A NEW VITA WEAPON INPUT
 * ROUTER. Attack ID->weapon/animation/damage semantics NOT PROVEN.
 * In particular these IDs DO NOT equal WeaponDB attack index 4.
 */
#include <stdint.h>
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
enum {B24_G197_ORIGINAL_DOATTACK_SOURCE_ENTRIES=26};
typedef struct {
  uint32_t original_attack_selector_index;
  uint32_t original_ARM_jump_table_entry_VM;
  uint32_t original_ARM_branch_target_VM;
} B24G197OriginalAttackEntry;
static const uint32_t b24_g197_original_2010_source_destinations[26]={
  0x000F6A30u, /*  0: non-default original branch */
  0x000F6930u, /*  1 */
  0x000F6648u, /*  2 */
  0x000F6598u, /*  3: common default */
  0x000F65C4u, /*  4 */
  0x000F6598u, /*  5 */
  0x000F6598u, /*  6 */
  0x000F6598u, /*  7 */
  0x000F6598u, /*  8 */
  0x000F6598u, /*  9 */
  0x000F6598u, /* 10 */
  0x000F6598u, /* 11 */
  0x000F6648u, /* 12 */
  0x000F6598u, /* 13 */
  0x000F6598u, /* 14 */
  0x000F6598u, /* 15 */
  0x000F6598u, /* 16 */
  0x000F6598u, /* 17 */
  0x000F6930u, /* 18 */
  0x000F6598u, /* 19 */
  0x000F6598u, /* 20 */
  0x000F6598u, /* 21 */
  0x000F6598u, /* 22 */
  0x000F6598u, /* 23 */
  0x000F6598u, /* 24 */
  0x000F6648u  /* 25 */
};
static inline B24G197OriginalAttackEntry
b24_g197_original_source_attack_entry(uint32_t native_input_index){
  B24G197OriginalAttackEntry r;
  r.original_attack_selector_index=native_input_index;
  r.original_ARM_jump_table_entry_VM=native_input_index<26u?
      0x000F6530u+native_input_index*4u:0x000F652Cu;
  r.original_ARM_branch_target_VM=native_input_index<26u?
      b24_g197_original_2010_source_destinations[native_input_index]:0x000F6598u;
  return r;
}
/* Only the actual 2010 original compiled callsite VM IDs select
 * native Source SceneImpl group 14 Dummy_Chest or 33 Dummy_Foot_L.
 * Return 0 for any input that is not one of those ORIGINAL VM sites;
 * never guess a live Vita weapon event from an unknown input.
 */
static inline uint32_t
b24_g197_original_source_unibeam_dummy_group_by_native_ARM_call_VM(uint32_t vm){
  switch(vm){
    case 0x000F6638u: return 14u;
    case 0x000F6D8Cu: return 14u;
    case 0x000F6E04u: return 33u;
    default: return 0u;
  }
}
static inline const char *
b24_g197_original_source_scene_group_name(uint32_t group){
  switch(group){
    case 14u:return "Dummy_Chest";
    case 33u:return "Dummy_Foot_L";
    default:return NULL;
  }
}
#ifdef __cplusplus
}
#endif
#endif
