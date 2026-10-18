/* G218 real authenticated 2010 original source G217 4-suit state header
 * + actual G8 source clip filename -> strict single original native
 * StateData source index + source-only timing metadata observation.
 * NO 2010 weapon mapping, damage, missile, physics or Vita VPK.
 * Compile against generated G217 owner source C11 header via CI download.
 */
#include "b24_g218_live_authentic_2010_state_observer.h"
#include <stdio.h>
#include <string.h>
#define REQ(condition) do{if(!(condition)){fprintf(stderr,"G218 failed line %d: %s\n",__LINE__,#condition);return 1;}}while(0)
static int original(int suit,const char *real_im2v,const char *state,int native_state,
                    uint32_t source_attack_type,uint32_t original_attack_raw){
 B24G218LiveObserver g={0};
 REQ(b24_g218_observe_actually_loaded_G8_clip(&g,suit,real_im2v,1,0)==1);
 REQ(g.source_state_index_correlated_by_filename_ONLY);
 REQ(g.source_native_state_index==(unsigned)native_state);
 REQ(g.source_state_name_correspondence_ONLY!=NULL);
 REQ(!strcmp(g.source_state_name_correspondence_ONLY,state));
 REQ(g.source_authored_AttackType_or_UNKNOWN==source_attack_type);
 REQ(g.source_attack_event_start_raw_UNCLASSIFIED==original_attack_raw);
 REQ(g.selected_actual_G8_IM2V_clip==real_im2v);
 REQ(g.successfully_correlated==1u&&g.source_animation_frames_observed==1u);
 REQ(g.unmapped_source_clip_frames==0u);
 REQ(g.actual_2010_StateMgr_runtime_state_PROVEN==0);
 REQ(g.actual_2010_melee_hit_or_projectile_event_PROVEN==0);
 /* Only the game-selected ACTUALLY LOADED G8 source may be counted. */
 REQ(b24_g218_observe_actually_loaded_G8_clip(&g,suit,real_im2v,0,0)==0);
 REQ(g.source_state_index_correlated_by_filename_ONLY==0);
 REQ(g.source_state_name_correspondence_ONLY==NULL);
 REQ(g.actual_2010_melee_hit_or_projectile_event_PROVEN==0);
 REQ(b24_g218_observe_actually_loaded_G8_clip(&g,suit,real_im2v,1,1)==0);
 REQ(g.source_state_index_correlated_by_filename_ONLY==0);
 return 0;
}
int main(void){
 REQ(B24G217_ARMOR_COUNT==4);
 REQ(B24G217_SOURCE_STATES_PER_ARMOR==194);
 REQ(B24G217_TRUE_SOURCE_ATTACK_TRAIL_EVENT_COUNT>=70);
 REQ(!strcmp(b24g217_original_suit_source_names[0],"IronMan"));
 REQ(!strcmp(b24g217_original_suit_source_names[1],"IronMan_suitcase"));
 REQ(!strcmp(b24g217_original_suit_source_names[2],"Warmachine"));
 REQ(!strcmp(b24g217_original_suit_source_names[3],"stealth"));
 REQ(original(0,"ironman_ironman_ground_idel","Idle",0,B24G217_UNKNOWN_U32,B24G217_UNKNOWN_U32)==0);
 REQ(original(0,"ironman_ironman_walk_f","Move_Walk",2,B24G217_UNKNOWN_U32,B24G217_UNKNOWN_U32)==0);
 REQ(original(0,"ironman_ironman_run","Move_Run",3,B24G217_UNKNOWN_U32,B24G217_UNKNOWN_U32)==0);
 REQ(original(0,"ironman_ironman_fly_f","Fly",14,B24G217_UNKNOWN_U32,B24G217_UNKNOWN_U32)==0);
 REQ(original(0,"ironman_ironman_ground_combo_1","Attack_Ground_COMBO1",40,0u,300u)==0);
 REQ(original(0,"ironman_ironman_ground_combo_2","Attack_Ground_COMBO2",42,0u,200u)==0);
 REQ(original(0,"ironman_ironman_ground_combo_3","Attack_Ground_COMBO3",44,0u,500u)==0);
 REQ(original(4,"suitcase_ironman_ground_combo_1","Attack_Ground_COMBO1",40,0u,300u)==0);
 REQ(original(0,"ironman_ironman_aim_m_ground_idle","Attack_M_Ground_idle",66,2u,260u)==0);
 REQ(original(2,"warmachine_warmachine_aim_m_ground_idle","Attack_M_Ground_idle",66,25u,260u)==0);
 REQ(original(0,"ironman_ironman_aim_m_float_idle","Attack_M_Float_idle",65,2u,250u)==0);
 REQ(original(2,"warmachine_warmachine_aim_m_float_idle","Attack_M_Float_idle",65,25u,250u)==0);
 REQ(original(0,"ironman_ironman_aim_ground_beam1","Attack_Ground_Beam_prepare",84,4u,B24G217_UNKNOWN_U32)==0);
 REQ(original(0,"ironman_ironman_aim_ground_beam2","Attack_Ground_Beam",85,4u,B24G217_UNKNOWN_U32)==0);
 REQ(original(0,"ironman_ironman_aim_ground_beam3","Attack_Ground_Beam_out",86,4u,413u)==0);
 REQ(original(4,"suitcase_ironman_aim_float_beam3","Attack_Float_Beam_out",89,4u,507u)==0);
 B24G218LiveObserver w={0};
 REQ(b24_g218_observe_actually_loaded_G8_clip(&w,2,"warmachine_warmachine_aim_m_ground_idle_att",1,0)==0);
 REQ(w.unmapped_source_clip_frames==1u);
 REQ(b24_g218_observe_actually_loaded_G8_clip(&w,3,"stealth_ironman_aim_ground_beam2",1,0)==0);
 REQ(w.unmapped_source_clip_frames==2u);
 REQ(b24_g218_observe_actually_loaded_G8_clip(&w,2,"warmachine_warmachine_aim_ground_idle",1,0)==0);
 REQ(w.unmapped_source_clip_frames==3u);
 REQ(b24_g218_observe_actually_loaded_G8_clip(&w,0,"ironman_ironman_aim_ground_beam4",1,0)==0);
 REQ(w.unmapped_source_clip_frames==4u);
 REQ(!w.actual_2010_melee_hit_or_projectile_event_PROVEN);
 REQ(!w.actual_2010_StateMgr_runtime_state_PROVEN);
 B24G218LiveObserver native={0};
 REQ(b24_g218_observe_actually_loaded_G8_clip(&native,0,"ironman_ironman_ground_combo_1",1,0));
 REQ(native.source_authored_next_state_or_UNKNOWN==41u);
 REQ(native.source_authored_type_or_UNKNOWN==4u);
 REQ(native.source_authored_loop_or_UNKNOWN==0u);
 REQ(b24_g218_observe_actually_loaded_G8_clip(&native,0,"ironman_ironman_aim_ground_beam1",1,0));
 REQ(native.source_authored_next_state_or_UNKNOWN==85u); /* original prepare->Beam source */
 REQ(native.source_authored_type_or_UNKNOWN==24u);
 REQ(b24_g218_observe_actually_loaded_G8_clip(&native,0,"ironman_ironman_aim_ground_beam2",1,0));
 REQ(native.source_authored_next_state_or_UNKNOWN==B24G217_UNKNOWN_U32); /* looping */
 REQ(native.source_authored_loop_or_UNKNOWN==1u);
 REQ(b24_g218_observe_actually_loaded_G8_clip(&native,0,"ironman_ironman_aim_ground_beam3",1,0));
 REQ(native.source_authored_next_state_or_UNKNOWN==0u); /* source original Beam out to Idle */
 REQ(b24_g218_observe_actually_loaded_G8_clip(&native,4,"suitcase_ironman_aim_float_beam3",1,0));
 REQ(native.source_authored_next_state_or_UNKNOWN==11u); /* original return Float */
 REQ(b24_g218_observe_actually_loaded_G8_clip(&native,2,"warmachine_warmachine_aim_m_ground_idle",1,0));
 REQ(native.source_authored_next_state_or_UNKNOWN==60u); /* source WM Aim_M Ground idle */
 REQ(native.source_authored_AttackType_or_UNKNOWN==25u);
 REQ(!native.actual_2010_StateMgr_runtime_state_PROVEN);
 REQ(!native.actual_2010_melee_hit_or_projectile_event_PROVEN);
 REQ(b24_g218_observe_actually_loaded_G8_clip(&native,2,"not_an_original_2010_clip",1,0)==0);
 REQ(native.source_authored_next_state_or_UNKNOWN==B24G217_UNKNOWN_U32);
 REQ(native.source_authored_loop_or_UNKNOWN==B24G217_UNKNOWN_U32);
 b24_g218_observer_reset(&w);
 REQ(w.source_animation_frames_observed==0u);
 puts("G218 PASS actual 2010 G8 original IM2V filename -> 4 source armor 194 StateData/AttackType + raw true StateTrack event telemetry, 0 damage, no guesses and NO VPK");
 return 0;
}
