#!/usr/bin/env python3
"""G81 documented original 2010 player moveset from EXISTING verified B18
catalog; can run with no owner IPA or native source assets at CI runtime.
All 304 IronMan/WarMachine sources are mapped to an index usable for B24
runtime routing; action tags are hints, NOT real hit frames/control rules.
Underwater 34 need separate original rig and full referenced source bank.
No VPK.
"""
from __future__ import annotations
import argparse,csv,json,re,collections
from pathlib import Path
ENTRY=re.compile(r'^\|\s*`((?:IronMan|Ironman|Warmachine)_[^\`]+\.anim)`\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|',re.I|re.M)
def tags(source):
 s=source.casefold()
 group=[]
 for name,pattern in [('melee_combo','combo|punch|kick|melee|ground_att'),
 ('hurt_death','hurt|death|dead|hit|die'),
 ('grounded','walk|run|ground|jump|raise|throw'),
 ('airborne','fly|float|air|land'),
 ('repulsor_aim','aim|shoot|fire|_att'),
 ('transition','2run|2ground|2float|f2l|f2r|ftol|ftor|ltof|rtof|land|start|end'),
 ('qte_mission','qte|boss|obstacle|bomb|machine_man')]:
  if re.search(pattern,s):group.append(name)
 return group or ['uncategorized']
def run(document,out):
 body=document.read_text()
 rows=ENTRY.findall(body)
 if len(rows)!=304:raise ValueError(f'Need 304 authenticated B18 2010 sources, got {len(rows)}')
 clips=[]
 for filename,ms,channels in rows:
  rig='WarMachine' if filename.casefold().startswith('warmachine_') else 'IronMan'
  original_stem=filename.removesuffix('.anim').casefold()
  stream=original_stem.split('_',1)[0]+'_'+original_stem
  clips.append({'2010_source_animation_name':filename,'duration_ms':int(ms),
    'source_track_count':int(channels),
    'body_rig_from_filename':rig,'2010_move_categories_name_based_only':tags(filename),
    'canonical_G8_stream_alias_candidate':stream,
    'real_native_hit_frame_verified':False,
    '2010_original_move_control_binding_verified':False,
    'G73_runtime_clip_appears_in_G8_source_not_all_playable':True})
 if len({x['2010_source_animation_name'].casefold() for x in clips})!=304:
  raise ValueError('Original authenticated B18 contains duplicated 2010 source labels')
 counts=collections.Counter(x['body_rig_from_filename'] for x in clips)
 assert counts=={'IronMan':248,'WarMachine':56}
 byname={x['2010_source_animation_name'].casefold():x for x in clips}
 for n in ('ironman_ground_combo_1.anim','ironman_ground_combo_2.anim',
           'ironman_ground_combo_3.anim','ironman_ground_hurt1.anim',
           'ironman_fly_f_rush.anim','ironman_air_counteratt.anim',
           'warmachine_aim_fly_m.anim'):
  if n not in byname:raise AssertionError('Original source game clip missing: '+n)
 assert [byname[f'ironman_ground_combo_{i}.anim']['duration_ms'] for i in (1,2,3)]==[266,300,500]
 result={'verified_2010_reference':'research/B18_COMPLETE_304_PLAYER_ANIMATIONS_CATALOG_TR.md',
   'full_legacy_2010_player_animation_catalog_count':len(clips),
   'per_rig':dict(counts),
   'extra_original_Underwater_34_present_but_NOT_in_this_304_document':True,
   'original_staged_363_motion_and_304_internal_rig_structures_unverified_in_THIS_host_step':True,
   'source_all_972_original_IPA_redecoded_in_this_action':False,
   'real_touchHLE_original_game_reference_playback_performed_in_this_step':False,
   'full_original_native_combat_event_hit_timing_known':False,
   'original_weapon_damage_value_per_instance_verified':False,
   'approved_to_package_new_test_VPK':False,
   'no_game_build_requested':True,
   'G81_documented_2010_player_moves':clips}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G81_304_PLAYER_MOVES_SOURCE_REGISTRY_NO_IPA_NO_VPK.json').write_text(
    json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 with (out/'G81_304_PLAYER_MOVES_SOURCE_REGISTRY.csv').open('w',newline='') as f:
  w=csv.writer(f)
  w.writerow(['original_2010_name','source_duration_ms','bones','rig',
      'B24_source_alias_candidate','classifications'])
  for q in clips:w.writerow([q['2010_source_animation_name'],q['duration_ms'],
     q['source_track_count'],q['body_rig_from_filename'],
     q['canonical_G8_stream_alias_candidate'],';'.join(q['2010_move_categories_name_based_only'])])
 print('PASS G81 AUTHENTIC LEGACY 304 documented original 2010 IronMan/WarMachine clips',dict(counts))
 print('PASS 3 original combo 266,300,500 ms; no original hit-window invented; NO VPK')
if __name__=='__main__':
 parser=argparse.ArgumentParser()
 parser.add_argument('--doc',type=Path,required=True)
 parser.add_argument('--out',type=Path,required=True)
 q=parser.parse_args();run(q.doc,q.out)
