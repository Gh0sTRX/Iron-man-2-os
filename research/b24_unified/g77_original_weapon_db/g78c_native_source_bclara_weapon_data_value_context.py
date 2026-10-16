#!/usr/bin/env python3
"""G78C authentic 2010 game clev/level1..10 BCLARA binary inspection.
Locate true projectile/attack Damage keywords separately for each scene.
Tell shared native class schema/property name occurrences from actual
instance property values. No unproven numeric stats, no IPA/VPK exported.
"""
import argparse,collections,json,re,struct,zipfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode
TARGETS=[b'Damage',b'SplashDamage',b'AttackType',b'ProjectileType',
 b'MaxSpeed',b'InitialSpeed',b'SplashRadius',b'UniformSplashDamage']
def run(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  pack=z.read('Payload/IronMan2.app/clev')
 records=decode(pack,'.bclara')
 cases=[]
 for rec in records:
  native=pack[rec.start:rec.end]
  keys=[]
  for key in TARGETS:
   locations=[]
   at=0
   while True:
    at=native.find(key,at)
    if at<0:break
    bef=native[max(0,at-12):at]
    aft=native[at+len(key):at+len(key)+28]
    anchor=(struct.unpack_from('<H',native,at-2)[0]==len(key)) if at>=2 else False
    nearest=struct.unpack_from('<I',native,at-6)[0] if at>=6 else None
    locations.append({'real_source_offset':at,
       'is_native_length_prefixed_name':anchor,
       'prequel_short_hex':bef.hex(),
       'following_28bytes_hex':aft.hex(),
       'immediately_previous_u32_if_length_prefixed':nearest if anchor else None,
       'confirmed_real_weapon_damage_value':False})
    at+=len(key)
   if locations:keys.append({'native_original_2010_key':key.decode(),'occurrences':locations})
  cases.append({'real_level_record':rec.name,'source_bytes':len(native),
      'key_occurrences':keys})
 report={'authentic_original_iOS_2010_clev_BCLARA_record_count':len(records),
         'source_CLARA_2010_property_dictionary_or_values_unproven':True,
         'per_original_scene_BCLARA_keyword_context':cases,
         'no_damage_constant_guessed_from_context_bytes':True,
         'source_only_no_VPK':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G78C_NATIVE_CLEV_BCLARA_WEAPON_FIELD_VALUE_OR_TEMPLATE_CONTEXT.json').write_text(
   json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 for scene in cases:
  print('G78C LEVEL',scene['real_level_record'],'bytes',scene['source_bytes'])
  for key in scene['key_occurrences']:
   print(' NATIVE_KEY',key['native_original_2010_key'],
    'count',len(key['occurrences']),
    'length-prefixed',sum(x['is_native_length_prefixed_name'] for x in key['occurrences']),
    'positions',[x['real_source_offset'] for x in key['occurrences'][:10]])
 print('G78C no assumption that template-name adjacent 4 bytes are real weapon damage')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();run(a.ipa,a.out)
