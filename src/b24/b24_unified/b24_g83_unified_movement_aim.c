#include "b24_g83_unified_movement_aim.h"
#include "im2_suit_profile.h"
#include "b24_g83_authentic_2010_source_durations.h"
#ifdef B24_G172_WM_NATIVE_M_GROUND_BANK
#include "b24_g172_wm_ground_m_source.h"
#endif
#include <math.h>
#include <stddef.h>
#include <string.h>
/* Every literal below was independently checked against the authenticated
 * 2010 iOS 304-motion B18/G81 registry. No procedural imitation keyframes. */
static const char *const mk_walk[5]={
 "ironman_ironman_ground_idel","ironman_ironman_walk_f",
 "ironman_ironman_walk_b","ironman_ironman_walk_l",
 "ironman_ironman_walk_r"};
static const char *const mk_air[5]={
 "ironman_ironman_air_idel","ironman_ironman_air_move_f",
 "ironman_ironman_air_move_b","ironman_ironman_air_move_l",
 "ironman_ironman_air_move_r"};
static const char *const mk_ground_aim[5]={
 "ironman_ironman_aim_ground_idle","ironman_ironman_aim_ground_move_f",
 "ironman_ironman_aim_ground_move_b","ironman_ironman_aim_ground_move_l",
 "ironman_ironman_aim_ground_move_r"};
static const char *const mk_ground_aim_fire[5]={
 "ironman_ironman_aim_ground_idle_att","ironman_ironman_aim_ground_move_f_att",
 "ironman_ironman_aim_ground_move_b_att","ironman_ironman_aim_ground_move_l_att",
 "ironman_ironman_aim_ground_move_r_att"};
static const char *const mk_ground_m[5]={
 "ironman_ironman_aim_m_ground_idle","ironman_ironman_aim_m_ground_move_f",
 "ironman_ironman_aim_m_ground_move_b","ironman_ironman_aim_m_ground_move_l",
 "ironman_ironman_aim_m_ground_move_r"};
static const char *const mk_ground_m_fire[5]={
 "ironman_ironman_aim_m_ground_idle_att","ironman_ironman_aim_m_ground_move_f_att",
 "ironman_ironman_aim_m_ground_move_b_att","ironman_ironman_aim_m_ground_move_l_att",
 "ironman_ironman_aim_m_ground_move_r_att"};
static const char *const mk_hover_aim[5]={
 "ironman_ironman_aim_float_idle","ironman_ironman_aim_float_move_f",
 "ironman_ironman_aim_float_move_b","ironman_ironman_aim_float_move_l",
 "ironman_ironman_aim_float_move_r"};
static const char *const mk_hover_aim_fire[5]={
 "ironman_ironman_aim_float_idle_att","ironman_ironman_aim_float_move_f_att",
 "ironman_ironman_aim_float_move_b_att","ironman_ironman_aim_float_move_l_att",
 "ironman_ironman_aim_float_move_r_att"};
static const char *const mk_hover_m[5]={
 "ironman_ironman_aim_m_float_idle","ironman_ironman_aim_m_float_move_f",
 "ironman_ironman_aim_m_float_move_b","ironman_ironman_aim_m_float_move_l",
 "ironman_ironman_aim_m_float_move_r"};
static const char *const mk_hover_m_fire[5]={
 "ironman_ironman_aim_m_float_idle_att","ironman_ironman_aim_m_float_move_f_att",
 "ironman_ironman_aim_m_float_move_b_att","ironman_ironman_aim_m_float_move_l_att",
 "ironman_ironman_aim_m_float_move_r_att"};
static const char *const mk_fly[5]={
 "ironman_ironman_fly_f","ironman_ironman_fly_f",
 "ironman_ironman_fly_b","ironman_ironman_fly_l",
 "ironman_ironman_fly_r"};
static const char *const wm_ground_aim[5]={
 "warmachine_warmachine_aim_ground_idle","warmachine_warmachine_aim_ground_move_f",
 "warmachine_warmachine_aim_ground_move_b","warmachine_warmachine_aim_ground_move_l",
 "warmachine_warmachine_aim_ground_move_r"};
static const char *const wm_ground_aim_fire[5]={
 "warmachine_warmachine_aim_ground_idle_att","warmachine_warmachine_aim_ground_move_f_att",
 "warmachine_warmachine_aim_ground_move_b_att","warmachine_warmachine_aim_ground_move_l_att",
 "warmachine_warmachine_aim_ground_move_r_att"};
