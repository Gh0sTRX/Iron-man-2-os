#ifndef B24_G124_REAL_ORIGINAL_NPC_SOURCE_STATE_H
#define B24_G124_REAL_ORIGINAL_NPC_SOURCE_STATE_H
#include <stdint.h>
/* iOS owner G123 native ARM:
  CNPC::isAttackState 0xE1A20 => last state node +0x0C in {4,5}.
  CNPC::SetState 0xE1694 => original signed priority +0x680
     <= incoming r2, then store state r1 at +0x684 and new priority.
  CNPC::shootFrequencyDone 0xE19E0 => 32-bit clock BL 0x54D84,
     signed(now-[CNPC+0x6DC]) >= [CNPC+0x56C].
  CNPC::isMelee 0xEA220 BASE returns 0; derived may override.
  MissionConditionKill::EvaluateComplete 0xCB5B8 cached+0x50
     or owned-list+0x6C count<=0 => success; full virtual actor
     checks NOT yet ported.
  GS_GamePlay::UpdateSkyBox 0xC2810 renderer global +0x554==1
     and loaded scene node +0x10 required before sky transform.
*/
typedef enum {B24_G124_UNKNOWN=0,B24_G124_FALSE=1,B24_G124_TRUE=2} B24G124Bool;
typedef struct {
 int32_t current_priority_0x680,current_state_0x684;
 int32_t last_shot_time_0x6dc,interval_0x56c;
 int native_shoot_times_verified;
} B24G124NativeNPC;
B24G124Bool b24_g124_source_npc_is_attack_state(int state_node_verified,int32_t state_type_plus0xc);
B24G124Bool b24_g124_source_npc_base_is_melee(void);
int b24_g124_source_npc_set_priority(B24G124NativeNPC *,int32_t state,int32_t priority);
B24G124Bool b24_g124_source_npc_fire_cooldown(const B24G124NativeNPC *,int32_t native_now,int native_clock_verified);
typedef struct {
 uint8_t cached_complete_plus0x50;
 int32_t original_source_owned_actor_count;
 int actor_count_from_native_plus0x6c_verified;
} B24G124NativeKillMission;
B24G124Bool b24_g124_source_kill_mission_early_branch(B24G124NativeKillMission *);
typedef struct {
 int native_global_game_renderer_found;
 int32_t renderer_mode_0x554;
 int original_scene_sky_node_0x10_loaded;
} B24G124Sky;
B24G124Bool b24_g124_source_gameplay_sky_update_gate(const B24G124Sky *);
#endif
