#!/usr/bin/env python3
"""G100 source-only original 2010 BCLARA Attack EntityData serialization
investigation. Native ARM G98 proved AttackEntity::LoadFromFile copies
integer 'Damage' into AttackEntity+0x60, not where the 26 serialized
instance values live. Inspect exact class108 schema and bounded named
Attack bytes, distinguish typed data from raw hex UNVERIFIED guesses.
"""
import argparse,json,struct,zipfile,sys,re,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode,get_exact
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
def main(ipa,out):
 if ipa.stat().st_size!=248613763:raise ValueError('Owner original iOS 2010 IPA required')
 with zipfile.ZipFile(ipa) as z:packed=z.read('Payload/IronMan2.app/clev')
 raw=get_exact(packed,decode(packed,'.bclara'),'level1.bclara')
 data=summarize(raw)
 objs=data['source_2010_typed_class_instances']
 attacks=sorted((x for x in objs if x['original_class_name']=='Attack'),
   key=lambda x:x['original_name_offset'])
 if len(attacks)!=26:raise ValueError('Original 2010 C1L1 Attack entity count drift')
 schema=[x for x in data['source_2010_class_schema'] if x['original_class_id']==108]
 if len(schema)!=1:raise ValueError('2010 Attack class108 definition missing')
 m=schema[0];schema_offset=m['original_class_name_file_offset']
 found=[]
 for key in (b'Damage',b'AttackType',b'ProjectileType',b'ExplosionRadius',
             b'TailEmmiterId',b'SplashDamage',b'Trail'):
  for mat in re.finditer(re.escape(key),raw):
   pos=mat.start()
   if pos>130000:continue
   found.append({'source_original_class_schema_property_name':key.decode('ascii'),
    'source_exact_offset':pos,
    'len_prefixed_in_original_bytes':pos>=2 and struct.unpack_from('<H',raw,pos-2)[0]==len(key),
    'source_24bytes_before_and_32after':raw[max(0,pos-24):min(len(raw),pos+len(key)+32)].hex(' '),
    'source_u16_at_minus4':struct.unpack_from('<H',raw,pos-4)[0] if pos>=4 else None,
    'source_u16_at_minus8':struct.unpack_from('<H',raw,pos-8)[0] if pos>=8 else None})
 # The first entity original serialized data could be variable-length,
 # so name-off to name-off is just a byte region, not a parsed object.
 names=sorted(int(o['original_name_offset']) for o in objs)
 regions=[]
 for obj in attacks:
  st=obj['original_name_offset']
  end=next((n for n in names if n>st),len(raw))
  # Other object structures may intervene. DO NOT parse guessed TLV here.
  sample=raw[max(0,st-24):min(len(raw),st+len(obj['original_name'])+320)]
  regions.append({'verified_original_entity_name':obj['original_name'],
    'original_entity_class':obj['original_class_name'],
    'native_instance_original_offset':st,
    'original_next_known_named_object_offset':end,
    'original_window_start':max(0,st-24),
    'real_named_original_bytes_344_hex_for_manual_schema_inference':sample.hex(' '),
    'untyped_i32_close_to_name_are_NOT_verified_2010_damage':True})
 report={'original_game':'user owned 2010 IronMan2 iOS level1.bclara',
  'real_class_id108_Attack_schema_name_offset':schema_offset,
  'real_attack_entity_count':len(attacks),
  'original_source_property_schema_token_context':found,
  'real_original_26_Attack_named_binary_regions':regions,
  'native_AttackEntity_GetParamValue_DAMAGE_INT_at_memory_offset_0x60_ALREADY_G98_verified':True,
  'per_attack_original_damage_values_proven':False,
  'raw_bytes_represent_damage_without_parser':False,
  'no_VPK':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G100_ORIGINAL_2010_LEVEL1_CLASS108_26_ATTACK_RECORD_SCHEMA_WINDOWS.json').write_text(
  json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS G100 authenticated C1L1 original 26 Attack class108 native serialized byte schema windows; original damage int field +0x60 confirmed G98, numerical stats UNKNOWN')
 for x in found:
  if x['source_original_class_schema_property_name'] in ('Damage','AttackType','Trail'):
   print('SOURCE_PROPERTY',x['source_original_class_schema_property_name'],
    'pos',hex(x['source_exact_offset']), 'native preceding field window',
    x['source_24bytes_before_and_32after'])
 for x in regions[:5]:
  print('REAL_ATTACK_ENTITY',x['verified_original_entity_name'],
   'offset',hex(x['native_instance_original_offset']),
   'name-window-hex',x['real_named_original_bytes_344_hex_for_manual_schema_inference'])
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();main(a.ipa,a.out)
