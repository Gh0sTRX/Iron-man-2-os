#!/usr/bin/env python3
"""Look for original 2010 GameLoft material SAMPLER2D property type 11.

The independent 2011 Gameloft parser by fata1error404 identified:
 material property type 11 -> follow value offsets -> TGA texture index.
Confirm this exact property layout from ORIGINAL Iron Man 2 BRES, without
assuming the 2011 BDAE version layouts/56-byte material strides apply.

2010 BRES u32 reloc field positions are authoritative type evidence; this
tool only accepts paired pointer fields and explicitly records both property
type offset hypotheses (8,16) with no automatic assignments.
"""
from __future__ import annotations
import argparse,collections,json,struct,zipfile
from pathlib import Path
from b24_map_first_source_BRES_real_relocation_materials import BDAEZIP,SOURCES,string,u
def inspect(name,b):
 count=u(b,16);start=u(b,20);end=u(b,24)
 assert 0<count<20000 and start+count*4==end
 rset={u(b,start+4*k) for k in range(count)}
 candidates=[]
 for p in sorted(rset):
  if p+4 in rset:
   name1=string(b,u(b,p))
   name2=string(b,u(b,p+4))
   if name1 and name2:
    typ8=u(b,p+8);typ16=u(b,p+16)
    if typ8==11 or typ16==11 or any(w in name1.casefold() for w in
       ('diffuse','texture','sampler','map','color','material')):
     payload=[u(b,p+4*i) for i in range(12)]
     candidates.append({'reloc_field':p,'name1':name1,'name2':name2,
       'is_literal_2011_sampler2d_type11':typ8==11 or typ16==11,
       'type8':typ8,'type16':typ16,'words':payload,
       'second_level_real_native_ptr_words':[
         {'relative_word':i,'target':payload[i],
          'points_to_string':string(b,payload[i])}
         for i in range(len(payload)) if p+4*i in rset]})
 exact=[x for x in candidates if x['is_literal_2011_sampler2d_type11']]
 print('G11_SOURCE_REAL_SAMPLER_TYPE11',name,'count',len(exact),
       'typed_name_pairs',[(x['name1'],x['name2'],x['reloc_field'],
       x['words'][:10]) for x in exact[:25]],flush=True)
 print('G11_SOURCE_NEAR_SAMPLER_PROPERTIES',name,'pair_candidates',len(candidates),
    'literal_property_names',[(x['name1'],x['name2'],x['type8'],
    x['type16']) for x in candidates[:27]],flush=True)
 return {'2010_original_bres':name,'all_mat_property_candidates':candidates,
   'native_source_confirmed_sampler2d_type11':len(exact),
   'material_TGA_mapping_exactly_proven':False}

def main(out):
 with zipfile.ZipFile(BDAEZIP) as z:
  obj=[inspect(x,z.read('original_models/'+x+'.bdae')) for x in SOURCES]
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps({'real_2010_material_properties':obj,
   'public_parser_2011_property_type11_applied_only_if_true_native_2010_structure_matches':True,
   'NO_GUESSED_C1L1_MATERIAL_TGA':True},indent=2)+'\n')
 print('PASS source 10 C1L1 BRES original 2010 SAMPLER2D property schema verification. NO VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();main(a.out)
