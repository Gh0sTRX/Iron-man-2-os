#!/usr/bin/env python3
"""G72: privately render TWO authenticated 2010 C1L1 sky PVR atlases from user
IPA, compare native sky BRES mesh UVs; do not guess 2717/2718/2719 binds.
Only diagnostic PNG and JSON leave the ephemeral owner IPA runner.
"""
import argparse,contextlib,hashlib,io,json,sys,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from b24_owner_pack_extract import decode,get_exact
from b24_g39_original_C1L1_53_Deco_authentic_meshes_local_placement_map import source_parser
from b24_g11_original_2010_city_texture_and_window_ui_contact import pvr_pixels
NAMED=['C1L1_sky_02.tga','C1L1_sky_03.tga']
def draw(ipa,out,report):
 with zipfile.ZipFile(ipa) as z:
  model_pack=z.read('Payload/IronMan2.app/models')
  texture_pack=z.read('Payload/IronMan2.app/textures')
 model=get_exact(model_pack,decode(model_pack,'.bdae'),'C1L1_sky_001.bdae')
 with contextlib.redirect_stdout(io.StringIO()):
  meshes,_=source_parser()(model)
 bank={x.name.casefold():x for x in decode(texture_pack,'.tga')}
 previews=[];meta=[]
 for name in NAMED:
  x=bank[name.casefold()];pvr=texture_pack[x.start:x.end]
  img,details=pvr_pixels(pvr,name)
  assert min(img.size)>=16 and max(img.size)<=2048
  previews.append(img.convert('RGBA'))
  meta.append({'native_atlas_filename':name,'atlas_width_height':list(img.size),
   'original_private_PVR_SHA256':hashlib.sha256(pvr).hexdigest(),
   'source_2010_pvr_decoded':True,
   'direct_2717_2718_2719_material_binding_PROVEN':False})
 try:f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
 except OSError:f=ImageFont.load_default()
 W=1120;H=660
 preview=Image.new('RGB',(W,H),'#202b3d');d=ImageDraw.Draw(preview)
 d.text((18,14),'2010 C1L1 SKY — TWO REAL OWNER-SOURCE PVR ATLAS REFERENCES',font=f,fill='white')
 # checker for alpha, authored data never modified
 for i,(img,name) in enumerate(zip(previews,NAMED)):
  view=img.copy();view.thumbnail((530,520))
  bx=20+i*550;by=67
  cb=Image.new('RGBA',view.size,'#44475b');bg=ImageDraw.Draw(cb)
  for iy in range(0,view.height,20):
   for ix in range(0,view.width,20):
    if ((ix//20)+(iy//20))%2==0:bg.rectangle((ix,iy,ix+19,iy+19),fill='#8493a9')
  cb.alpha_composite(view)
  preview.paste(cb.convert('RGB'),(bx,by))
  d.text((bx,H-68),name+'  '+str(img.size),font=f,fill='#d4e8ff')
 d.text((18,H-28),'ORIGINAL PIXELS  |  MATERIAL-ID / SKYBOX STAGE STILL UNPROVEN',font=f,fill='#f6d5a0')
 out.parent.mkdir(parents=True,exist_ok=True);preview.save(out)
 meshrows=[]
 for i,m in enumerate(meshes):
  uv=np.asarray(m.get('uv',[]),dtype=np.float32)
  meshrows.append({'mesh':i,'triangles':len(m['faces']),
   'UV_min':uv.min(axis=0).round(4).tolist() if uv.size else None,
   'UV_max':uv.max(axis=0).round(4).tolist() if uv.size else None,
   'UV_coords_nonconstant':bool(uv.size and np.ptp(uv,axis=0).max()>1e-6)})
 report.parent.mkdir(parents=True,exist_ok=True)
 report.write_text(json.dumps({'original_source_model':'C1L1_sky_001.bdae',
     'original_source_atlases':meta,'source_mesh_uvs':meshrows,
     'original_sky_material_and_shader_binding_not_recovered':True,
     'no_gameloft_shaders_reconstructed':True},indent=2)+'\n')
 print('PASS G72: two original owner source C1L1 sky atlas PVR decoded for private visual inspection; material binding not guessed')
if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',type=Path,required=True)
 p.add_argument('--png',type=Path,required=True)
 p.add_argument('--json',type=Path,required=True)
 a=p.parse_args();draw(a.ipa,a.png,a.json)
