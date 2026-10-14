#include "b24_g8_live_original_motion.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

static int stage_direction(float x,float y) {
 /* 0 stationary, 1 forward, 2 back, 3 left, 4 right, in PLAYER space.
    Uses same values already consumed by the authoritative B14 movement. */
 if(!isfinite(x)||!isfinite(y)||fabsf(x)>1.01f||fabsf(y)>1.01f)return -1;
 if(fmaxf(fabsf(x),fabsf(y))<.18f)return 0;
 if(fabsf(x)>fabsf(y))return x<0?3:4;
 return y<0?2:1;
}
static const char * const mark6_walk[]={
 "ironman_ironman_ground_idel",
 "ironman_ironman_walk_f","ironman_ironman_walk_b",
 "ironman_ironman_walk_l","ironman_ironman_walk_r"
};
static const char * const mark6_float[]={
 "ironman_ironman_aim_float_idle",
 "ironman_ironman_aim_float_move_f","ironman_ironman_aim_float_move_b",
 "ironman_ironman_aim_float_move_l","ironman_ironman_aim_float_move_r"
};
static const char * const mark6_fly[]={
 "ironman_ironman_fly_f", "ironman_ironman_fly_f",
 "ironman_ironman_fly_b","ironman_ironman_fly_l","ironman_ironman_fly_r"
};
static const char * const wm_float[]={
 "warmachine_warmachine_aim_float_idle",
 "warmachine_warmachine_aim_float_move_f","warmachine_warmachine_aim_float_move_b",
 "warmachine_warmachine_aim_float_move_l","warmachine_warmachine_aim_float_move_r"
};
const char *b24_g8_motion_route(int suit,B24MotionStage mode,float x,float y){
 const int d=stage_direction(x,y);
 if(d<0||mode>B24M_LAND)return NULL;
 /* G8 suit order: Mark VI 0, War Machine 2. Never load 802v Mark VI
    on differently skinned Mark IV, Stealth, Mark V or Underwater. */
 if(suit==0){
  switch(mode){
   case B24M_IDLE:return mark6_walk[0];
   case B24M_WALK:return mark6_walk[d?d:1];
   case B24M_RUN:return "ironman_ironman_run";
   case B24M_HOVER:return mark6_float[0];
   case B24M_DRIFT:return mark6_float[d];
   case B24M_CRUISE:return mark6_fly[d?d:1];
   case B24M_RUSH:return "ironman_ironman_fly_f_rush";
   case B24M_LAND:
    /* Do not start authored landing clip until true FOOT contact timing
       is verified from original scene. Keep existing B14 landing. */
    return NULL;
  }
 }
 if(suit==2){
  switch(mode){
   case B24M_HOVER:return wm_float[0];
   case B24M_DRIFT:return wm_float[d];
   case B24M_CRUISE:return "warmachine_warmachine_aim_fly_m";
   /* Preserve user-liked original G8 WM relaxed walk/hover, as well as
      the existing prototype rush lean where WM has no named native Rush. */
   default:return NULL;
  }
 }
 return NULL;
}
/* The exact 2010 owner-source filenames for full-body movement+attack.
   In this prototype they are played ONLY after a successful REPULSOR event.
   Their name _Att alone does not prove original iOS weapon-event semantics. */
