#ifndef B24_G11_COMBAT_STAGE_POLICY_H
#define B24_G11_COMBAT_STAGE_POLICY_H
/* One authoritative decision BEFORE original B14 movement and B16 shot.
   The original B14 (2010 port prototype) stage2 threshold is .96
   from ground/hover, .88 while already fast; strict .82 cap avoids both.
   No fabricated animation clips and no altering the original rush anim. */
typedef struct {
 float move_x,move_y;
 int boost,trigger,paused,flying,prior_flight_stage;
} B24G11CombatInput;
typedef struct {
 float move_x,move_y;
 int boost,allow_repulsor,allow_unibeam,allow_missile;
 int force_walk,force_stage1;
} B24G11CombatDecision;
int b24_g11_combat_stage_policy(const B24G11CombatInput *in,
                                B24G11CombatDecision *out);
int b24_g11_stage_allows_hand_attack(int flying,int current_flight_stage);
#endif
