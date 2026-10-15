#!/usr/bin/env python3
"""Gameloft Iron Man 2 2010 BRES original C1L1 material table record structure.

The value 778 at 0x10 of C1L1_ground_001 is the RELOCATION COUNT,\nnot a version number. Historic version is not assumed equal to
public 010 BDAE v779 template. Prove independent MATERIAL table (64-byte
entries), follow actual material property pointers and locate source
textured diffuse slot, without assigning guessed C1L1 texture samplers.

v779 010Editor info: material name1/name2/material_file/shader_name,
properties_count, properties_offset, material property name1/name2,
type,count,offset,value.
"""
from __future__ import annotations
import argparse,collections,json,struct,zipfile
from pathlib import Path
from b24_map_first_2010_material_property_dictionary_recovery import BDAEZIP,SOURCES,string,u

def rd(b,p,n=16):
 if p<0 or p+4*n>len(b):return []
 return [u(b,p+4*i) for i in range(n)]
def parse(blob,srcname):
 # Native 2010 MAT table: exactly 64-byte aligned sequences of source
 # material pointers, two identical string values and material .fx shader.
 material_candidates=[]
 for p in range(4,len(blob)-64,4):
  a=string(blob,u(blob,p))
  c=string(blob,u(blob,p+4))
  fx=string(blob,u(blob,p+12))
  if not(a and c and fx and a==c and fx.startswith('#') and
       fx.lower().find(a.lower())>=0):continue
  words=rd(blob,p,16)
  material_candidates.append({'offset':p,'name':a,'shader':fx,
     'record_16_u32':words,
     'candidate_props_count_at_16':words[4],
     'candidate_props_pointer_20':words[5],
     'candidate_props_point_abs':words[5] if words[5]<len(blob) else None,
     'candidate_props_point_rel':p+20+words[5] if p+20+words[5]<len(blob) else None,
     'candidate_shader_property_names':[]})
 if not material_candidates:raise ValueError('original material table not found '+srcname)
 # Group entries into true authored consecutive tables (64 bytes expected)
 offsets={entry['offset'] for entry in material_candidates}
 longest=[]
 for t in material_candidates:
  if t['offset']-64 in offsets:continue
  run=[t['offset']]
  while run[-1]+64 in offsets:run.append(run[-1]+64)
  if len(run)>len(longest):longest=run
 if len(longest)<1:raise ValueError('no authentic material records '+srcname)
 active=[t for t in material_candidates if t['offset'] in longest]
 for t in active:
  for tag,base in (('absolute',t['candidate_props_point_abs']),
                   ('relative',t['candidate_props_point_rel'])):
   if base is None:continue
   prop_words=rd(blob,base,18)
   names=[]
   for q in range(0,len(prop_words),1):
    name=string(blob,prop_words[q])
    if name and len(name)<80:
     names.append({'relative_word':q,'name':name})
   t['candidate_shader_property_names'].append({
     'pointer_interpretation':tag,'pointer':base,
     'words':prop_words[:14],'source_strings':names[:12]})
 for t in active[:6]:
  print('G11_AUTHORED_MATERIAL_SOURCE',srcname,
    'offset',t['offset'],'name',t['name'],
    'record_16_u32',t['record_16_u32'],
    'property_records',t['candidate_shader_property_names'],flush=True)
 summary={'bres_name':srcname,'native_2010_relocation_count_u32_16':u(blob,16),
     '64byte_table_run_start':longest[0],'64byte_material_definitions':len(active),
     'source_material_definitions':active}
 print('G11_AUTHORED_MATERIAL_HEADER',srcname,
    '2010_pointer_count',u(blob,16),'true64_definitions',len(active),
    'range',longest[0],longest[-1]+64,flush=True)
 return summary

def main(out):
 rows=[]
 with zipfile.ZipFile(BDAEZIP) as z:
  for name in SOURCES:
   b=z.read('original_models/'+name+'.bdae')
   rows.append(parse(b,name))
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps({'original_real_BRES_material_decl_tables':rows,
    'material_to_exact_PVR_samplers_verified':False,
    'no_speculative_diffuse_assignments':True},indent=2)+'\n')
 print('PASS source exact 2010 BRES 64-byte material declarations/props pointers for 10 level1 chunks, NO VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();main(a.out)
