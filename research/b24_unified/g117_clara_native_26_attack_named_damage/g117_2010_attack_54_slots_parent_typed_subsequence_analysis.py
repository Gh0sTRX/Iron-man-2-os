#!/usr/bin/env python3
"""G117 2010 REAL owner CLARA 26 Attack x 54 typed TLV slots vs original
class110 Object 23 locally defined descriptor tags. Unlike G105's failed
CONTIGUOUS window, test ORIGINAL REVERSED/ORDER-PRESERVING SUBSEQUENCES.
This is a strict type/boundary diagnostic, NOT class-parent proof. Never
promote candidate Damage slot/value without original runtime.
NO VPK / no executable / no guessed damage.
"""
import argparse,collections,json
from pathlib import Path
TYPED_LEN={1:1,2:4,4:4,8:4,512:4}
def go(src,out):
 d=json.loads(src.read_text())
 assert d['source_named_instances_verified']==26 and d['all_26_length_streams_pass']
 rows=d['all_26_original_named_Attack_property_size_stream_attempts']
 obj=d['G103_native_Object110_full_source_local_property_list'][1:]
 assert len(rows)==26 and len(obj)==23
 assert all(len(r['sample_source_fields'])==54 for r in rows)
 assert len([p for p in obj if p['source_property']=='Damage'])==1
 lengths=[[e['actual_source_data_length'] for e in r['sample_source_fields']] for r in rows]
 def eligible(prop,j):
  expected=TYPED_LEN.get(prop['original_binary_type_tag'])
  if expected is None:return prop['original_binary_type_tag']==1024
  return all(row[j]==expected for row in lengths)
 formats={}
 for orientation,fields in [('native',obj),('reversed',list(reversed(obj)))]:
  valid=[[j for j in range(54) if eligible(p,j)] for p in fields]
  # DP counts monotonic subsequence alignments; can be enormous: cap
  # huge counts to keep tests bounded and never claim unique mapping
  # if cap reached.
  maxcount=10**12
  forward=[[0]*54 for _ in fields]
  for j in valid[0]:forward[0][j]=1
  for i in range(1,len(fields)):
   accum=0
   options=set(valid[i])
   for j in range(54):
    if j in options:forward[i][j]=min(maxcount,accum)
    accum=min(maxcount,accum+forward[i-1][j])
  backward=[[0]*54 for _ in fields]
  for j in valid[-1]:backward[-1][j]=1
  for i in range(len(fields)-2,-1,-1):
   accum=0;choices=set(valid[i])
   for j in range(53,-1,-1):
    if j in choices:backward[i][j]=min(maxcount,accum)
    accum=min(maxcount,accum+backward[i+1][j])
  total=min(maxcount,sum(forward[-1]))
  di=next(i for i,v in enumerate(fields) if v['source_property']=='Damage')
  possibles=[]
  for j in valid[di]:
   if forward[di][j] and backward[di][j]:
    values=[r['sample_source_fields'][j]['decoded_i32_only_IF_four_byte_field'] for r in rows]
    possibles.append({'unproven_2010_Damage_serialized_slot':j,
      'original_26_runtime_Damage_values_ACTUALLY_PROVEN':False,
      'all_26_original_length_matches_type_tag':True,
      '26_source_raw_integers_only_if_fourbytes':values,
      'number_of_full_tag_sequence_alignments_using_slot_capped':min(
          maxcount,forward[di][j]*backward[di][j])})
  formats[orientation]={'all_23_parent_descriptors_order_satisfiable':total>0,
    'order_preserving_type_only_total_alignments_capped':total,
    'possible_Damage_slot_positions_with_full_23_descriptor_consistency':possibles,
    'original_class108_Attack_is_actual_subclass_of_Object110_proven':False}
 report={'original_owner_2010_class108_Attack_records':26,
  'source_2010_declared_Object110_local_props':23,
  'g105_CONTIGUOUS_type_signature_no_alignments':True,
  'type_lengths_from_actual_26_x_54_owner_bytes_not_guessed':True,
  'source_only_typed_subsequence_hypotheses':formats,
  'native_2010_EntityData_runtime_name_ptr_to_TLV_index_PROVEN':False,
  'authentic_2010_26_per_attack_damage_numeric_values_PROVEN':False,
  'safe_enable_per_attack_damage':False,'VPK_generated':False}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('G117 ORIGINAL 2010 CLARA 26x54 vs Object110 23 typed subsequences:')
 for k,f in formats.items():
  print(k,'total capped',f['order_preserving_type_only_total_alignments_capped'],
        'unproven damage slot options',[(v['unproven_2010_Damage_serialized_slot'],
         v['26_source_raw_integers_only_if_fourbytes'][:5])
         for v in f['possible_Damage_slot_positions_with_full_23_descriptor_consistency']])
 print('G117 no original class110 inherited parent claim, no damage runtime promotion, NO VPK.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--g101',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 go(a.g101,a.out)
