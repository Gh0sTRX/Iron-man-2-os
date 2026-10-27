#include "b24_g103_verified_original_actor_attack_classification.h"
/* Original native ARM 0xD9278, source from G97 complete disassembly:
 * [r0,+0x2b8] attacker typed integer.
 * If it equals 0:
 *   target+0x2b8==3 => return 1;
 *   target+0x2b8==2 => return 0;
 *   target+0x2b8==4 => target vtable+0x17C (UNKNOWN without target);
 *   otherwise return 1.
 * If attacker typed integer!=0:
 *   !=1 => return0;
 *   ==1 => match original allow-list [r0,+0x158] count +0x160;
 *      fallback target vtable when not matched, UNKNOWN without list.
 * This is a SOURCE verified subset, NOT entire original combat permission.
 */
B24G103AttackPermission b24_g103_can_attack_proven_native_classes(
 int32_t attacker,int32_t target) {
 if(attacker==0) {
  if(target==2)return B24_G103_ORIGINAL_PERMISSION_DENIED;
  if(target==4)return B24_G103_ORIGINAL_PERMISSION_UNKNOWN;
  return B24_G103_ORIGINAL_PERMISSION_ALLOWED;
 }
 if(attacker!=1)return B24_G103_ORIGINAL_PERMISSION_DENIED;
 return B24_G103_ORIGINAL_PERMISSION_UNKNOWN;
}
