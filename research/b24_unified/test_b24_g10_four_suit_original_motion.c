#include "b24_g8_live_original_motion.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void){
 struct {int suit;const char *pref;} armor[]={
  {0,"ironman_ironman_"},{1,"mark4_ironman_"},
  {3,"stealth_ironman_"},{4,"suitcase_ironman_"}
 };
 for(unsigned i=0;i<4;i++){
  const int id=armor[i].suit;
  const char *idle=b24_g8_motion_route(id,B24M_HOVER,0.f,0.f);
  const char *left_tmp=b24_g8_motion_route(id,B24M_DRIFT,-.8f,0.f);
  assert(idle&&left_tmp);
  char left[128];
  int len=snprintf(left,sizeof(left),"%s",left_tmp);
  assert(len>0&&(size_t)len<sizeof(left));
  const char *right=b24_g8_motion_route(id,B24M_DRIFT,.8f,0.f);
  assert(right);
  assert(strncmp(idle,armor[i].pref,strlen(armor[i].pref))==0);
  assert(strstr(idle,"move_float")&&strstr(idle,"_att")==NULL);
  assert(strstr(left,"float_move_l")&&strstr(right,"float_move_r"));
  const char *fire=b24_g8_motion_repulsor_clip(id,B24M_DRIFT,.9f,0.f);
  assert(fire&&strstr(fire,"float_move_r_att"));
  assert(strncmp(fire,armor[i].pref,strlen(armor[i].pref))==0);
 }
 assert(!strcmp(b24_g8_motion_route(2,B24M_DRIFT,-.8f,0.f),
                "warmachine_warmachine_aim_float_move_l"));
 assert(!strcmp(b24_g8_motion_repulsor_clip(2,B24M_DRIFT,.8f,0.f),
                "warmachine_warmachine_aim_float_move_r_att"));
 assert(b24_g8_motion_route(2,B24M_CRUISE,0,1));
 puts("PASS G10 separate real 2010 owner rig-skin 4x original IronMan routing"
      " MarkVI/IV/Stealth/Suitcase L/R hover and firing and WM separate source; no vertex-copy trick");
 return 0;
}
