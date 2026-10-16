#!/usr/bin/env python3
"""G75 Moon/sky original location forensics. Real 2010 C1L1 sky authored
BRES six submeshes and raw mesh material binding metadata, no imagined
native sky shader, no Vita VPK output. """
import argparse,contextlib,io,zipfile,hashlib,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_owner_pack_extract import decode,get_exact
from b24_g39_original_C1L1_53_Deco_authentic_meshes_local_placement_map import source_parser
from b24_map_first_source_BRES_real_relocation_materials import load as relocs
def run(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  models=z.read('Payload/IronMan2.app/models')
 bres=get_exact(models,decode(models,'.bdae'),'C1L1_sky_001.bdae')
 parser=source_parser()
 with contextlib.redirect_stdout(io.StringIO()):
  meshes,other=parser(bres)
 assert len(meshes)==6
 chunks=[]
 for index,m in enumerate(meshes):
  verts=np.asarray(m['positions'],dtype=np.float64)
  uv=np.asarray(m['uv'],dtype=np.float64)
  values={k:str(type(v).__name__) for k,v in m.items()}
  native_fields={}
  for k,v in m.items():
   if any(x in k.lower() for x in ('material','texture','shader','name','mesh_id','group')):
    if isinstance(v,(str,int,float)) or v is None:
     native_fields[k]=v
    elif isinstance(v,(list,tuple)) and len(v)<20:
     native_fields[k]=repr(v)[:300]
  chunks.append({
    'source_mesh':index,'source_face_count':len(m['faces']),
    'source_local_bbox_min':verts.min(axis=0).round(5).tolist(),
    'source_local_bbox_max':verts.max(axis=0).round(5).tolist(),
    'authored_uv_range':{
      'min':uv.min(axis=0).round(5).tolist(),
      'max':uv.max(axis=0).round(5).tolist()},
    'native_decoder_mesh_available_keys':values,
    'native_material_or_shader_name_metadata':native_fields,
    'actual_native_material_to_sky_02_03_link_confirmed':False
  })
 try:
  with contextlib.redirect_stdout(io.StringIO()):
   material=relocs('C1L1_sky_001',bres)
  rebind={'native_authored_materials':material['materials'],
          'native_authored_BRES_texture_tables':material['textures'],
          'native_direct_relocation_links':material['native_material_to_texture_direct_links']}
 except Exception as e:
  rebind={'native_BRES_relocation_decoder_limitation':type(e).__name__+': '+str(e)[:200]}
 report={'source_game':'Iron Man 2 original 2010',
    'sky_source':'C1L1_sky_001.bdae',
    '2010_original_source_BRES_sha256':hashlib.sha256(bres).hexdigest(),
    'native_sky_submesh_material_and_UV_reports':chunks,
    'native_material_relocation_proof':rebind,
    'original_moon_original_2010_screen_position_proven':False,
    'G73_current_mesh_to_atlas_guess':[1,0,0,0,0,0],
    'G73_current_moon_position_original_parity_proven':False,
    'G75_source_only_no_VPK':True}
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 print('PASS G75 actual sky source BRES six submesh UV + native material names evidence captured, no invented moon rotation')
 for m in chunks:
  print('Sky mesh',m['source_mesh'],'material metadata',m['native_material_or_shader_name_metadata'])
 print('Relocated native original material links',len(rebind.get('native_direct_relocation_links',[])))
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();run(a.ipa,a.out)
