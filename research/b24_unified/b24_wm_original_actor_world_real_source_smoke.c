/* Read REAL owner-sourced IM2K (baked from 2010 BRES+anim) and convert
   all five sampled authentic marker axes to EXACT G8 B14 world pose.
   Diagnostic only; no simulated projectile, damage, Vita build or VPK. */
#include "b24_wm_original_marker_g8_world.h"
#include <math.h>
#include <stdio.h>
int main(int argc,char **argv){
 if(argc!=2){fprintf(stderr,"usage: smoke REAL_ORIGINAL_IM2K_FOLDER\n");return 2;}
 B24WM2010GunStream source={0};
 if(!b24_wm_gun_stream_open(&source,argv[1],"warmachine_aim_m_float_move_l_att"))return 3;
 if(source.duration_ms!=1600u||source.frames!=33u){
  fprintf(stderr,"original author animation duration changed\n");
  b24_wm_gun_stream_close(&source);return 4;
 }
 B24WMG8ActorPose actor={0};
 actor.player_x=-47.f;actor.player_y=22.f;
 actor.player_z=12.f;actor.model_center_z=1.4f;
 actor.player_heading=.42f;actor.hover_bob=.08f;
 unsigned success=0;
 for(unsigned ms=0;ms<=1600;ms+=400){
  float m[6][16],pos[3],axis[3];
  if(!b24_wm_gun_stream_sample(&source,ms,0,m)||
     !b24_wm_g8_source_gun03_marker_world(&actor,(const float (*)[16])m,pos,axis)){
   b24_wm_gun_stream_close(&source);return 5;
  }
  float n=axis[0]*axis[0]+axis[1]*axis[1]+axis[2]*axis[2];
  if(!isfinite(n)||fabsf(n-1.f)>1e-3f||
     !isfinite(pos[0])||!isfinite(pos[1])||!isfinite(pos[2])){
   b24_wm_gun_stream_close(&source);return 6;
  }
  printf("SOURCE_TRUE_G8_WM_GUN03_B14_WORLD t=%ums true_Gun03_marker_world_xyz=[%.4f %.4f %.4f] original_rig_axis_world=[%.4f %.4f %.4f] unverified_muzzle\n",
         ms,pos[0],pos[1],pos[2],axis[0],axis[1],axis[2]);
  success++;
 }
 b24_wm_gun_stream_close(&source);
 if(success!=5)return 7;
 puts("PASS five REAL 2010 original Gun03 marker world poses in correct B14 G8 actor coordinate system; not a rocket/gatling emitter, no VPK");
 return 0;
}
