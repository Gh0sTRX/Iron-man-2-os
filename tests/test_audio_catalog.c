#include "im2_audio_catalog.h"
#include "audio_fixture.h"
int main(int argc,char **argv){
 if(argc==2){
  assert(im2_audio_catalog_load(argv[1]));
  for(int i=1;i<=803;i++)assert(im2_audio_catalog_pcm(i));
  im2_audio_catalog_close();puts("PASS external native catalog: 803 bounded paths and original anchor IDs");return 0;
 }
 assert(argc==1);
 size_t size;unsigned char *data=fixture_catalog(&size);
 assert(!im2_audio_catalog_pcm(88));
 for(size_t n=0;n<size;n++)assert(!im2_audio_catalog_decode(data,n));
 assert(im2_audio_catalog_decode(data,size));
 assert(!strcmp(im2_audio_catalog_pcm(1),"fixture_1.pcm"));
 assert(!strcmp(im2_audio_catalog_pcm(803),"fixture_803.pcm"));
 assert(!strcmp(im2_audio_catalog_pcm(88),"m_pre_cutscene_intro.pcm"));
 assert(!im2_audio_catalog_pcm(0)&&!im2_audio_catalog_pcm(804));
 assert(!im2_audio_catalog_decode(data,size));
 im2_audio_catalog_close();
 const size_t mutations[]={0,4,8,12,16,16+803*4,size-1};
 for(unsigned i=0;i<sizeof(mutations)/sizeof(mutations[0]);i++){
  size_t at=mutations[i];unsigned char before=data[at];data[at]=255;
  assert(!im2_audio_catalog_decode(data,size));assert(!im2_audio_catalog_pcm(88));
  data[at]=before;
 }
 data[16+803*4]='.';assert(!im2_audio_catalog_decode(data,size));
 free(data);puts("PASS synthetic 803-ID catalog: bounds, two native anchors, path safety, atomic load");return 0;
}
