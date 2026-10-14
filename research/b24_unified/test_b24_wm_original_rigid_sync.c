#include "b24_wm_original_rigid_sync.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static int closef(float a,float b){return fabsf(a-b)<.0003f;}
static void emit(void){
 FILE *f=fopen("warmachine_aim_float_idle.im2k","wb");assert(f);
 unsigned char h[20]={'I','M','2','K'};
 const unsigned v[4]={6u,3u,20u,100u};
 for(int j=0;j<4;j++)for(int k=0;k<4;k++)
   h[4+j*4+k]=(unsigned char)(v[j]>>(8*k));
 assert(fwrite(h,1,20,f)==20);
 for(int frame=0;frame<3;frame++)
  for(int n=0;n<6;n++)for(int k=0;k<16;k++){
   float val=(k==15)?1.f:0.f;
   if(k==3&&(n==4||n==5))val=1.f+(float)frame+(n==5?.02f:0.f);
   if(k==7&&(n==4||n==5))val=2.f;
   if(k==11&&(n==4||n==5))val=3.f;
   assert(fwrite(&val,4,1,f)==1);
  }
 fclose(f);
}
int main(void){
 emit();
 B24WMRigidSync sync={0};
 B24WMG8ActorPose a={0};
 a.player_x=17.f;a.player_y=-9.f;a.player_z=4.f;a.model_center_z=1.3f;
 const char *body="warmachine_warmachine_aim_float_idle";
 assert(b24_wm_rigid_sync_tick(&sync,".",body,3,100,1000,1000,1,&a));
 assert(sync.candidate_pose_valid&&sync.opens==1&&sync.samples==1);
 assert(closef(sync.world_tip[0],15.98f)&&closef(sync.world_tip[1],-11.f));
 assert(closef(sync.world_axis[0],-1.f)&&closef(sync.world_axis[1],0.f));
 assert(b24_wm_rigid_sync_tick(&sync,".",body,3,100,1000,1025,1,&a));
 assert(sync.opens==1&&sync.samples==2);
 assert(closef(sync.world_tip[0],15.48f));
 /* B14 actor heading is not tied to gun animation state; change freely. */
 a.player_heading=1.57079632679f;
 assert(b24_wm_rigid_sync_tick(&sync,".",body,3,100,1000,1050,1,&a));
 assert(closef(sync.world_tip[0],15.f)&&closef(sync.world_tip[1],-6.98f));
 assert(closef(sync.world_axis[0],0.f)&&closef(sync.world_axis[1],1.f));
 /* An original source file not found MUST NOT invent gun position or fire */
 const char *unknown="warmachine_warmachine_source_unavailable";
 assert(b24_wm_rigid_sync_tick(&sync,".",unknown,3,100,1000,1075,1,&a));
 assert(!sync.candidate_pose_valid&&sync.source_missing&&sync.missing_names==1);
 assert(b24_wm_rigid_sync_tick(&sync,".",unknown,3,100,1000,1090,1,&a));
 assert(sync.missing_names==1); /* never probe file storage each frame */
 assert(b24_wm_rigid_sync_tick(&sync,".",body,3,100,1000,1100,1,&a));
 assert(sync.candidate_pose_valid&&sync.opens==2);
 /* Source duration mismatch is not silently accepted. */
 b24_wm_rigid_sync_release(&sync);
 assert(b24_wm_rigid_sync_tick(&sync,".",body,4,120,1000,1000,1,&a));
 assert(!sync.candidate_pose_valid&&sync.source_missing);
 b24_wm_rigid_sync_release(&sync);
 assert(b24_wm_rigid_sync_tick(&sync,".",body,3,100,1000,1100,0,&a));
 assert(!sync.candidate_pose_valid&&!sync.rigid.file);
 assert(b24_wm_rigid_sync_tick(&sync,".","ironman_ironman_fly_f",3,100,1000,1100,1,&a));
 assert(!sync.candidate_pose_valid&&!sync.rigid.file);
 b24_wm_rigid_sync_release(&sync);
 remove("warmachine_aim_float_idle.im2k");
 puts("PASS G8 WM rigid source G8-body IM2V synchronized gun clip and B14 player heading/world:"
      " correct 20Hz samples, timeline changes, no repeated missing-file IO,"
      " duration check, other-suit fallback, NO muzzle actor/particle or VPK");
 return 0;
}
