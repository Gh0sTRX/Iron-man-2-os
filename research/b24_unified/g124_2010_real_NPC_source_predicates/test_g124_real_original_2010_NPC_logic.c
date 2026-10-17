#include "b24_g124_real_original_NPC_source_state.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 assert(b24_g124_source_npc_is_attack_state(0,4)==B24_G124_UNKNOWN);
 for(int i=-4;i<20;i++)
  assert(b24_g124_source_npc_is_attack_state(1,i)==
   ((i==4||i==5)?B24_G124_TRUE:B24_G124_FALSE));
 assert(b24_g124_source_npc_base_is_melee()==B24_G124_FALSE);
 B24G124NativeNPC npc={0};
 npc.current_priority_0x680=3;
 assert(!b24_g124_source_npc_set_priority(&npc,9,2));
 assert(npc.current_state_0x684==0&&npc.current_priority_0x680==3);
 assert(b24_g124_source_npc_set_priority(&npc,11,3));
 assert(npc.current_state_0x684==11);
 assert(b24_g124_source_npc_set_priority(&npc,12,5));
 assert(npc.current_priority_0x680==5&&npc.current_state_0x684==12);
 assert(!b24_g124_source_npc_set_priority(&npc,13,4));
 npc.last_shot_time_0x6dc=105;npc.interval_0x56c=250;
 npc.native_shoot_times_verified=1;
 assert(b24_g124_source_npc_fire_cooldown(&npc,354,1)==B24_G124_FALSE);
 assert(b24_g124_source_npc_fire_cooldown(&npc,355,1)==B24_G124_TRUE);
 assert(b24_g124_source_npc_fire_cooldown(&npc,400,0)==B24_G124_UNKNOWN);
 npc.last_shot_time_0x6dc=INT32_MAX-5;
 assert(b24_g124_source_npc_fire_cooldown(&npc,INT32_MIN+244,1)==B24_G124_TRUE);
 B24G124NativeKillMission m={0};
 assert(b24_g124_source_kill_mission_early_branch(&m)==B24_G124_UNKNOWN);
 m.actor_count_from_native_plus0x6c_verified=1;
 m.original_source_owned_actor_count=3;
 assert(b24_g124_source_kill_mission_early_branch(&m)==B24_G124_UNKNOWN);
 assert(!m.cached_complete_plus0x50);
 m.original_source_owned_actor_count=0;
 assert(b24_g124_source_kill_mission_early_branch(&m)==B24_G124_TRUE);
 assert(m.cached_complete_plus0x50);
 m.original_source_owned_actor_count=4;
 assert(b24_g124_source_kill_mission_early_branch(&m)==B24_G124_TRUE);
 B24G124Sky sky={0};
 assert(b24_g124_source_gameplay_sky_update_gate(&sky)==B24_G124_UNKNOWN);
 sky.native_global_game_renderer_found=1;
 assert(b24_g124_source_gameplay_sky_update_gate(&sky)==B24_G124_FALSE);
 sky.renderer_mode_0x554=1;
 assert(b24_g124_source_gameplay_sky_update_gate(&sky)==B24_G124_FALSE);
 sky.original_scene_sky_node_0x10_loaded=1;
 assert(b24_g124_source_gameplay_sky_update_gate(&sky)==B24_G124_TRUE);
 puts("PASS G124 original 2010 ARM real NPC attack enum 4,5 / signed SetState priority / 32-bit cooldown fields / base melee false / mission zero-owned actor early-exit / sky render mode original gate; NO VPK.");
 return 0;
}
