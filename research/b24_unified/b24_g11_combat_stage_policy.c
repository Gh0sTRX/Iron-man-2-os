#include "b24_g11_combat_stage_policy.h"
#include <math.h>
int b24_g11_stage_allows_hand_attack(int flying,int stage){
 return (!flying||stage<=1)&&stage>=0;
}
int b24_g11_combat_stage_policy(const B24G11CombatInput *in,
                                B24G11CombatDecision *out){
 if(!in||!out||!isfinite(in->move_x)||!isfinite(in->move_y)||
    fabsf(in->move_x)>1.01f||fabsf(in->move_y)>1.01f||
    in->prior_flight_stage<0||in->prior_flight_stage>3)return 0;
 B24G11CombatDecision d={0};
 d.move_x=in->move_x;d.move_y=in->move_y;
 d.boost=in->boost!=0;
 /* Driver cannot enter stage2/RUSH while holding a hand weapon during
    stage1. Stage2/RUSH is NOT suddenly slowed because R was pressed:
    incoming shots are ignored until back to stage1/ground. */
 const int prohibit_air_attack=in->flying&&in->prior_flight_stage>=2;
 const int restricting=in->trigger&&!in->paused&&!prohibit_air_attack;
 if(restricting){
  float v=hypotf(d.move_x,d.move_y);
  if(v>.82f){
   float q=.82f/v;
   d.move_x*=q;d.move_y*=q;
  }
  d.boost=0;
  d.force_walk=!in->flying;d.force_stage1=in->flying;
 }
 const int stage_allows=!prohibit_air_attack&&!in->paused;
 d.allow_repulsor=in->trigger&&stage_allows;
 d.allow_unibeam=in->trigger&&stage_allows;
 /* No Stage2 missile animation/source impact researched yet; do NOT
    accidentally introduce an unproved flying missile emission. */
 d.allow_missile=in->trigger&&stage_allows;
 *out=d;
 return 1;
}
