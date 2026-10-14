#include "b24_g8_wm_shoulder_gameplay.h"
#include <math.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>

static int count_kind(const B24WMOutput *out,B24WMEventKind type){
 int n=0;
 for(unsigned i=0;i<out->event_count;i++)if(out->events[i].kind==type)n++;
 return n;
}
int main(void){
 B24WMConfig cfg; b24_wm_default_config(&cfg);
 assert(cfg.skill_active_seconds==20.f && cfg.skill_cooldown_seconds==20.f);
 B24WMShoulder wm={0};assert(b24_wm_init(&wm,&cfg));
 B24WMInput in={0};
 in.war_machine_selected=1;
 in.dt=.1f;
 in.muzzle_right_gatling=(B24WMVec3){1.f,0.f,2.f};
 in.muzzle_left_rocket=(B24WMVec3){-1.f,0.f,2.f};
 in.rocket_aim_direction=(B24WMVec3){0.f,1.f,0.f};
 B24WMTarget targets[]={
  {17,{3.f,7.f,2.f},1,1,0},
  {21,{8.f,3.f,3.f},1,1,1}, /* occluded: never fire */
  {24,{90.f,0.f,0.f},1,1,0}, /* out of range */
  {33,{2.f,4.f,2.f},0,1,0}, /* not alive */
 };
 B24WMOutput o={0};
 in.trigger_skill_edge=1;
 in.real_enemies_loaded=0;
 in.targets=targets;in.target_count=4;
 assert(b24_wm_tick(&wm,&in,&o));
 assert(o.active && o.event_count==0 && o.locked_target_id==-1);
 in.trigger_skill_edge=0;in.real_enemies_loaded=1;
 assert(b24_wm_tick(&wm,&in,&o));
 assert(o.active&&o.locked_target_id==17);
 assert(count_kind(&o,B24WM_EVENT_GATLING_SHOT_RIGHT)==1);
 assert(count_kind(&o,B24WM_EVENT_GATLING_SPARK_RIGHT)==1);
 assert(o.events[0].origin.x==1.f);
 assert(o.events[0].target_id==17);
 assert(o.events[0].damage==1.f);
 assert(fabsf(o.events[0].direction.y)>.7f);
 in.trigger_missile_edge=1;
 assert(b24_wm_tick(&wm,&in,&o));
 assert(count_kind(&o,B24WM_EVENT_MISSILE_LAUNCH_LEFT)==1);
 assert(count_kind(&o,B24WM_EVENT_MISSILE_EXHAUST_LEFT)==1);
 assert(o.events[0].origin.x==-1.f); /* LEFT, not right */
 in.trigger_missile_edge=0;
 assert(b24_wm_tick(&wm,&in,&o));
 assert(count_kind(&o,B24WM_EVENT_MISSILE_LAUNCH_LEFT)==0);
 /* turret maintains acquired target regardless of the player's
    changing facing; state has no player heading/camera fields */
 targets[0].occluded=1;
 assert(b24_wm_tick(&wm,&in,&o));
 assert(o.locked_target_id==-1 && count_kind(&o,B24WM_EVENT_GATLING_SHOT_RIGHT)==0);
 targets[1].occluded=0;
 assert(b24_wm_tick(&wm,&in,&o));
 assert(o.locked_target_id==21); /* true right-shoulder independent new lock */
 targets[1].alive=0;
 assert(b24_wm_tick(&wm,&in,&o));
 assert(o.locked_target_id==-1);
 targets[0].occluded=0;
 /* 20s total elapsed active -> 20s cooldown after expiry. */
 for(int i=0;i<210;i++){
  assert(b24_wm_tick(&wm,&in,&o));
 }
 assert(!o.active && o.cooldown_left>0 && o.cooldown_left<=20.f);
 assert(wm.fired_gatling>0 && wm.fired_missiles==1);
 in.trigger_skill_edge=1;
 assert(b24_wm_tick(&wm,&in,&o));
 assert(!o.active && !o.ready); /* cooldown cannot bypass */
 in.trigger_skill_edge=0;
 for(int i=0;i<211;i++)assert(b24_wm_tick(&wm,&in,&o));
 assert(o.ready&&!o.active);
 in.trigger_skill_edge=1;
 assert(b24_wm_tick(&wm,&in,&o));assert(o.active);
 in.war_machine_selected=0;
 assert(b24_wm_tick(&wm,&in,&o));
 assert(!o.active && o.event_count==0); /* switching suits cancels */
 in.dt=NAN;assert(!b24_wm_tick(&wm,&in,&o));
 in.dt=.1f;in.war_machine_selected=1;in.target_count=1025;
 assert(!b24_wm_tick(&wm,&in,&o));
 puts("PASS WM left missile right target-independent Gatling game events:"
      " original shoulder orientation, actual alive/visible/LOS, target"
      " switch, no ghost actors, shot cooldown, 20s active + 20s recharge,"
      " right muzzle and valid event directions; host-only no VPK");
 return 0;
}
