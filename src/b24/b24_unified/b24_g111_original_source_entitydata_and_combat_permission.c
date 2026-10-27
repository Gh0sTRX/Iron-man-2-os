#include "b24_g111_original_source_entitydata_and_combat_permission.h"
#include "b24_g103_verified_original_actor_attack_classification.h"
#include "b24_g89_real_2010_melee_state_predicates.h"
#include <string.h>
/* Original strcasecmp is an imported iOS runtime function from user iOS
 * native BL 0x47111C; implement strict ASCII property namespace here for
 * cross-platform Vita libc/host, no locale-dependent properties invented. */
static unsigned fold(unsigned ch){return ch>='A'&&ch<='Z'?ch+('a'-'A'):ch;}
static int key_equal(const char *a,const char *b){
 if(!a||!b)return 0;
 for(size_t k=0;k<128;k++){
  const unsigned aa=(unsigned char)a[k],bb=(unsigned char)b[k];
  if(fold(aa)!=fold(bb))return 0;
  if(!aa)return 1;
 }
 return 0;
}
static const B24G111OriginalProperty *find(
 const B24G111OriginalEntityData *d,const char *name){
 if(!d||!d->names_from_original_class_schema_verified||
    !d->values_from_original_typed_entitydata_verified||
    !d->entries||!name||d->count>1024u)return NULL;
 for(size_t i=0;i<d->count;i++){
  const B24G111OriginalProperty *p=&d->entries[i];
  if(key_equal(p->native_param_name,name))return p;
 }
 return NULL;
}
int b24_g111_native_original_get_int(const B24G111OriginalEntityData *d,
 const char *name,int32_t *out){
 if(!out)return 0;
 const B24G111OriginalProperty *v=find(d,name);
 if(!v||!v->original_typed_serialized_bytes||
    v->original_native_length_bytes!=4u)return 0;
 memcpy(out,v->original_typed_serialized_bytes,4u);
 return 1;
}
int b24_g111_native_original_get_bool(const B24G111OriginalEntityData *d,
 const char *name,uint8_t *out){
 if(!out)return 0;
 const B24G111OriginalProperty *v=find(d,name);
 if(!v||!v->original_typed_serialized_bytes||
    v->original_native_length_bytes!=1u)return 0;
 /* Native source preserves stored bool byte; do not invent !=0 mapping. */
 memcpy(out,v->original_typed_serialized_bytes,1u);
 return 1;
}
int b24_g111_native_source_attack_permission_and_damage(
 const B24G111OriginalEntityData *entity,
 int actors_proven,int32_t attacker,int32_t target,
 int native_melee_state_proven,uint32_t melee,int32_t *damage){
 if(!actors_proven||!native_melee_state_proven||!damage)return 0;
 if(b24_g103_can_attack_proven_native_classes(attacker,target)!=
      B24_G103_ORIGINAL_PERMISSION_ALLOWED)return 0;
 if(!b24_g89_is_melee_attack_state(melee))return 0;
 int32_t temp=0;
 if(!b24_g111_native_original_get_int(entity,"Damage",&temp)||temp<=0)return 0;
 *damage=temp;
 return 1;
}
