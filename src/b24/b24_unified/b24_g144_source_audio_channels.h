#ifndef B24_G144_SOURCE_AUDIO_CHANNELS_H
#define B24_G144_SOURCE_AUDIO_CHANNELS_H
#include <stddef.h>
#include "b24_g142_native_sound_source_truth.h"
/* 2010 actual native Game source music ID88=>m_pre_cutscene_intro,
 * voice ID320=>vfx_intro_level1_jarvis_1 via 803x40 original table.
 * All on Vita are 48000Hz s16le interleaved stereo .pcm extracted from
 * user's unmodified 2010 original .www WAVE, NOT synthesized tracks. */
const char *b24_g144_original_source_pcm_filename(int original_lua_id);
int b24_g144_original_source_pcm_vita_path(
 int original_lua_id,char *out,size_t out_size);
#ifdef B24_G144_VITA_NATIVE
#include "b24_g141_vita_stream_worker.h"
typedef struct {
 B24G139Music music_output;
 B24G139Music voice_output;
 B24G141VitaWorker music_worker;
 B24G141VitaWorker voice_worker;
 B24G139Music effect_output[4];
 B24G141VitaWorker effect_worker[4];
 int effect_running[4];
 int pause_state;
 int current_native_music_index;
 int current_native_voice_index;
 int music_running;
 int voice_running;
} B24G144NativeAudio;
void b24_g144_source_audio_init(B24G144NativeAudio *a);
void b24_g144_source_audio_release(B24G144NativeAudio *a);
B24G142Backend b24_g144_source_audio_backend(B24G144NativeAudio *a);
/* Explicit source event API. No filename/ID is guessed from button presses.
 * Four effect MAIN ports can overlap voice and BGM. Full returns failure,
 * never steals another original cue or fabricates an acknowledged event. */
int b24_g144_source_play_effect(B24G144NativeAudio *a,int original_lua_id);
/* User pause-menu output control, NOT original Lua PauseMusic/fade semantics. */
int b24_g144_source_audio_pause(B24G144NativeAudio *a,int pause);
#endif
#endif
