#include "b24_g141_owner_pcm_stream.h"
#include <string.h>
#include <limits.h>
int b24_g141_pcm_open(B24G141PcmStream *s,const char *path,int loop){
 if(!s||!path)return 0;
 memset(s,0,sizeof(*s));
 FILE *f=fopen(path,"rb");
 if(!f)return 0;
 if(fseek(f,0,SEEK_END)!=0){fclose(f);return 0;}
 long n=ftell(f);
 if(n<=0||n>INT32_MAX||((unsigned long)n%4u)!=0u||
    fseek(f,0,SEEK_SET)!=0){fclose(f);return 0;}
 s->file=f;
 s->source_bytes=(uint32_t)n;
 s->loop=!!loop;
 return 1;
}
size_t b24_g141_pcm_fill(B24G141PcmStream *s,void *buffer,size_t frames){
 if(!buffer||!frames||frames>512u)return 0;
 size_t wanted=frames*4u;
 memset(buffer,0,wanted);
 if(!s||!s->file||s->paused||s->finished)return 0;
 uint8_t *out=(uint8_t*)buffer;
 size_t have=0;
 int rewound_without_data=0;
 while(have<wanted){
  size_t n=fread(out+have,1,wanted-have,s->file);
  have+=n;
  s->bytes_read+=(uint32_t)n;
  if(n>0){rewound_without_data=0;continue;}
  if(ferror(s->file)){s->finished=1;break;}
  if(!s->loop||rewound_without_data){s->finished=1;break;}
  clearerr(s->file);
  if(fseek(s->file,0,SEEK_SET)!=0){s->finished=1;break;}
  s->bytes_read=0;
  rewound_without_data=1;
 }
 return have/4u;
}
void b24_g141_pcm_pause(B24G141PcmStream *s,int pause){
 if(s)s->paused=!!pause;
}
void b24_g141_pcm_close(B24G141PcmStream *s){
 if(!s)return;
 if(s->file)fclose(s->file);
 memset(s,0,sizeof(*s));
}
