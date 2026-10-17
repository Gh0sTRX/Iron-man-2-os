#include "b24_g144_source_audio_channels.h"
#include <string.h>
#include <stdio.h>
const char *b24_g144_original_source_pcm_filename(int id){
 /* Only genuine original 803*40 sound table entries verified with
  * code refs; no fake full audio-ID database or fallback guesses. */
 switch(id){
  case 88:return "m_pre_cutscene_intro.pcm";
  case 320:return "vfx_intro_level1_jarvis_1.pcm";
  default:return 0;
 }
}
int b24_g144_original_source_pcm_vita_path(
 int id,char *out,size_t length){
 const char *name=b24_g144_original_source_pcm_filename(id);
 if(!name||!out||length<2u)return 0;
 int n=snprintf(out,length,"ux0:data/ironman2/audio/%s",name);
 return n>0&&(size_t)n<length;
}
#ifdef B24_G144_VITA_NATIVE
#include <psp2/audioout.h>
/* Separate BGM and MAIN audio-output ports allow real source JARVIS
 * voice to play over real source 2010 background music. Never create
 * more than the platform's one BGM port. No B14/gameplay thread mixing. */
static int voice_open(void *ctx,int frames,int hz){
 (void)ctx;
 return sceAudioOutOpenPort(SCE_AUDIO_OUT_PORT_TYPE_MAIN,frames,hz,
  SCE_AUDIO_OUT_MODE_STEREO);
}
static int voice_volume(void *ctx,int port,int l,int r){
 (void)ctx;int v[2]={l,r};
 return sceAudioOutSetVolume(port,
  (SceAudioOutChannelFlag)(SCE_AUDIO_VOLUME_FLAG_L_CH|
                           SCE_AUDIO_VOLUME_FLAG_R_CH),v)>=0;
}
static int voice_close(void *ctx,int port){
 (void)ctx;return sceAudioOutReleasePort(port)>=0;
}
void b24_g144_source_audio_init(B24G144NativeAudio *a){
 if(!a)return;
 memset(a,0,sizeof(*a));
 a->current_native_music_index=-1;
 a->current_native_voice_index=-1;
 a->music_output.port=-1;
 a->voice_output.port=-1;
 a->music_worker.thread_id=-1;
 a->voice_worker.thread_id=-1;
}
void b24_g144_source_audio_release(B24G144NativeAudio *a){
 if(!a)return;
 if(a->music_running)b24_g141_vita_stop(&a->music_worker);
 if(a->voice_running)b24_g141_vita_stop(&a->voice_worker);
 a->music_running=a->voice_running=0;
 b24_g139_music_close(&a->voice_output);
 b24_g139_music_close(&a->music_output);
 a->current_native_music_index=a->current_native_voice_index=-1;
}
static int start_music(void *ctx,int native_index,int loop,float fade){
 B24G144NativeAudio *a=(B24G144NativeAudio*)ctx;
 char path[140];
 /* Lua ID88 equals zero-based native 87, and 0.0f default fade.
  * Do not substitute a background song or a random audio asset. */
 if(!a||native_index!=87||fade!=0.0f||
    !b24_g144_original_source_pcm_vita_path(88,path,sizeof(path)))
  return 0;
 if(a->music_running){
  b24_g141_vita_stop(&a->music_worker);
  a->music_running=0;
 }
 if(!a->music_output.output_open &&
    !b24_g139_music_init(&a->music_output,
                          b24_g139_native_vita_audio_backend()))
  return 0;
 if(!b24_g139_music_resume(&a->music_output))return 0;
 if(!b24_g141_vita_start(&a->music_worker,&a->music_output,path,loop))
  return 0;
 a->music_running=1;
 a->current_native_music_index=native_index;
 return 1;
}
static int start_voice(void *ctx,int native_index){
 B24G144NativeAudio *a=(B24G144NativeAudio*)ctx;
 char path[140];
 if(!a||native_index!=319||
   !b24_g144_original_source_pcm_vita_path(320,path,sizeof(path)))
  return 0;
 if(a->voice_running){
  b24_g141_vita_stop(&a->voice_worker);
  a->voice_running=0;
 }
 if(!a->voice_output.output_open){
  B24G139AudioBackend backend={a,voice_open,voice_volume,voice_close};
  if(!b24_g139_music_init(&a->voice_output,backend))return 0;
 }
 if(!b24_g139_music_resume(&a->voice_output))return 0;
 if(!b24_g141_vita_start(&a->voice_worker,&a->voice_output,path,0))
  return 0;
 a->voice_running=1;
 a->current_native_voice_index=native_index;
 return 1;
}
static int stop_music(void *ctx,int native_index,float original_arg){
 B24G144NativeAudio *a=(B24G144NativeAudio*)ctx;
 if(!a||!a->music_running||
    a->current_native_music_index!=native_index)return 0;
 /* Original 2010 PC3 passes exactly 2000.0 into VoxEngine emitter
  * stop. We do NOT know yet if units are ms or frames; do not silently
  * treat it as instantaneous stop or only port mute. Fail closed until
  * native source stop ramp semantics recovered/implemented. */
 if(original_arg>0.f)return 0;
 b24_g141_vita_stop(&a->music_worker);
 a->music_running=0;
 a->current_native_music_index=-1;
 return 1;
}
B24G142Backend b24_g144_source_audio_backend(B24G144NativeAudio *a){
 B24G142Backend b={0};
 b.ctx=a;b.start_music=start_music;b.start_voice=start_voice;
 b.stop_current_music=stop_music;
 return b;
}
#endif
