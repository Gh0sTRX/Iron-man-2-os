#include "b24_g11_practice_melee_feedback.h"
#include <math.h>
int b24_g11_practice_melee_hit(B24G11PracticeMeleeFeedback *st,
 const B24G10PracticeTarget *t,
 float px,float py,float pz,
 uint32_t now,int edge,int ground){
 if(!st||!b24_g10_practice_target_valid(t)||
    !isfinite(px)||!isfinite(py)||!isfinite(pz))return 0;
 if(!edge||!ground)return 0;
 float horizontal=hypotf(px-t->x,py-t->y);
 float vertical=fabsf((pz+1.f)-t->z);
 if(horizontal>2.5f+t->radius||vertical>2.3f){
  st->whiffs++;return 0;
 }
 /* Only accepted melee swing produces hit indicator. Do not claim hit
    frames are original 2010 authored or change the invincible HP. */
 if(st->ever_hit&&(uint32_t)(now-st->last_hit_ms)<180u)return 0;
 st->ever_hit=1;st->last_hit_ms=now;st->flash_until_ms=now+190u;
 st->successful_hits++;
 return 1;
}
float b24_g11_practice_hit_flash(const B24G11PracticeMeleeFeedback *s,uint32_t now){
 if(!s||!s->ever_hit||(int32_t)(s->flash_until_ms-now)<=0)return 0.f;
 float v=(float)(s->flash_until_ms-now)/190.f;
 return v>1.f?1.f:v;
}
