#!/usr/bin/env python3
"""Build a source-accurate Underwater clip manifest from original archived B15 CSV.
Does not export fabricated .im2v or claim Underwater suit geometry is present.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

SCENE_CLIPS = {
    'underwater_bomb_idle.anim',
    'underwater_cannon_attack.anim',
    'underwater_cannon_idle.anim',
    'underwater_ship02_fall.anim',
    'underwater_ship02_idle.anim',
    'underwater_ship02_shake.anim',
    'underwater_ship_fall.anim',
    'underwater_ship_idle.anim',
    'underwater_ship_shake.anim',
}

def classify(name):
    if name in SCENE_CLIPS:
        return 'scene_object'
    if name.startswith('Underwater_'):
        if '_Dead_' in name:
            return 'player_death'
        if '_Movie' in name:
            return 'player_cinematic_candidate'
        if '_Swim_' in name or '_2_Swim' in name or '_2_Float' in name:
            return 'player_swim'
        if '_Aim_' in name:
            return 'player_aim'
        return 'player_float'
    raise ValueError('Unexpected underwater clip '+name)

def build(csv_bytes):
    records=list(csv.DictReader(csv_bytes.decode('utf-8-sig').splitlines()))
    assert len(records)==972, f'Expected 2010 iOS 1.0.0 total 972, got {len(records)}'
    underwater=[r for r in records if r['name'].lower().startswith('underwater_')]
    assert len(underwater)==43, f'Expected 43 underwater prefix records, got {len(underwater)}'
    result=[]
    for row in underwater:
        name=row['name'];category=classify(name)
        ms=int(row['duration_ms']);labels=int(row['joint_labels'])
        if category!='scene_object':
            assert labels==38, f'Unexpected rig label count: {name}: {labels}'
        result.append({
            'source':name,'duration_ms':ms,'joint_labels':labels,
            'category':category,'requires_original_rig':category!='scene_object',
            'safe_bake':category!='scene_object' and ms>0,
            'source_sha256':row['raw_sha256']
        })
    assert sum(x['category']=='scene_object' for x in result)==9
    assert sum(x['requires_original_rig'] for x in result)==34
    return {
       'source':'Original iOS 1.0.0 anims / B15_ALL_972_ANIMATIONS.csv',
       'source_csv_sha256':hashlib.sha256(csv_bytes).hexdigest(),
       'original_count':972,'underwater_count':43,
       'player_rig_candidate_count':34,'scene_prop_count':9,
       'underwater_model_verified':False,'vita_bake_verified':False,
       'disclaimer':'Original underwater BDAE bind pose, animation source bytes and skinning test required. No fake IM2V output.',
       'clips':result
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive',type=Path,help='Private research/B15_Original_All_Mechanics_Audit.zip')
    parser.add_argument('--out',type=Path,default=Path('UNDERWATER_CLIPS_MANIFEST.json'))
    args=parser.parse_args()
    with ZipFile(args.archive) as z:
        source=z.read('B15_ALL_972_ANIMATIONS.csv')
    manifest=build(source)
    args.out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print('UNDERWATER: 34 player-rig candidates and 9 scene object clips independently checked.')
    print('Baking BLOCKED until original .anim bytes and matching underwater .bdae rig are recovered.')

if __name__=='__main__':
    main()
