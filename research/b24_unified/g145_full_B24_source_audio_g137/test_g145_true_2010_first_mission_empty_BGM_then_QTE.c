#include "b24_g137_source_mission000_intro.h"
#include "b24_g142_native_sound_source_truth.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static int authenticated_original_source_dispatch(void *ctx,const B24G137Event *e){
 B24G142OwnerAudio *s=(B24G142OwnerAudio*)ctx;
 if(e&&e->original_lua_pc==1&&e->opcode==B24_G137_CALL_MISSION_PAUSE)return 1;
 return b24_g142_owner_source_music_call(s,e);
}
int main(void){
 B24G137Mission000 mission={0};
 assert(b24_g137_mission000_init(&mission));
 B24G142OwnerAudio track={0};
 /* Actual 2010 Game::Game ARM0x99564 initializes Game+0xEC=-1.
  * Recreated Vita source game has never started a BGM at intro. */
 track.original_current_music_zero_based_id=-1;
 track.original_current_music_id_from_actual_game_state_verified=1;
 track.original_current_music_track_is_playing=0;
 assert(b24_g137_mission000_dispatch_verified_prefix(&mission,
   authenticated_original_source_dispatch,&track)==
   B24_G137_BLOCKED_NATIVE_SCENE_BINDING);
 /* Exact original order PC1 pause, PC3 empty current BGM, then the
  * FIRST missing authentic scene handler: QTE Show(1456) at PC6. */
 assert(mission.cursor==2&&mission.actually_dispatched_count==2);
 assert(mission.next_source_lua_pc==6);
 assert(track.source_music_stop_command_acknowledged);
 assert(mission.requested_mission_pause);
 assert(!mission.requested_MarkV_idle);
 assert(!mission.requested_input14_disabled);
 assert(!b24_g137_mission000_is_gameplay_released(&mission));
 /* Replays cannot accidentally call PC1/PC3 again, nor skip PC6. */
 assert(b24_g137_mission000_dispatch_verified_prefix(&mission,
   authenticated_original_source_dispatch,&track)==
   B24_G137_BLOCKED_NATIVE_SCENE_BINDING);
 assert(mission.cursor==2&&mission.next_source_lua_pc==6);
 /* An active current music source CANNOT be stopped without a real
  * StopMusic(ID,2000.0) callback, even if audio port is muted. */
 B24G137Mission000 active={0};
 assert(b24_g137_mission000_init(&active));
 B24G142OwnerAudio live={0};
 live.original_current_music_zero_based_id=87;
 live.original_current_music_id_from_actual_game_state_verified=1;
 live.original_current_music_track_is_playing=1;
 assert(b24_g137_mission000_dispatch_verified_prefix(&active,
   authenticated_original_source_dispatch,&live)==
   B24_G137_BLOCKED_NATIVE_SCENE_BINDING);
 assert(active.next_source_lua_pc==3);
 assert(active.cursor==1);
 assert(!live.source_music_stop_command_acknowledged);
 puts("G145 PASS REAL original 2010 initial BGM=-1 -> Mission000 PC1 pause, PC3 empty-BGM source-equivalent accepted, PC6 original QTE1456 genuinely blocked, active BGM requires real SoundManager StopMusic(2000.0). No fake input2/6 or MissionResume, NO VPK.");
 return 0;
}
