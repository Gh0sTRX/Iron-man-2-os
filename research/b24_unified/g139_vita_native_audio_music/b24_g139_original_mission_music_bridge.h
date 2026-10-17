#ifndef B24_G139_ORIGINAL_MISSION_MUSIC_BRIDGE_H
#define B24_G139_ORIGINAL_MISSION_MUSIC_BRIDGE_H
#include <stdint.h>
#include "b24_g137_source_mission000_intro.h"
/* G139: NEW PS Vita audio backend, ORIGINAL 2010 author Lua event
 * PauseMusic PC3. Not original 2010 SoundManager engine or codec.
 * No audio tracks yet mapped; backend silence is not original playback.
 * Do not acknowledge event unless physically opened music output
 * and successful output volume control. */
typedef struct {
 void *ctx;
 int (*open_music_output)(void *ctx,int frames,int sample_rate);
 int (*set_music_stereo_volume)(void *ctx,int port,int left,int right);
 int (*close_music_output)(void *ctx,int port);
} B24G139AudioBackend;
typedef struct {
 B24G139AudioBackend backend;
 int port;
 uint8_t output_open;
 uint8_t music_paused;
 uint8_t native_output_volume_applied;
 uint8_t original_2010_sound_ID88_track_mapped;
 uint32_t pause_call_count;
} B24G139Music;
int b24_g139_music_init(B24G139Music *music,B24G139AudioBackend backend);
int b24_g139_music_pause(B24G139Music *music);
int b24_g139_music_resume(B24G139Music *music);
void b24_g139_music_close(B24G139Music *music);
int b24_g139_original_Mission000_audio_dispatch(void *ctx,const B24G137Event *e);
#ifdef B24_G139_REAL_VITA_AUDIO_OUT
B24G139AudioBackend b24_g139_native_vita_audio_backend(void);
#endif
#endif
