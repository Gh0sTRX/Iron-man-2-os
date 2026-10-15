#!/usr/bin/env python3
"""C1MT v1: true 2010 C1L1 BRES per-material shader sampler -> 39 original atlas names.

Proof chain:
  10 SOURCE BRES C1L1_*.bdae (authentic relocated pointers)
  20-byte original TGA resource table filename
  88-byte authored shader/material table with source name
  pointers to 60-byte per-material properties
  property[14] = original shader sampler image-table INDEX (not material ordinal)
  C1MA exact file-qualified 94 material keys (source 370 meshes/22919 faces)
  owner's source 2010 packed 39 C1L1 TGAs available -> C1TX files.

Unresolved/missing original PVRs remain 0xffff UNTEXTURED, never guessed.
Cross-validation of B12 original vehicles and both obj2/obj4 building4.
C1MT binary: <4sIIII> C1MT version, nmat, natlas, namesize,
               nmat*<H> bank index (0xffff = no SOURCE link),
               natlas* {u8 strlen, safe lowercase ASCII .c1tx name}.
This does not change face winding, models or user gameplay.
"""
from __future__ import annotations
import argparse,contextlib,io,json,struct,zipfile,hashlib
from pathlib import Path
from b24_owner_pack_extract import decode as archived
from recover_c1l1_triangle_materials import generate as gen_c1ma
from b24_map_first_2010_source_60byte_material_texture_index_recovery import decode as native_decode
from b24_map_first_source_BRES_real_relocation_materials import BDAEZIP,SOURCES
HEADER=struct.Struct('<4sIIII')

