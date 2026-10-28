#include "im2_test_opponent.h"
#include <math.h>
#include <string.h>
void im2_test_opponent_reset(Im2TestOpponent *s){if(s){memset(s,0,sizeof(*s));s->player_hp=100.f;}}
int im2_test_opponent_spawn(Im2TestOpponent *s,const B24C1OriginalCollision *city,
 float px,float py,float pz,float heading,uint32_t now){
 if(!s||!city||!city->ready||!isfinite(px)||!isfinite(py)||!isfinite(pz)||!isfinite(heading))return 0;
 /* Debug placement search, not an original scripted spawn. Source geometry
  * must provide both support and room for the same upright body. */
 const float angles[]={0.f,.65f,-.65f,1.3f,-1.3f,3.14159265f};
 for(unsigned distance=0;distance<3;distance++)for(unsigned angle=0;angle<6;angle++){
  const float r=5.f+(float)distance*2.f;
  const float x=px+sinf(heading+angles[angle])*r,y=py+cosf(heading+angles[angle])*r;
  float z=0;
  if(!b24_g75_floor_crossed(city,x,y,pz+8.f,pz-8.f,&z)||
     !b24_g75_body_clear_at(city,x,y,z,.35f,2.24f))continue;
  float exact=0;if(!b24_g75_support_at(city,x,y,z,&exact))continue;
  const float viewer[]={px,py,pz+1.f},target[]={x,y,z+1.f};
  if(im2_test_segment_blocked(city,viewer,target))continue;
  im2_test_opponent_reset(s);s->x=x;s->y=y;s->z=z;s->heading=atan2f(px-x,py-y);
  s->target=(B16TestTarget){{x,y,z+1.f},.7f,100.f,0,1};
  s->spawned=1;s->phase_since=now;s->attack_since=now;s->attack_clock_set=1;return 1;
 }
 return 0;
}
void im2_test_opponent_tick(Im2TestOpponent *s,float px,float py,float pz,uint32_t now,int paused){
 if(!s||!s->spawned||paused||!isfinite(px)||!isfinite(py)||!isfinite(pz))return;
 if(s->target.hp>0.f)s->heading=atan2f(px-s->x,py-s->y);
 if(s->target.hits!=s->observed_hits){
  s->observed_hits=s->target.hits;s->phase=s->target.hp>0.f?IM2_TEST_HURT:IM2_TEST_DOWN;s->phase_since=now;
 }
 if(s->target.hp<=0.f||s->player_hp<=0.f)return;
 if(s->phase!=IM2_TEST_IDLE)return;
 /* Stationary sparring AI. Prototype attack timing/damage are explicitly
  * test-only; native game event timing and player health are untouched. */
 if(!s->player_occluded&&hypotf(px-s->x,py-s->y)<=2.2f&&fabsf(pz-s->z)<1.f&&
    (!s->attack_clock_set||(uint32_t)(now-s->attack_since)>=1200u)){
  s->phase=IM2_TEST_ATTACK;s->phase_since=s->attack_since=now;s->attack_clock_set=1;
  s->player_hp=fmaxf(0.f,s->player_hp-10.f);s->attacks++;
 }
}
void im2_test_opponent_animation_done(Im2TestOpponent *s,uint32_t now){
 if(s&&s->phase!=IM2_TEST_DOWN){s->phase=IM2_TEST_IDLE;s->phase_since=now;}
}
int im2_test_segment_blocked(const B24C1OriginalCollision *city,const float a[3],const float b[3]){
 if(!city||!city->ready||!a||!b)return 1;
 float d[3];for(unsigned k=0;k<3;k++){if(!isfinite(a[k])||!isfinite(b[k]))return 1;d[k]=b[k]-a[k];}
 for(unsigned i=0;i<city->count;i++){
  const float *v=city->faces[i].xyz;
  float e1[3],e2[3],p[3],t[3],q[3];for(unsigned k=0;k<3;k++){e1[k]=v[3+k]-v[k];e2[k]=v[6+k]-v[k];t[k]=a[k]-v[k];}
  p[0]=d[1]*e2[2]-d[2]*e2[1];p[1]=d[2]*e2[0]-d[0]*e2[2];p[2]=d[0]*e2[1]-d[1]*e2[0];
  const float det=e1[0]*p[0]+e1[1]*p[1]+e1[2]*p[2];if(fabsf(det)<1.e-8f)continue;
  const float u=(t[0]*p[0]+t[1]*p[1]+t[2]*p[2])/det;if(u<0||u>1)continue;
  q[0]=t[1]*e1[2]-t[2]*e1[1];q[1]=t[2]*e1[0]-t[0]*e1[2];q[2]=t[0]*e1[1]-t[1]*e1[0];
  const float w=(d[0]*q[0]+d[1]*q[1]+d[2]*q[2])/det;if(w<0||u+w>1)continue;
  const float at=(e2[0]*q[0]+e2[1]*q[1]+e2[2]*q[2])/det;if(at>.001f&&at<.999f)return 1;
 }
 return 0;
}
