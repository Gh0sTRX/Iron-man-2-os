/* G304 audit exact original G213B/G217 sourced 2010 iOS StateData and
 * native attack track against the G83/G82 port animator HIT contract.
 * G217 input header is generated from original fully parsed states in CI.
 * G8 real IM2V clip names/timing are original, but neither that name
 * nor StateTrack raw integer has a proven runtime hit/weapon effect.
 * This must NOT emit an additional source-2010 hit request.
 * No IPA assets copied, no VPK or fictitious damage windows. */
#include "b24_g83_unified_movement_aim.h"
#include "b24_g217_AUTHENTIC_original_2010_iOS_source_states_ONLY_NO_VPK.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
static const B24G217_SourceState *source_state(int group,int index,
                                               const char *name,
                                               uint32_t attack_type){
 const B24G217_SourceState *s=&b24g217_true_2010_owner_states[group][index];
 assert(s->native_source_state_index==(uint16_t)index);
 assert(!strcmp(s->original_source_state_name,name));
 assert(s->original_AttackType_or_UNKNOWN==attack_type);
 return s;
}
static int native_track(int group,int state,int raw_start){
 int found=0;
 for(unsigned i=0;i<B24G217_TRUE_SOURCE_ATTACK_TRAIL_EVENT_COUNT;i++){
  const B24G217_SourceEvent *e=&b24g217_source_attack_trail_events[i];
  if(e->native_suit_group_index!=(uint16_t)group ||
     e->native_original_state_index!=(uint16_t)state)continue;
  if(strcmp(e->native_original_track_name,"attack")&&
     strcmp(e->native_original_track_name,"Attack"))continue;
  if(e->raw_original_2010_start==(uint32_t)raw_start)found++;
 }
 return found;
}
int main(void){
 assert(B24G217_ARMOR_COUNT==4);
 assert(B24G217_SOURCE_STATES_PER_ARMOR==194);
 /* These are REALLY original-authored native state fields; they are
  * NOT source proof that WM _M is a missile or that r2 is hit damage. */
 (void)source_state(0,40,"Attack_Ground_COMBO1",0u);
 (void)source_state(0,42,"Attack_Ground_COMBO2",0u);
 (void)source_state(0,44,"Attack_Ground_COMBO3",0u);
 (void)source_state(0,66,"Attack_M_Ground_idle",2u);
 (void)source_state(2,66,"Attack_M_Ground_idle",25u);
 (void)source_state(0,85,"Attack_Ground_Beam",4u);
 assert(native_track(0,40,300)>0);
 assert(native_track(0,42,200)>0);
 assert(native_track(0,44,500)>0);
 /* Confirm a SOURCE discrepancy in inference: the first combo source
  * IM2V pose lasts 266ms while the actual original StateTrack raw
  * 'attack' entry has START=300 of UNKNOWN units. They cannot safely be
  * equated, or turned into any Vita contact time. */
 B24G83Input in={0};
 in.suit_index=B24G83_MARKVI;
 in.motion=B24G83_GROUND;
 in.axis_y=1.f;
 in.aim=B24G83_AIM_HAND;
 in.accepted_weapon_event=1;
 B24G83Selection out={0};
 assert(b24_g83_select_original_motion(&in,&out));
 assert(out.stem&&!strcmp(out.stem,"ironman_ironman_aim_ground_move_f_att"));
 assert(out.one_shot_not_looping&&out.original_source_duration_ms==866u);
 assert(!out.needs_2010_hit_event&&!out.input_semantics_verified_original_ios);
 B24G82Combat chain={0};
 b24_g82_request_melee(&chain,1000,1,0);
 assert(b24_g83_select_combined(&chain,1001,&in,&out));
 assert(out.stem&&!strcmp(out.stem,"ironman_ironman_ground_combo_1"));
 assert(out.original_source_duration_ms==266u);
 assert(!out.needs_2010_hit_event);
 /* False-source contact never applies damage: even if an original
  * attack TRACK EXISTS, G82 still requires verified ACTOR contact,
  * native attack instance Damage and attacker/target permission. */
 B24G82Contact evidence={0};
 B24G76DamageResource target={0};
 const unsigned before=chain.accepted_hits;
 assert(b24_g82_resolve_source_contact(&chain,&evidence,&target)==B24_G76_NO_HIT);
 assert(chain.accepted_hits==before);
 assert(chain.rejected_unverified_events==1u);
 in.suit_index=B24G83_WARMACHINE;
 in.aim=B24G83_AIM_M_UNCLASSIFIED;
 in.accepted_weapon_event=1;
 assert(b24_g83_select_original_motion(&in,&out));
 assert(out.stem&&!strcmp(out.stem,"warmachine_warmachine_aim_m_ground_move_f_att"));
 assert(!out.needs_2010_hit_event);
 /* WM raw AttackType 25 is authentically DIFFERENT from Mark VI 2.
  * Their semantic mapping to missile/gatling/repulsor remains UNKNOWN. */
 assert(b24g217_true_2010_owner_states[2][66].original_AttackType_or_UNKNOWN==25u);
 assert(b24g217_true_2010_owner_states[0][66].original_AttackType_or_UNKNOWN==2u);
 puts("G304 PASS original fully recovered iOS G217 StateData AttackType + unclassified raw StateTrack events prove NO native damage time; G83 no false secondary hit, G82 unverified contacts blocked; NO VPK");
 return 0;
}
