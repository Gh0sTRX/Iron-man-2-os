#include "b24_g142_native_sound_source_truth.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
typedef struct {
 int allowed,stop_count,start_count,voice_count,last_index,loop;
 float fade;
} FakeOriginalMusicState;
static int stop(void *v,int id,float fade){
 FakeOriginalMusicState *a=(FakeOriginalMusicState*)v;
 a->stop_count++;a->last_index=id;a->fade=fade;
 return a->allowed;
}
static int play(void *v,int id,int loop,float fade){
 FakeOriginalMusicState *a=(FakeOriginalMusicState*)v;
 a->start_count++;a->last_index=id;a->loop=loop;a->fade=fade;
 return a->allowed;
}
static int voice(void *v,int id){
 FakeOriginalMusicState *a=(FakeOriginalMusicState*)v;
 a->voice_count++;a->last_index=id;return a->allowed;
}
int main(void){
 assert(strcmp(b24_g142_verified_source_filename_by_one_based_id(88),
  "m_pre_cutscene_intro.www")==0);
 assert(strcmp(b24_g142_verified_source_filename_by_one_based_id(320),
  "vfx_intro_level1_jarvis_1.www")==0);
 assert(b24_g142_verified_source_filename_by_one_based_id(32)==0);
 FakeOriginalMusicState mock={0};
 B24G142OwnerAudio m={0};
 m.backend=(B24G142Backend){&mock,stop,play,voice};
 B24G137Event pc3={0};pc3.original_lua_pc=3;
 pc3.opcode=B24_G137_CALL_PAUSE_MUSIC;
 /* Original PC3 must be BLOCKED if current Game+0xEC has not been
  * recovered from source playback state; mute-port != StopCrtBGM. */
 assert(!b24_g142_owner_source_music_call(&m,&pc3));
 assert(mock.stop_count==0);
 /* G145 real native 2010 Game initial +0xEC == -1: no track has
  * started and no output emitter exists; portable empty-stop can
  * acknowledge without claiming a VoxEngine Stop(-1) native trace. */
 m.original_current_music_zero_based_id=-1;
 m.original_current_music_id_from_actual_game_state_verified=1;
 m.original_current_music_track_is_playing=0;
 assert(b24_g142_owner_source_music_call(&m,&pc3));
 assert(m.source_music_stop_command_acknowledged);
 assert(mock.stop_count==0);
 /* Never allow fake stop when state says playing but id remains -1 */
 m.original_current_music_track_is_playing=1;
 assert(!b24_g142_owner_source_music_call(&m,&pc3));
 m.original_current_music_track_is_playing=0;
 m.original_current_music_zero_based_id=87;
 m.original_current_music_id_from_actual_game_state_verified=1;
 assert(!b24_g142_owner_source_music_call(&m,&pc3));
 assert(mock.stop_count==1&&mock.fade==2000.f);
 mock.allowed=1;
 assert(b24_g142_owner_source_music_call(&m,&pc3));
 assert(mock.stop_count==2&&mock.last_index==87);
 assert(mock.fade==2000.f&&m.source_music_stop_command_acknowledged);
 B24G137Event pc62={0};pc62.original_lua_pc=62;
 pc62.opcode=B24_G137_CALL_PLAY_MUSIC;
 pc62.source_arg0=88;pc62.original_arg1_boolean=1;
 assert(b24_g142_owner_source_music_call(&m,&pc62));
 assert(mock.start_count==1&&mock.last_index==87&&mock.loop==1);
 assert(mock.fade==0.f&&m.source_music88_started);
 B24G137Event pc70={0};pc70.original_lua_pc=70;
 pc70.opcode=B24_G137_CALL_PLAYVOICE;pc70.source_arg0=320;
 assert(b24_g142_owner_source_music_call(&m,&pc70));
 assert(mock.voice_count==1&&mock.last_index==319);
 puts("G142 PASS TRUE OWNER 2010 native PauseMusic→Game StopCrtBGM(Game+0xEC,2000.0), PlayMusic(88)=table index87 m_pre_cutscene_intro, PlayVoice(320)=index319 vfx_intro_level1_jarvis_1; disallow fake mute for original stop, NO VPK");
 return 0;
}
