#!/usr/bin/env python3
"""G78B: find owner 2010 weapon stat definitions, not merely compiled
getter property names. Survey ALL source app containers, including files
excluded by G77A's conservative 12MB scan. Report metadata ONLY:
archive/name/size, property-key occurrence locations, source compression
magic. The payload and individual copyrighted assets are never emitted.
"""
import argparse,collections,hashlib,json,re,struct,zipfile
from pathlib import Path
KEYS=[b'SplashDamage',b'UniformSplashDamage',b'CollisionRadius',
 b'AttackType',b'DetonationEmmiterLife1',b'Damage',b'MaxSpeed',
 b'ProjectileType',b'EntityData',b'WeaponDB']
EXCLUDES=('sfx_','text_','voice_','music_','video_')
def probe(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  app='Payload/IronMan2.app/'
  members=[i for i in z.infolist() if i.filename.startswith(app) and not i.is_dir()]
  names=[]
  keywords=[]
  for info in members:
   path=info.filename[len(app):]
   if '/' in path:continue
   names.append({'name':path,'uncompressed_bytes':info.file_size})
   if path.startswith(EXCLUDES) or path.lower().endswith(
     ('.png','.jpg','.jpeg','.wav','.mp3','.ttf','.t','.swf')):continue
   if info.file_size==0:continue
   if info.file_size>300000000:continue
   data=z.read(info)
   matches=[]
   for key in KEYS:
    hits=[]
    at=-1
    for _ in range(16):
     at=data.find(key,at+1)
     if at<0:break
     hits.append(at)
    if hits:
     matches.append({'native_2010_binary_property_name':key.decode(),
                     'first_16_occurrence_offsets':hits,
                     'at_least_count':len(hits)})
   magic=data[:16]
   if matches or path in ('demodata','clev','models','states','anims',
                          'idiot_savant','igpdata','gll_res.pak'):
    keywords.append({'source_file':path,
      'size_bytes':len(data),'actual_magic_bytes_hex':magic.hex(),
      'source_key_locations':matches,
      'original_payload_output_or_unverified_damage_numbers':False})
  names.sort(key=lambda a:-a['uncompressed_bytes'])
  report={'original_iOS_2010_unmodified_IPA':True,
          'owner_file_count':len(names),
          'largest_original_app_resources':names[:90],
          'all_non_audio_non_localized_root_resource_files':[
            x for x in names if not x['name'].startswith(EXCLUDES)
             and not x['name'].lower().endswith(('.png','.jpg','.jpeg','.wav','.mp3','.ttf','.t','.swf'))][:180],
          'original_property_name_location_hits':keywords,
          'numbers_are_not_confirmed_damage_values':True,
          'source_archive_did_NOT_export_assets':True,
          'new_VPK_generated':False}
  out.mkdir(parents=True,exist_ok=True)
  (out/'G78B_REAL_2010_ALL_CONTAINER_ATTACK_DAMAGE_SOURCE_LOCATOR.json').write_text(
     json.dumps(report,ensure_ascii=False,indent=2)+'\n')
  print('G78B original app total',len(names))
  for row in keywords:
   print('2010 SOURCE CONFIG CANDIDATE',row['source_file'],row['size_bytes'],
    [(q['native_2010_binary_property_name'],q['at_least_count']) for q in row['source_key_locations']])
  print('G78B top original resource names',
       [(x['name'],x['uncompressed_bytes']) for x in names[:40]])
  print('No unverified per-weapon stat numbers published or package generated')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--ipa',required=True,type=Path)
 a.add_argument('--out',required=True,type=Path);q=a.parse_args();probe(q.ipa,q.out)