static const char *const wm_hover[5]={
 "warmachine_warmachine_aim_float_idle","warmachine_warmachine_aim_float_move_f",
 "warmachine_warmachine_aim_float_move_b","warmachine_warmachine_aim_float_move_l",
 "warmachine_warmachine_aim_float_move_r"};
static const char *const wm_hover_fire[5]={
 "warmachine_warmachine_aim_float_idle_att","warmachine_warmachine_aim_float_move_f_att",
 "warmachine_warmachine_aim_float_move_b_att","warmachine_warmachine_aim_float_move_l_att",
 "warmachine_warmachine_aim_float_move_r_att"};
static const char *const wm_hover_m[5]={
 "warmachine_warmachine_aim_m_float_idle","warmachine_warmachine_aim_m_float_move_f",
 "warmachine_warmachine_aim_m_float_move_b","warmachine_warmachine_aim_m_float_move_l",
 "warmachine_warmachine_aim_m_float_move_r"};
static const char *const wm_hover_m_fire[5]={
 "warmachine_warmachine_aim_m_float_idle_att",
 "warmachine_warmachine_aim_m_float_move_f_att",
 "warmachine_warmachine_aim_m_float_move_b_att",
 "warmachine_warmachine_aim_m_float_move_l_att",
 "warmachine_warmachine_aim_m_float_move_r_att"};
static const char *const mk_transition[8]={
 NULL,"ironman_ironman_ground_float","ironman_ironman_fly_start",
 "ironman_ironman_fly_end","ironman_ironman_fly2ground",
 "ironman_ironman_fly2run","ironman_ironman_fly_left_dodge",
 "ironman_ironman_fly_right_dodge"};
