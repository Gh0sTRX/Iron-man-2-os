#include "b24_g77_native_weapon_db_index.h"
#include <stddef.h>
const void *b24_g77_native_attack_at(const B24G77NativeAttackArray *db,int index) {
 if(!db || index<0 || index>=db->source_attack_count
    || !db->source_attack_entries)return NULL;
 return db->source_attack_entries[index];
}
