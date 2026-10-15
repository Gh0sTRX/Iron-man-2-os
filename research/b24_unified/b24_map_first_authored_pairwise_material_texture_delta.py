#!/usr/bin/env python3
"""Recover original C1L1 material->TGA evidence via SOURCE-SOURCE deltas.

The authentic 2010 urban files C1L1_obj_001..004 share almost identical
material and texture dictionaries with small insertion/removals. Comparing
original native material-string and original TGA-name *set differences*
can reveal independently corroborated candidate bindings (e.g. a MATERIAL
and a TEXTURE added together in one author source chunk).

CRUCIAL: Cooccurrence is evidence, not proof of an actual material sampler.
Never write this output into Vita material table before per-face source
render/2010 original sampler pointer confirms it. This is MAP-ONLY research.
"""
from __future__ import annotations
import argparse,itertools,json,zipfile,collections
from pathlib import Path
from b24_map_first_source_BRES_real_relocation_materials import load,BDAEZIP,SOURCES
def norm(s):return s.strip().casefold()
def run(out):
 with zipfile.ZipFile(BDAEZIP) as z:
  src={name:load(name,z.read('original_models/'+name+'.bdae')) for name in SOURCES}
 groups={}
 for g,names in {
  'ground_urban':SOURCES[:5],
  'urban_sources':SOURCES[1:5],
  'light_sources':SOURCES[-3:],
  'all_original_sources':SOURCES
 }.items():
  comp=[]
  for left,right in itertools.combinations(names,2):
   a,b=src[left],src[right]
   ma={norm(x['original_BRES_material_name']) for x in a['materials']}
   mb={norm(x['original_BRES_material_name']) for x in b['materials']}
   ta={norm(x['name']) for x in a['textures']}
   tb={norm(x['name']) for x in b['textures']}
   remove_mat=sorted(ma-mb);add_mat=sorted(mb-ma)
   remove_tex=sorted(ta-tb);add_tex=sorted(tb-ta)
   comp.append({'a':left,'b':right,
     'material_removed_in_b':remove_mat,'material_added_in_b':add_mat,
     'atlas_removed_in_b':remove_tex,'atlas_added_in_b':add_tex,
     'single_add_pair_CANDIDATE_NOT_PROVEN':{
       'material':add_mat[0],'tex':add_tex[0]} if len(add_mat)==len(add_tex)==1 else None,
     'single_remove_pair_CANDIDATE_NOT_PROVEN':{
       'material':remove_mat[0],'tex':remove_tex[0]} if len(remove_mat)==len(remove_tex)==1 else None,
     'common_mat':len(ma&mb),'common_tex':len(ta&tb)})
  groups[g]=comp
  for x in comp:
   if x['single_add_pair_CANDIDATE_NOT_PROVEN'] or x['single_remove_pair_CANDIDATE_NOT_PROVEN']:
    print('C1L1_REAL_2010_CROSS_SOURCE_SINGLETON_ADD_REMOVE',
     x['a'],x['b'],
     'source_extra_MATERIAL',x['material_added_in_b'],
     'source_extra_TEXTURE',x['atlas_added_in_b'],
     'source_removed_MATERIAL',x['material_removed_in_b'],
     'source_removed_TEXTURE',x['atlas_removed_in_b'],flush=True)
 # Stability metric: two sources same material-name in different original
 # textures sets => material cannot just be assigned "nth texture".
 contradictions=[]
 for left,right in itertools.combinations(SOURCES[1:5],2):
  a,b=src[left],src[right]
  aa={norm(m['original_BRES_material_name']):i for i,m in enumerate(a['materials'])}
  bb={norm(m['original_BRES_material_name']):i for i,m in enumerate(b['materials'])}
  ta=[norm(t['name']) for t in a['textures']]
  tb=[norm(t['name']) for t in b['textures']]
  for name in sorted(aa.keys()&bb.keys()):
   i,j=aa[name],bb[name]
   if i<len(ta) and j<len(tb) and ta[i]!=tb[j]:
    contradictions.append({'same_original_material':name,'first_source':left,
      'other_source':right,'first_same_index_texture':ta[i],
      'other_same_index_texture':tb[j],
      'ordinal_direct_atlas_binding_UNSAFE':True})
 print('C1L1_2010_NTH_MATERIAL_TGA_INDEX_IS_UNSAFE',len(contradictions),
       'examples',contradictions[:8],flush=True)
 data={'source_2010_original_BRES_model_count':10,'comparisons':groups,
       'source_same_material_but_different_NTH_TGA_index_contradictions':contradictions,
       'texture_identity_from_set_difference_IS_UNPROVEN':True,
       'not_a_valid_final_diffuse_material_map':True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(data,indent=2)+'\n')
 print('PASS 2010 source 10 BRES cross-file independent material+atlas dictionary variation analyzed without fabricated identity or VPK')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();run(a.out)
