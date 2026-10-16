#!/usr/bin/env python3
"""G81 complete ORIGINAL 2010 Iron Man 2 (1.0.0) moveset inventory.
Parse all 972 original .anim track streams, not animation names alone.
Emit an honest ALL-moves playable rig / combat / NPC / QTE catalog,
no imaginary live attack timing. Source-only, no new VPK.

"Complete moveset" release gate cannot pass just because 972 entries are
decoded: it also requires 2010 behavior replay on touchHLE, hit windows,
source attack parameters, world-facing combat, and actual Vita QA.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re,sys,zipfile,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'g76_original_combat'))
from b24_owner_pack_extract import decode,get_exact
from g76_2010_combat_animation_binary_forensics import parse_anim
UNDERWATER_OBJECTS={
 'underwater_bomb_idle','underwater_cannon_attack','underwater_cannon_idle',
 'underwater_ship02_idle','underwater_ship02_shake','underwater_ship02_fall',
 'underwater_ship_idle','underwater_ship_shake','underwater_ship_fall'}
def classify(name):
 n=name.lower().removesuffix('.anim')
 if n.startswith('ironman_'):rig='IronMan'
 elif n.startswith('warmachine_'):rig='WarMachine'
 elif n.startswith('underwater_'):
  rig='UnderwaterObject' if n in UNDERWATER_OBJECTS else 'UnderwaterArmor'
 elif n.startswith(('drone_','enemy_','boss_','whiplash_','firepower_')):
  rig='NPC_Boss_or_Drone'
 else:rig='OtherNPC_or_Scene'
 tags=[]
 for word,pattern in (
  ('melee_combo',r'combo|punch|kick|melee|_att_s|_ground_att|_air_counter'),
  ('grab_throw',r'raise|throw|put_down|hold_boss|fall_on_boss'),
  ('hurt_death',r'hurt|hit|injur|death|dead|_die|dying|_falling'),
  ('ranged_attack',r'missile|unibeam|beam|_att|_shoot|cannon|_fire|laser'),
  ('defense_dodge',r'dodge|defence|defense|block|paralys|pushaway'),
  ('locomotion',r'walk|_run|fly|float|swim|_move|_rush|_drift'),
  ('transition',r'2ground|2run|2float|2fly|2swim|2land|ftol|ftor|ltof|rtof|land'),
  ('mission_qte',r'qte|boss|machine_man|obstacle|jump_bomb|_movie')):
  if re.search(pattern,n):tags.append(word)
 if not tags:tags=['idle_pose_or_other']
 return rig,tags
def audit(ipa:Path,out:Path):
 with zipfile.ZipFile(ipa) as z:
  raw=z.read('Payload/IronMan2.app/anims')
 rows=decode(raw,'.anim')
 assert len(rows)==972,"Original 2010 iOS IPA version/animation bank mismatch"
 result=[];sha=hashlib.sha256(raw).hexdigest()
 for row in rows:
  source=get_exact(raw,rows,row.name)
  info=parse_anim(source)
  rig,tags=classify(row.name)
  result.append({
   'original_source_file':row.name,
   'original_archive_byte_offset':row.start,
   'original_source_bytes_sha256':hashlib.sha256(source).hexdigest(),
   'source_duration_ms':info['time_last_ms'], # original B13 duration equals last keyed timestamp; four source clips begin late
   'source_first_time_ms':info['time_first_ms'],
   'source_last_time_ms':info['time_last_ms'],
   'native_joint_track_count':info['channels'],
   'source_animated_xyz_channel_count':info['animated_translation_channels'],
   'source_animated_quaternion_channel_count':info['animated_rotation_channels'],
   'original_src_decoded_full_raw_channel_content':True,
   'rig_from_filename_only':rig,
   'tags_from_filename_only':tags,
   'hit_active_window_recovered_from_original_native_gameplay':False,
   'full_gameplay_transition_condition_decoded':False,
   'B24_Vita_rig_and_anim_state_bound_tested':False})
 rigs=collections.Counter(x['rig_from_filename_only'] for x in result)
 assert rigs['IronMan']==248 and rigs['WarMachine']==56
 assert rigs['UnderwaterArmor']==34 and rigs['UnderwaterObject']==9
 assert sum(rigs.values())==972
 player=[r for r in result if r['rig_from_filename_only'] in
         ('IronMan','WarMachine','UnderwaterArmor')]
 assert len(player)==338
 combo=[r for r in player if 'melee_combo' in r['tags_from_filename_only']]
 zero=[r for r in player if r['source_duration_ms']==0]
 assert combo and zero
 coverage={'2010_original_all_972_raw_ANIM_files_decoded':len(result),
   '2010_original_anim_pack_sha256':sha,
   'owner_authenticated_data_only':True,
   'rig_distribution_name_derived':dict(rigs),
   'genuine_player_named_ironman_wm_underwater_armor':len(player),
   'original_movement_and_combat_clips_count_from_regex_only':len(combo),
   'original_zero_duration_player_clips':len(zero),
   'source_972_anim_registry':result,
   'original_movement_B24_source_baked_vs_playable_all_338':False,
   'G75_gameplay_integration_complete':False,
   'original_combat_damage_and_hit_window_integration_complete':False,
   'touchHLE_original_iOS_1_0_0_interactive_combat_capture_complete':False,
   'original_all_moveset_input_transitions_verified_against_touchHLE':False,
   'NO_VPK_until_all_release_gates_pass':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G81_ALL_ORIGINAL_972_ANIMS_AND_338_PLAYER_MOVESET.json').write_text(
   json.dumps(coverage,indent=2,ensure_ascii=False)+'\n')
 with (out/'G81_ORIGINAL_338_PLAYER_MOVESET.csv').open('w',newline='') as f:
  writer=csv.writer(f)
  writer.writerow(['native_clip','source_duration_ms','source_channels','xyz_channels','quat_channels',
       'rig_name_prefix','categories_filename_only','original_hit_window_known'])
  for q in player:
   writer.writerow([q['original_source_file'],q['source_duration_ms'],
      q['native_joint_track_count'],q['source_animated_xyz_channel_count'],
      q['source_animated_quaternion_channel_count'],q['rig_from_filename_only'],
      ';'.join(q['tags_from_filename_only']),'NO'])
 with (out/'G81_COMBAT_POWER_THROW_HURT_AND_DODGE_NAMED_SOURCE_CLIPS.csv').open('w',newline='') as f:
  writer=csv.writer(f)
  writer.writerow(['native_original_clip','duration_ms','rig','categories'])
  for q in result:
   if any(n in q['tags_from_filename_only'] for n in
          ('melee_combo','grab_throw','hurt_death','ranged_attack','defense_dodge')):
    writer.writerow([q['original_source_file'],q['source_duration_ms'],
         q['rig_from_filename_only'],';'.join(q['tags_from_filename_only'])])
 print('PASS G81 decoded all 972 original iOS ANIM, 338 named player motions',dict(rigs))
 print('SOURCE G81 player melee/combo named',len(combo),'zero-duration',len(zero))
 print('G81 selected original player authored combo sources:',
   [(v['original_source_file'],v['source_duration_ms']) for v in combo[:24]])
 print('HARD VPK GATE BLOCKED: native original touchHLE real behavior/input and all gameplay combat integration NOT YET tested')
if __name__=='__main__':
 a=argparse.ArgumentParser()
 a.add_argument('--ipa',required=True,type=Path)
 a.add_argument('--out',required=True,type=Path)
 p=a.parse_args();audit(p.ipa,p.out)
