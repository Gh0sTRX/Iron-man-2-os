#ifndef B24_G89_REAL_2010_MELEE_STATE_PREDICATES_H
#define B24_G89_REAL_2010_MELEE_STATE_PREDICATES_H
#include <stdint.h>
/* Strict 2010 iOS native ARM source-derived state field predicates.
 * Exact native bytes are NOT shipped. No real hit windows or damage values.
 * MainCharacter::native slots this+0x824 and this+0x828.
 * Implement only the proven read-only predicates / reset semantics.
 * NOT a fully decoded 13-attack combo, NO gameplay owner or VPK. */
typedef struct {
 uint32_t field_at_original_offset_0x824;
 uint32_t field_at_original_offset_0x828;
} B24G89NativeMeleeSlots;
int b24_g89_is_melee_attack_state(uint32_t original_state);
int b24_g89_is_melee_attack_end_state(uint32_t original_state);
int b24_g89_is_melee_attack_slide_state(uint32_t original_state);
void b24_g89_reset_native_state_slots(B24G89NativeMeleeSlots *slots);
#endif
