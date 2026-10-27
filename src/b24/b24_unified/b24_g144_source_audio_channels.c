#include "b24_g144_source_audio_channels.h"
#include "im2_audio_catalog.h"
#include <string.h>
#include <stdio.h>
const char *b24_g144_original_source_pcm_filename(int id){
 const char *catalog_name=im2_audio_catalog_pcm(id);
 if(catalog_name)return catalog_name;
 /* External catalog is produced only after verified executable + native
  * 803x40 inline-name table validation. Without it, retain only two proven IDs. */
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
 atomic_init(&a->music_output.output_open,0);atomic_init(&a->music_output.music_paused,0);
 atomic_init(&a->voice_output.output_open,0);atomic_init(&a->voice_output.music_paused,0);
 a->music_output.port=-1;
 a->voice_output.port=-1;
 a->music_worker.thread_id=-1;
 a->voice_worker.thread_id=-1;
 for(unsigned i=0;i<4;i++){
  a->effect_output[i].port=-1;a->effect_worker[i].thread_id=-1;
  atomic_init(&a->effect_output[i].output_open,0);
  atomic_init(&a->effect_output[i].music_paused,0);
 }
}
void b24_g144_source_audio_release(B24G144NativeAudio *a){
 if(!a)return;
 if(a->music_running)b24_g141_vita_stop(&a->music_worker);
 if(a->voice_running)b24_g141_vita_stop(&a->voice_worker);
 for(unsigned i=0;i<4;i++){
  if(a->effect_running[i])b24_g141_vita_stop(&a->effect_worker[i]);
  a->effect_running[i]=0;b24_g139_music_close(&a->effect_output[i]);
 }
 a->music_running=a->voice_running=0;
 b24_g139_music_close(&a->voice_output);
 b24_g139_music_close(&a->music_output);
 a->current_native_music_index=a->current_native_voice_index=-1;
 a->pause_state=0;
}
static int start_music(void *ctx,int native_index,int loop,float fade){
 B24G144NativeAudio *a=(B24G144NativeAudio*)ctx;
 char path[256];
 /* Lua ID88 equals zero-based native 87, and 0.0f default fade.
  * Do not substitute a background song or a random audio asset. */
 if(!a||native_index<0||native_index>=803||fade!=0.0f||
    !b24_g144_original_source_pcm_vita_path(native_index+1,path,sizeof(path)))
  return 0;
 if(a->music_running){
  b24_g141_vita_stop(&a->music_worker);
  a->music_running=0;
 }
 if(!a->music_output.output_open &&
    !b24_g139_music_init(&a->music_output,
                          b24_g139_native_vita_audio_backend()))
  return 0;
 if(!(a->pause_state?b24_g139_music_pause(&a->music_output):
                     b24_g139_music_resume(&a->music_output)))return 0;
 if(!b24_g141_vita_start(&a->music_worker,&a->music_output,path,loop))
  return 0;
 a->music_running=1;
 a->current_native_music_index=native_index;
 return 1;
}
static int start_voice(void *ctx,int native_index){
 B24G144NativeAudio *a=(B24G144NativeAudio*)ctx;
 char path[256];
 if(!a||native_index<0||native_index>=803||
   !b24_g144_original_source_pcm_vita_path(native_index+1,path,sizeof(path)))
  return 0;
 if(a->voice_running){
  b24_g141_vita_stop(&a->voice_worker);
  a->voice_running=0;
 }
 if(!a->voice_output.output_open){
  B24G139AudioBackend backend={a,voice_open,voice_volume,voice_close};
  if(!b24_g139_music_init(&a->voice_output,backend))return 0;
 }
 if(!(a->pause_state?b24_g139_music_pause(&a->voice_output):
                     b24_g139_music_resume(&a->voice_output)))return 0;
 if(!b24_g141_vita_start(&a->voice_worker,&a->voice_output,path,0))
  return 0;
 a->voice_running=1;
 a->current_native_voice_index=native_index;
 return 1;
}
int b24_g144_source_play_effect(B24G144NativeAudio *a,int id){
 char path[256];
 if(!a||!im2_audio_catalog_pcm(id)||
    !b24_g144_original_source_pcm_vita_path(id,path,sizeof(path)))return 0;
 for(unsigned i=0;i<4;i++){
  if(a->effect_running[i]&&!a->effect_worker[i].stream_end)continue;
  if(a->effect_running[i]){
   b24_g141_vita_stop(&a->effect_worker[i]);a->effect_running[i]=0;
  }
  if(!a->effect_output[i].output_open){
   B24G139AudioBackend backend={a,voice_open,voice_volume,voice_close};
   if(!b24_g139_music_init(&a->effect_output[i],backend))return 0;
  }
  if(!(a->pause_state?b24_g139_music_pause(&a->effect_output[i]):
                       b24_g139_music_resume(&a->effect_output[i])))return 0;
  if(!b24_g141_vita_start(&a->effect_worker[i],&a->effect_output[i],path,0))return 0;
  a->effect_running[i]=1;return 1;
 }
 return 0;
}
int b24_g144_source_audio_pause(B24G144NativeAudio *a,int pause){
 if(!a)return 0;
 pause=!!pause;
 B24G139Music *outputs[]={&a->music_output,&a->voice_output,
  &a->effect_output[0],&a->effect_output[1],&a->effect_output[2],&a->effect_output[3]};
 int settled=a->pause_state==pause;
 for(unsigned i=0;i<6;i++)if(outputs[i]->output_open&&outputs[i]->music_paused!=pause)settled=0;
 /* Remember desired user state even if one port fails; retry unsettled ports
  * and let newly started sounds inherit the requested pause state. */
 a->pause_state=pause;
 if(settled)return 1;
 int ok=1;
 for(unsigned i=0;i<6;i++)if(outputs[i]->output_open){
  if(!(pause?b24_g139_music_pause(outputs[i]):b24_g139_music_resume(outputs[i])))ok=0;
 }
 return ok;
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
