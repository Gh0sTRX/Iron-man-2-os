#!/usr/bin/env python3
"""G80 decode authentic 2010 CLARA Attack(class 108) schema property tags,
then correlate against real 26 source Attack_type and enemy attack value
record bytes. Preserve original user data privacy: report selected numeric
candidate values and field IDs, no complete source BCLARA/IPA package.
"""
import argparse,collections,json,re,struct,zipfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode,get_exact
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
TEXT=re.compile(rb'[\x20-\x7e]{2,80}')
KEYWORDS=re.compile('(?i)damage|speed|attacktype|projectile|radius|accuracy|gravity|trigger|travel|splash|missile|cooldown|weapon|health')
def audit(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  pack=z.read('Payload/IronMan2.app/clev')
 raw=get_exact(pack,decode(pack,'.bclara'),'level1.bclara')
 original=summarize(raw)
 sc=sorted(original['source_2010_class_schema'],key=lambda x:x['original_class_name_file_offset'])
 tokens=[]
 for pos,q in enumerate(sc):
  # G81 also inspect nested projectile and damage class field definitions.
  end=sc[pos+1]['original_class_name_file_offset']-6 if pos+1<len(sc) else 38719
  start=q['original_class_name_file_offset']+len(q['original_class_name'])
  fields=[]
  for m in TEXT.finditer(raw,start,end):
   a=m.start();b=m.group()
   if a<4 or struct.unpack_from('<H',raw,a-2)[0]!=len(b):continue
   try:name=b.decode('ascii')
   except UnicodeDecodeError:continue
   fields.append({'source_property':name,
      'source_offset':a,
      'prefix_previous_2_bytes_hex':raw[a-4:a-2].hex(),
      'property_ID_candidate_u16_at_name_minus_4':
       struct.unpack_from('<H',raw,a-4)[0],
      'native_tag_candidate_at_name_minus_7':struct.unpack_from('<H',raw,a-7)[0] if a>=8 and raw[a-8]==1 else None,
      'native_value_type_or_size_NOT_proven':True})
  if q['original_class_id'] not in (104,107,108) and not any(
      KEYWORDS.search(v['source_property']) for v in fields):
   continue
  tokens.append({'class_id':q['original_class_id'],
    'source_class_name':q['original_class_name'],
    'schema_byte_region_start':start,
    'schema_byte_region_end':end,
    'native_schema_field_names':fields})
 name_offsets=sorted([r['original_name_offset'] for r in original['source_2010_typed_class_instances']])
 records=[]
 for obj in original['source_2010_typed_class_instances']:
  if obj['original_class_name'] not in ('Attack','Weapon'):continue
  data_start=obj['original_name_offset']+len(obj['original_name'])+9
  after=[n for n in name_offsets if n>obj['original_name_offset']]
  max_end=(after[0]-7) if after else len(raw)
  # Data layout varies. The first 480 bytes are interpreted as a *probe*
  # and ONLY validated tag+length pairs will be considered actual fields.
  chunk=raw[data_start:min(len(raw),data_start+480)]
  possibles=[]
  for p in range(0,len(chunk)-6):
   tag,size=struct.unpack_from('<HH',chunk,p)
   if size not in (1,2,4,8,12,16):continue
   # Source schema class tag uniqueness will be established downstream.
   for schema in tokens:
    # Source nested property class may differ from owning Attack class.
    same=[v for v in schema['native_schema_field_names'] if
         v['native_tag_candidate_at_name_minus_7']==tag]
    if not same:continue
    data=chunk[p+4:p+4+size]
    if len(data)!=size:continue
    if size==4:
     value_i32=struct.unpack('<i',data)[0]
     value_f32=struct.unpack('<f',data)[0]
     value_float=round(value_f32,5) if abs(value_f32)<100000 else None
    else:value_i32=None;value_float=None
    possibles.append({'offset_into_instance_bytes':p,'original_native_property_tag':tag,
      'matching_original_schema_properties':[v['source_property'] for v in same],
       'defining_native_schema_class_id':schema['class_id'],
       'defining_native_schema_class_name':schema['source_class_name'],
      'native_field_payload_size_bytes':size,
      'raw_original_value_i32_candidate':value_i32,
      'raw_original_value_f32_candidate':value_float,
      'has_exact_verified_type_and_unique_structural_parent':False})
  # Reduce to combat relevant candidates (not print all unrelated potential)
  possibles=[x for x in possibles if any(KEYWORDS.search(k) for k in x['matching_original_schema_properties'])]
  records.append({'name':obj['original_name'],
   'class':obj['original_class_name'],
   'original_property_region_source_offset':data_start,
   'next_native_instance_name_offset':max_end,
   'candidate_properties_with_tag_and_payload_length':possibles[:100],
   'candidate_values_UNVERIFIED_until_tag_parent_and_schema_serialization_proven':True})
 result={'source_game':'2010 owner iOS original C1L1.bclara',
    'authentic_class108_Attack_and_107_Weapon_schema':tokens,
    '26_attack_and_13_weapon_original_instance_tag_candidates':records,
    'original_silaha_gore_Damage_sayilari_kesinlesti':False,
    'no_VPK':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G80_REAL_ORIGINAL_C1L1_WEAPON_DAMAGE_CLASS_PROPERTY_TAG_CROSSWALK.json').write_text(
    json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('G80 source genuine weapon class property tags:')
 for s in tokens:
  print(' REAL_SCHEMA',s['class_id'],s['source_class_name'],'fields',len(s['native_schema_field_names']))
  print(' DAMAGE-related native schema',[(x['source_property'],
    x['native_tag_candidate_at_name_minus_7']) for x in s['native_schema_field_names']
      if KEYWORDS.search(x['source_property'])][:48])
 for r in records:
  if r['class']!='Attack':continue
  a=[(p['matching_original_schema_properties'],p['raw_original_value_i32_candidate'])
    for p in r['candidate_properties_with_tag_and_payload_length']]
  print(' G80 authentic Attack',r['name'],'tagged value candidates',a[:20])
 print('G80 stage field tag crosswalk complete; no damage numbers promoted without a verified field parent')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();audit(a.ipa,a.out)
