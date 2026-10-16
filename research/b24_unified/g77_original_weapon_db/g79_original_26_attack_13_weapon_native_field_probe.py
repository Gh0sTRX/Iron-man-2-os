#!/usr/bin/env python3
"""G79 inspect genuine 2010 Stark Expo 26 native Attack and 13 Weapon
instance binary payload field boundaries. Emit selected short HEX windows,
not a redistributed game package. Source observation, not guessed damage.
"""
import argparse,collections,json,struct,zipfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode,get_exact
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
def scan(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  packed=z.read('Payload/IronMan2.app/clev')
 raw=get_exact(packed,decode(packed,'.bclara'),'level1.bclara')
 scene=summarize(raw)
 classes={int(r['original_class_id']):r for r in scene['source_2010_class_schema']}
 targets=[r for r in scene['source_2010_typed_class_instances']
          if r['original_class_name'] in ('Attack','Weapon','WeaponAccessory')]
 assert sum(r['original_class_name']=='Attack' for r in targets)==26
 assert sum(r['original_class_name']=='Weapon' for r in targets)==13
 def ascii_sample(buf):
  return ''.join(chr(c) if 32<=c<127 else '.' for c in buf)
 points=[]
 for obj in targets:
  p=obj['original_name_offset']+len(obj['original_name'])+9
  native=raw[p:p+112]
  words=[struct.unpack_from('<I',native,k)[0] for k in range(0,len(native)//4*4,4)]
  points.append({'original_name':obj['original_name'],
    'original_class_name':obj['original_class_name'],
    'class_ID':obj['original_class_id'],
    'source_entity_ID':obj['original_numeric_name_id'],
    'payload_start_offset_after_native_class_ID':p,
    'next_112_source_bytes_hex':native.hex(),
    'next_112_source_bytes_printable':ascii_sample(native),
    'first_28_possible_u32_word_values_as_untyped_raw':words,
    'these_words_are_NOT_proven_damage_values':True})
 templates=[]
 for cid in (104,107,108):
  q=classes[cid]
  loc=q['original_class_name_file_offset']+len(q['original_class_name'])
  window=raw[loc:loc+320]
  templates.append({'class_ID':cid,'class_name':q['original_class_name'],
    'native_class_name_end_source_offset':loc,
    'next_320_source_bytes_hex':window.hex(),
    'next_320_source_bytes_printable':ascii_sample(window)})
 report={'source':'unmodified real 2010 level1.bclara, native typed Attack/Weapon',
   'scene_attack_instance_count':26,'scene_weapon_instance_count':13,
   'actual_binary_instance_payloads':points,
   'original_template_attack_weapon_class_data':templates,
   'unverified_2010_numeric_weapon_damage':True,
   'no_VPK':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G79_C1L1_26_ATTACK_13_WEAPON_ORIGINAL_INSTANCE_BINARY_FIELD_PROBE.json').write_text(
   json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS G79 owner genuine 2010 26 Attack /13 Weapon /1 Accessory source typed instance binary field windows decoded')
 for e in points[:26]:
  print(' G79 Attack',e['original_name'],'classid',e['class_ID'],
    'payload offset',e['payload_start_offset_after_native_class_ID'],
    'first 16 word candidates',e['first_28_possible_u32_word_values_as_untyped_raw'][:16])
 print('NO per-weapon stats asserted until native class attribute serializer parsed')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path);a=p.parse_args();scan(a.ipa,a.out)
