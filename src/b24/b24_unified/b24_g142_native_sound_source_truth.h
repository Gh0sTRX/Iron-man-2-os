#ifndef B24_G142_NATIVE_SOUND_SOURCE_TRUTH_H
#define B24_G142_NATIVE_SOUND_SOURCE_TRUTH_H
#include <stdint.h>
#include "b24_g137_source_mission000_intro.h"
/* ORIGINAL user-owned iOS ARM 2010:
 * PauseMusic(lua_State*) 0x17ECC = Game::StopCrtBGM(2000.f) 0x97728
 * -> SoundManager::StopMusic(this+0xEC, 2000.f) 0x142188.
 * NOT SoundManager::PauseAllMusic() 0x14213C and NOT port-volume mute.
 * PlayMusic(lua_State*) 0x18000: ID-1 -> SoundManager::PlayMusic
 * PlayVoice(lua_State*) 0x18A04: ID-1 -> Game::PlayVoice
 * Original 803 source names 40-byte array at 0x473700, identical copy
 * after 803*40 bytes, all names match user IPA .www archive exactly:
 * ID88 -> m_pre_cutscene_intro.www, ID320 ->
 * vfx_intro_level1_jarvis_1.www.
 * This tiny verified table is NOT the full SFX registry. */
typedef struct {
 void *ctx;
 int (*stop_current_music)(void *ctx,int original_zero_based_id,
                             float exact_original_native_fade_argument);
 int (*start_music)(void *ctx,int original_zero_based_id,int original_loop,
                     float original_fade_argument);
 int (*start_voice)(void *ctx,int original_zero_based_id);
} B24G142Backend;
typedef struct {
 B24G142Backend backend;
 int original_current_music_zero_based_id;
 uint8_t original_current_music_id_from_actual_game_state_verified;
 uint8_t original_current_music_track_is_playing;
 uint8_t source_music_stop_command_acknowledged;
 uint8_t source_music88_started;
 uint8_t source_voice320_started;
} B24G142OwnerAudio;
const char *b24_g142_verified_source_filename_by_one_based_id(int id);
int b24_g142_owner_source_music_call(
 B24G142OwnerAudio *music,const B24G137Event *original_lua_event);
#endif
