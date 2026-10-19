#!/usr/bin/env python3
"""G255 single-VPK-only AFTER real original gameplay/hardware source gates.
Fail closed: no VPK packaging, no user source assets. Source provenance,
C11 and ARM ELF success are not physical Vita acceptance.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/"g83_final_vpk_gate"/"READINESS_STATUS.json"
OUT=Path("/tmp/g255_vpk_release_guard/G255_SINGLE_VPK_SOURCE_AND_HARDWARE_ACCEPTANCE_STATUS.json")
REQUIRED_GATES={
 "original_2010_972_animation_source_record_indexed",
 "all_338_player_named_clips_implemented_as_rig_compatible_streams",
 "original_Mark_V_suitcase_629v_full_move_family_playable",
 "ground_hover_cruise_rush_direction_transitions_actually_playable",
 "original_combo_power_counter_throw_grab_input_transition_conditions_verified",
 "original_repulsor_missile_unibeam_damage_and_hit_frames_verified",
 "original_WeaponDB_per_attack_damage_and_projectile_values_typed_from_2010_26_attacks",
 "original_NPC_drone_hit_hurt_death_AI_and_mission_wave_behaviour_integrated",
 "G68_original_Expo_collision_camera_flight_lighting_issues_regressed",
 "2010_touchHLE_gameplay_reference_recorded_and_parity_checked",
 "final_game_source_host_integration_and_vita_arm_cross_compile_all_pass",
 "original_Mission000_QTE_cutscene_audio_and_mission_complete_playable",
}
HARDWARE_MUST_BE_EVIDENCED={
 "ground_hover_cruise_rush_direction_transitions_actually_playable",
 "original_Mark_V_suitcase_629v_full_move_family_playable",
 "G68_original_Expo_collision_camera_flight_lighting_issues_regressed",
 "original_Mission000_QTE_cutscene_audio_and_mission_complete_playable",
}
def status(path:Path):
 d=json.loads(path.read_text())
 gates=d.get("gates")
 if not isinstance(gates,dict) or set(gates)!=REQUIRED_GATES:
  raise ValueError("one-VPK gate schema mismatch: missing/added original 12 acceptance cases")
 passed,blocked=[],[]
 for name,item in gates.items():
  if not isinstance(item,dict) or not isinstance(item.get("verified"),bool):
   raise ValueError(f"invalid one VPK gate verified type {name}")
  evidence=item.get("evidence_uri")
  if item["verified"]:
   if not isinstance(evidence,str) or not evidence.startswith("https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/"):
    raise ValueError(f"verified gate missing real CI provenance {name}")
   if name in HARDWARE_MUST_BE_EVIDENCED and "physical vita" not in str(item.get("test_details","")).lower():
    raise ValueError(f"marked hardware gate without explicit physical Vita QA metadata: {name}")
   passed.append(name)
  else:blocked.append(name)
 return {
  "policy":"Exactly one integrated PS Vita VPK test ONLY after all 12 native-2010 gameplay, visuals, mission, hardware quality gates have evidence; never pack on source hypothesis.",
  "readiness_file_date":d.get("updated"),
  "original_release_acceptance_gates_total":len(gates),
  "actually_verified_acceptance_gates":passed,
  "actually_blocking_VPK_acceptance_gates":blocked,
  "verified_count":len(passed),
  "blocking_count":len(blocked),
  "VPK_build_authorized_by_gates":not blocked,
  "native_source_G252_SpawnPoint_class71_NPC_spawn_wave_methods_proven":True,
  "native_source_G254_original_MainCharacter_LoadFromFile_Init_chain_proven":True,
  "native_original_player_world_start_scene_transform_and_real_ground_height_PROVEN":False,
  "G251_host_2010_city_grounded_104_of_128_directions_is_not_device_parity":True,
  "G229_real_physical_Vita_120_ground_frames_telemetry_received_as_of_2026_10_19":False,
  "actual_Playable_Vita_Mission000_QTE_enemy_wave_ending_acceptance_as_of_2026_10_19_PROVEN":False,
  "no_VPK_produced_by_this_audit":True,
 }
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--readiness",type=Path,default=DEFAULT)
 p.add_argument("--out",type=Path,default=OUT)
 p.add_argument("--require-ready",action="store_true")
 a=p.parse_args()
 report=status(a.readiness)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print(f"G255 ONE VPK RELEASE GUARD: source or hardware acceptance verified {report['verified_count']}/12, blocked {report['blocking_count']}/12")
 for row in report["actually_blocking_VPK_acceptance_gates"]:print("G255 REAL REMAINING BLOCKER",row)
 print("G255 VPK PACKAGE NOT BUILT; no physics, animation, camera, combat or gameplay changed.")
 if a.require_ready and not report["VPK_build_authorized_by_gates"]:
  print("G255 NOT READY: fail closed; do NOT build one Vita VPK yet",file=sys.stderr)
  return 3
 return 0
if __name__=="__main__":sys.exit(main())
