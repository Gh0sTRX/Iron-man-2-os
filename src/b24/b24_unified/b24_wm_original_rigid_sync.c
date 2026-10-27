#include "b24_wm_original_rigid_sync.h"
#include <string.h>
#include <math.h>
void b24_wm_rigid_sync_release(B24WMRigidSync *s){
 if(!s)return;
 b24_wm_gun_stream_close(&s->rigid);
 memset(s,0,sizeof(*s));
}
int b24_wm_rigid_sync_tick(B24WMRigidSync *s,const char *root,
                          const char *body,uint32_t frames,uint32_t ms,
                          uint32_t started,uint32_t now,int wm,
                          const B24WMG8ActorPose *actor){
 if(!s||!root||!actor)return 0;
 if(!wm||!body||strncmp(body,"warmachine_warmachine_",22)!=0){
  /* G8 Mark VI and other suits cannot accidentally reuse WM socket data. */
  b24_wm_gun_stream_close(&s->rigid);
  s->selected_body_asset[0]=0;
  s->source_missing=0;s->candidate_pose_valid=0;
  return 1;
 }
 if(strlen(body)>=sizeof(s->selected_body_asset)||frames<1||ms>120000u)
  return 0;
 s->candidate_pose_valid=0;
 if(strcmp(s->selected_body_asset,body)!=0){
  b24_wm_gun_stream_close(&s->rigid);
  strcpy(s->selected_body_asset,body);
  s->source_missing=0;
  /* Filename is original source base without the G8 armor namespace.
     Never guess a new original 2010 weapon clip name. */
  const char *gun_name=body+11;
  if(!b24_wm_gun_stream_open(&s->rigid,root,gun_name)){
   s->source_missing=1;s->missing_names++;return 1;
  }
  if(s->rigid.frames!=frames||s->rigid.duration_ms!=ms){
   b24_wm_gun_stream_close(&s->rigid);
   s->source_missing=1;s->missing_names++;return 1;
  }
  s->opens++;
 }
 if(s->source_missing||!s->rigid.file)return 1;
 float matrices[6][16],tip[3],axis[3];
 const uint32_t age=now-started;
 if(!b24_wm_gun_stream_sample(&s->rigid,age,1,matrices)||
    !b24_wm_g8_source_gun03_marker_world(actor,
             (const float (*)[16])matrices,tip,axis))return 0;
 for(int k=0;k<3;k++){
  s->world_tip[k]=tip[k];s->world_axis[k]=axis[k];
 }
 s->candidate_pose_valid=1;s->samples++;
 return 1;
}
