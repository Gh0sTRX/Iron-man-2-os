#include "b24_g169_native_source_unibeam.h"
#include "b24_g11_original_unibeam_sequence.h"
#include <stddef.h>
static const char *const suitcase_ground[3]={
 "suitcase_ironman_aim_ground_beam1",
 "suitcase_ironman_aim_ground_beam2",
 "suitcase_ironman_aim_ground_beam3"};
static const char *const suitcase_hover[3]={
 "suitcase_ironman_aim_float_beam1",
 "suitcase_ironman_aim_float_beam2",
 "suitcase_ironman_aim_float_beam3"};
static const char *const native_markvi_ground[3]={
 "ironman_ironman_aim_ground_beam1",
 "ironman_ironman_aim_ground_beam2",
 "ironman_ironman_aim_ground_beam3"};
static const char *const native_markvi_hover[3]={
 "ironman_ironman_aim_float_beam1",
 "ironman_ironman_aim_float_beam2",
 "ironman_ironman_aim_float_beam3"};
int b24_g169_native_beam_begin(B24G169Beam *actor,int suit,int hover,uint32_t at_ms){
 if(!actor||!(suit==0||suit==4)||!(hover==0||hover==1))return 0;
 actor->suit=suit;actor->hover=hover;actor->began_ms=at_ms;actor->active=1;
 return 1;
}
const char *b24_g169_native_beam_clip(B24G169Beam *actor,int suit,int hover,
                                      int flight_stage,uint32_t now_ms){
 if(!actor||!actor->active)return NULL;
 if(suit!=actor->suit||hover!=actor->hover||flight_stage>=2){
  actor->active=0;return NULL;
 }
 const uint32_t age=(uint32_t)(now_ms-actor->began_ms);
 const uint32_t end=b24_g11_unibeam_duration_ms(hover);
 if(age>=end){actor->active=0;return NULL;}
 /* Genuine source IM2V exact phase lengths from 2010 B18 registry:
  * grounded BEAM1=400ms, BEAM2=400ms, BEAM3=1000ms;
  * hover BEAM1=600ms, BEAM2=400ms, BEAM3=1266ms.
  * No invented sockets/damage/beam VFX or stage2/RUSH weapons. */
 int phase=age<(hover?600u:400u)?0:
           age<(hover?1000u:800u)?1:2;
 if(suit==4)return (hover?suitcase_hover:suitcase_ground)[phase];
 return (hover?native_markvi_hover:native_markvi_ground)[phase];
}
