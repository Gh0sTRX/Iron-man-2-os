#include "b24_g127_authentic_2010_states_mgr.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 B24G127OriginalStateNode n4={1,4},n5={1,5},n3={1,3},nv={0,4};
 const B24G127OriginalStateNode *items[]={&n4,&n5,&n3};
 B24G127OriginalStateGroup group={items,3,1};
 const B24G127OriginalStateGroup *groups[]={&group};
 B24G127OriginalStatesMgr mgr={&n4,groups,1,0,1};
 assert(b24_g127_native_get_state(&mgr,-1)==&n4);
 assert(b24_g127_native_get_state(&mgr,-9)==&n4);
 assert(b24_g127_native_get_state(&mgr,0)==&n4);
 assert(b24_g127_native_get_state(&mgr,1)==&n5);
 assert(b24_g127_native_get_state(&mgr,2)==&n3);
 assert(b24_g127_native_get_state(&mgr,3)==&n4);
 assert(b24_g127_native_get_state(&mgr,100)==&n4);
 assert(b24_g127_native_CNPC_is_attack_state_from_original_manager(&mgr)==B24_G124_TRUE);
 mgr.original_current_state_pointer_0xc=&n5;
 assert(b24_g127_native_CNPC_is_attack_state_from_original_manager(&mgr)==B24_G124_TRUE);
 mgr.original_current_state_pointer_0xc=&n3;
 assert(b24_g127_native_CNPC_is_attack_state_from_original_manager(&mgr)==B24_G124_FALSE);
 mgr.original_current_state_pointer_0xc=&nv;
 assert(b24_g127_native_CNPC_is_attack_state_from_original_manager(&mgr)==B24_G124_UNKNOWN);
 mgr.original_current_state_pointer_0xc=&n4;
 mgr.current_group_index_0x14=-1;
 assert(b24_g127_native_get_state(&mgr,0)==NULL);
 assert(b24_g127_native_get_state(&mgr,-1)==&n4);
 mgr.current_group_index_0x14=2;
 assert(b24_g127_native_get_state(&mgr,0)==NULL);
 mgr.current_group_index_0x14=0;
 group.authentic_original_state_values_verified=0;
 assert(b24_g127_native_get_state(&mgr,0)==NULL);
 group.authentic_original_state_values_verified=1;
 mgr.source_2010_state_graph_fully_loaded_and_verified=0;
 assert(b24_g127_native_get_state(&mgr,-1)==NULL);
 assert(b24_g127_native_CNPC_is_attack_state_from_original_manager(&mgr)==B24_G124_UNKNOWN);
 puts("G127 PASS genuine source 2010 StatesMgr::GetState(-1) current state, nonnegative indexed 0x2AC/0x2B0, -1 group sentinel, index overflow fallback, actor CNPC isAttackState 4/5 chained actual logical source, no fake live actor, NO VPK");
 return 0;
}
