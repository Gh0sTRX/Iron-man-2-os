#include "b24_g83_unified_movement_aim.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void expect(B24G83Input x,const char *stem){
 B24G83Selection out={0};
 assert(b24_g83_select_original_motion(&x,&out));
 assert(out.stem&&strcmp(out.stem,stem)==0);
 assert(out.source_authored_name);
 assert(!out.input_semantics_verified_original_ios);
}
int main(void){
 B24G83Input wm={0};
 wm.suit_index=B24G83_WARMACHINE;
 wm.motion=B24G83_GROUND;
 wm.aim=B24G83_AIM_NONE;
 expect(wm,"warmachine_warmachine_aim_ground_idle");
 wm.axis_y=-1;
 expect(wm,"warmachine_warmachine_aim_ground_move_b");
 wm.axis_x=-1;wm.axis_y=0;
 expect(wm,"warmachine_warmachine_aim_ground_move_l");
 wm.axis_x=1;
 expect(wm,"warmachine_warmachine_aim_ground_move_r");
 wm.axis_x=0;wm.axis_y=1;
 expect(wm,"warmachine_warmachine_aim_ground_move_f");
 wm.motion=B24G83_RUSH;
 expect(wm,"warmachine_warmachine_aim_fly_m");
 wm.motion=B24G83_HOVER;wm.axis_x=0;wm.axis_y=0;
 expect(wm,"warmachine_warmachine_aim_float_idle");
 wm.aim=B24G83_AIM_HAND;wm.motion=B24G83_GROUND;
 wm.accepted_weapon_event=1;
 expect(wm,"warmachine_warmachine_aim_ground_idle_att");
 puts("G165 PASS original 2010 War Machine directional grounded 5 clips, source hover and temporary no-native-RUSH flight pose; no invented attacks, no Vita hardware claims");
 return 0;
}
