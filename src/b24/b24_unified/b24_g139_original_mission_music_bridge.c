#include "b24_g139_original_mission_music_bridge.h"
#include <string.h>
/* 512 frames at 48kHz is a valid Vita BGM output format.
 * This adapter controls real device BGM output volume. It does not
 * stream or decode the original 2010 .www RIFF/WAVE soundtrack. */
int b24_g139_music_init(B24G139Music *m,B24G139AudioBackend b){
 if(!m||!b.open_music_output||!b.set_music_stereo_volume||
    !b.close_music_output)return 0;
 memset(m,0,sizeof(*m));
 atomic_init(&m->output_open,0);
 atomic_init(&m->music_paused,0);
 m->port=-1;m->backend=b;
 int port=b.open_music_output(b.ctx,512,48000);
 if(port<0)return 0;
 m->port=port;m->output_open=1;
 return 1;
}
int b24_g139_music_pause(B24G139Music *m){
 if(!m||!m->output_open||!m->backend.set_music_stereo_volume)
  return 0;
 if(!m->backend.set_music_stereo_volume(m->backend.ctx,m->port,0,0))
  return 0;
 m->native_output_volume_applied=1;
 m->music_paused=1;
 m->pause_call_count++;
 return 1;
}
int b24_g139_music_resume(B24G139Music *m){
 if(!m||!m->output_open||!m->backend.set_music_stereo_volume)
  return 0;
 if(!m->backend.set_music_stereo_volume(m->backend.ctx,m->port,32768,32768))
  return 0;
 m->native_output_volume_applied=1;
 m->music_paused=0;
 return 1;
}
void b24_g139_music_close(B24G139Music *m){
 if(!m)return;
 if(m->output_open&&m->backend.close_music_output)
  (void)m->backend.close_music_output(m->backend.ctx,m->port);
 m->output_open=0;m->port=-1;
}
int b24_g139_original_Mission000_audio_dispatch(void *ctx,
 const B24G137Event *event){
 if(!ctx||!event)return 0;
 if(event->original_lua_pc==1&&
    event->opcode==B24_G137_CALL_MISSION_PAUSE)return 1;
 /* G142 REAL 2010 iOS ARM CORRECTION: PauseMusic(lua_State*)
  * 0x17ECC calls Game::StopCrtBGM(2000.f) 0x97728, which calls
  * SoundManager::StopMusic([Game+0xEC],2000.f). It DOES NOT call
  * SoundManager::PauseAllMusic and is NOT "mute BGM port".
  * Until current 2010 BGM ID/track/fade-stop callback is actually
  * bound, do not acknowledge PC3 or advance Mission000. The native
  * G139 music_pause() remains a real output-control utility only. */
 if(event->original_lua_pc==3&&
    event->opcode==B24_G137_CALL_PAUSE_MUSIC)
  return 0;
 /* QTE source Show(1456) Lua PC6 remains unbound; DO NOT auto
  * enable 2/6 or fake MissionResume from later Lua branches. */
 return 0;
}
#ifdef B24_G139_REAL_VITA_AUDIO_OUT
#include <psp2/audioout.h>
static int vita_open(void *ctx,int frames,int hz){
 (void)ctx;
 return sceAudioOutOpenPort(SCE_AUDIO_OUT_PORT_TYPE_BGM,
  frames,hz,SCE_AUDIO_OUT_MODE_STEREO);
}
static int vita_volume(void *ctx,int port,int left,int right){
 (void)ctx;
 int volume[2]={left,right};
 return sceAudioOutSetVolume(port,
   (SceAudioOutChannelFlag)(SCE_AUDIO_VOLUME_FLAG_L_CH|
                            SCE_AUDIO_VOLUME_FLAG_R_CH),volume)>=0;
}
static int vita_close(void *ctx,int port){
 (void)ctx;return sceAudioOutReleasePort(port)>=0;
}
B24G139AudioBackend b24_g139_native_vita_audio_backend(void){
 B24G139AudioBackend b={0};
 b.open_music_output=vita_open;
 b.set_music_stereo_volume=vita_volume;
 b.close_music_output=vita_close;
 return b;
}
#endif
