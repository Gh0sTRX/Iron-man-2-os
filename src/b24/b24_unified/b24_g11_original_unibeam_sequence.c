#include "b24_g11_original_unibeam_sequence.h"
static const char *const ground[3]={
 "ironman_ironman_aim_ground_beam1",
 "ironman_ironman_aim_ground_beam2",
 "ironman_ironman_aim_ground_beam3"
};
static const char *const hover[3]={
 "ironman_ironman_aim_float_beam1",
 "ironman_ironman_aim_float_beam2",
 "ironman_ironman_aim_float_beam3"
};
uint32_t b24_g11_unibeam_duration_ms(int flying){return flying?2266u:1800u;}
const char *b24_g11_unibeam_clip(int suit,int flying,uint32_t elapsed_ms){
 if(!(suit==0||suit==1||suit==3||suit==4))return 0;
 if(elapsed_ms>=b24_g11_unibeam_duration_ms(flying))return 0;
 if(flying){
  return elapsed_ms<600?hover[0]:elapsed_ms<1000?hover[1]:hover[2];
 }
 return elapsed_ms<400?ground[0]:elapsed_ms<800?ground[1]:ground[2];
}
