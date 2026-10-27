#include "b24_g89_real_2010_melee_state_predicates.h"
#include <stddef.h>
/* Original MainCharacter::IsInMeleeAttackState at 0xEA3C0:
 * ldr r1,[r0,#0x824]; sub r0,r1,#2; cmp r0,#0xA;
 * movhi r0,#0; movls r0,#1; bx lr.
 * ARM unsigned LS after subtraction => IDs exactly [2,12]. */
int b24_g89_is_melee_attack_state(uint32_t source){
 return (uint32_t)(source-2u)<=10u;
}
/* Original MainCharacter::IsInMeleeAttackEndState at 0xEA3D8:
 * ldr r1,[r0,#0x824]; sub r0,r1,#9; cmp r0,#3;
 * movhi r0,#0; movls r0,#1; bx lr => IDs [9,12]. */
int b24_g89_is_melee_attack_end_state(uint32_t source){
 return (uint32_t)(source-9u)<=3u;
}
/* MainCharacter::IsInMeleeAttackSlideState() const, native 0xFE09C:
 * ldr r0,[r0,#0x824]; cmp r0,#1; movne r0,#0; moveq r0,#1 */
int b24_g89_is_melee_attack_slide_state(uint32_t source){
 return source==1u;
}
/* MainCharacter::ResetMeleeAttackState native 0xEA518:
 * mov r3,#0; str r3,[r0,#0x824]; str r3,[r0,#0x828].
 * This is an isolated data reference, not an executed gameplay reset. */
void b24_g89_reset_native_state_slots(B24G89NativeMeleeSlots *slots){
 if(!slots)return;
 slots->field_at_original_offset_0x824=0u;
 slots->field_at_original_offset_0x828=0u;
}
