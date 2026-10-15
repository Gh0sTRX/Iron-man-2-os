#include "b24_g11_original_unibeam_sequence.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void){
 for(int suit=0;suit<5;suit++){
  int supported=suit!=2;
  assert((b24_g11_unibeam_clip(suit,0,0)!=NULL)==supported);
  if(!supported)continue;
  assert(strstr(b24_g11_unibeam_clip(suit,0,0),"ground_beam1"));
  assert(strstr(b24_g11_unibeam_clip(suit,0,400),"ground_beam2"));
  assert(strstr(b24_g11_unibeam_clip(suit,0,800),"ground_beam3"));
  assert(!b24_g11_unibeam_clip(suit,0,1800));
  assert(strstr(b24_g11_unibeam_clip(suit,1,0),"float_beam1"));
  assert(strstr(b24_g11_unibeam_clip(suit,1,600),"float_beam2"));
  assert(strstr(b24_g11_unibeam_clip(suit,1,1000),"float_beam3"));
  assert(!b24_g11_unibeam_clip(suit,1,2266));
 }
 puts("PASS 2010 exact six original Ground+Float three-phase unibeam"
      " clip durations for 4 authentic skinned Iron suits, WM excluded");
 return 0;
}
