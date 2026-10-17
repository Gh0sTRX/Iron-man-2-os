#include "b24_g173_authored_beam_priority.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void yes(int suit,const char *s){
 assert(b24_g173_is_authored_beam(suit,s));
 assert(b24_g173_authored_beam_pose_priority(suit,s,0));
 assert(!b24_g173_authored_beam_pose_priority(suit,s,1));
}
static void no(int suit,const char *s){
 assert(!b24_g173_is_authored_beam(suit,s));
 assert(!b24_g173_authored_beam_pose_priority(suit,s,0));
}
int main(void){
 static const char *const phase[]={"beam1","beam2","beam3"};
 static const char *const mode[]={"ground","float"};
 char name[160];
 unsigned count=0;
 for(int v=0;v<2;v++)for(int m=0;m<2;m++)for(int k=0;k<3;k++){
  int suit=v?4:0;
  const char *prefix=v?"suitcase_ironman_aim_":"ironman_ironman_aim_";
  int n=snprintf(name,sizeof(name),"%s%s_%s",prefix,mode[m],phase[k]);
  assert(n>0&&(size_t)n<sizeof(name));
  yes(suit,name);
  no(2,name); /* WM has NO G169 source beam */
  no(v?0:4,name); /* no mismatched source-armor skin */
  count++;
 }
 no(4,"ironman_ironman_aim_ground_beam1");
 no(4,"suitcase_ironman_aim_ground_beam4");
 no(4,"suitcase_ironman_aim_m_ground_idle");
 no(4,"suitcase_ironman_aim_ground_idle_att");
 no(0,"ironman_ironman_aim_ground_idle_att");
 no(0,"ironman_ironman_ground_combo_1");
 no(0,"ironman_ironman_fly_f_rush");
 no(2,"warmachine_warmachine_aim_m_ground_move_f_att");
 no(4,0);
 assert(!b24_g173_authored_beam_pose_priority(4,0,0));
 puts("G173 PASS exact 12 source-authored 2010 G169 MarkV/MarkVI three-phase ground/float Beam IM2V stems; safe negative weapon/melee/WM cases, melee owns first; NO VPK");
 return count==12?0:1;
}
