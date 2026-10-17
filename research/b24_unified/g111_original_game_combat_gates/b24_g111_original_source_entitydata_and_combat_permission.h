#ifndef B24_G111_ORIGINAL_SOURCE_ENTITYDATA_COMBAT_PERMISSION_H
#define B24_G111_ORIGINAL_SOURCE_ENTITYDATA_COMBAT_PERMISSION_H
#include <stdint.h>
#include <stddef.h>
/* Original 2010 ARM EntityData::GetParamValue(char const*, int*) 0xD7548
 * and bool* 0xD76BC from user-owned MachO, G109/G110:
 * this+0x20 -> descriptor count(+0x0C) and stride-12 property names(+0x10)
 * this+0x1C -> matching payload pointer+length stride-8 values
 * original runtime strcasecmp imported at 0x47111C; copied payload with
 * original memcpy imported at 0x470E88. This is the portable SAFE logical
 * equivalent, NOT literal 2010 VM memory layout on 64-bit host.
 * Does not guess which 54 CLARA slot corresponds to the Damage property.
 */
typedef struct {
 const char *native_param_name;
 const void *original_typed_serialized_bytes;
 uint32_t original_native_length_bytes;
} B24G111OriginalProperty;
typedef struct {
 const B24G111OriginalProperty *entries;
 size_t count;
 int names_from_original_class_schema_verified;
 int values_from_original_typed_entitydata_verified;
} B24G111OriginalEntityData;
int b24_g111_native_original_get_int(const B24G111OriginalEntityData *data,
 const char *source_property,int32_t *out_value);
int b24_g111_native_original_get_bool(const B24G111OriginalEntityData *data,
 const char *source_property,uint8_t *out_value);
/* These 3 original properties are INDEPENDENT gates. We require their
 * original source provenance, NOT an unverified guess based on clip name.
 * Original actor+0x2B8 categories and MainCharacter+0x824 states were
 * disassembled in G103 and G89. Unknown original dynamic vtable must DENY.
 */
int b24_g111_native_source_attack_permission_and_damage(
 const B24G111OriginalEntityData *real_entitydata,
 int original_actor_fields_verified,
 int32_t original_attacker_type_0x2b8,
 int32_t original_target_type_0x2b8,
 int original_melee_state_field_0x824_verified,
 uint32_t original_melee_state_0x824,
 int32_t *out_original_damage);
#endif
