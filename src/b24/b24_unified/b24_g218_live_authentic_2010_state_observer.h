/* G218 observational bridge: G8's successfully loaded original 2010 IM2V
 * clip -> G217's real original iOS 2010 StateData/StateTrack.
 * It never changes G83 decisions, G8 streams, B14 movement or B16 attack.
 * Exact clip-to-state pairing is a NAME-BASED CORRESPONDENCE CANDIDATE,
 * not proof that original 2010 StateMgr selected that StateData at runtime.
 * Original attack event ticks have an UNKNOWN unit; never execute damage
 * or missiles at these numbers. A hit on this table is NOT hitbox proof.
 * Requires the externally loaded owner-authenticated StateData bank.
 * No VPK, no source IPA or proprietary pose bytes embedded here. */
#ifndef B24_G218_LIVE_AUTHENTIC_2010_STATE_OBSERVER_H
#define B24_G218_LIVE_AUTHENTIC_2010_STATE_OBSERVER_H
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "im2_original_tables.h"
#include "b24_g197_original_2010_attack_dispatch_reference.h"

typedef struct {
  uint32_t source_animation_frames_observed;
  uint32_t successfully_correlated;
  uint32_t unmapped_source_clip_frames;
  uint32_t native_raw_attack_event_rows_observed;
  uint16_t source_suit_group;
  uint16_t source_native_state_index;
  uint32_t source_authored_AttackType_or_UNKNOWN;
  /* G305 original ARM jump table is SOURCE STATIC, attached to an IM2V
   * filename-correspondence CANDIDATE, never selected native StateMgr. */
  uint32_t source_candidate_original_DoAttack_ARM_entry_VM_or_UNKNOWN;
  uint32_t source_candidate_original_DoAttack_ARM_target_VM_or_UNKNOWN;
  uint8_t source_static_DoAttack_ARM_branch_proven_FOR_CANDIDATE_ONLY;
  uint8_t source_native_DoAttack_runtime_event_proven; /* always zero */
  uint8_t source_WeaponDB_runtime_index_or_weapon_identity_proven; /* always zero */
  uint32_t source_authored_next_state_or_UNKNOWN; /* exact original StateData next_state, not auto-executed */
  uint32_t source_authored_type_or_UNKNOWN;       /* original type, weapon semantics unproven */
  uint32_t source_authored_loop_or_UNKNOWN;       /* original loop flag, no new G8 timing */
  uint32_t source_attack_event_start_raw_UNCLASSIFIED;
  uint32_t source_attack_event_third_u32_UNCLASSIFIED; /* native G221/G222 Actor consumes this in r2, not confirmed hit/damage */
  const char *source_state_name_correspondence_ONLY;
  const char *selected_actual_G8_IM2V_clip;
  uint8_t source_state_index_correlated_by_filename_ONLY;
  uint8_t actual_2010_StateMgr_runtime_state_PROVEN; /* always zero */
  uint8_t actual_2010_melee_hit_or_projectile_event_PROVEN; /* always zero */
  /* G305: old native_raw_attack_event_rows_observed incorrectly rose once
   * per RENDERED FRAME on a held G8 clip, not once on a loaded-clip edge.
   * Track the last actually active IM2V so one original read-only raw row
   * cannot masquerade as 60+ repeated native attacks at 60 FPS. */
  uint8_t last_observed_G8_clip_valid;
  int last_observed_Vita_suit;
  char last_observed_G8_clip[128];
} B24G218LiveObserver;

