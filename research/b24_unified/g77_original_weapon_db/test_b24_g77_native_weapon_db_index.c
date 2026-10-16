#include "b24_g77_native_weapon_db_index.h"
#include <assert.h>
#include <stddef.h>
#include <stdio.h>
int main(void) {
 const int a=10,b=20,c=30;
 const void *const entries[]={&a,&b,&c};
 B24G77NativeAttackArray db={entries,3};
 assert(b24_g77_native_attack_at(&db,0)==&a);
 assert(b24_g77_native_attack_at(&db,1)==&b);
 assert(b24_g77_native_attack_at(&db,2)==&c);
 assert(b24_g77_native_attack_at(&db,-1)==NULL);
 assert(b24_g77_native_attack_at(&db,3)==NULL);
 assert(b24_g77_native_attack_at(&db,1000)==NULL);
 db.source_attack_count=0;
 assert(b24_g77_native_attack_at(&db,0)==NULL);
 assert(b24_g77_native_attack_at(NULL,0)==NULL);
 puts("PASS G77 original 2010 WeaponDB::GetAttackEntityByIndex range-guard/array index, no invented attack stats or VPK");
 return 0;
}
