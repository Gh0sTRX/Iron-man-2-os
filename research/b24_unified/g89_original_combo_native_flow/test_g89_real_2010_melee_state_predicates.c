/* Deterministic exact native ARM predicate truth table, NO VPK. */
#include "b24_g89_real_2010_melee_state_predicates.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
int main(void){
 for(uint32_t v=0u;v<32u;v++){
  assert(b24_g89_is_melee_attack_state(v)==(v>=2u&&v<=12u));
  assert(b24_g89_is_melee_attack_end_state(v)==(v>=9u&&v<=12u));
  assert(b24_g89_is_melee_attack_slide_state(v)==(v==1u));
 }
 const uint32_t odd[]={UINT32_MAX,UINT32_MAX-1u,65536u,0x80000000u};
 for(unsigned i=0;i<sizeof(odd)/sizeof(odd[0]);i++){
  assert(!b24_g89_is_melee_attack_state(odd[i]));
  assert(!b24_g89_is_melee_attack_end_state(odd[i]));
  assert(!b24_g89_is_melee_attack_slide_state(odd[i]));
 }
 B24G89NativeMeleeSlots slots={0xBu,0xCu};
 b24_g89_reset_native_state_slots(&slots);
 assert(!slots.field_at_original_offset_0x824);
 assert(!slots.field_at_original_offset_0x828);
 b24_g89_reset_native_state_slots(NULL);
 puts("PASS G89 AUTHENTIC 2010 ARM native source melee predicates: slide=1, attacking=2..12, ending=9..12, reset +0x824/+0x828=0. NO original hit frame/damage invented. NO VPK.");
 return 0;
}
