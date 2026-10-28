#include "b24_original_im2v_stream.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
int main(int argc,char **argv){
 assert(argc==2);const char *clips[]={"ironman_ironman_ground_idel","ironman_ironman_ground_hurt1","ironman_ironman_ground_combo_1","ironman_ironman_ground_death"};
 float xyz[802*3];
 for(unsigned i=0;i<4;i++){
  B24OriginalIM2VStream s={0};assert(b24_original_im2v_open(&s,argv[1],clips[i],802));
  assert(b24_original_im2v_sample(&s,0,0,xyz));assert(b24_original_im2v_sample(&s,s.duration_ms/2,0,xyz));
  assert(b24_original_im2v_sample(&s,s.duration_ms,0,xyz));b24_original_im2v_close(&s);
 }
 puts("PASS four existing802v source streams for explicitly labelled Mark IV test opponent; no native NPC proof");return 0;
}
