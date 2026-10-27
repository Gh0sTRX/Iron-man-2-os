#ifndef IM2_TEST_AUDIO_FIXTURE_H
#define IM2_TEST_AUDIO_FIXTURE_H
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static inline void fixture_u32(unsigned char *p,uint32_t x){
 for(unsigned i=0;i<4;i++)p[i]=(unsigned char)(x>>(i*8));
}
static inline unsigned char *fixture_catalog(size_t *bytes){
 unsigned char *p=calloc(1,16+803*4+803*128);assert(p);
 memcpy(p,"IM2A",4);fixture_u32(p+4,1);fixture_u32(p+8,803);
 size_t used=0;
 for(unsigned i=0;i<803;i++){
  char name[128];
  if(i==87)snprintf(name,sizeof(name),"m_pre_cutscene_intro.pcm");
  else if(i==319)snprintf(name,sizeof(name),"vfx_intro_level1_jarvis_1.pcm");
  else snprintf(name,sizeof(name),"fixture_%u.pcm",i+1);
  fixture_u32(p+16+i*4,(uint32_t)used);
  memcpy(p+16+803*4+used,name,strlen(name)+1);used+=strlen(name)+1;
 }
 fixture_u32(p+12,(uint32_t)used);*bytes=16+803*4+used;return p;
}
#endif
