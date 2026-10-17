#include "b24_g83_unified_movement_aim.h"
#include "b24_g172_wm_ground_m_source.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void test_one(int fire,unsigned dir,const char *expected,unsigned ms){
 B24G83Input in={0};
 B24G83Selection out={0};
 in.suit_index=B24G83_WARMACHINE;
 in.motion=B24G83_GROUND;
 in.aim=B24G83_AIM_M_UNCLASSIFIED;
 in.accepted_weapon_event=fire;
 switch(dir){
  case 1:in.axis_y=1.f;break;
  case 2:in.axis_y=-1.f;break;
  case 3:in.axis_x=-1.f;break;
  case 4:in.axis_x=1.f;break;
 }
 assert(b24_g83_select_original_motion(&in,&out));
 assert(out.stem&&strcmp(out.stem,expected)==0);
 assert(out.original_source_duration_ms==ms);
 assert(out.source_authored_name==1);
 assert(out.one_shot_not_looping==!!fire);
 assert(out.needs_2010_hit_event==!!fire);
 assert(out.input_semantics_verified_original_ios==0);
 assert(b24_g172_wm_m_ground_duration(out.stem)==ms);
}
int main(void){
 const char *idle[5]={
 "warmachine_warmachine_aim_m_ground_idle",
 "warmachine_warmachine_aim_m_ground_move_f",
 "warmachine_warmachine_aim_m_ground_move_b",
 "warmachine_warmachine_aim_m_ground_move_l",
 "warmachine_warmachine_aim_m_ground_move_r"};
 const char *att[5]={
 "warmachine_warmachine_aim_m_ground_idle_att",
 "warmachine_warmachine_aim_m_ground_move_f_att",
 "warmachine_warmachine_aim_m_ground_move_b_att",
 "warmachine_warmachine_aim_m_ground_move_l_att",
 "warmachine_warmachine_aim_m_ground_move_r_att"};
 unsigned fires[5]={1600,866,1399,866,866};
 for(unsigned dir=0;dir<5;dir++){
  test_one(0,dir,idle[dir],1600);
  test_one(1,dir,att[dir],fires[dir]);
 }
 B24G83Input wm={0}; B24G83Selection out={0};
 wm.suit_index=B24G83_WARMACHINE;wm.motion=B24G83_GROUND;
 wm.aim=B24G83_AIM_HAND;
 assert(b24_g83_select_original_motion(&wm,&out));
 assert(!strcmp(out.stem,"warmachine_warmachine_aim_ground_idle"));
 wm.aim=B24G83_AIM_NONE;wm.motion=B24G83_RUSH;
 assert(b24_g83_select_original_motion(&wm,&out));
 assert(!strcmp(out.stem,"warmachine_warmachine_aim_fly_m"));
 wm.motion=B24G83_HOVER;wm.aim=B24G83_AIM_M_UNCLASSIFIED;
 assert(b24_g83_select_original_motion(&wm,&out));
 assert(!strcmp(out.stem,"warmachine_warmachine_aim_m_float_idle"));
 assert(!b24_g172_wm_m_ground_clip(5,0));
 assert(!b24_g172_wm_m_ground_duration("warmachine_not_authored"));
 puts("G172 PASS 10 authentic 2010 WM M-ground clip names/durations, 5 directions, fire-event separate from native hit semantics, hover/rush/basic aim preserved. NO VPK.");
 return 0;
}
