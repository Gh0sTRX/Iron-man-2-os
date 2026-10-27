#include "b24_g141_vita_stream_worker.h"
#ifdef B24_G141_VITA_NATIVE
#include <psp2/audioout.h>
#include <psp2/kernel/threadmgr.h>
#include <string.h>
/* Never block B14 character physics/render tick on sceAudioOutOutput:
 * own kernel audio thread; <=2 KiB blocks each 10.667 ms at 48 kHz. */
static int b24_g141_worker_entry(SceSize args,void *argp){
 B24G141VitaWorker *worker=0;
 if(args!=sizeof(worker)||!argp)return -1;
 memcpy(&worker,argp,sizeof(worker));
 if(!worker||!worker->out)return -1;
 uint8_t block[512u*4u] __attribute__((aligned(64)));
 while(worker->running&&worker->out->output_open){
  if(worker->out->music_paused){
   sceKernelDelayThread(10000);
   continue;
  }
  size_t got=b24_g141_pcm_fill(&worker->pcm,block,512);
  if(!got){worker->stream_end=1;break;}
  /* fill() zero pads EOF; downstream output always exactly 512 frames. */
  int rc=sceAudioOutOutput(worker->out->port,block);
  if(rc<0){worker->output_last_error=rc;break;}
 }
 return 0;
}
int b24_g141_vita_start(B24G141VitaWorker *w,B24G139Music *out,
 const char *path,int loop){
 if(!w||!out||!out->output_open||!path)return 0;
 memset(w,0,sizeof(*w));
 w->out=out;w->thread_id=-1;
 if(!b24_g141_pcm_open(&w->pcm,path,loop))return 0;
 SceUID tid=sceKernelCreateThread("im2_source_audio",b24_g141_worker_entry,
  0x10000100,0x10000,0,0,NULL);
 if(tid<0){b24_g141_pcm_close(&w->pcm);return 0;}
 w->running=1;
 w->thread_id=tid;
 B24G141VitaWorker *passed=w;
 if(sceKernelStartThread(tid,sizeof(passed),&passed)<0){
  w->running=0;
  sceKernelDeleteThread(tid);
  w->thread_id=-1;
  b24_g141_pcm_close(&w->pcm);
  return 0;
 }
 return 1;
}
void b24_g141_vita_stop(B24G141VitaWorker *w){
 if(!w)return;
 w->running=0;
 if(w->thread_id>=0){
  int status=0;
  sceKernelWaitThreadEnd(w->thread_id,&status,NULL);
  sceKernelDeleteThread(w->thread_id);
  w->thread_id=-1;
 }
 b24_g141_pcm_close(&w->pcm);
}
#endif
