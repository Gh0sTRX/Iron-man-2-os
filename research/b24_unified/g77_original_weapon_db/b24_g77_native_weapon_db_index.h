#ifndef B24_G77_NATIVE_WEAPON_DB_INDEX_H
#define B24_G77_NATIVE_WEAPON_DB_INDEX_H
/* iOS 2010 real ARM method WeaponDB::GetAttackEntityByIndex(int),
 * instructions at 0xAB3EC. Original ARM ABI has array pointer at +0x30
 * and count at +0x38. This PORTABLE HOST reference intentionally
 * does not reinterpret 32-bit iOS object offsets as 64-bit C struct ABI.
 * No original attack damage/weapon table objects available yet. */
typedef struct {
 const void *const *source_attack_entries;
 int source_attack_count;
} B24G77NativeAttackArray;
/* Reconstructed original ARM conditional array indexing semantics only. */
const void *b24_g77_native_attack_at(const B24G77NativeAttackArray *db,int index);
#endif