static inline int b24_g218_owner_group_for_Vita_suit(int suit){
  /* Genuine native asset bank player StateSet names, NOT original touch IDs.
   * Only the 0,2,4 fully source-streamed suits are audited. */
  return suit==0?0:suit==4?1:suit==2?2:-1;
}
static inline const char *b24_g218_known_state_name_from_real_G8_stem(
    int suit,const char *stem){
  if(!stem)return NULL;
  const char *s=NULL;
  if(suit==0){
    if(strncmp(stem,"ironman_ironman_",16)!=0)return NULL;
    s=stem+16;
  }else if(suit==4){
    if(strncmp(stem,"suitcase_ironman_",17)!=0)return NULL;
    s=stem+17;
  }else if(suit==2){
    if(strncmp(stem,"warmachine_warmachine_",22)!=0)return NULL;
    s=stem+22;
  }else return NULL;
  /* Exact G8/G83/G169 source-author names only: fail CLOSED on everything
   * ambiguous (e.g. gun01, _att, missile, rush, fall, fly2run).
   * Names align SOURCE vocabulary, not proven native iOS selection IDs. */
  if(suit!=2){
    if(!strcmp(s,"ground_idel"))return "Idle";
    if(!strcmp(s,"walk_f")||!strcmp(s,"walk_b")||
       !strcmp(s,"walk_l")||!strcmp(s,"walk_r"))return "Move_Walk";
    if(!strcmp(s,"run"))return "Move_Run";
    if(!strcmp(s,"fly_f")||!strcmp(s,"fly_b")||
       !strcmp(s,"fly_l")||!strcmp(s,"fly_r"))return "Fly";
    if(!strcmp(s,"ground_combo_1"))return "Attack_Ground_COMBO1";
    if(!strcmp(s,"ground_combo_2"))return "Attack_Ground_COMBO2";
    if(!strcmp(s,"ground_combo_3"))return "Attack_Ground_COMBO3";
    if(!strcmp(s,"aim_float_idle"))return "Attack_Float_idle";
    if(!strcmp(s,"aim_m_ground_idle"))return "Attack_M_Ground_idle";
    if(!strcmp(s,"aim_m_float_idle"))return "Attack_M_Float_idle";
    if(!strcmp(s,"aim_ground_beam1"))return "Attack_Ground_Beam_prepare";
    if(!strcmp(s,"aim_ground_beam2"))return "Attack_Ground_Beam";
    if(!strcmp(s,"aim_ground_beam3"))return "Attack_Ground_Beam_out";
    if(!strcmp(s,"aim_float_beam1"))return "Attack_Float_Beam_prepare";
    if(!strcmp(s,"aim_float_beam2"))return "Attack_Float_Beam";
    if(!strcmp(s,"aim_float_beam3"))return "Attack_Float_Beam_out";
  }else{
    if(!strcmp(s,"aim_m_ground_idle"))return "Attack_M_Ground_idle";
    if(!strcmp(s,"aim_m_float_idle"))return "Attack_M_Float_idle";
    if(!strcmp(s,"aim_float_idle"))return "Attack_Float_idle";
  }
  return NULL;
}
static inline void b24_g218_observer_reset(B24G218LiveObserver *observer){
  if(observer)memset(observer,0,sizeof(*observer));
}
static inline int b24_g218_observe_actually_loaded_G8_clip(
     B24G218LiveObserver *obs,int suit,const char *actual_G8_clip,
     int G8_animation_active,int G8_source_missing){
  if(!obs)return 0;
  obs->source_state_index_correlated_by_filename_ONLY=0;
  obs->source_state_name_correspondence_ONLY=NULL;
  obs->selected_actual_G8_IM2V_clip=NULL;
  obs->source_authored_AttackType_or_UNKNOWN=B24G217_UNKNOWN_U32;
  obs->source_candidate_original_DoAttack_ARM_entry_VM_or_UNKNOWN=B24G217_UNKNOWN_U32;
  obs->source_candidate_original_DoAttack_ARM_target_VM_or_UNKNOWN=B24G217_UNKNOWN_U32;
  obs->source_static_DoAttack_ARM_branch_proven_FOR_CANDIDATE_ONLY=0;
  obs->source_native_DoAttack_runtime_event_proven=0;
  obs->source_WeaponDB_runtime_index_or_weapon_identity_proven=0;
  obs->source_authored_next_state_or_UNKNOWN=B24G217_UNKNOWN_U32;
  obs->source_authored_type_or_UNKNOWN=B24G217_UNKNOWN_U32;
  obs->source_authored_loop_or_UNKNOWN=B24G217_UNKNOWN_U32;
  obs->source_attack_event_start_raw_UNCLASSIFIED=B24G217_UNKNOWN_U32;
  obs->source_attack_event_third_u32_UNCLASSIFIED=B24G217_UNKNOWN_U32;
  obs->actual_2010_StateMgr_runtime_state_PROVEN=0;
  obs->actual_2010_melee_hit_or_projectile_event_PROVEN=0;
  if(!im2_original_tables_ready()){
    obs->last_observed_G8_clip_valid=0;return 0;
  }
  if(!actual_G8_clip||!actual_G8_clip[0]||
     !G8_animation_active||G8_source_missing){
    obs->last_observed_G8_clip_valid=0; /* next valid reentry is a new edge */
    return 0;
  }
  ++obs->source_animation_frames_observed;
  const size_t clip_len=strlen(actual_G8_clip);
  if(clip_len>=sizeof(obs->last_observed_G8_clip)){
    ++obs->unmapped_source_clip_frames;
    obs->last_observed_G8_clip_valid=0;
    return 0;
  }
  const int newly_loaded_clip=!obs->last_observed_G8_clip_valid||
     obs->last_observed_Vita_suit!=suit||
     strcmp(obs->last_observed_G8_clip,actual_G8_clip)!=0;
  if(newly_loaded_clip){
    memcpy(obs->last_observed_G8_clip,actual_G8_clip,clip_len+1u);
    obs->last_observed_Vita_suit=suit;
    obs->last_observed_G8_clip_valid=1;
  }
  const int group=b24_g218_owner_group_for_Vita_suit(suit);
  const char *state=b24_g218_known_state_name_from_real_G8_stem(suit,actual_G8_clip);
  if(group<0||!state){
    ++obs->unmapped_source_clip_frames;
    return 0;
  }
  /* Search REAL original G217 authored StateData. Duplicate names fail closed.
   * We don't overwrite real G8 selected original animation nor synthesize
   * any weapon, hit window, combo or input gesture here. */
  const B24G217_SourceState *src=NULL;
  unsigned found=0;
  for(unsigned i=0;i<194;++i){
    const B24G217_SourceState *candidate=
       &b24g217_true_2010_owner_states[group][i];
    if(!strcmp(candidate->original_source_state_name,state)){
      src=candidate;
      ++found;
    }
  }
  if(found!=1||!src){
    ++obs->unmapped_source_clip_frames;
    return 0;
  }
  ++obs->successfully_correlated;
  obs->source_suit_group=(uint16_t)group;
  obs->source_native_state_index=src->native_source_state_index;
  obs->source_authored_AttackType_or_UNKNOWN=src->original_AttackType_or_UNKNOWN;
  /* Original G197 ARM 0..25 jump table proven, but correspondence to
   * THIS loaded G8 file is only via the G218 guessed native StateData
   * name. No WeaponDB row, missile, gatling or repulsor inferred. */
  if(src->original_AttackType_or_UNKNOWN<26u){
    const B24G197OriginalAttackEntry native=
       b24_g197_original_source_attack_entry(src->original_AttackType_or_UNKNOWN);
    obs->source_candidate_original_DoAttack_ARM_entry_VM_or_UNKNOWN=
        native.original_ARM_jump_table_entry_VM;
    obs->source_candidate_original_DoAttack_ARM_target_VM_or_UNKNOWN=
        native.original_ARM_branch_target_VM;
    obs->source_static_DoAttack_ARM_branch_proven_FOR_CANDIDATE_ONLY=1;
  }
  obs->source_authored_next_state_or_UNKNOWN=src->original_next_state_or_UNKNOWN;
  obs->source_authored_type_or_UNKNOWN=src->original_state_type_or_UNKNOWN;
  obs->source_authored_loop_or_UNKNOWN=src->original_loop_or_UNKNOWN;
  obs->selected_actual_G8_IM2V_clip=actual_G8_clip;
  obs->source_state_name_correspondence_ONLY=src->original_source_state_name;
  obs->source_state_index_correlated_by_filename_ONLY=1;
  /* The source event is read-only telemetry, NEVER timed gameplay or damage. */
  for(unsigned i=0;i<B24G217_TRUE_SOURCE_ATTACK_TRAIL_EVENT_COUNT;++i){
    const B24G217_SourceEvent *e=&b24g217_source_attack_trail_events[i];
    if(e->native_suit_group_index==(uint16_t)group&&
       e->native_original_state_index==src->native_source_state_index&&
       (!strcmp(e->native_original_track_name,"attack")||
        !strcmp(e->native_original_track_name,"Attack"))){
      obs->source_attack_event_start_raw_UNCLASSIFIED=e->raw_original_2010_start;
      /* G221 original Actor::UpdateStateAttack reads event[index]+8
       * to C++ virtual DoAttack(AttackType, third); G222 proves MainCharacter.
       * This is the first SOURCE event for a name-based matched StateData;
       * it is NOT verified original runtime current-index selection, and
       * must never spawn any attack or cause damage here. */
      obs->source_attack_event_third_u32_UNCLASSIFIED=e->raw_original_2010_third_field_UNCLASSIFIED;
      /* Original event record is immutable. Observing 60 rendered frames
       * of this ONE clip is not evidence of 60 native attack callbacks. */
      if(newly_loaded_clip)++obs->native_raw_attack_event_rows_observed;
      break;
    }
  }
  return 1;
}
#endif /* B24_G218_LIVE_AUTHENTIC_2010_STATE_OBSERVER_H */