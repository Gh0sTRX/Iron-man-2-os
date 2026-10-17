#include "b24_g141_owner_pcm_stream.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
int main(void){
 const char *name="/tmp/g141_real_format_source_pcm_test.bin";
 FILE *f=fopen(name,"wb");
 assert(f);
 uint8_t original[4*5];
 for(unsigned i=0;i<sizeof(original);i++)original[i]=(uint8_t)(i+1);
 assert(fwrite(original,1,sizeof(original),f)==sizeof(original));
 fclose(f);
 B24G141PcmStream s={0};
 uint8_t block[512*4];
 assert(b24_g141_pcm_open(&s,name,0));
 assert(b24_g141_pcm_fill(&s,block,4)==4);
 assert(!memcmp(block,original,16));
 b24_g141_pcm_pause(&s,1);
 assert(b24_g141_pcm_fill(&s,block,3)==0);
 for(unsigned i=0;i<12;i++)assert(block[i]==0);
 assert(s.bytes_read==16);
 b24_g141_pcm_pause(&s,0);
 assert(b24_g141_pcm_fill(&s,block,4)==1);
 assert(!memcmp(block,original+16,4));
 for(unsigned i=4;i<16;i++)assert(block[i]==0);
 assert(s.finished);
 b24_g141_pcm_close(&s);
 assert(b24_g141_pcm_open(&s,name,1));
 assert(b24_g141_pcm_fill(&s,block,512)==512);
 assert(!memcmp(block,original,20));
 assert(!memcmp(block+20,original,20));
 b24_g141_pcm_close(&s);
 assert(b24_g141_pcm_fill(NULL,block,513)==0);
 assert(remove(name)==0);
 puts("PASS G141 strict PCM source 48000 S16LE stereo 512-frame ring and EOF zero-pad loop / true playhead pause no sample advance; native Vita audio threading separate, NO VPK");
 return 0;
}