static B24G83Dir classify(float x,float y){
 if(fmaxf(fabsf(x),fabsf(y))<.18f)return B24G83_DIR_IDLE;
 if(fabsf(x)>fabsf(y))return x<0?B24G83_DIR_L:B24G83_DIR_R;
 return y<0?B24G83_DIR_B:B24G83_DIR_F;
}
B24G83Dir b24_g83_physical_flight_dir(B24G83Mode mode,
                                      float axis_x,float axis_y){
 if(mode!=B24G83_FLIGHT || !isfinite(axis_x)||!isfinite(axis_y)||
    fabsf(axis_x)>1.01f||fabsf(axis_y)>1.01f)
  return B24G83_DIR_IDLE;
 return classify(axis_x,axis_y);
}
static int valid(const B24G83Input *p){
 return p&&isfinite(p->axis_x)&&isfinite(p->axis_y)&&
    fabsf(p->axis_x)<=1.01f&&fabsf(p->axis_y)<=1.01f&&
    (unsigned)p->motion<=(unsigned)B24G83_RUSH&&
    (unsigned)p->aim<=(unsigned)B24G83_AIM_M_UNCLASSIFIED&&
    (unsigned)p->transition<=(unsigned)B24G83_EVENT_DODGE_RIGHT&&
    (unsigned)p->previous_flight_dir<=(unsigned)B24G83_DIR_R;
}
int b24_g83_select_original_motion(const B24G83Input *p,
 B24G83Selection *out){
 if(!out||!valid(p))return 0;
 memset(out,0,sizeof(*out));
 const int markvi=im2_suit_uses_802_bank(p->suit_index);
 const int wm=p->suit_index==B24G83_WARMACHINE;
#ifdef B24_G85_NATIVE_MARKV_629
 /* These same original 2010 IronMan joint tracks are rebaked from genuine
    B13 hierarchy onto the UNIQUE Mark V 629 weighted-skin palette. */
 const int markv=p->suit_index==B24G83_MARKV;
#else
 const int markv=0;
#endif
 const int original_ironman_rig=markvi||markv;
 if(!original_ironman_rig&&!wm)return 1; /* never skin unsupported Mark V/etc with VI mesh */
 if(p->paused)return 1;
 const B24G83Dir dir=classify(p->axis_x,p->axis_y);
 out->direction=dir;
 const int fire=p->accepted_weapon_event!=0;
 const B24G83Aim aim=p->aim;
 const int ground=p->motion==B24G83_GROUND;
 const int hover=p->motion==B24G83_HOVER;
 const int flight=p->motion==B24G83_FLIGHT;
 const int rush=p->motion==B24G83_RUSH;
 const char *stem=NULL;
 int oneshot=0;
 if(p->transition!=B24G83_EVENT_NONE){
  /* Animated land requires an authentic physics foot-contact event.
   * No gesture/FPS-driven automatic landing or imaginary WM retarget. */
  if(markvi &&
     ((p->transition!=B24G83_EVENT_FLY_TO_GROUND &&
       p->transition!=B24G83_EVENT_FLY_TO_RUN) ||
      p->grounded_contact_verified)){
   stem=mk_transition[p->transition];oneshot=stem!=NULL;
  }
 }else if(original_ironman_rig){
  if(ground){
   if(aim==B24G83_AIM_NONE){
    stem=(p->run&&dir!=B24G83_DIR_IDLE)?
       "ironman_ironman_run":mk_walk[dir];
   }else if(aim==B24G83_AIM_M_UNCLASSIFIED){
    stem=(fire?mk_ground_m_fire:mk_ground_m)[dir];
   }else{
    stem=(fire?mk_ground_aim_fire:mk_ground_aim)[dir];
    if(dir==B24G83_DIR_IDLE){
     if(aim==B24G83_AIM_DUAL)
      stem=fire?"ironman_ironman_aim_ground_idle_att_2h":
                 "ironman_ironman_aim_ground_idle_2h";
     if(aim==B24G83_AIM_LEFT)
      stem=fire?"ironman_ironman_aim_ground_idle_att_l":
                 "ironman_ironman_aim_ground_idle_l";
    }
   }
  }else if(hover){
   if(aim==B24G83_AIM_NONE)stem=mk_air[dir];
   else if(aim==B24G83_AIM_M_UNCLASSIFIED)
    stem=(fire?mk_hover_m_fire:mk_hover_m)[dir];
   else{
    stem=(fire?mk_hover_aim_fire:mk_hover_aim)[dir];
    if(dir==B24G83_DIR_IDLE){
     if(aim==B24G83_AIM_DUAL)
      stem=fire?"ironman_ironman_aim_float_idle_att_2h":
                 "ironman_ironman_aim_float_idle_2h";
     if(aim==B24G83_AIM_LEFT)
      stem=fire?"ironman_ironman_aim_float_idle_att_l":
                 "ironman_ironman_aim_float_idle_l";
    }
   }
  }else if(flight){
   /* Real 2010 F->L/R and L/R->F authored clips. Dispatch only on
    * input direction changes supplied by main B14 player controller. */
   stem=mk_fly[dir];
   if(p->previous_flight_dir==B24G83_DIR_F&&dir==B24G83_DIR_L)
    stem="ironman_ironman_fly_ftol",oneshot=1;
   else if(p->previous_flight_dir==B24G83_DIR_F&&dir==B24G83_DIR_R)
    stem="ironman_ironman_fly_ftor",oneshot=1;
   else if(p->previous_flight_dir==B24G83_DIR_L&&dir==B24G83_DIR_F)
    stem="ironman_ironman_fly_ltof",oneshot=1;
   else if(p->previous_flight_dir==B24G83_DIR_R&&dir==B24G83_DIR_F)
    stem="ironman_ironman_fly_rtof",oneshot=1;
   /* Flight weapon animations _fly_att_s/_m not mapped to real original
    * weapon choice: do NOT auto-use unrelated mesh motion to fire here. */
  }else if(rush){
   stem="ironman_ironman_fly_f_rush";
  }
 }else if(wm){
  if(ground){
#ifdef B24_G165_WM_SOURCE_DIRECTIONAL_FALLBACK
   /* Genuine original warmachine_warmachine_aim_ground_move_*
    * source clips ALREADY play while L aim is held. Without L, the
    * old route returned NULL, falling back to unrelated G8 motions.
    * Actual original WM relaxed-neutral stance has not been proven.
    * Reuse named 2010 aimed-ground directional locomotion as
    * EXPERIMENTAL presentational fallback, not authentic neutral. */
   if(aim==B24G83_AIM_NONE)stem=wm_ground_aim[dir];
   else
#endif
#ifdef B24_G172_WM_NATIVE_M_GROUND_BANK
   /* 10 actual 2010 War Machine Aim_M_Ground native clips. Unlike old
    * generic WM Ground aimed fallback, route authored M bank to the
    * G83/G8 owner. M is an UNKNOWN native weapon meaning; do not
    * assign missiles/gatling or change B16 accepted-fire authority. */
   if(aim==B24G83_AIM_M_UNCLASSIFIED)
    stem=b24_g172_wm_m_ground_clip((unsigned)dir,fire);
   else
#endif
   if(aim!=B24G83_AIM_NONE){
    stem=(fire?wm_ground_aim_fire:wm_ground_aim)[dir];
    if(dir==B24G83_DIR_IDLE){
     if(aim==B24G83_AIM_DUAL&&!fire)
      stem="warmachine_warmachine_aim_ground_idle_2h";
     if(aim==B24G83_AIM_LEFT&&!fire)
      stem="warmachine_warmachine_aim_ground_idle_lh";
    }
   } /* NO fake WarMachine original relaxed-ground cycle */
  }else if(hover){
   stem=aim==B24G83_AIM_M_UNCLASSIFIED?
       (fire?wm_hover_m_fire:wm_hover_m)[dir]:
       (fire?wm_hover_fire:wm_hover)[dir];
   if(dir==B24G83_DIR_IDLE&&aim==B24G83_AIM_DUAL&&!fire)
    stem="warmachine_warmachine_aim_float_idle_2h";
  }else if(flight){
   stem="warmachine_warmachine_aim_fly_m";
   /* M suffix not proof of missile! */
  }
#ifdef B24_G165_WM_SOURCE_DIRECTIONAL_FALLBACK
  else if(rush){
   /* Original 2010 WM RUSH-only source clip NOT decoded.
    * Reuse true original wm aim_fly_m flight posture rather than
    * old G8 fallback ground run, explicitly TEMPORARY. */
   stem="warmachine_warmachine_aim_fly_m";
  }
#endif
  /* Source-authored WM RUSH-only motion remains unverified. */
 }
 out->stem=stem;
 out->source_authored_name=stem!=NULL;
 out->one_shot_not_looping=oneshot || (fire && aim!=B24G83_AIM_NONE && (ground||hover));
 out->original_source_duration_ms=b24_g83_authentic_source_duration(stem);
#ifdef B24_G172_WM_NATIVE_M_GROUND_BANK
 if(wm&&ground&&aim==B24G83_AIM_M_UNCLASSIFIED)
  out->original_source_duration_ms=b24_g172_wm_m_ground_duration(stem);
#endif
 /* G304 original-2010 source correction, not a cosmetic rename.
  * G213B/G217 recovered actual StateData AttackType rows and raw
  * StateTrack::attack event fields; G221/G222 recovered native dispatch
  * provenance, NOT proof of a Vita weapon hit, original controller
  * mapping, native event time-unit or target. A source _att IM2V name
  * alone is insufficient to request ANY additional game hit. Earlier
  * G83 code set this flag for every accepted aimed attack and could
  * be read as authorising an unverified SECOND damage path.
  * B16/G82 remain the sole separately gated port events. */
 out->input_semantics_verified_original_ios=0;
 out->needs_2010_hit_event=0;
 return 1;
}
int b24_g83_select_combined(B24G82Combat *combat,uint32_t time_ms,
 const B24G83Input *in,B24G83Selection *out){
 if(!b24_g83_select_original_motion(in,out))return 0;
 if(in->paused)return 1;
 if(combat){
  const char *melee=b24_g82_tick(combat,time_ms);
  if(melee){
   /* Original G8 combo has priority over walk/aim/etc when grounded. */
   if(in->motion==B24G83_GROUND&&
      (im2_suit_uses_802_bank(in->suit_index)
#ifdef B24_G85_NATIVE_MARKV_629
       ||in->suit_index==B24G83_MARKV
#endif
       )){
    out->stem=melee;
    out->source_authored_name=1;
    out->one_shot_not_looping=1;
    out->original_source_duration_ms= combat->clip.phase==1?266u:combat->clip.phase==2?300u:500u;
    /* G304: an original combo clip is proven animation, not proven
     * native hit contact. G82 validates actual source contact separately. */
    out->needs_2010_hit_event=0;
   }
  }
 }
 return 1;
}
