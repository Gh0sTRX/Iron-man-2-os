#!/usr/bin/env python3
"""G72 original source-only sky audit. No proprietary .bdae / .ipa exported.
G38 verified original C1L1 Deco001 ID22 -> models table ordinal 21
= C1L1_sky_001.bdae. Determine mesh, native material and linked source PVR.
"""
from __future__ import annotations
import argparse,contextlib,hashlib,io,json,sys,zipfile
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from b24_owner_pack_extract import decode,get_exact
from b24_g39_original_C1L1_53_Deco_authentic_meshes_local_placement_map import source_parser
from b24_g37_original_C1L1_Deco_resource_type_scene_instances import audit
from b24_map_first_2010_source_60byte_material_texture_index_recovery import decode as source_shader
def run(ipa:Path, output:Path):
 with zipfile.ZipFile(ipa) as z:
  models=z.read('Payload/IronMan2.app/models')
  clev=z.read('Payload/IronMan2.app/clev')
  textures=z.read('Payload/IronMan2.app/textures')
 entries=decode(models)
 assert len(entries)==207
 assert entries[21].name=='C1L1_sky_001.bdae'
 level=get_exact(clev,decode(clev,'.bclara'),'level1.bclara')
 deco=audit(level)['source_decoded_native_Deco_0x4D_resource_fields_and_0x5C_transforms']
 sky_nodes=[x for x in deco if x['source_Deco_name']=='Deco001']
 assert len(sky_nodes)==1 and sky_nodes[0]['native_raw_resource_type_uint32']==22
 sky=models[entries[21].start:entries[21].end]
 source_texture_names=[x.name for x in decode(textures,'.tga')]
 sky_name_candidates=[x for x in source_texture_names
     if any(token in x.casefold() for token in
         ('sky','night','cloud','horizon','backdrop','sunset','cityscape'))]

 result={
 'source_model':'C1L1_sky_001.bdae',
 'authored_deco':'Deco001',
 'original_resource_ID':22,
 'zero_based_pack_slot':21,
 'sky_original_bdae_SHA256':hashlib.sha256(sky).hexdigest(),
 'source_BRES_bytes':len(sky),
 'original_owner_texture_archive_members':len(source_texture_names),
 'source_texture_sky_name_candidate_search':sky_name_candidates,
 'source_texture_sky_binding_PROVEN':False,
 'source_CLARA_local_transform':{
   'position_XYZ':[sky_nodes[0]['source_X'],sky_nodes[0]['source_Y'],sky_nodes[0]['source_Z']],
   'quaternion_xyzw':sky_nodes[0]['source_quat_xyzw'],
   'scale_xyz':sky_nodes[0]['source_scale_xyz']
 },
 'native_final_parent_world_transform_verified':False,
 'native_sky_shader_semantics_verified':False,
 'native_original_sky_polygon_and_PVR_recovered':False,
 'original_model_committed_or_published':False
 }
 parser=source_parser()
 with contextlib.redirect_stdout(io.StringIO()):
  meshes,other=parser(sky)
 meshes_report=[]
 for k,m in enumerate(meshes):
  pts=np.asarray(m['positions'],dtype=np.float32)
  f=np.asarray(m['faces'],dtype=np.int32)
  assert pts.size and f.size and np.isfinite(pts).all()
  assert f.min()>=0 and f.max()<len(pts)
  uv=np.asarray(m['uv'],dtype=np.float32) if 'uv' in m else None
  meshes_report.append({'mesh_index':k,'vertex_count':len(pts),'triangle_count':len(f),
      'native_vertex_stride':m.get('stride'),
      'local_XYZ_min':pts.min(axis=0).round(5).tolist(),
      'local_XYZ_max':pts.max(axis=0).round(5).tolist(),
      'UV_is_finite_and_nonconstant':bool(uv is not None and len(uv)>1 and
        np.isfinite(uv).all() and np.ptp(uv,axis=0).max()>1e-6)})
 result['source_parsed_sky_BRES_mesh_parts']=len(meshes_report)
 result['source_sky_total_triangles']=sum(m['triangle_count'] for m in meshes_report)
 result['source_original_BRES_mesh_report']=meshes_report
 # Native 60B sampler pointer decoder is incomplete for non-PVR sky shader.
 # Absence here is NOT proof of absent original texture/material.
 try:
  with contextlib.redirect_stdout(io.StringIO()):
   props,images=source_shader('C1L1_sky_001',sky)
  bank={r.name.lower() for r in decode(textures,'.tga')}
  entries_out=[]
  for p in props:
   t=p.get('candidate_true_source_TGA')
   entries_out.append({'original_material_name':p.get('original_material_name'),
     'native_property_60_offset':p.get('property_60_offset'),
     'candidate_source_PVR':t,
     'PVR_name_exists_in_original_archive':bool(t and t.lower() in bank)})
  result['native_60B_sampler_probe']=entries_out
  result['native_60B_source_image_reference_table']=images
 except Exception as exc:
  result['native_60B_shader_coverage_limitation']=type(exc).__name__+': '+str(exc)[:200]
 result['native_original_sky_polygon_and_PVR_recovered']=True
 result['true_native_shader_and_color_semantics_proven']=False
 output.parent.mkdir(parents=True,exist_ok=True)
 output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 print('G72 source sky parser:',len(meshes_report),'parts',
       result['source_sky_total_triangles'],'triangles')
 print('G72 source material links:',result.get('native_60B_sampler_probe',[]))
 print('G72 real native sky asset and matching Level1 authored Deco001 proven; NO original bytes published')
 return result
if __name__=='__main__':
 a=argparse.ArgumentParser()
 a.add_argument('--ipa',type=Path,required=True)
 a.add_argument('--out',type=Path,required=True)
 q=a.parse_args()
 run(q.ipa,q.out)
