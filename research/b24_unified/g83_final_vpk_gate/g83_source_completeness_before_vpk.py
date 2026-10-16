#!/usr/bin/env python3
"""G83 fail-closed NEXT Iron Man 2 Vita VPK release readiness gate.

Owner explicitly requires complete original iOS 2010 moveset + combat +
touchHLE behavioral parity BEFORE producing next test VPK. This code never
compiles/builds packages. Its only function is to REFUSE to proceed unless
independent source QA reports are provided for all mandatory requirements.
An isolated module/unit test cannot stand in for complete-game acceptance.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

REQUIRED=(
 'original_2010_972_animation_source_record_indexed',
 'all_338_player_named_clips_implemented_as_rig_compatible_streams',
 'original_Mark_V_suitcase_629v_full_move_family_playable',
 'ground_hover_cruise_rush_direction_transitions_actually_playable',
 'original_combo_power_counter_throw_grab_input_transition_conditions_verified',
 'original_repulsor_missile_unibeam_damage_and_hit_frames_verified',
 'original_WeaponDB_per_attack_damage_and_projectile_values_typed_from_2010_26_attacks',
 'original_NPC_drone_hit_hurt_death_AI_and_mission_wave_behaviour_integrated',
 'G68_original_Expo_collision_camera_flight_lighting_issues_regressed',
 '2010_touchHLE_gameplay_reference_recorded_and_parity_checked',
 'final_game_source_host_integration_and_vita_arm_cross_compile_all_pass'
)
def audit(status:dict):
 results=status.get('gates',{})
 if not isinstance(results,dict):raise ValueError('gates must be a dict')
 missing=[]
 for gate in REQUIRED:
  proof=results.get(gate)
  if not isinstance(proof,dict) or proof.get('verified') is not True:
   missing.append((gate,'missing objective passing test evidence'))
   continue
  if not isinstance(proof.get('evidence_uri'),str) or len(proof['evidence_uri'])<10:
   missing.append((gate,'verified flag alone not allowed: evidence_uri absent'))
  if not isinstance(proof.get('test_details'),str) or len(proof['test_details'])<20:
   missing.append((gate,'actual source/device test description absent'))
 return missing
def run(path:Path,strict:bool):
 status=json.loads(path.read_text())
 missing=audit(status)
 print('G83 original Iron Man 2 complete-playable combat/moveset packaging release gate')
 print('DONE WITH VERIFIED SOURCES:',len(REQUIRED)-len(missing),'/',len(REQUIRED))
 for gate,reason in missing:
  print(' NOT YET APPROVED:',gate,'--',reason)
 if missing:
  print('BLOCKED: Do NOT create or ship a new test VPK until every gate passes.')
  return 1 if strict else 0
 print('ALL mandatory source-only host and touchHLE parity evidence reported. VPK packaging may be separately requested.')
 return 0
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--status',type=Path,required=True)
 p.add_argument('--strict',action='store_true',
    help='Exit nonzero if ANY mandatory task is unfinished; use in future build prerequisite')
 a=p.parse_args()
 sys.exit(run(a.status,a.strict))
