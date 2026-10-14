#include "b24_wm_original_marker_g8_world.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static int near(float a,float b){return fabsf(a-b)<2.e-4f;}
int main(void){
 B24WMG8ActorPose actor={0};
 actor.player_x=8.f;actor.player_y=11.f;actor.player_z=4.f;
 actor.model_center_z=1.25f;actor.hover_bob=.2f;actor.player_heading=0.f;
 float p[3]={1.f,2.f,3.f},w[3]={0};
 assert(b24_wm_g8_marker_world_point(&actor,p,w));
 assert(near(w[0],7.f)&&near(w[1],9.f)&&near(w[2],5.95f));
 actor.player_heading=1.57079632679f;
 assert(b24_wm_g8_marker_world_point(&actor,p,w));
 assert(near(w[0],6.f)&&near(w[1],12.f)&&near(w[2],5.95f));
 float d[3]={1.f,0.f,0.f},wd[3]={0};
 assert(b24_wm_g8_marker_world_direction(&actor,d,wd));
 assert(near(wd[0],0.f)&&near(wd[1],1.f)&&near(wd[2],0.f));
 float m[6][16];memset(m,0,sizeof(m));
 /* Source originals use two distinct 2010 Gun03 marker matrices,
    indices 4 and 5 in verified IM2K files. */
 m[4][3]=1.f;m[4][7]=2.f;m[4][11]=3.f;m[4][15]=1.f;
 m[5][3]=1.02f;m[5][7]=2.f;m[5][11]=3.f;m[5][15]=1.f;
 float tip[3],axis[3];
 assert(b24_wm_g8_source_gun03_marker_world(&actor,(const float (*)[16])m,tip,axis));
 assert(near(tip[0],6.f)&&near(tip[1],12.02f)&&near(tip[2],5.95f));
 assert(near(axis[0],0.f)&&near(axis[1],1.f));
 float old=axis[1];actor.player_x+=10.f;actor.player_y-=7.f;
 assert(b24_wm_g8_source_gun03_marker_world(&actor,(const float (*)[16])m,tip,axis));
 assert(near(tip[0],16.f)&&near(tip[1],5.02f)&&near(axis[1],old));
 actor.player_heading=0.f;
 assert(b24_wm_g8_source_gun03_marker_world(&actor,(const float (*)[16])m,tip,axis));
 assert(near(axis[0],-1.f)&&near(axis[1],0.f));
 actor.player_heading=NAN;
 assert(!b24_wm_g8_source_gun03_marker_world(&actor,(const float (*)[16])m,tip,axis));
 puts("PASS original WM source Gun03 marker -> exact B14/G8 third-person"
      " world translation and heading (Z-up), real two-marker direction,"
      " invalid actor guard. NO rocket/Gatling muzzle assignment or VPK.");
 return 0;
}
