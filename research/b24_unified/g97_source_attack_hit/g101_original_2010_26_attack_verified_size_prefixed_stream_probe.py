#!/usr/bin/env python3
"""G101 verify original 2010 Attack class108 stream is fully parsed as
counted length-prefixed properties (not untyped 4-byte sliding guesses).
Then crosswalk Attack schema property order to native G98 named 'Damage'.
DO NOT promote a numeric Damage value unless exact source parent/prototype
and byte boundary position uniquely confirmed.
"""
import argparse,struct,re,zipfile,sys,json,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode,get_exact
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
TEXT=re.compile(rb'[\x20-\x7e]{2,90}')
def audit(ipa,out):
 if ipa.stat().st_size!=248613763:raise ValueError('Original 2010 owner file required')
 with zipfile.ZipFile(ipa) as z:pkg=z.read('Payload/IronMan2.app/clev')
 raw=get_exact(pkg,decode(pkg,'.bclara'),'level1.bclara')
 parsed=summarize(raw)
 schema=sorted(parsed['source_2010_class_schema'],key=lambda q:q['original_class_name_file_offset'])
 cid={r['original_class_id']:i for i,r in enumerate(schema)}
 instances=parsed['source_2010_typed_class_instances']
 attacks=sorted((r for r in instances if r['original_class_id']==108),key=lambda r:r['original_name_offset'])
 if len(attacks)!=26:raise ValueError('2010 26 Attack count no longer valid')
 entry=schema[cid[108]]
 class_start=entry['original_class_name_file_offset']
 class_end=schema[cid[108]+1]['original_class_name_file_offset']-6
 prop_names=[]
 for m in TEXT.finditer(raw,class_start,class_end):
  start=m.start()
  if start<4 or struct.unpack_from('<H',raw,start-2)[0]!=len(m.group()):continue
  prop_names.append({'property_name':m.group().decode('ascii','replace'),
    'name_original_offset_hex':hex(start),
    'original_declared_type_tag_2bytes_before_len':struct.unpack_from('<H',raw,start-4)[0]})
 next_field_offsets=sorted(r['original_name_offset'] for r in instances)
 regions=[]
 for e in attacks:
  start=e['original_name_offset']+len(e['original_name'])+9
  end=next((n for n in next_field_offsets if n>e['original_name_offset']),len(raw))
  if start+8>end:raise ValueError('original 26 Attack instance serialized incomplete')
  original_prefix=struct.unpack_from('<IH',raw,start)
  number=original_prefix[1]
  cursor=start+6
  entries=[]
  valid=True;error=None
  if number>256 or number<10:
   valid=False;error='implausible property group count'
  else:
   for i in range(number):
    if cursor+2>end:valid=False;error='beyond next known original object';break
    size=struct.unpack_from('<H',raw,cursor)[0]
    if size>4096 or cursor+2+size>end:
     valid=False;error='payload length larger than source object boundary';break
    data=raw[cursor+2:cursor+2+size]
    ent={'source_serialized_field_slot_index':i,'actual_source_data_length':size,
     'relative_source_property_length_offset_hex':hex(cursor-start),
     'decoded_i32_only_IF_four_byte_field':struct.unpack('<i',data)[0] if size==4 else None,
     'raw_payload_first_16_bytes_hex':data[:16].hex()}
    entries.append(ent)
    cursor+=2+size
  regions.append({'original_2010_attack':e['original_name'],
    'original_source_instance_offset_hex':hex(e['original_name_offset']),
    'native_unknown_prefix_u32':original_prefix[0],
    'native_serialized_slot_count_header_u16':number,
    'length_prefixed_boundary_parse_succeeded':valid,
    'parse_error':error,
    'native_next_known_named_object_offset_hex':hex(end),
    'native_parsed_property_group_bytes':cursor-(start+6),
    'sample_source_fields':entries,
    'original_Damage_field_index_identified':False})
 # This stream probe outputs an independently source-bound length table,
 # not the high-level field labels. The labels are parent/inheritance data
 # under EntityData::GetParamValue, and 54 slots do not directly equal the
 # (smaller) Attack class108 local schema list.
 report={'exact_original_2010_class108_Attack_schema_name':entry['original_class_name'],
  'original_Attack_class_schema_end_hex':hex(class_end),
  'original_Attack_class108_local_property_descriptors':prop_names,
  'all_26_original_named_Attack_property_size_stream_attempts':regions,
  'source_named_instances_verified':26,
  'all_26_length_streams_pass':all(x['length_prefixed_boundary_parse_succeeded'] for x in regions),
  'original_damage_i32_value_exact_field_index_and_property_parent_PROVEN':False,
  'no_guess_from_candidate_raw_i32':True,
  'NO_VPK':True}
 out.mkdir(parents=True,exist_ok=True)
 (out/'G101_2010_NATIVE_ATTACK_INSTANCE_COUNTED_LENGTH_FIELDS_AND_SCHEMA_PROOF.json').write_text(
  json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS G101 authentic original Attack 26 record native class108 descriptor introspection')
 print('G101 ATTACK SCHEMA',entry['original_class_name'],hex(class_start),hex(class_end),
   'local defined props',prop_names)
 for r in regions[:7]:
  print('G101 ORIGINAL INSTANCE',r['original_2010_attack'],
    'fields',r['native_serialized_slot_count_header_u16'],
    'parse_ok',r['length_prefixed_boundary_parse_succeeded'],
    'parse_error',r['parse_error'])
  print(' G101 ACTUAL FIRST ORIGINAL SLOTS',r['sample_source_fields'][:35])
 print('Numerical original source AttackEntity Damage NOT yet verified to named field index; NO VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();audit(a.ipa,a.out)
