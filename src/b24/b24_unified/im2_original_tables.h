#ifndef IM2_ORIGINAL_TABLES_H
#define IM2_ORIGINAL_TABLES_H
#include <stddef.h>
#include <stdint.h>
/* Interface only. Original StateData and Lua rows are external owner assets. */
#define B24G217_ARMOR_COUNT 4
#define B24G217_SOURCE_STATES_PER_ARMOR 194
#define B24G217_TRUE_SOURCE_ATTACK_TRAIL_EVENT_COUNT 224
#define B24G217_UNKNOWN_U32 UINT32_C(0xffffffff)
typedef struct B24G217_SourceState {
 const char *original_source_state_name;
 uint32_t original_AttackType_or_UNKNOWN,original_next_state_or_UNKNOWN;
 uint32_t original_state_type_or_UNKNOWN,original_loop_or_UNKNOWN;
 uint16_t native_source_state_index,original_state_track_count;
} B24G217_SourceState;
typedef struct B24G217_SourceEvent {
 const char *native_original_track_name;
 uint32_t raw_original_2010_start,raw_original_2010_duration;
 uint32_t raw_original_2010_third_field_UNCLASSIFIED;
 uint16_t native_suit_group_index,native_original_state_index;
} B24G217_SourceEvent;
extern const char *b24g217_original_suit_source_names[4];
extern B24G217_SourceState b24g217_true_2010_owner_states[4][194];
extern B24G217_SourceEvent b24g217_source_attack_trail_events[224];
int im2_original_tables_ready(void);
int im2_original_tables_load(const char *path);
int im2_original_tables_decode(const void *data,size_t size);
void im2_original_tables_close(void);
#endif
