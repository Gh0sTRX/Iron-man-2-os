#!/usr/bin/env python3
"""Forensic authenticated 88-byte BRES shader resource records.

2010 source ground textures table = 14 *20-byte; directly adjacent is
material shader metadata beginning exactly after last TGA record:
C1L1_ground offset 12868: 'Material__2558-fx' + 'Material__2558'.
Next record at 12956: 'Material__45-fx', exactly stride 88.
Separate 64-byte MATERIAL display records begin later (14940).
This 88-byte author shader table and following property data is missing
link to original C1L1 diffuse atlas. Reverse records, not metadata guesses.
"""
from __future__ import annotations
import argparse,collections,json,struct,zipfile
from pathlib import Path
from b24_map_first_source_BRES_real_relocation_materials import load,BDAEZIP,SOURCES,string,u

def parse(name,b):
 original=load(name,b)
 tga=original['textures'];mat=original['materials']
 n=len(b)
 reloc={u(b,u(b,20)+4*i) for i in range(u(b,16))}
 base=tga[0]['offset']+20*len(tga) if tga else 0
 rows=[]
 candidates=[]
 for p in range(max(32,base-60),min(n-88,base+200),4):
  sh=string(b,u(b,p)); label=string(b,u(b,p+4))
  if sh and label and sh==label+'-fx':
   candidates.append(p)
 if not candidates:raise ValueError('2010 88B shader resource list not found '+name)
 a=candidates[0]
 for idx in range(len(mat)):
  p=a+88*idx
  sh=string(b,u(b,p));label=string(b,u(b,p+4))
  if not sh or sh!=label+'-fx':
   raise ValueError('2010 BRES 88byte property table split at '+name+' index '+str(idx))
  words=[u(b,p+i*4) for i in range(22)]
  pointers=[{'word':i,'target':val,'name':string(b,val)} for i,val in enumerate(words)
            if p+4*i in reloc]
  tex_names={x['name'].casefold() for x in tga}
  native_tex_ptr=[x for x in pointers if x['name'] and x['name'].casefold() in tex_names]
  # All raw potential shader texture slot assignments are CANDIDATES:
  numbers=[{'word':i,'num':val} for i,val in enumerate(words)
           if val is not None and val<len(tga)]
  rows.append({'material':label,'shader_record_offset':p,'record_88_all_native_u32':words,
   'relocated_actual_pointer_fields':pointers,
   'direct_TGA_string_native_links':native_tex_ptr,
   'possible_texture_index_numbers_NO_PROOF':numbers})
 props_start=a+88*len(mat)
 # the valid 64byte material declaration table begins later, identify bytes
 mat64=min(x['source_record_offset'] for x in mat)
 between=b[props_start:mat64]
 report={'2010_owner_BRES':name,'source_shader88_offset':a,
  'source_shader88_records_count':len(rows),'source_shader88_end':props_start,
  'source_material_64_first_offset':mat64,
  'source_shader_prop_region_between_len':len(between),
  'shader_prop_between_u32_first_60':[u(b,p) for p in range(props_start,min(mat64,props_start+4*60),4)],
  'material_shader_properties':rows,
  'native_relocated_direct_MATERIAL_TEXTURE_links_confirmed':sum(len(x['direct_TGA_string_native_links']) for x in rows)}
 print('G11_MAP_TRUE_88BYTE_SHADER_DEF',name,'materials',len(mat),
       'shader_88_first',a,'shader_88_last',props_start,
       'material64_first',mat64,'PROPERTY_REGION_BYTES',len(between),
       'genuine_direct_TGA_ptrs',report['native_relocated_direct_MATERIAL_TEXTURE_links_confirmed'],flush=True)
 for row in rows[:5]:
  print('G11_MAP_2010_AUTHOR_88_SAMPLE',name,row['material'],
    'words',row['record_88_all_native_u32'],
    'pointers',row['relocated_actual_pointer_fields'],
    'possible_index_fields',row['possible_texture_index_numbers_NO_PROOF'],flush=True)
 print('G11_MAP_TRUE_PROPERTY_BETWEEN_64_AND_88_SAMPLE',name,
       report['shader_prop_between_u32_first_60'][:40],flush=True)
 return report

def main(out):
 with zipfile.ZipFile(BDAEZIP) as z:
  rows=[parse(n,z.read('original_models/'+n+'.bdae')) for n in SOURCES]
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps({'source_original_2010_BRES_88byte_shader_property_tables':rows,
   'material_shader_texture_sampler_proven':False},indent=2)+'\n')
 print('PASS source authentic 2010 88byte material shader records and interleaved property bytes decoded exact 10 original C1L1 models — NO VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();main(a.out)
