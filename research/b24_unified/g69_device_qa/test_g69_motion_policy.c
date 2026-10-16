#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "g69_motion_policy.h"
static void check(G69Stage s,float x,float y,const char *name){
 G69Playback p=g69_select((G69Input){x,y,s,0,0});
 assert(p.original_anim&&strcmp(p.original_anim,name)==0);
}
int main(void){
 check(G69_GROUND,0,0,"IronMan_Ground_Idel.anim");
 check(G69_GROUND,0,1,"IronMan_Walk_F.anim");
 check(G69_GROUND,0,-1,"IronMan_Walk_B.anim");
 check(G69_GROUND,-1,0,"IronMan_Walk_L.anim");
 check(G69_GROUND,1,0,"IronMan_Walk_R.anim");
 check(G69_HOVER,0,1,"IronMan_Aim_Float_move_F.anim");
 check(G69_HOVER,0,-1,"IronMan_Aim_Float_move_B.anim");
 check(G69_HOVER,-1,0,"IronMan_Aim_Float_move_L.anim");
 check(G69_HOVER,1,0,"IronMan_Aim_Float_move_R.anim");
 check(G69_CRUISE,0,1,"Ironman_Fly_F.anim");
 check(G69_CRUISE,0,-1,"Ironman_Fly_B.anim");
 check(G69_CRUISE,-1,0,"Ironman_Fly_L.anim");
 check(G69_CRUISE,1,0,"Ironman_Fly_R.anim");
 check(G69_RUSH,0,1,"Ironman_Fly_F_RUSH.anim");
 check(G69_RUSH,0,-1,"Ironman_Fly_B.anim");
 check(G69_RUSH,-1,0,"Ironman_Fly_L.anim");
 assert(g69_select((G69Input){0,0,G69_GROUND,0,1}).one_shot);
 assert(g69_select((G69Input){0,0,G69_GROUND,1,0}).one_shot);
 assert(g69_dir(0,.15f)==G69_STOP);
 assert(g69_dir(NAN,1.f)==G69_STOP);
 puts("PASS G69 all four ground, hover, cruise and rush-safe original motion directions");
 return 0;
}
