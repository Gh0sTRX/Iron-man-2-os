#include "b24_g83_authentic_timed_router.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void){
 B24G83Input in={0};
 B24G83Selection out;
 B24G83Timeline t={0};
 in.suit_index=B24G83_MARKVI;in.motion=B24G83_GROUND;
 in.axis_y=1.f;in.aim=B24G83_AIM_HAND;
 in.accepted_weapon_event=1;
 assert(b24_g83_timeline_tick(&t,NULL,1000,&in,&out));
 assert(out.stem&&!strcmp(out.stem,"ironman_ironman_aim_ground_move_f_att"));
 assert(out.original_source_duration_ms==866u);
 assert(out.one_shot_not_looping);
 assert(out.needs_2010_hit_event==1);
 in.accepted_weapon_event=0;in.axis_y=-1.f;
 assert(b24_g83_timeline_tick(&t,NULL,1800,&in,&out));
 assert(!strcmp(out.stem,"ironman_ironman_aim_ground_move_f_att"));
 assert(!out.needs_2010_hit_event); /* no repeat gunfire on held pose */
 assert(b24_g83_timeline_tick(&t,NULL,1866,&in,&out));
 assert(!strcmp(out.stem,"ironman_ironman_aim_ground_move_b"));
 assert(t.completed_one_shots==1u);
 in.aim=B24G83_AIM_NONE;in.motion=B24G83_FLIGHT;
 in.axis_y=0;in.axis_x=-1.f;in.previous_flight_dir=B24G83_DIR_F;
 assert(b24_g83_timeline_tick(&t,NULL,2000,&in,&out));
 assert(!strcmp(out.stem,"ironman_ironman_fly_ftol"));
 assert(out.original_source_duration_ms==800u);
 in.previous_flight_dir=B24G83_DIR_L;
 assert(b24_g83_timeline_tick(&t,NULL,2100,&in,&out));
 assert(!strcmp(out.stem,"ironman_ironman_fly_ftol"));
 assert(b24_g83_timeline_tick(&t,NULL,2800,&in,&out));
 assert(!strcmp(out.stem,"ironman_ironman_fly_l"));
 in.transition=B24G83_EVENT_DODGE_RIGHT;
 assert(b24_g83_timeline_tick(&t,NULL,2900,&in,&out));
 assert(!strcmp(out.stem,"ironman_ironman_fly_right_dodge"));
 assert(out.original_source_duration_ms==699u);
 in.transition=B24G83_EVENT_NONE;
 assert(b24_g83_timeline_tick(&t,NULL,3100,&in,&out));
 assert(!strcmp(out.stem,"ironman_ironman_fly_right_dodge"));
 in.grounded_contact_verified=1;in.transition=B24G83_EVENT_FLY_TO_GROUND;
 assert(b24_g83_timeline_tick(&t,NULL,3200,&in,&out));
 assert(!strcmp(out.stem,"ironman_ironman_fly2ground"));
 assert(out.original_source_duration_ms==633u);
 b24_g83_timeline_reset(&t);
 assert(!t.has_pinned_one_shot);
 B24G82Combat combat={0};
 in.motion=B24G83_GROUND;in.transition=B24G83_EVENT_NONE;
 in.grounded_contact_verified=1;in.axis_y=1.f;
 in.aim=B24G83_AIM_HAND;in.accepted_weapon_event=1;
 assert(b24_g83_timeline_tick(&t,&combat,4000,&in,&out));
 assert(!strcmp(out.stem,"ironman_ironman_aim_ground_move_f_att"));
 b24_g82_request_melee(&combat,4050,1,0);
 in.accepted_weapon_event=0;
 assert(b24_g83_timeline_tick(&t,&combat,4051,&in,&out));
 assert(!strcmp(out.stem,"ironman_ironman_ground_combo_1"));
 assert(!t.has_pinned_one_shot);
 assert(out.original_source_duration_ms==266u);

 /* G300 regression: original fly_ftol is a legitimate 800ms one-shot,
  * but it cannot visually mask a newer B14 Rush state or change rigs.
  * This proves route ownership, not physical Vita animation playback. */
 B24G83Timeline switcher={0};
 B24G83Input stage={0};
 stage.suit_index=B24G83_MARKVI;
 stage.motion=B24G83_FLIGHT;
 stage.axis_x=-1.f;
 stage.previous_flight_dir=B24G83_DIR_F;
 assert(b24_g83_timeline_tick(&switcher,NULL,6000,&stage,&out));
 assert(out.stem&&!strcmp(out.stem,"ironman_ironman_fly_ftol"));
 assert(switcher.has_pinned_one_shot);
 stage.motion=B24G83_RUSH;
 assert(b24_g83_timeline_tick(&switcher,NULL,6030,&stage,&out));
 assert(out.stem&&!strcmp(out.stem,"ironman_ironman_fly_f_rush"));
 assert(!switcher.has_pinned_one_shot);
 assert(switcher.completed_one_shots==0u&&switcher.interrupted_one_shots==1u);
 stage.motion=B24G83_FLIGHT;
 stage.previous_flight_dir=B24G83_DIR_IDLE;
 assert(b24_g83_timeline_tick(&switcher,NULL,6050,&stage,&out));
 assert(out.stem&&!strcmp(out.stem,"ironman_ironman_fly_l"));
 stage.motion=B24G83_GROUND;
 stage.axis_x=0.f;stage.axis_y=1.f;
 stage.aim=B24G83_AIM_HAND;
 stage.accepted_weapon_event=1;
 assert(b24_g83_timeline_tick(&switcher,NULL,6100,&stage,&out));
 assert(out.stem&&!strcmp(out.stem,"ironman_ironman_aim_ground_move_f_att"));
 assert(switcher.has_pinned_one_shot);
 stage.suit_index=B24G83_WARMACHINE;
 stage.accepted_weapon_event=0;
 assert(b24_g83_timeline_tick(&switcher,NULL,6110,&stage,&out));
 assert(out.stem&&!strcmp(out.stem,"warmachine_warmachine_aim_ground_move_f"));
 assert(!switcher.has_pinned_one_shot);
 assert(switcher.completed_one_shots==0u&&switcher.interrupted_one_shots==2u);
 stage.motion=B24G83_HOVER;
 stage.accepted_weapon_event=1;
 assert(b24_g83_timeline_tick(&switcher,NULL,6200,&stage,&out));
 assert(out.stem&&!strcmp(out.stem,"warmachine_warmachine_aim_float_move_f_att"));
 assert(switcher.has_pinned_one_shot);
 stage.suit_index=B24G83_MARKVI;
 stage.accepted_weapon_event=0;
 assert(b24_g83_timeline_tick(&switcher,NULL,6220,&stage,&out));
 assert(out.stem&&!strcmp(out.stem,"ironman_ironman_aim_float_move_f"));
 assert(!switcher.has_pinned_one_shot&&switcher.interrupted_one_shots==3u);
 assert(switcher.completed_one_shots==0u);
 puts("PASS G83 original 2010 animation duration timeline: moving attack 866ms, flight steering 800ms, dodge 699ms, landing 633ms, G82 three-hit priority; paused, no invented hit frame, no repeated weapon fire, NO VPK");
 return 0;
}
