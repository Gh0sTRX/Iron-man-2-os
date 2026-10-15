#!/usr/bin/env python3
"""2010 BRES guaranteed relocations, author material and C1L1 texture tables.

Key authentic header discovery: count=u32(16), pointer-location-table=u32(20),
strings_offset=u32(24) == ptrtable+count*4; EACH pointer field is listed
at these relocation offsets. Use this real game-authored type information
to stop incorrectly reading BRES numeric material fields as texture pointers.

Link geometry Submesh MATERIAL NAMES to separately authored materials by name.
Link texture names only upon a native relocation/property relationship.
"""
from __future__ import annotations
import argparse,collections,json,struct,zipfile
from pathlib import Path
from b24_map_first_2010_material_property_dictionary_recovery import BDAEZIP,SOURCES,string,u
def load(name,data):
 num=u(data,16);begin=u(data,20);end=u(data,24)
 if not(0<num<100000 and begin>=32 and begin+4*num==end<len(data)):
  raise ValueError('Source authentic BRES relocated pointer table failed '+name)
 fields=[u(data,begin+4*i) for i in range(num)]
 if any((f is None or f%4 or f>len(data)-4) for f in fields) or len(set(fields))!=num:
  raise ValueError('Source relocation pointer positions bad '+name)
 reloc=set(fields)
 # Source actual first material record identified by two same literal-name
 # strings, a null unused name slot and '#' prefixed author fx material.
 candidates=[]
 for p in range(0,len(data)-64,4):
  if not all(p+o in reloc for o in (0,4,12)):continue
  x=string(data,u(data,p));y=string(data,u(data,p+4));z=string(data,u(data,p+12))
  if x and x==y and z and z.startswith('#') and x in z and u(data,p+8)==0:
   candidates.append((p,x))
 lookup={p:m for p,m in candidates}
 groups=[]
 for p,n in candidates:
  if p-64 in lookup:continue
  nitems=1
  while p+64*nitems in lookup:nitems+=1
  groups.append((p,nitems))
 if not groups:raise ValueError('no material dictionary '+name)
 matpos,nmats=max(groups,key=lambda x:x[1])
 materials=[]
 for i in range(nmats):
  p=matpos+64*i
  fields_here=[{"field_off":o,"target":u(data,p+o),
               "string":string(data,u(data,p+o))}
               for o in range(0,64,4) if p+o in reloc]
  materials.append({"material_index":i,"original_BRES_material_name":lookup[p],
    "source_record_offset":p,"relocated_real_pointer_fields":fields_here,
    "u32_16_words":[u(data,p+4*j) for j in range(16)]})
 # Author original TGA resource mapping table: stride=20 u32, first three
 # entries all relocated pointer fields and filepath terminates ".tga".
 textures=[]
 for p in range(0,len(data)-20,4):
  if any(p+q not in reloc for q in (0,4,8)):continue
  a,b,c=(string(data,u(data,p+q)) for q in (0,4,8))
  if a and b and c and a.lower().endswith('.tga') and ('tga' in b.casefold()) and c.casefold().find('tga')>=0:
   textures.append({"offset":p,"name":a,"friendly":b,"path":c})
 tex={x['offset']:x for x in textures}
 runs=[]
 for p in sorted(tex):
  if p-20 in tex:continue
  nitems=1
  while p+20*nitems in tex:nitems+=1
  runs.append((p,nitems))
 tpos,tlen=max(runs,key=lambda x:x[1]) if runs else (None,0)
 assets=[tex[tpos+20*i] for i in range(tlen)] if tpos is not None else []
 # Verify if ANY non-string pointer genuinely connects source material
 # declarations to texture declaration entries or ANY arbitrary asset pointers.
 native_links=[]
 valid_texture_offsets={q+o for q in [x['offset'] for x in assets] for o in (0,4,8)}
 texture_string_offsets={u(data,k) for k in valid_texture_offsets}
 for m in materials:
  r=m['source_record_offset']
  for off in range(r,r+64,4):
   if off not in reloc:continue
   dest=u(data,off)
   if dest in valid_texture_offsets or dest in texture_string_offsets:
    native_links.append({'material':m['original_BRES_material_name'],
      'reloc_field':off,'target':dest})
 # Include raw relocated pointer neighborhoods around last MAT record to
 # find separate property resources that don't show direct material->texture.
 relation={"source_BRES":name,"bytes":len(data),
   "source_relocation_count":num,"source_relocations_end_equals_strings_start":True,
   "materials":materials,"textures":assets,
   "native_material_to_texture_direct_links":native_links,
   "confirmed_material_to_diffuse_name_by_2010_props":False,
   "diffuse_assignment_must_not_be_inferred_from_order":True}
 print('C1L1_REAL_2010_RELOCATED_SOURCE_TABLE',name,
       'relocation_count',num,'true_material_defs',len(materials),
       'source_tga_resources',len(assets),'direct_mat_tex_relocs',native_links[:9],
       'material_names_first',[(x['material_index'],x['original_BRES_material_name'],
          x['relocated_real_pointer_fields']) for x in materials[:3]],
       'TGA_FIRST',assets[:3],flush=True)
 return relation

def main(out):
 with zipfile.ZipFile(BDAEZIP) as z:
  d=[load(n,z.read('original_models/'+n+'.bdae')) for n in SOURCES]
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps({'real_2010_BRES_files':d,
   'all_native_pointer_table_records_verified':True,
   'material_texture_sampler_assignment_proven':False},indent=2)+'\n')
 print('PASS actual 2010 BRES relocation-based 10 scene model material and TGA source structural validation, NO VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();main(a.out)
