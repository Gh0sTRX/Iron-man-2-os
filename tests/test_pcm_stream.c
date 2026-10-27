#include "b24_g141_owner_pcm_stream.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
static const char *path="synthetic-stream.pcm";
static void write_bytes(const void *p,size_t bytes){
 FILE *f=fopen(path,"wb");assert(f);
 assert(fwrite(p,1,bytes,f)==bytes);assert(!fclose(f));
}
int main(void){
 const uint8_t source[]={1,2,3,4,5,6,7,8,9,10,11,12};
 B24G141PcmStream s;uint8_t out[512*4];
 write_bytes(source,sizeof(source));assert(b24_g141_pcm_open(&s,path,0));
 b24_g141_pcm_pause(&s,1);memset(out,255,sizeof(out));
 assert(!b24_g141_pcm_fill(&s,out,4));assert(s.bytes_read==0);
 for(unsigned i=0;i<16;i++)assert(out[i]==0);
 b24_g141_pcm_pause(&s,0);assert(b24_g141_pcm_fill(&s,out,4)==3);
 assert(!memcmp(out,source,12));for(unsigned i=12;i<16;i++)assert(out[i]==0);
 assert(s.finished&&!b24_g141_pcm_fill(&s,out,4));b24_g141_pcm_close(&s);
 assert(!s.file);b24_g141_pcm_close(&s);
 assert(b24_g141_pcm_open(&s,path,1));assert(b24_g141_pcm_fill(&s,out,512)==512);
 for(unsigned i=0;i<sizeof(out);i++)assert(out[i]==source[i%12]);
 b24_g141_pcm_pause(&s,1);uint32_t before=s.bytes_read;
 assert(!b24_g141_pcm_fill(&s,out,512)&&s.bytes_read==before);
 b24_g141_pcm_pause(&s,0);assert(b24_g141_pcm_fill(&s,out,1)==1);
 assert(!memcmp(out,source+8,4));b24_g141_pcm_close(&s);
 /* External file disappearing/truncating after validation must terminate,
  * otherwise the audio worker's stop/join can never complete. */
 write_bytes(source,sizeof(source));assert(b24_g141_pcm_open(&s,path,1));
 write_bytes(source,0);assert(b24_g141_pcm_fill(&s,out,512)<=3);assert(s.finished);
 b24_g141_pcm_close(&s);assert(!b24_g141_pcm_open(&s,path,1));
 write_bytes(source,3);assert(!b24_g141_pcm_open(&s,path,0));
 assert(!b24_g141_pcm_fill(NULL,out,513));assert(!b24_g141_pcm_fill(NULL,NULL,1));
 assert(remove(path)==0);puts("PASS PCM pause/EOF/loop/truncated-input termination (synthetic only)");return 0;
}
