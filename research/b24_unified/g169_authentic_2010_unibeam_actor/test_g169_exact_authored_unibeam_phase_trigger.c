#include "b24_g169_native_source_unibeam.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void expect(B24G169Beam *a,int suit,int hover,int stage,unsigned now,
                   const char *name){
 const char *got=b24_g169_native_beam_clip(a,suit,hover,stage,now);
 assert((!name&&!got)||(name&&got&&!strcmp(name,got)));
}
int main(void){
 B24G169Beam a={0};
 assert(!b24_g169_native_beam_begin(&a,2,0,1000)); /* WM HAS NO 2010 Beam IM2V */
 assert(b24_g169_native_beam_begin(&a,4,0,1000));
 expect(&a,4,0,0,1000,"suitcase_ironman_aim_ground_beam1");
 expect(&a,4,0,0,1399,"suitcase_ironman_aim_ground_beam1");
 expect(&a,4,0,0,1400,"suitcase_ironman_aim_ground_beam2");
 expect(&a,4,0,0,1799,"suitcase_ironman_aim_ground_beam2");
 expect(&a,4,0,0,1800,"suitcase_ironman_aim_ground_beam3");
 expect(&a,4,0,0,2799,"suitcase_ironman_aim_ground_beam3");
 expect(&a,4,0,0,2800,NULL);
 assert(b24_g169_native_beam_begin(&a,4,1,5000));
 expect(&a,4,1,1,5599,"suitcase_ironman_aim_float_beam1");
 expect(&a,4,1,1,5600,"suitcase_ironman_aim_float_beam2");
 expect(&a,4,1,1,6000,"suitcase_ironman_aim_float_beam3");
 expect(&a,4,1,1,7265,"suitcase_ironman_aim_float_beam3");
 expect(&a,4,1,1,7266,NULL);
 assert(b24_g169_native_beam_begin(&a,0,0,100));
 expect(&a,0,0,0,100,"ironman_ironman_aim_ground_beam1");
 expect(&a,0,0,2,110,NULL);
 assert(b24_g169_native_beam_begin(&a,4,0,200));
 expect(&a,2,0,0,250,NULL);
 puts("G169 six exact original 2010 IM2V Beam1/2/3 phase IDs/sourced durations MarkV and native MarkVI C11 PASS; not native iOS weapon-event proof; no VPK");
 return 0;
}
