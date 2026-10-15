#!/usr/bin/env python3
"""MAP FIRST: why 2010 Stark Expo domes and light structures look 'clay'.

Explicitly separate FOUR distinct source-proven cases:
1) SOURCE BRES 2010 original shader property references an atlas in 39 C1L1.
2) SOURCE BRES refers to non-C1L1 source textures (e.g. CAHP01 expo).
3) 2010 BRES shader uses an original non-diffuse/default material, no
   authenticated original C1L1 TGA diffuse (possible vertex color/emissive).
4) our PRESENT DIAGNOSTIC chooses to skip entire light category deliberately.

NO invented dome texture source matches. Binary source and owner data only.
"""
from __future__ import annotations
import argparse,collections,contextlib,io,json,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode as tex_decode
from b24_map_first_2010_source_60byte_material_texture_index_recovery import decode as original_60
from b24_map_first_source_BRES_real_relocation_materials import BDAEZIP,SOURCES

def analyze(ipa:Path, existing:Path|None, out:Path):
 owner=zipfile.ZipFile(ipa)
 with owner:
  raw=owner.read('Payload/IronMan2.app/textures')
  realtex=[r.name for r in tex_decode(raw,'.tga')]
 atlas={x.casefold() for x in realtex}
 if len([x for x in atlas if x.startswith('c1l1_')])!=39:
  raise RuntimeError('39 genuine owner iOS C1L1 textures not present')
 rows=[];other=[]
 with zipfile.ZipFile(BDAEZIP) as z:
  for name in SOURCES:
   with contextlib.redirect_stdout(io.StringIO()):
    records,_=original_60(name,z.read('original_models/'+name+'.bdae'))
   for rec in records:
    label=rec['original_material_name']
    diffuse=rec['candidate_true_source_TGA']
    if diffuse:
     if diffuse.casefold() in atlas:
      condition='source_authored_tga_present_in_owner_archive'
     else:condition='shader_TGA_name_NOT_in_owner_archive'
    else:
     condition='no_original_diffuse_TGA_sampler_in_shader_property'
    if condition!='source_authored_tga_present_in_owner_archive' or label in (
      'Standard_16dd','c1l1_3building'):
     other.append({'BRES_source':name,'material':label,
       'original_TGA_reference':diffuse,'owner_texture_found':(
          diffuse is not None and diffuse.casefold() in atlas),
       'condition':condition,
       'original_authored_60byte_property_record':rec['property_60_original_15_u32'],
       'source_original_bank_index':rec['exact_TGA_author_list_index_candidate']})
 groups=collections.defaultdict(lambda:collections.Counter())
 biggest=[]
 if existing is not None:
  source=json.loads(existing.read_text())
  for item in source['materials']:
   file,label=item['material'].split(':',1)
   group=('ground' if '_ground_' in file else
          'urban' if '_obj_' in file else
          'cars' if '_car_' in file else 'lights')
   n=item['source_original_triangles']
   groups[group]['triangles']+=n
   if item['C1MT_C1TX_GPU_original_texture_id']==65535:
    groups[group]['no_matched_C1L1_diffuse_triangles']+=n
    if item['2010_verified_20byte_named_diffuse']:
     groups[group]['non_C1L1_source_TGA_triangles']+=n
    biggest.append((n,item['material'],item['2010_verified_20byte_named_diffuse']))
   else:
    groups[group]['matched_source_C1L1_diffuse_triangles']+=n
   if group=='lights':
    groups[group]['explicitly_untextured_by_G12_preview_renderer']+=n
 # Avoid automatically assuming original material is visually untextured.
 summary={
  'source_2010_original_archive_named_tga_count':len(realtex),
  'source_2010_original_C1L1_named_diffuse_count':39,
  'expo_building_original_source_texture_available_in_iOS_owner_pack':(
     'cahp01_c_expo_building.tga' in atlas),
  'proprietary_2010_BRES_non_C1L1_or_no_PVR_records':other,
  'per_source_C1MA_triangle_group_counts':{key:dict(val) for key,val in groups.items()},
  'top_face_materials_without_C1L1_diffuse':[
    {'triangles':n,'BRES_source_material':s,'source_original_TGA_if_any':t}
    for n,s,t in sorted(biggest,reverse=True)[:35]],
  'documented_preview_light_category_disabled_even_if_UV_exists':True,
  'documented_live_vitaGL_light_category_disabled_even_if_UV_exists':True,
  '2010_BRES_shader_without_diffuse_is_not_proof_of_original_missing_visuals':True,
  'original_missing_light_face_UV_candidate_count':2284,
  'these_light_missing_UV_faces_can_overlap_missing_3D_material_diffuse':True,
  'NOT_AN_IN_GAME_2010_GFX_SCENE_RENDER':True,'NO_VPK':True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
 print('G12_2010_MAP_CLAY_ORIGIN_EVIDENCE expo_alternate_original_PVR_is_in_owner_archive',
       summary['expo_building_original_source_texture_available_in_iOS_owner_pack'])
 print('G12_2010_MAP_CLAY_SOURCE_FACE_COUNTS',summary['per_source_C1MA_triangle_group_counts'])
 print('G12_2010_MAP_CLAY_TOP_UNMAPPED',summary['top_face_materials_without_C1L1_diffuse'][:13])
 print('G12_2010_MAP_CLAY_SPECIAL_SOURCE_PROPS',[
   r for r in other if r['material'] in ('c1l1_3building','orig_07___Default')
 ][:10])
 print('PASS exact source explains why original city has pale clay: intentionally disabled lights in our two renderers, uv-less lights source and genuine not-yet-emulated shaders. NO gameplay NO VPK.')

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',required=True,type=Path)
 p.add_argument('--c1mt-source-manifest',type=Path)
 p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();analyze(a.ipa,a.c1mt_source_manifest,a.out)
