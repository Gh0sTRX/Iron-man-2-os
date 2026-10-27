#include "b24_g124_real_original_NPC_source_state.h"
B24G124Bool b24_g124_source_npc_is_attack_state(int verified,int32_t s){
 if(!verified)return B24_G124_UNKNOWN;
 return (s==4||s==5)?B24_G124_TRUE:B24_G124_FALSE;
}
B24G124Bool b24_g124_source_npc_base_is_melee(void){
 return B24_G124_FALSE; /* original CNPC base 0xEA220 mov r0,#0 */
}
int b24_g124_source_npc_set_priority(B24G124NativeNPC *a,int32_t state,int32_t p){
 if(!a||a->current_priority_0x680>p)return 0;
 a->current_state_0x684=state;
 a->current_priority_0x680=p;
 return 1;
}
B24G124Bool b24_g124_source_npc_fire_cooldown(
 const B24G124NativeNPC *a,int32_t now,int clock_verified){
 if(!a||!clock_verified||!a->native_shoot_times_verified)return B24_G124_UNKNOWN;
 /* Owner 2010 ARM rsb modulo32, then signed cmp, not a naive millis
  * float approximation; defined portable wrapping equivalence. */
 const uint32_t delta=(uint32_t)now-(uint32_t)a->last_shot_time_0x6dc;
 const int32_t d=delta<=INT32_MAX?(int32_t)delta:
                 (int32_t)(delta-0x80000000u)+INT32_MIN;
 return d>=a->interval_0x56c?B24_G124_TRUE:B24_G124_FALSE;
}
B24G124Bool b24_g124_source_kill_mission_early_branch(B24G124NativeKillMission *m){
 if(!m)return B24_G124_UNKNOWN;
 if(m->cached_complete_plus0x50)return B24_G124_TRUE;
 if(!m->actor_count_from_native_plus0x6c_verified)return B24_G124_UNKNOWN;
 if(m->original_source_owned_actor_count<=0){
  m->cached_complete_plus0x50=1;return B24_G124_TRUE;
 }
 /* Nonempty list requires native virtual Actor status semantics. */
 return B24_G124_UNKNOWN;
}
B24G124Bool b24_g124_source_gameplay_sky_update_gate(const B24G124Sky *s){
 if(!s||!s->native_global_game_renderer_found)return B24_G124_UNKNOWN;
 if(s->renderer_mode_0x554!=1)return B24_G124_FALSE;
 return s->original_scene_sky_node_0x10_loaded?B24_G124_TRUE:B24_G124_FALSE;
}
