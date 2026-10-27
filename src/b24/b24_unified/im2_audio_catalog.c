#include "im2_audio_catalog.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static char *pool;
static const char *names[803];
static uint32_t u32(const unsigned char *p){
 return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;
}
void im2_audio_catalog_close(void){free(pool);pool=NULL;memset(names,0,sizeof(names));}
const char *im2_audio_catalog_pcm(int id){return pool&&id>=1&&id<=803?names[id-1]:NULL;}
int im2_audio_catalog_decode(const void *data,size_t bytes){
 const unsigned char *p=data;
 if(pool||!p||bytes<16+803*4||memcmp(p,"IM2A",4)||u32(p+4)!=1||u32(p+8)!=803)return 0;
 const uint32_t n=u32(p+12);
 if(!n||n>131072||bytes!=16+803*4+(size_t)n)return 0;
 char *text=malloc(n);if(!text)return 0;
 memcpy(text,p+16+803*4,n);const char *temp[803];int ok=1;uint32_t next_offset=0;
 for(unsigned i=0;i<803;i++){
  const uint32_t offset=u32(p+16+i*4);
  if(offset>=n||offset!=next_offset){ok=0;break;}
  const char *s=text+offset,*end=memchr(s,0,n-offset);
  if(!end||end-s<5||end-s>123||memcmp(end-4,".pcm",4)){ok=0;break;}
  for(const char *q=s;q<end-4;q++)if(!((*q>='a'&&*q<='z')||(*q>='A'&&*q<='Z')||
     (*q>='0'&&*q<='9')||*q=='_'||*q=='-')){ok=0;break;}
  if(!ok)break;
  temp[i]=s;
  next_offset=(uint32_t)(end-text)+1u;
 }
 if(ok&&next_offset!=n)ok=0;
 if(ok&&(strcmp(temp[87],"m_pre_cutscene_intro.pcm")||
         strcmp(temp[319],"vfx_intro_level1_jarvis_1.pcm")))ok=0;
 if(!ok){free(text);return 0;}
 memcpy(names,temp,sizeof(names));pool=text;return 1;
}
int im2_audio_catalog_load(const char *path){
 if(!path||pool)return 0;
 FILE *f=fopen(path,"rb");if(!f)return 0;
 int ok=fseek(f,0,SEEK_END)==0;long n=ok?ftell(f):-1;
 if(n<16+803*4||n>134300||fseek(f,0,SEEK_SET))ok=0;
 unsigned char *data=ok?malloc((size_t)n):NULL;if(!data)ok=0;
 if(ok&&fread(data,1,(size_t)n,f)!=(size_t)n)ok=0;
 if(fclose(f))ok=0;
 if(ok)ok=im2_audio_catalog_decode(data,(size_t)n);
 free(data);return ok;
}
