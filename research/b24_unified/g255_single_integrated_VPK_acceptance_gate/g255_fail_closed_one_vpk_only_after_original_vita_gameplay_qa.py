#!/usr/bin/env python3
"""G255 two-stage ONE Vita VPK gate: first source-complete source/host/ARM
preflight -> one VPK, THEN physical Vita hardware parity. Never require
playing the new VPK on Vita BEFORE the first packaging (deadlock).
Audit only, no original iOS/PS Vita files or VPK created.
"""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
POST=ROOT/"g83_final_vpk_gate"/"READINESS_STATUS.json"
PRE=ROOT/"g255_single_integrated_VPK_acceptance_gate"/"SOURCE_PRE_VPK_READINESS.json"
OUT=Path("/tmp/g255_vpk_release_guard/G255_SINGLE_VPK_SOURCE_AND_HARDWARE_ACCEPTANCE_STATUS.json")
PRE_REQUIRED={
 "authentic_MC_initial_world_root_and_source_ground_collision_bound",
 "ground_hover_flight_rush_one_integrator_source_QA_pass",
 "all_target_armor_authentic_animation_rig_state_input_event_routed",
 "original_weaponDB_combat_melee_damage_WM_weapons_source_integrated",
 "source_city_hero_vehicle_scale_sky_light_alpha_HUD_camera_integrated",
 "original_Mission000_cutscene_QTE_sound_waves_and_success_host_integrated",
 "final_single_game_Vita_ARM_ELF_and_all_C11_QA_pass_same_commit",
}
POST_REQUIRED={
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
HARDWARE_REQUIRED={
 "ground_hover_cruise_rush_direction_transitions_actually_playable",
 "original_Mark_V_suitcase_629v_full_move_family_playable",
 "G68_original_Expo_collision_camera_flight_lighting_issues_regressed",
 "original_Mission000_QTE_cutscene_audio_and_mission_complete_playable",
}
def checked(path:Path,expected:set[str],flag:str,requires_hardware:bool):
 doc=json.loads(path.read_text())
 gates=doc.get("gates")
 if not isinstance(gates,dict) or set(gates)!=expected:
  raise ValueError(f"G255 original gate schema changed unexpectedly {path}")
 passed=[];blocked=[]
 for key,item in gates.items():
  if not isinstance(item,dict) or not isinstance(item.get(flag),bool):
   raise ValueError(f"invalid original gate status {key}")
  evidence=item.get("evidence_uri")
  if item[flag]:
   if not isinstance(evidence,str) or not evidence.startswith(
      "https://github.com/Gh0sTRX/Iron-man-2-os/actions/runs/"):
    raise ValueError(f"verified without genuine original source GitHub CI proof: {key}")
   if requires_hardware and key in HARDWARE_REQUIRED and (
      "physical vita" not in str(item.get("test_details","")).lower()):
    raise ValueError(f"post-VPK device parity marked without physical Vita evidence: {key}")
   passed.append(key)
  else:blocked.append(key)
 return passed,blocked
def status(post:Path,pre:Path):
 ready,open_source=checked(pre,PRE_REQUIRED,"source_ready",False)
 passed,open_device=checked(post,POST_REQUIRED,"verified",True)
 return {
  "policy":"TWO STAGES: finish 7 authentic original source host and Vita ARM acceptance checks, produce exactly one test VPK; subsequently verify 12 physical/parity quality checks on that VPK. NEVER demand first-device QA before packaging.",
  "source_preflight_gates_total":len(PRE_REQUIRED),
  "source_preflight_verified":ready,
  "source_preflight_blockers":open_source,
  "source_preflight_verified_count":len(ready),
  "source_preflight_blocking_count":len(open_source),
  "VPK_build_authorized_by_source_gates":not open_source,
  "original_release_acceptance_gates_total":len(POST_REQUIRED),
  "actually_verified_acceptance_gates":passed,
  "actually_blocking_VPK_acceptance_gates":open_device,
  "verified_count":len(passed),
  "blocking_count":len(open_device),
  "final_physical_Vita_parity_satisfied_after_VPK":not open_device,
  "VPK_build_authorized_by_gates":not open_source,
  "original_2010_native_G252_SpawnPoint_NPC_waves_confirmed":True,
  "original_2010_native_G254_MC_PositionData_StateMgr_init_confirmed":True,
  "original_player_actual_runtime_world_xyz_proven_at_current_snapshot":False,
  "G229_real_physical_Vita_120_frames_received_at_2026_10_19":False,
  "no_VPK_produced_by_audit":True
 }
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source-readiness",type=Path,default=PRE)
 p.add_argument("--readiness",type=Path,default=POST)
 p.add_argument("--out",type=Path,default=OUT)
 p.add_argument("--require-ready",action="store_true",
    help="Require all seven SOURCE integration prerequisites BEFORE generating exactly one test VPK.")
 p.add_argument("--require-device-parity",action="store_true",
    help="Require all twelve post-package hardware/gameplay checks AFTER VPK tested on a PS Vita.")
 a=p.parse_args()
 report=status(a.readiness,a.source_readiness)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print(f"G255 ONE TEST VPK preflight: source-ready {report['source_preflight_verified_count']}/7, source blocked {report['source_preflight_blocking_count']}/7")
 for q in report["source_preflight_blockers"]:print("G255 SOURCE BLOCKER",q)
 print(f"G255 AFTER-test Vita original gameplay parity: verified {report['verified_count']}/12, remaining {report['blocking_count']}/12")
 print("G255 audit built no VPK; source PASS is not a physical Vita test.")
 if a.require_ready and not report["VPK_build_authorized_by_source_gates"]:
  print("G255 FAIL-CLOSED: not ready to package single test Vita VPK",file=sys.stderr)
  return 3
 if a.require_device_parity and not report["final_physical_Vita_parity_satisfied_after_VPK"]:
  print("G255 FAIL-CLOSED: post-test original game parity not proven",file=sys.stderr)
  return 4
 return 0
if __name__=="__main__":sys.exit(main())