static const char *const mk6_hover_fire[]={
 "ironman_ironman_aim_float_idle_att",
 "ironman_ironman_aim_float_move_f_att",
 "ironman_ironman_aim_float_move_b_att",
 "ironman_ironman_aim_float_move_l_att",
 "ironman_ironman_aim_float_move_r_att"
};
static const char *const wm_hover_fire[]={
 "warmachine_warmachine_aim_float_idle_att",
 "warmachine_warmachine_aim_float_move_f_att",
 "warmachine_warmachine_aim_float_move_b_att",
 "warmachine_warmachine_aim_float_move_l_att",
 "warmachine_warmachine_aim_float_move_r_att"
};
static const char *const mk6_ground_fire[]={
 "ironman_ironman_aim_ground_idle_att",
 "ironman_ironman_aim_ground_move_f_att",
 "ironman_ironman_aim_ground_move_b_att",
 "ironman_ironman_aim_ground_move_l_att",
 "ironman_ironman_aim_ground_move_r_att"
};
static const char *const wm_ground_fire[]={
 "warmachine_warmachine_aim_ground_idle_att",
 "warmachine_warmachine_aim_ground_move_f_att",
 "warmachine_warmachine_aim_ground_move_b_att",
 "warmachine_warmachine_aim_ground_move_l_att",
 "warmachine_warmachine_aim_ground_move_r_att"
};
const char *b24_g8_motion_repulsor_clip(int suit,B24MotionStage stage,float x,float y){
 int d=stage_direction(x,y);
 if(d<0)return NULL;
 if(suit==0){
  if(stage==B24M_HOVER||stage==B24M_DRIFT)return mk6_hover_fire[d];
  if(stage==B24M_WALK||stage==B24M_IDLE)return mk6_ground_fire[d];
 }else if(suit==2){
  if(stage==B24M_HOVER||stage==B24M_DRIFT)return wm_hover_fire[d];
  if(stage==B24M_WALK||stage==B24M_IDLE)return wm_ground_fire[d];
 }
 return NULL;
}
void b24_g8_motion_repulsor_trigger(B24G8LiveOriginalMotion *a,uint32_t now){
 if(!a||!a->nv)return;
 if(!a->repulsor_pending || (uint32_t)(now-a->repulsor_started_ms)>1600u){
  a->repulsor_started_ms=now;a->repulsor_pending=1;
 }
}
void b24_g8_motion_melee_trigger(B24G8LiveOriginalMotion *a,uint32_t now){
 if(!a||a->suit_index!=0||!a->nv)return;
 b24_g8_melee_press(&a->melee,now);
}
int b24_g8_motion_melee_source_active(const B24G8LiveOriginalMotion *a){
 return a&&b24_g8_melee_active(&a->melee)&&a->active&&!a->missing;
}
int b24_g8_motion_whole_body_fire(const B24G8LiveOriginalMotion *a){
 return a&&a->whole_body_repulsor_active&&a->active&&!a->missing;
}
void b24_g8_motion_release(B24G8LiveOriginalMotion *a){
 if(!a)return;
 b24_original_im2v_close(&a->stream);
 b24_hover_pose_blend_close(&a->blend);
 free(a->source_xyz);free(a->result_xyz);free(a->snapshot_xyz);
 memset(a,0,sizeof(*a));
}
static int fresh(B24G8LiveOriginalMotion *a,size_t nv,int suit){
 if(nv<3||nv>16000)return 0;
 if(a->nv==nv&&a->suit_index==suit&&a->source_xyz)return 1;
 b24_g8_motion_release(a);
 a->source_xyz=(float*)malloc(nv*3*sizeof(float));
 a->result_xyz=(float*)malloc(nv*3*sizeof(float));
 a->snapshot_xyz=(float*)malloc(nv*3*sizeof(float));
 if(!a->source_xyz||!a->result_xyz||!a->snapshot_xyz||
    !b24_hover_pose_blend_init(&a->blend,nv)){
  b24_g8_motion_release(a);return 0;
 }
 a->nv=nv;a->suit_index=suit;
 return 1;
}
int b24_g8_motion_tick(B24G8LiveOriginalMotion *a,const char *dir,
                       void *vertices,size_t stride,size_t nv,int suit,
                       B24MotionStage mode,float left_x,float forward,
                       uint32_t now){
 if(!a||!dir||!vertices||stride<3*sizeof(float))return 0;
 const char *desired=b24_g8_motion_route(suit,mode,left_x,forward);
 /* Only an ACCEPTED B16 repulsor shot can request an original _Att clip.
    The source IM2V duration is authoritative; never auto-fire a projectile. */
 const char *shot=b24_g8_motion_repulsor_clip(suit,mode,left_x,forward);
 if(a->repulsor_pending&&a->stream.file&&a->whole_body_repulsor_active&&
    (uint32_t)(now-a->repulsor_started_ms)>=a->stream.duration_ms){
    a->repulsor_pending=0;a->whole_body_repulsor_active=0;
 }
 /* Original melee has priority over aim/repulsor _Att; the right-arm
    B16 mask must not fight a full-body 2010 punch pose. */
 const char *melee=NULL;
 if(suit==0 && mode<=B24M_RUN)
    melee=b24_g8_melee_tick(&a->melee,now);
 else a->melee=(B24G8MeleeChain){0};
 if(melee)desired=melee;
 else if(a->repulsor_pending&&shot)desired=shot;
 else if(a->repulsor_pending&&!shot){
    a->repulsor_pending=0;a->whole_body_repulsor_active=0;
 }
 if(!desired|| (suit==0&&nv!=802u) || (suit==2&&nv!=1292u)){
  /* Unsupported suit or mode explicitly leaves the proven G8 pose intact. */
  if(a->active||a->missing)b24_g8_motion_release(a);
  return 1;
 }
 if(!fresh(a,nv,suit))return 0;
 size_t n=nv*3;
 unsigned char *verts=(unsigned char*)vertices;
 for(size_t i=0;i<nv;i++){
  const float *v=(const float*)(const void*)(verts+i*stride);
  for(int k=0;k<3;k++){
   if(!isfinite(v[k]))return 0;
   a->snapshot_xyz[i*3+(size_t)k]=v[k];
  }
 }
 if(strcmp(a->selected,desired)!=0){
  /* B14 has just recomputed its legacy pose for this frame. Source-to-source
     interruption MUST start at the previous actually rendered original pose,
     not that intermediary: e.g. L_MOVE -> R_MOVE should not snap to idle. */
  if(a->active&&!a->missing&&a->successful_frames>0)
   memcpy(a->snapshot_xyz,a->result_xyz,n*sizeof(float));
  /* Source missing? Transactional read never damages previous valid pose.
     Suppress repeated storage probes for same missing name. */
  a->missing=0;
  if(!b24_original_im2v_open(&a->stream,dir,desired,(uint32_t)nv)){
   a->missing=1;a->misses++;
   b24_original_im2v_close(&a->stream);
  }
  if(strlen(desired)>=sizeof(a->selected))return 0;
  strcpy(a->selected,desired);
  a->started_ms=now;a->previous_ms=now;
  a->active=!a->missing;
  a->whole_body_repulsor_active=(a->active&&a->repulsor_pending&&shot&&
                                 desired==shot&&!melee);
  if(a->missing&&a->repulsor_pending){
    /* Preserve B16 single right-palm attack if source file missing. */
    a->repulsor_pending=0;a->whole_body_repulsor_active=0;
  }
  if(a->active){
   /* Capture PREVIOUS *rendered* pose, including interruptions. */
   if(!b24_hover_pose_blend_begin(&a->blend,a->snapshot_xyz,.15f))return 0;
   a->transitions++;
  }
 }
 if(a->missing||!a->active)return 1;
 const uint32_t age=now-a->started_ms;
 if(!b24_original_im2v_sample(&a->stream,age,1,a->source_xyz))return 0;
 const float dt=fminf((float)(now-a->previous_ms)*.001f,.5f);
 if(!b24_hover_pose_blend_step(&a->blend,a->source_xyz,a->result_xyz,dt))
  return 0;
 a->previous_ms=now;
 for(size_t i=0;i<nv;i++){
  float *v=(float*)(void*)(verts+i*stride);
  for(int k=0;k<3;k++)v[k]=a->result_xyz[i*3+(size_t)k];
 }
 a->successful_frames++;
 return 1;
}
