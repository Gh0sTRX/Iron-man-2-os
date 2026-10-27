#include "b24_g127_authentic_2010_states_mgr.h"
const B24G127OriginalStateNode *b24_g127_native_get_state(
 const B24G127OriginalStatesMgr *m,int32_t index){
 if(!m||!m->source_2010_state_graph_fully_loaded_and_verified)
  return NULL;
 /* Original 0x9F910 cmp r1,#0 ; bge 0x9F920;
  * ldr r0,[r0,#0x0C] ; bx lr. Negative ANY (not just -1). */
 if(index<0)return m->original_current_state_pointer_0xc;
 /* Original 0x9F920 ldr r3,[r0,#0x14]; cmp r3,#0;
  * movlt r0,#0 ; bxlt lr. */
 if(m->current_group_index_0x14<0)return NULL;
 const uint32_t k=(uint32_t)m->current_group_index_0x14;
 if(k>=m->source_group_vector_length_for_bounds||
    !m->source_group_vector_0x8)return NULL;
 const B24G127OriginalStateGroup *group=m->source_group_vector_0x8[k];
 if(!group||!group->authentic_original_state_values_verified)return NULL;
 /* 0x9F938 load SourceGroup+0x2AC count, signed CMP r1,r2:
  * if index >= count -> 0x9F918 fallback to current at +0x0C.
  */
 if(index>=group->original_state_count_0x2ac)
  return m->original_current_state_pointer_0xc;
 if(!group->source_pointer_array_0x2b0)return NULL;
 return group->source_pointer_array_0x2b0[index];
}
B24G124Bool b24_g127_native_CNPC_is_attack_state_from_original_manager(
 const B24G127OriginalStatesMgr *m){
 /* Original CNPC::isAttackState 0xE1A20 passes -1 to StatesMgr::GetState.
  * Then loads StateNode+0x0C and compares 4/5. */
 const B24G127OriginalStateNode *s=b24_g127_native_get_state(m,-1);
 if(!s||!s->actual_original_node_class_verified)return B24_G124_UNKNOWN;
 return b24_g124_source_npc_is_attack_state(
  1,s->source_state_type_at_original_offset_0xc);
}
