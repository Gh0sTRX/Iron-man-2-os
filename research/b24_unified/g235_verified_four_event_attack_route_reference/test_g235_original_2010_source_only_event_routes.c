#include "b24_g235_original_2010_event_source_reference.h"
#include <assert.h>
#include <stdio.h>
#include <stdint.h>
int main(void){
 const uint32_t types[]={0u,1u,18u};
 const B24G235OriginalSourcePath p[]={
  B24_G235_ORIGINAL_GETWEAPON_SLOT0_DB_ATTACK0,
  B24_G235_ORIGINAL_GETASSISTANT_SLOT0_DB_ATTACK1,
  B24_G235_ORIGINAL_UNIBEAM_CHEST_GROUP14,
  B24_G235_ORIGINAL_UNIBEAM_FOOTL_GROUP33,
 };
 const uint32_t branch[]={0xF6C60u,0xF6CE0u,0xF6D58u,0xF6D98u};
 for(unsigned i=0;i<sizeof(types)/sizeof(types[0]);++i){
  for(uint32_t event=0u;event<4u;++event){
   B24G235EventReference ref=b24_g235_original_source_event(types[i],event);
   assert(ref.candidate_source_path==p[event]);
   assert(ref.source_native_ARM_event_branch_start==branch[event]);
   assert(ref.original_ARM_source_proven);
   assert(!ref.original_runtime_selected_state_proven);
   assert(!ref.original_controller_or_gameplay_effect_proven);
   if(event==0u){
    assert(ref.original_get_weapon_or_assistant_Cpp_VM==0xB1F14u);
    assert(ref.original_weapon_db_attack_index_or_UNKNOWN==0u);
   }
   if(event==1u){
    assert(ref.original_get_weapon_or_assistant_Cpp_VM==0xB1D2Cu);
    assert(ref.original_weapon_db_attack_index_or_UNKNOWN==1u);
   }
   if(event>=2u){
    assert(!ref.original_get_weapon_or_assistant_Cpp_VM);
    assert(ref.original_weapon_db_attack_index_or_UNKNOWN==UINT32_MAX);
    assert(ref.original_unibeam_actor_dummy_group_or_ZERO==(event==2u?14u:33u));
   }
  }
 }
 /* 25 is WM Attack_M source state ID: it routes to a DIFFERENT native
  * branch and must NOT fabricate four-way event/UniBeam equivalence. */
 for(uint32_t type=0;type<=26u;++type){
  if(type==0u||type==1u||type==18u)continue;
  for(uint32_t event=0;event<5u;++event){
   B24G235EventReference ref=b24_g235_original_source_event(type,event);
   assert(ref.candidate_source_path==B24_G235_UNKNOWN);
   assert(!ref.original_ARM_source_proven);
   assert(!ref.original_controller_or_gameplay_effect_proven);
  }
 }
 for(uint32_t type=0;type<=18u;type+=9u){
  B24G235EventReference bad=b24_g235_original_source_event(type,4u);
  assert(bad.candidate_source_path==B24_G235_UNKNOWN);
 }
 puts("G235 PASS ORIGINAL 2010 source upper AttackType 0/1/18 and true 0..3 event selector metadata; WM25 remains UNKNOWN; 0 gameplay side effects; NO VPK");
 return 0;
}
