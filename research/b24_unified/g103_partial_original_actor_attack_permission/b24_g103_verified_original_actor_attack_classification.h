#ifndef B24_G103_VERIFIED_2010_ACTOR_ATTACK_CLASSIFICATION_H
#define B24_G103_VERIFIED_2010_ACTOR_ATTACK_CLASSIFICATION_H
#include <stdint.h>
/* Original source 2010 Actor::CanAttack(Actor*) native ARM 0xD9278.
 * Data members actor+0x2B8 (both actors), 0x158/0x160 original allow-list,
 * target virtual dispatch if attacker type 0 vs target type 4.
 * Do not invent that 'type 0' is Iron Man or a missile target!
 * Partial native proven cases only. Unknown MUST fail-closed in G82.
 */
typedef enum {
 B24_G103_ORIGINAL_PERMISSION_UNKNOWN=-1,
 B24_G103_ORIGINAL_PERMISSION_DENIED=0,
 B24_G103_ORIGINAL_PERMISSION_ALLOWED=1
} B24G103AttackPermission;
B24G103AttackPermission b24_g103_can_attack_proven_native_classes(
 int32_t original_attacker_field_0x2b8,
 int32_t original_target_field_0x2b8);
#endif