def build(ipa:Path,out:Path,manifest:Path):
 with zipfile.ZipFile(ipa) as z:
  raw=z.read('Payload/IronMan2.app/textures')
  names=sorted((r.name for r in archived(raw,'.tga')
                if r.name.casefold().startswith('c1l1_')),key=str.casefold)
 if len(names)!=39 or len({s.casefold() for s in names})!=39:
  raise ValueError('source 2010 actual 39 C1L1 texture filenames changed')
 bank=[x[:-4].casefold()+'.c1tx' for x in names]
 indices={x.casefold():i for i,x in enumerate(names)}
 if len(set(bank))!=39 or any(len(x)>70 or
     not all(ch in 'abcdefghijklmnopqrstuvwxyz0123456789_.' for ch in x)
     for x in bank):raise ValueError('unsafe original 2010 C1L1 atlas filename')
 with zipfile.ZipFile(BDAEZIP) as z:
  source={}
  duplicate=[]
  for basename in SOURCES:
   # The original source validator prints enormous tables, only bank metrics
   # are shown by this converter (stored metadata still has per-mat provenance).
   with contextlib.redirect_stdout(io.StringIO()):
    props,_=native_decode(basename,z.read('original_models/'+basename+'.bdae'))
   for p in props:
    key=basename+'.bdae:'+p['original_material_name']
    if key in source:duplicate.append(key)
    source[key]=p
 if duplicate:raise ValueError('duplicate same-file original material '+str(duplicate[:3]))
 import tempfile
 with tempfile.TemporaryDirectory(prefix='C1MT_REAL_OWNER_C1MA_') as t:
  c1ma=Path(t)/'real.c1ma';c1manifest=Path(t)/'real_c1ma.json'
  with contextlib.redirect_stdout(io.StringIO()):
   layout=gen_c1ma(c1ma,c1manifest)
  materials=layout['materials']
  if len(materials)!=94 or not layout['all_source_glb_faces_and_material_ranges_verified']:
   raise ValueError('exact 94 real source material ID ordering not proven')
  records=[];outmat=[]
  for row in materials:
   key=row['source_material']
   if key not in source:raise ValueError('C1MA contains source material absent from original 2010 BRES shader bank '+key)
   item=source[key]
   tex=item['candidate_true_source_TGA']
   texid=indices.get(tex.casefold(),65535) if tex else 65535
   status=('matched_original_2010_PVR_C1TX' if texid!=65535 else
           'not_authored_textured_or_atlas_not_in_39_owner_images')
   outmat.append(texid)
   records.append({'C1MA_2010_source_mat_id':row['id'],'material':key,
      'source_original_2010_BRES_shader_88_record':item['shader_88_offset'],
      'source_original_2010_BRES_property_60_record':item['property_60_offset'],
      'source_original_bank_20byte_index':item['exact_TGA_author_list_index_candidate'],
      '2010_verified_20byte_named_diffuse':tex,
      'C1MT_C1TX_GPU_original_texture_id':texid,'source_original_triangles':row['triangles'],
      'mapping_status':status})
 if any(x>65535 for x in outmat):raise ValueError('index overflow')
 vehicles=[a for a in records if a['material'].split(':',1)[0] in ('C1L1_car_01.bdae','C1L1_car_02.bdae')]
 if len(vehicles)!=2 or not all(a['2010_verified_20byte_named_diffuse'] and
          a['2010_verified_20byte_named_diffuse'].casefold()=='c1l1_vehicles.tga'
          for a in vehicles):raise ValueError('B12 original two car atlases not reconfirmed')
 assert all(a['C1MT_C1TX_GPU_original_texture_id']==indices['c1l1_vehicles.tga'] for a in vehicles)
 for basename in ('C1L1_obj_002.bdae','C1L1_obj_004.bdae'):
  key=basename+':Material__47'
  mat=next((x for x in records if x['material']==key),None)
  if (mat is None or mat['2010_verified_20byte_named_diffuse'] is None or
      mat['2010_verified_20byte_named_diffuse'].casefold()!='c1l1_building4.tga'):
   raise ValueError('cross-original building4 material47 sampler regression '+key)
 # Binary string bank remains ONLY 39 original source C1TX; missing links -> 0xffff
 names_bytes=bytearray()
 for filename in bank:
  encoded=filename.encode('ascii')
  names_bytes.append(len(encoded))
  names_bytes+=encoded
 data=bytearray(HEADER.pack(b'C1MT',1,len(outmat),len(bank),len(names_bytes)))
 data+=struct.pack('<%dH'%len(outmat),*outmat)
 data+=names_bytes
 if len(data)!=20+188+len(names_bytes):raise ValueError('bad C1MT native ABI length')
 out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
 summary={'file_format':'C1MT 1 (TRUE original 2010 shader88->property60 texture index)',
  'C1MT_sha256':hashlib.sha256(data).hexdigest(),'true_material_count':len(records),
  'true_2010_atlas_count':len(bank),
  'materials_authentically_textured_from_original_2010':sum(i!=65535 for i in outmat),
  'materials_with_no_confirmed_original_C1L1_image':sum(i==65535 for i in outmat),
  'diffuse_triangulated_faces_with_original_texture':sum(x['source_original_triangles']
       for x in records if x['C1MT_C1TX_GPU_original_texture_id']!=65535),
  'total_original_triangles':sum(x['source_original_triangles'] for x in records),
  'material_indices_are_exact_real_C1MA_ID_not_index_guesses':True,
  'B12_original_verified_vehicles_still_match':True,
  'Material47_independently_verified_Building4_in_obj2_and_obj4':True,
  'unchanged_original_39_C1TX_bank_files':bank,
  'materials':records,'NO_FULL_OWNER_IPA_OR_PVR_UPLOADED':True}
 manifest.parent.mkdir(parents=True,exist_ok=True)
 manifest.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
 print('PASS C1MT authentic 2010 C1L1 original 94 C1MA names and 39 original PVR C1TX names',
   'true_textured_materials',summary['materials_authentically_textured_from_original_2010'],
   'true_source_textured_faces',summary['diffuse_triangulated_faces_with_original_texture'],
   '/22919, remaining untextured fail-closed, B12 cars and 2 building4 proven, NO VPK')
 return summary
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True)
 p.add_argument('--manifest',type=Path,required=True)
 a=p.parse_args();build(a.ipa,a.out,a.manifest)
