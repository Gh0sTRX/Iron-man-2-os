#ifndef B24_G141_VITA_STREAM_WORKER_H
#define B24_G141_VITA_STREAM_WORKER_H
#include "b24_g141_owner_pcm_stream.h"
#include "b24_g139_original_mission_music_bridge.h"
/* BGM PCM stream prepared offline from original 2010 source WAV;
 * user authored Level1 PCM filename selected outside mission script.
 * This does NOT map original music ID88 or PlayVoice320.
 * Real sound playback only after user loads source PCM onto Vita. */
#ifdef B24_G141_VITA_NATIVE
#include <psp2/kernel/threadmgr.h>
typedef struct {
 B24G139Music *out;
 B24G141PcmStream pcm;
 SceUID thread_id;
 volatile int running;
 int output_last_error;
 int stream_end;
} B24G141VitaWorker;
int b24_g141_vita_start(B24G141VitaWorker *w,B24G139Music *out,
 const char *original_audio_pcm_path,int loop);
void b24_g141_vita_stop(B24G141VitaWorker *w);
#endif
#endif
