#!/usr/bin/env python3
"""G77A inspect ORIGINAL owner IPA's weapon/stat/attack definition provenance.
Read-only 2010 game: locate actual ZIP app resources and named pack entries.
Report source offsets and cautious text context; do not invent stats or
publish raw config/IPA/executable/music data. Never produce a VPK.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re,struct,zipfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode
KEYS=(b'weapon',b'attackentity',b'attack',b'projectile',b'damage',b'shield',
      b'health',b'initweapon',b'armor',b'actor',b'hitpoint',b'hit_points',
      b'strength',b'firepower',b'combopower',b'crit',b'splash')
PACK_SUFFIXES=('models','textures','anims','clev')
def scan(blob:bytes,limit:int=120):
    lowered=blob.lower()
    out=[]
    for key in KEYS:
        where=0;cnt=0;examples=[]
        while True:
            at=lowered.find(key,where)
            if at<0:break
            cnt+=1
            if len(examples)<6 and len(out)<limit:
                window=blob[max(0,at-20):min(len(blob),at+64)]
                examples.append({'source_byte_offset':at,
                'nearby_ascii':''.join(chr(c) if 32<=c<=126 else '.' for c in window)[:84]})
            where=at+len(key)
        if cnt:out.append({'needle':key.decode(),'matches':cnt,'context_sample':examples})
    return out
def run(ipa:Path,out:Path):
    with zipfile.ZipFile(ipa) as z:
        root='Payload/IronMan2.app/'
        allfiles=[f for f in z.infolist()
             if f.filename.startswith(root) and not f.is_dir()
               and '/' not in f.filename[len(root):]]
        samples=[];archives=[]
        for f in sorted(allfiles,key=lambda x:x.filename):
            name=f.filename[len(root):]
            rec={'real_game_app_entry':name,'uncompressed_bytes':f.file_size,
                 'native_zip_compressed_bytes':f.compress_size}
            # Scan only small (<12MiB) unknown files, excluding player private
            # assets, binary artwork and SFX. Original resource pack entries are
            # probed by name rather than dumping arbitrary binary contents.
            if f.file_size<=12*1024*1024 and not name.startswith(('sfx_','music_')):
                content=z.read(f)
                rec['native_first_16_bytes_hex']=content[:16].hex()
                if name not in PACK_SUFFIXES:
                    rec['weapon_stat_config_token_probe']=scan(content)
            samples.append(rec)
        for bank,ext in [('clev','.bclara'),('models','.bdae')]:
            raw=z.read(root+bank)
            entries=decode(raw,ext)
            matched=[]
            for r in entries:
                if not any(x in r.name.casefold() for x in
                  ('weapon','attack','damage','shield','hit','enemy','actor','projectile')):
                    continue
                entry=raw[r.start:r.end]
                matched.append({'real_native_record_name':r.name,
                  'native_record_bytes':len(entry),
                  'matching_property_name_tokens':scan(entry,80)})
            archives.append({'game_native_asset_archive':bank,
               'source_record_count':len(entries),'matching_named_source_records':matched})
        # No entire source app binary is put in results, only names and addresses.
        result={'user_provided_original_2010_IPA_asset_scan':True,
                'source_top_level_files_count':len(allfiles),
                'real_source_app_entries':samples,'named_packed_source_records':archives,
                'damage_values_verifiably_mapped_to_original_WeaponDB':False,
                'no_source_inference_based_solely_on_string_keywords':True,
                'VPK_generated':False}
    out.mkdir(parents=True,exist_ok=True)
    p=out/'G77A_REAL_2010_WEAPON_DB_ASSET_AND_FIELD_ORIGIN_AUDIT.json'
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('PASS G77A real original app files',len(allfiles))
    for row in samples:
        if row.get('weapon_stat_config_token_probe'):
            print('POSSIBLE ORIGINAL WEAPON CONFIG',row['real_game_app_entry'],
                  row['uncompressed_bytes'],[q['needle'] for q in row['weapon_stat_config_token_probe'][:12]])
    for a in archives:
        print('2010 SOURCE',a['game_native_asset_archive'],'records',a['source_record_count'],
              'weapon/hit named',len(a['matching_named_source_records']))
        print('Names',[(x['real_native_record_name'],x['native_record_bytes'])
            for x in a['matching_named_source_records'][:35]])
    print('No original numeric damage stat claimed until typed weapon schema and ARM data flow link verified')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.ipa,a.out)
