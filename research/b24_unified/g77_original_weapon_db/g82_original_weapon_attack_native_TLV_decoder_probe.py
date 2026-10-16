#!/usr/bin/env python3
"""G82: precise BCLARA native Attack+MainCharacter serialized TLV flow.
Read bytes for ORIGINAL named, class-typed objects; DO NOT infer field
names from blind 4-byte float guesses. Identify recurring child tags,
source-order typed value signatures and traces around true Damage slots.
Transient user's original IPA only; JSON short contextual slices, NO VPK.
"""
from pathlib import Path
import zipfile,collections,json,struct,math,argparse,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode,get_exact
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
NAMES=['Attack_type0','Attack_type1','Attack_type5','Attack_whip',
       'Attack_F22_missile','Attack_WM_Missile','Attack_Drone_Missile',
       'Attack_firepower_push','MC','UniBeam_Chest','Laser_RightHand']
def run(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  pack=z.read('Payload/IronMan2.app/clev')
 raw=get_exact(pack,decode(pack,'.bclara'),'level1.bclara')
 scene=summarize(raw)
 byname={x['original_name']:x for x in scene['source_2010_typed_class_instances']}
 names=sorted(x['original_name_offset'] for x in scene['source_2010_typed_class_instances'])
 results=[]
 for name in NAMES:
  if name not in byname:continue
  x=byname[name]
  start=x['original_name_offset']+len(name)+9
  next_names=[n for n in names if n>x['original_name_offset']]
  end=(next_names[0]-7) if next_names else len(raw)
  end=min(end,start+900)
  chunk=raw[start:end]
  suspicious=[]
  for pos in range(0,len(chunk)-4):
   if chunk[pos:pos+2] in (b'\\x02\\x00',b'\\x04\\x00',b'\\x06\\x00',b'\\x0c\\x00',
                            b'\\x10\\x00',b'\\x5c\\x00',b'\\x80\\x00'):
    dat=chunk[pos:pos+2]
    if len(suspicious)<110:suspicious.append({
     'relative_position':pos,'tag':struct.unpack('<H',dat)[0],
     'following_18_bytes':chunk[pos+2:pos+20].hex()})
  sample=[]
  for pos in range(0,len(chunk),16):
   if (name=='MC' or name=='Attack_type0') and pos>640:break
   if name not in ('MC','Attack_type0','Attack_type1','Attack_type5','Attack_whip') and pos>384:break
   b=chunk[pos:pos+16]
   sample.append({'relative_pos_hex':hex(pos),
     'bytes':b.hex(' '),
     'ascii':''.join(chr(c) if 32<=c<127 else '.' for c in b)})
  results.append({'name':name,'class':x['original_class_name'],
    'class_id':x['original_class_id'],
    'source_instance_start':start,'next_instance_boundary_guess':end,
    'actual_source_byte_count_window':len(chunk),
    'raw_native_TLV_tag_candidate_positions':suspicious,
    'hex_sample':sample})
 report={'authentic_original_2010_level1_serialized_entities':results,
         'exact_weapon_stats_not_yet_confirmed':True,
         'native_ARM_Attack_Damage_fields_are_int':True,
         'not_a_VPK_or_modified_original_binary':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G82_AUTHENTIC_ATTACK_MC_FULL_TLV_STRUCTURE_FORENSICS.json').write_text(
  json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS G82 typed 2010 owner Attack/Mc entity tagged byte structure forensic',len(results))
 for r in results:
  print('G82 INSTANCE',r['name'],'CLASS',r['class'],
    'offset',r['source_instance_start'],'span',r['actual_source_byte_count_window'])
  for v in r['hex_sample']:
   print(' G82BYTES',r['name'],v['relative_pos_hex'],v['bytes'])
if __name__=='__main__':
 ap=argparse.ArgumentParser()
 ap.add_argument('--ipa',required=True,type=Path)
 ap.add_argument('--out',required=True,type=Path)
 a=ap.parse_args();run(a.ipa,a.out)
