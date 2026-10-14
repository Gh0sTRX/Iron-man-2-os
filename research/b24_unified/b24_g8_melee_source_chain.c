#include "b24_g8_melee_source_chain.h"
#include <stddef.h>

static const char *const clips[6]={
 NULL,
 "ironman_ironman_ground_combo_1",
 "ironman_ironman_ground_combo_2",
 "ironman_ironman_ground_combo_3",
 "ironman_ironman_ground_combo_1_end",
 "ironman_ironman_ground_combo_2_end"
};
static const uint32_t author_duration_ms[6]={0,266,300,500,233,300};
void b24_g8_melee_press(B24G8MeleeChain *a,uint32_t now){
 if(!a)return;
 if(!a->phase){a->phase=1;a->started_ms=now;a->buffered=0;}
 else if(a->phase<3)a->buffered=1;
}
const char *b24_g8_melee_tick(B24G8MeleeChain *a,uint32_t now){
 if(!a||!a->phase)return NULL;
 unsigned steps=0;
 while(a->phase&&steps++<6u){
  uint32_t duration=author_duration_ms[a->phase];
  uint32_t age=now-a->started_ms;
  if(age<duration)break;
  a->started_ms+=duration;
  if(a->phase==1||a->phase==2){
   const unsigned old=a->phase;
   a->completed_attacks++;
   if(a->buffered){a->phase=old+1;a->buffered=0;}
   else a->phase=old==1?4:5;
  }else{
   if(a->phase==3)a->completed_attacks++;
   a->phase=0;a->buffered=0;
  }
 }
 return a->phase?clips[a->phase]:NULL;
}
int b24_g8_melee_active(const B24G8MeleeChain *a){
 return a&&a->phase!=0;
}
