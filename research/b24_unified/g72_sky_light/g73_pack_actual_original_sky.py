#!/usr/bin/env python3
"""G73 author sky geometry + TWO real sky 2010 PVR atlases for isolated G73
VitaGL scene visual candidate (NOT recovered material shader semantics).
BRES mesh and actual UV NEVER changed. 512->256 downsampling is explicitly
marked as Vita diagnostic memory adaptation, not exact native pixels.
Group 0 sky03 and 1..5 sky02 are UV/shape-driven HYPOTHESES, not proof.
"""
from pathlib import Path
import argparse,contextlib,hashlib,io,json,struct,sys,zipfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from b24_owner_pack_extract import decode,get_exact
from b24_g39_original_C1L1_53_Deco_authentic_meshes_local_placement_map import source_parser
from b24_g11_original_2010_city_texture_and_window_ui_contact import pvr_pixels
from PIL import Image
FMT=np.dtype([('p','<f4',(3,)),('uv','<f4',(2,)),('rgba','u1',(4,))])
def build(ipa:Path,out:Path):
 with zipfile.ZipFile(ipa) as z:
  modelarchive=z.read('Payload/IronMan2.app/models')
  pvrarchive=z.read('Payload/IronMan2.app/textures')
  levelarchive=z.read('Payload/IronMan2.app/clev')
 res=get_exact(modelarchive,decode(modelarchive,'.bdae'),'C1L1_sky_001.bdae')
 with contextlib.redirect_stdout(io.StringIO()):
  meshes,_=source_parser()(res)
 assert len(meshes)==6
 names=['C1L1_sky_02.tga','C1L1_sky_03.tga']
 refs=decode(pvrarchive,'.tga')
 rawtextures={}
 tga_sha={}
 for name in names:
  b=get_exact(pvrarchive,refs,name)
  img,details=pvr_pixels(b,name)
  assert img.size==(512,512)
  rawtextures[name]=img
  tga_sha[name]=hashlib.sha256(b).hexdigest()
 out.mkdir(parents=True,exist_ok=True)
 # 256² output to reduce Vita VRAM footprint: TWO*256*256*4 = 524288B.
 for index,name in enumerate(names):
  picture=rawtextures[name].convert('RGBA').resize((256,256),Image.Resampling.LANCZOS)
  (out/f'G73_original_sky_tex_{index:02d}.g66t').write_bytes(
   b'G66T'+struct.pack('<III',1,256,256)+picture.tobytes())
 batches=[];rows=[];total=0
 mapping=[1,0,0,0,0,0] # tentative source UV+geometry plausible, unverified
 for i,m in enumerate(meshes):
  p=np.asarray(m['positions'],dtype=np.float32)
  u=np.asarray(m['uv'],dtype=np.float32)
  inds=np.asarray(m['faces'],dtype=np.int64).reshape(-1)
  assert p.ndim==2 and p.shape[1]==3 and u.shape==(len(p),2)
  assert np.isfinite(p).all() and np.isfinite(u).all()
  assert inds.min()>=0 and inds.max()<len(p)
  verts=np.empty(len(inds),dtype=FMT)
  verts['p']=p[inds];verts['uv']=u[inds];verts['rgba']=255
  rows.append(verts)
  batches.append((total,len(inds),mapping[i],0))
  total+=len(inds)
 assert total==288 and sum(b[1] for b in batches)//3==96
 packed=np.concatenate(rows)
 data=b'G73M'+struct.pack('<4I',1,total,len(batches),2)
 data+=b''.join(struct.pack('<4I',*b) for b in batches)
 data+=packed.tobytes()
 (out/'G73_original_sky_mesh.g73m').write_bytes(data)
 report={
 'stage':'G73 original sky visual candidate', 'actual_source_sky_BRES':'C1L1_sky_001.bdae',
 'source_sky_model_sha256':hashlib.sha256(res).hexdigest(),
 'source_C1L1_sky_001_triangle_count':96,'source_mesh_count':6,
 'source_C1L1_sky_02_03_PVR_original_SHA256':tga_sha,
 'original_sky_model_coordinates_and_authored_UV_unchanged':True,
 'original_sky_native_shader_proven':False,
 'source_material_2717_2718_2719_tga_binding_proven':False,
 'tentative_geometry_based_texture_map_source_mesh_0_to_5':mapping,
 'real_source_pvr_pixels_downsampled_512_to_256_for_Vita_debug':True,
 'new_base_sky_RGBA_bytes':524288,
 'geometry_VBO_bytes':288*24,
 'do_not_claim_final_sky_shader_or_Vita_frame_verified':True
 }
 (out/'G73_SKY_PROVENANCE.json').write_text(json.dumps(report,indent=2)+'\n')
 print('G73 real original sky: source 6 submeshes / 96 authored sky faces; 2 real sky atlases 256 RGBA textures staged',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();build(a.ipa,a.out)
