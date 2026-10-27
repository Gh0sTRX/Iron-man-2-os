/* Executes actual native-channel policy with fake OS ports/worker scheduling.
 * No hardware playback or native iOS effect-event binding is claimed. */
#include "b24_g144_source_audio_channels.h"
#include "im2_audio_catalog.h"
#include "audio_fixture.h"
static int next_port=1,open_ports,volume_calls,started,stopped,fail_volume_port;
int sceAudioOutOpenPort(int kind,int frames,int hz,int mode){
 assert((kind==0||kind==1)&&frames==512&&hz==48000&&mode==0);
 open_ports++;return next_port++;
}
int sceAudioOutSetVolume(int port,int flags,int *volume){
 assert(port>0&&flags==3&&volume);
 assert((volume[0]==0||volume[0]==32768)&&volume[0]==volume[1]);
 volume_calls++;
 if(port==fail_volume_port){fail_volume_port=0;return -1;}
 return 0;
}
int sceAudioOutReleasePort(int port){assert(port>0&&open_ports);open_ports--;return 0;}
int b24_g141_vita_start(B24G141VitaWorker *w,B24G139Music *out,const char *path,int loop){
 assert(w&&out&&out->output_open);memset(w,0,sizeof(*w));
 atomic_init(&w->running,0);atomic_init(&w->stream_end,0);
 if(!b24_g141_pcm_open(&w->pcm,path,loop))return 0;
 w->out=out;w->thread_id=started++;w->running=1;return 1;
}
void b24_g141_vita_stop(B24G141VitaWorker *w){
 assert(w&&w->running);w->running=0;w->thread_id=-1;
 b24_g141_pcm_close(&w->pcm);stopped++;
}
static void pcm(const char *name){
 char path[256];snprintf(path,sizeof(path),"ux0:data/ironman2/audio/%s",name);
 FILE *f=fopen(path,"wb");assert(f);const unsigned char stereo[]={1,0,2,0};
 assert(fwrite(stereo,sizeof(stereo),1,f)==1);assert(fclose(f)==0);
}
int main(void){
 size_t size;unsigned char *data=fixture_catalog(&size);
 assert(im2_audio_catalog_decode(data,size));free(data);
 for(int i=1;i<=6;i++)pcm(im2_audio_catalog_pcm(i));
 B24G144NativeAudio a;b24_g144_source_audio_init(&a);
 B24G142Backend backend=b24_g144_source_audio_backend(&a);
 assert(backend.start_music(backend.ctx,0,1,0.f));
 assert(backend.start_voice(backend.ctx,1));
 for(unsigned i=0;i<4;i++)assert(b24_g144_source_play_effect(&a,3));
 assert(!b24_g144_source_play_effect(&a,3)); /* full: no voice stealing */
 assert(open_ports==6&&started==6);
 assert(!backend.stop_current_music(backend.ctx,0,2000.f)); /* unknown native fade */
 assert(b24_g144_source_audio_pause(&a,1));
 assert(a.music_output.music_paused&&a.voice_output.music_paused);
 for(unsigned i=0;i<4;i++)assert(a.effect_output[i].music_paused);
 const int calls=volume_calls;
 assert(b24_g144_source_audio_pause(&a,1)&&volume_calls==calls);
 a.effect_worker[0].stream_end=1;
 assert(b24_g144_source_play_effect(&a,4));
 assert(a.effect_output[0].music_paused&&started==7&&stopped==1&&open_ports==6);
 assert(b24_g144_source_audio_pause(&a,0));
 assert(!a.music_output.music_paused&&!a.voice_output.music_paused);
 /* One failed OS volume operation must not leave successful channels
  * permanently paused when the user immediately resumes. */
 fail_volume_port=a.voice_output.port;
 assert(!b24_g144_source_audio_pause(&a,1));
 assert(a.music_output.music_paused&&!a.voice_output.music_paused);
 assert(b24_g144_source_audio_pause(&a,0));
 assert(!a.music_output.music_paused&&!a.voice_output.music_paused);
 for(unsigned i=0;i<4;i++)assert(!a.effect_output[i].music_paused);
 assert(!b24_g144_source_play_effect(&a,804));
 b24_g144_source_audio_release(&a);
 assert(open_ports==0&&stopped==started);
 im2_audio_catalog_close();
 for(int i=1;i<=6;i++){
  char path[256];snprintf(path,sizeof(path),"ux0:data/ironman2/audio/fixture_%d.pcm",i);assert(remove(path)==0);
 }
 puts("PASS actual audio policy: music+voice+4 effects, no stealing, pause/resume, ended-slot reuse, complete release");
 return 0;
}
