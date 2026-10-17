#include "b24_g142_native_sound_source_truth.h"
const char *b24_g142_verified_source_filename_by_one_based_id(int id){
 switch(id){
  case 88:return "m_pre_cutscene_intro.www";
  case 320:return "vfx_intro_level1_jarvis_1.www";
  case 321:return "vfx_intro_level1_tony_1.www";
  default:return 0; /* source has 803 IDs: do not invent others */
 }
}
int b24_g142_owner_source_music_call(
 B24G142OwnerAudio *m,const B24G137Event *e){
 if(!m||!e)return 0;
 if(e->original_lua_pc==3&&e->opcode==B24_G137_CALL_PAUSE_MUSIC){
  /* Original 2010 Game::StopCrtBGM reads current music index
   * from native Game+0xEC; we do NOT yet know that runtime value.
   * Only acknowledge when a track from original current game state
   * has really been mapped and backend stop operation accepted. */
  if(!m->original_current_music_id_from_actual_game_state_verified||
      !m->backend.stop_current_music||
      m->original_current_music_zero_based_id<0)return 0;
  if(!m->backend.stop_current_music(m->backend.ctx,
      m->original_current_music_zero_based_id,2000.0f))return 0;
  m->source_music_stop_command_acknowledged=1;
  m->original_current_music_track_is_playing=0;
  return 1;
 }
 if(e->original_lua_pc==62&&e->opcode==B24_G137_CALL_PLAY_MUSIC){
  /* Real original Lua PlayMusic(88,true), original native index 87;
   * lua_tonumber(third missing argument) =0.0f in genuine ARM. */
  if(e->source_arg0!=88||!e->original_arg1_boolean||
     !m->backend.start_music)return 0;
  if(!m->backend.start_music(m->backend.ctx,87,1,0.0f))return 0;
  m->source_music88_started=1;
  m->original_current_music_zero_based_id=87;
  m->original_current_music_track_is_playing=1;
  /* This is output state of *our* native Vita engine; do NOT assume
   * it is actual 2010 Game+0xEC or backfill the G137 PC3 source gate. */
  return 1;
 }
 if(e->original_lua_pc==70&&e->opcode==B24_G137_CALL_PLAYVOICE){
  if(e->source_arg0!=320||!m->backend.start_voice)return 0;
  if(!m->backend.start_voice(m->backend.ctx,319))return 0;
  m->source_voice320_started=1;return 1;
 }
 return 0;
}
