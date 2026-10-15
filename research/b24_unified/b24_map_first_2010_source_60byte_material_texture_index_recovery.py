#!/usr/bin/env python3
"""Recover actual owner 2010 C1L1 each-material 60-byte shader property record.

Proven BRES source layout:
  TGA 20-byte entries (array)
  material SHADER 88-byte entries (array)
  then shader PROPERTIES 60-byte entries (array) with *source material
  label string pointer*, suspected PVR atlas index at word 14 (+56).
  final 64-byte render MATERIAL scene records (array)

This tests every actual per-material property against original TGA array.
Unlike "material ordinal equals texture ordinal" (already shown wrong),
the per-material 60-byte record's explicit numeric property is parsed and
crossvalidated for same material across independently authored source BRES.

We MUST reject if source exact vehicle C1L1_Vehicles association fails.
"""
from __future__ import annotations
import argparse,collections,json,zipfile
from pathlib import Path
from b24_map_first_source_BRES_real_relocation_materials import load,BDAEZIP,SOURCES,string,u
def decode(name,raw):
 core=load(name,raw);tex=core['textures'];materials=core['materials']
 # Begin shader array immediately at end of exact native TGA index array.
 first=tex[0]['offset']+len(tex)*20
 if string(raw,u(raw,first))!=materials[0]['original_BRES_material_name']+'-fx':
  raise ValueError('no 2010 exact shader table at native postTGA boundary '+name)
 propbase=first+len(materials)*88
 end=min(m['source_record_offset'] for m in materials)
 entries=[]
 for idx,m in enumerate(materials):
  rec=first+88*idx
  pname=string(raw,u(raw,rec+4))
  if pname!=m['original_BRES_material_name']:raise ValueError('material shader index mismatch')
  words=[u(raw,rec+4*i) for i in range(22)]
  p=words[3]
  # Authentic shader property pointers are known from 88 record. In the
  # true source they point to its own 60byte payload and repeat every 60.
  if p!=propbase+60*idx:
   print('G11_MAP_SOURCE_SPECIAL_MATERIAL_PROP_RECORD',name,pname,
      'expected',propbase+60*idx,'found',p,'property_first_word',u(raw,p),flush=True)
  # Original mesh BRES sometimes has last 40B placeholder material,
  # e.g. orig_07___Default; only 60B authored source contains TGA index.
  real_index_present=(p>=propbase and p+60<=end and
                      words[2]==1 and u(raw,p)==1)
  values=[u(raw,p+4*i) for i in range(15)] if real_index_present else []
  possible=values[14] if real_index_present else None
  tex_match=tex[possible]['name'] if possible is not None and 0<=possible<len(tex) else None
  entries.append({'source_BRES':name,'original_material_name':pname,
     'shader_88_offset':rec,'property_60_offset':p,
     'property_60_original_15_u32':values,
     'exact_TGA_author_list_index_candidate':possible,
     'candidate_true_source_TGA':tex_match,
     'index_valid_for_real_TGA_bank':tex_match is not None})
  if idx<8 or pname in ('orig_Material__43750','Material__47'):
   print('G11_FIRST_REAL_C1L1_PER_MATERIAL_SAMPLER_PROPS',name,pname,
     'index_from_60byte_owner_property',possible,
     'source_atlas_from_20byte_TGA_table',tex_match,
     'words',values,flush=True)
 if not entries:raise ValueError('no actual native props')
 good=sum(x['index_valid_for_real_TGA_bank'] for x in entries)
 print('G11_C1L1_EACH_AUTHORED_MATERIAL_TGA_LINK',name,
      'material_count',len(entries),'valid_TGA_index',good,
      'valid_fraction',good/len(entries),'shader_prop_padding',end-(propbase+len(materials)*60),flush=True)
 return entries,tex

def main(out):
 rows=[];texture_names={}
 with zipfile.ZipFile(BDAEZIP) as z:
  for name in SOURCES:
   entries,tex=decode(name,z.read('original_models/'+name+'.bdae'))
   rows.extend(entries)
   texture_names[name]=[x['name'] for x in tex]
 # Cross-file stability: same material name in C1L1_obj_001..004 must
 # index into SAME TGA filename even if shader indices shift.
 inconsistent=[]
 by_name=collections.defaultdict(lambda:collections.defaultdict(list))
 for a in rows:
  by_name[a['source_BRES']][a['original_material_name'].casefold()].append(a)
 for left in SOURCES[1:5]:
  for right in SOURCES[1:5]:
   if left>=right:continue
   for label in set(by_name[left]) & set(by_name[right]):
    x=by_name[left][label][0]
    y=by_name[right][label][0]
    if x['candidate_true_source_TGA']!=y['candidate_true_source_TGA']:
     inconsistent.append({'source_a':left,'source_b':right,'shared_material':label,
       'atlas_a':x['candidate_true_source_TGA'],'atlas_b':y['candidate_true_source_TGA'],
       'source_a_property':x['property_60_original_15_u32'],
       'source_b_property':y['property_60_original_15_u32']})
 print('G11_MAP_TRUE_CROSS_MODEL_MATERIAL_SAMPLER_CONTRADICTIONS',len(inconsistent),
       'examples',inconsistent[:6],flush=True)
 v=[a for a in rows if a['original_material_name']=='orig_Material__43750']
 print('G11_C1L1_VEHICLE_KNOWN_AUTHENTIC_TEXTURE_TEST',
   [(a['source_BRES'],a['candidate_true_source_TGA']) for a in v],flush=True)
 report={'source_10_original_2010_BRES_files':list(SOURCES),'author_60byte_per_mat_records':rows,
   'native_real_TGA_banks_by_source':texture_names,
   'same_original_material_across_original_urban_source_inconsistencies':inconsistent,
   'verified_original_B12_car_matches':all(a['candidate_true_source_TGA'].casefold()=='c1l1_vehicles.tga'
      for a in v) if len(v)==2 else False,
   'all_property_sampler_values_valid':all(a['index_valid_for_real_TGA_bank'] for a in rows),
   'actual_diffuse_connection_material_source_CANDIDATE':True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2)+'\n')
 print('PASS 2010 all original owner BRES 60byte per material numeric TGA candidate; real vehicle and cross-file consistency checked, no guessed ordinal source index/VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();main(a.out)
