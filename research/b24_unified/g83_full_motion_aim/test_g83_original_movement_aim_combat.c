#include "b24_g83_unified_movement_aim.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static B24G83Input mk(void){
 B24G83Input in={0};
 in.suit_index=B24G83_MARKVI;
 in.motion=B24G83_GROUND;
 in.axis_y=1.f;
 return in;
}
static void route(B24G83Input in,const char *want,int oneshot){
 B24G83Selection out={0};
 assert(b24_g83_select_original_motion(&in,&out));
 if(want){
  assert(out.stem&&strcmp(out.stem,want)==0);
  assert(out.source_authored_name);
 }else assert(out.stem==NULL);
 assert(out.one_shot_not_looping==oneshot);
 assert(!out.input_semantics_verified_original_ios);
}
int main(void){
 B24G83Input in=mk();
 route(in,"ironman_ironman_walk_f",0);
 in.axis_y=-.5f;
 route(in,"ironman_ironman_walk_b",0);
 in.axis_y=0;in.axis_x=-1;
 route(in,"ironman_ironman_walk_l",0);
 in.axis_x=1;
 route(in,"ironman_ironman_walk_r",0);
 in.axis_x=0;in.axis_y=1;in.run=1;
 route(in,"ironman_ironman_run",0);
 in.aim=B24G83_AIM_HAND;
 route(in,"ironman_ironman_aim_ground_move_f",0);
 in.accepted_weapon_event=1;
 route(in,"ironman_ironman_aim_ground_move_f_att",0);
 in.axis_y=0;in.aim=B24G83_AIM_DUAL;
 route(in,"ironman_ironman_aim_ground_idle_att_2h",0);
 in.accepted_weapon_event=0;
 route(in,"ironman_ironman_aim_ground_idle_2h",0);
 in.aim=B24G83_AIM_LEFT;
 route(in,"ironman_ironman_aim_ground_idle_l",0);
 in.aim=B24G83_AIM_M_UNCLASSIFIED;
 route(in,"ironman_ironman_aim_m_ground_idle",0);
 in.accepted_weapon_event=1;in.axis_y=-1;
 route(in,"ironman_ironman_aim_m_ground_move_b_att",0);
 in.motion=B24G83_HOVER;in.aim=B24G83_AIM_NONE;
 in.accepted_weapon_event=0;
 route(in,"ironman_ironman_air_move_b",0);
 in.aim=B24G83_AIM_HAND;in.axis_y=0;
 route(in,"ironman_ironman_aim_float_idle",0);
 in.accepted_weapon_event=1;in.aim=B24G83_AIM_DUAL;
 route(in,"ironman_ironman_aim_float_idle_att_2h",0);
 in.motion=B24G83_FLIGHT;in.axis_y=1;in.axis_x=0;in.aim=B24G83_AIM_NONE;
 in.accepted_weapon_event=0;
 route(in,"ironman_ironman_fly_f",0);
 in.axis_y=0;in.axis_x=-1;in.previous_flight_dir=B24G83_DIR_F;
 route(in,"ironman_ironman_fly_ftol",1);
 in.axis_x=0;in.axis_y=1;in.previous_flight_dir=B24G83_DIR_L;
 route(in,"ironman_ironman_fly_ltof",1);
 in.previous_flight_dir=B24G83_DIR_IDLE;in.motion=B24G83_RUSH;
 route(in,"ironman_ironman_fly_f_rush",0);
 in.motion=B24G83_HOVER;in.transition=B24G83_EVENT_GROUND_TO_HOVER;
 route(in,"ironman_ironman_ground_float",1);
 in.transition=B24G83_EVENT_DODGE_LEFT;
 route(in,"ironman_ironman_fly_left_dodge",1);
 in.transition=B24G83_EVENT_DODGE_RIGHT;
 route(in,"ironman_ironman_fly_right_dodge",1);
 in.transition=B24G83_EVENT_FLY_TO_GROUND;in.grounded_contact_verified=0;
 route(in,NULL,0);
 in.grounded_contact_verified=1;
 route(in,"ironman_ironman_fly2ground",1);
 in.transition=B24G83_EVENT_NONE;in.suit_index=B24G83_WARMACHINE;
 in.motion=B24G83_GROUND;in.aim=B24G83_AIM_NONE;
 route(in,NULL,0);
 in.aim=B24G83_AIM_HAND;in.axis_y=1.f;
 route(in,"warmachine_warmachine_aim_ground_move_f",0);
 in.motion=B24G83_HOVER;in.aim=B24G83_AIM_M_UNCLASSIFIED;
 in.accepted_weapon_event=1;
 route(in,"warmachine_warmachine_aim_m_float_move_f_att",0);
 in.motion=B24G83_FLIGHT;
 route(in,"warmachine_warmachine_aim_fly_m",0);
 in.motion=B24G83_RUSH;
 route(in,NULL,0); /* no invented genuine WM rush source */
 in.suit_index=5;in.motion=B24G83_GROUND;
 route(in,NULL,0); /* no Mark V incorrectly using Mark VI skin */
 in.suit_index=B24G83_MARKVI;
 in.axis_x=NAN;
 B24G83Selection o;
 assert(!b24_g83_select_original_motion(&in,&o));
 in=mk();in.paused=1;
 route(in,NULL,0);
 B24G82Combat combat={0};
 b24_g82_request_melee(&combat,1000,1,0);
 in.paused=0;in.aim=B24G83_AIM_HAND;in.accepted_weapon_event=1;
 assert(b24_g83_select_combined(&combat,1005,&in,&o));
 assert(o.stem&&!strcmp(o.stem,"ironman_ironman_ground_combo_1"));
 assert(o.one_shot_not_looping&&o.needs_2010_hit_event);
 b24_g82_request_melee(&combat,1006,1,0);
 assert(b24_g83_select_combined(&combat,1266,&in,&o));
 assert(!strcmp(o.stem,"ironman_ironman_ground_combo_2"));
 printf("PASS G83 all original source locomotion+aim tests: 4way walk / run / aimed move+fire / dual+left / M (unclassified) / relaxed hover / directional fly-turn / RUSH / land guard / WM native clips / G82 combo wins / unsupported suit safe fallback. No source hit frame invented; NO VPK.\n");
 return 0;
}
