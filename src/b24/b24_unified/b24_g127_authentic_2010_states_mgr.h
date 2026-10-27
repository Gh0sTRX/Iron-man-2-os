#ifndef B24_G127_AUTHENTIC_2010_STATES_MGR_H
#define B24_G127_AUTHENTIC_2010_STATES_MGR_H
#include "b24_g124_real_original_NPC_source_state.h"
#include <stdint.h>
#include <stddef.h>
/* original iOS 2010 StatesMgr::GetState(int) 0x9F910:
 * if arg<0 return SourceMgr+0x0C (current/last-state pointer)
 * else source group at SourceMgr+0x8[last_group_index(+0x14)]
 * if last_group_index<0 return null;
 * if requested >= SourceGroup+0x2AC count return SourceMgr+0x0C
 * else return SourceGroup+0x2B0[index].
 * logical portable C structs; original iOS was 32-bit ARM, this is
 * NOT a layout-compatible reinterpretation of original 32-bit memory.
 */
typedef struct {
 uint32_t actual_original_node_class_verified;
 int32_t source_state_type_at_original_offset_0xc;
} B24G127OriginalStateNode;
typedef struct {
 const B24G127OriginalStateNode *const *source_pointer_array_0x2b0;
 int32_t original_state_count_0x2ac;
 uint32_t authentic_original_state_values_verified;
} B24G127OriginalStateGroup;
typedef struct {
 const B24G127OriginalStateNode *original_current_state_pointer_0xc;
 const B24G127OriginalStateGroup *const *source_group_vector_0x8;
 uint32_t source_group_vector_length_for_bounds;
 int32_t current_group_index_0x14;
 uint32_t source_2010_state_graph_fully_loaded_and_verified;
} B24G127OriginalStatesMgr;
const B24G127OriginalStateNode *b24_g127_native_get_state(
 const B24G127OriginalStatesMgr *mgr,int32_t index);
B24G124Bool b24_g127_native_CNPC_is_attack_state_from_original_manager(
 const B24G127OriginalStatesMgr *mgr);
#endif
