#include "b24_g144_source_audio_channels.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void){
 char path[140]={0};
 assert(strcmp(b24_g144_original_source_pcm_filename(88),
  "m_pre_cutscene_intro.pcm")==0);
 assert(strcmp(b24_g144_original_source_pcm_filename(320),
  "vfx_intro_level1_jarvis_1.pcm")==0);
 assert(!b24_g144_original_source_pcm_filename(319));
 assert(!b24_g144_original_source_pcm_filename(321));
 assert(b24_g144_original_source_pcm_vita_path(88,path,sizeof(path)));
 assert(!strcmp(path,"ux0:data/ironman2/audio/m_pre_cutscene_intro.pcm"));
 assert(b24_g144_original_source_pcm_vita_path(320,path,sizeof(path)));
 assert(!strcmp(path,"ux0:data/ironman2/audio/vfx_intro_level1_jarvis_1.pcm"));
 assert(!b24_g144_original_source_pcm_vita_path(88,path,8));
 assert(!b24_g144_original_source_pcm_vita_path(8,path,sizeof(path)));
 assert(!b24_g144_original_source_pcm_vita_path(320,0,0));
 puts("G144 PASS native original 803x40 2010 ID88 BGM and ID320 Jarvis source table maps to exact Vita ux0:data PCM paths, no guessed other IDs, NO VPK");
 return 0;
}
