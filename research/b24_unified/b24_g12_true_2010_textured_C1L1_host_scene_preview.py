#!/usr/bin/env python3
"""Original 2010 C1L1 real BRES+PVR 3D host SOURCE preview, not Vita screenshot.

Visual QA only: draw authentic original 22919 source world triangles in their
original B11 positions; source-authored C1MA triangle material names, true
BRES shader60 TGA indices and genuine 2010 iOS PVR RGBA atlas color.
Nearest pixel UV sampled at triangle center then drawn as FLAT triangle
(PIL diagnostic, NOT correct per-pixel VitaGL textured rasterization).
Displays both sparse G10 synthetic spawn (0,0) and source urban-density
center camera for original 2010 authored world footprint.
No generated city meshes and NO invented floor/texture assignment/VPK.
"""
from __future__ import annotations
import argparse,collections,io,json,math,zipfile,contextlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from b24_owner_pack_extract import decode as owner_decode
from b24_g11_original_2010_city_texture_and_window_ui_contact import pvr_pixels
from recover_c1l1_original_uv import BDAEZIP,SOURCES,GLBZIP,MEMBER,decode_glb,arr,category
from b24_map_first_2010_source_60byte_material_texture_index_recovery import decode as native

W,H=1280,760
def vunit(x):
 x=np.asarray(x,dtype=np.float64);v=float(np.linalg.norm(x))
 return x/v if v>0.00001 else x
def load_original(ipa):
 with zipfile.ZipFile(BDAEZIP) as z:
  ns={'__name__':'G12TrueOwnerBRES','__file__':'bdae_scene_parser.py'}
  exec(compile(z.read('bdae_scene_parser.py'),'bdae_scene_parser.py','exec'),ns)
  originals={};shader={}
  for base in SOURCES:
   raw=z.read('original_models/'+base+'.bdae')
   meshs,_=ns['parse'](raw)
   for k,m in enumerate(meshs):originals[base+'_'+str(k)]=(base,m)
   with contextlib.redirect_stdout(io.StringIO()):
    rec,_=native(base,raw)
   for item in rec:
    shader[base+'.bdae:'+item['original_material_name']]=item['candidate_true_source_TGA']
 with zipfile.ZipFile(GLBZIP) as z:
  d,b=decode_glb(z.read(MEMBER))
 with zipfile.ZipFile(ipa) as z:
  raw=z.read('Payload/IronMan2.app/textures')
 atlas={}
 for q in owner_decode(raw,'.tga'):
  if q.name.casefold().startswith('c1l1_'):
   img,_=pvr_pixels(raw[q.start:q.end],q.name)
   atlas[q.name.casefold()]=np.asarray(img.convert('RGB'),dtype=np.uint8)
 assert len(atlas)==39
 polys=[];centroids=[]
 for group in range(4):
  for mesh in d['meshes']:
   mesh_name=mesh.get('name','')
   if category(mesh_name)!=group:continue
   base,src=originals[mesh_name]
   pr=mesh['primitives'][0]
   verts=np.asarray(arr(d,b,pr['attributes']['POSITION']),dtype=np.float32)
   uv=np.asarray(src['uv'],dtype=np.float32)
   assert len(uv)==len(verts)
   indexes=np.asarray(arr(d,b,pr['indices']),dtype=np.uint32).reshape((-1,3))
   truefaces=np.asarray(src['faces'],dtype=np.uint32).reshape((-1,3))
   assert np.array_equal(indexes,truefaces)
   if group==1:centroids.append(verts[indexes].mean(axis=1)[:,:2])
   start=0
   for sub in src['submeshes']:
    count=len(sub['faces'])
    key=base+'.bdae:'+str(sub['material'])
    tga=shader.get(key)
    image=atlas.get(tga.casefold()) if tga else None
    for face in indexes[start:start+count]:
     pos=verts[face];ux=uv[face].mean(axis=0)
     if image is not None and group!=3:
      th,tw=image.shape[:2]
      # BRES texture repeat, original file's PVR RGBA; nearest triangle
      # centroid ONLY, actual VitaGL will interpolate UV per pixel.
      sx=int((float(ux[0])%1.0)*tw)%tw
      sy=int(((1.0-float(ux[1]))%1.0)*th)%th
      rgb=image[sy,sx].astype(np.float32)
      known=1
     else:
      rgb=np.array([(130,151,147),(157,178,187),(122,125,134),(133,172,175)][group],dtype=np.float32)
      known=0
     polys.append((pos,np.asarray(rgb,dtype=np.float32),group,known))
    start+=count
   assert start==len(indexes)
 assert len(polys)==22919
 xy=np.concatenate(centroids,axis=0)
 hist,xe,ye=np.histogram2d(xy[:,0],xy[:,1],bins=[np.arange(-600,701,55),np.arange(-650,701,55)])
 ix,iy=np.unravel_index(int(hist.argmax()),hist.shape)
 center=np.array([(xe[ix]+xe[ix+1])/2,(ye[iy]+ye[iy+1])/2,0.0])
 return polys,center,{'urban_dense_55m_cell_count':int(hist[ix,iy]),
    'original_urban_density_center_world_xy':center[:2].tolist(),
    'authentic_C1L1_model_triangles':len(polys),
    'texture_bank_count':len(atlas),
    'source_submesh_triangle_colors_are_centroid_samples_not_per_pixel_texturing':True}
def draw(polys,center,out,desc):
 eye=np.asarray(center,dtype=np.float64)+np.array([105.,-135.,90.])
 target=np.asarray(center,dtype=np.float64)+np.array([0.,0.,4.])
 front=vunit(target-eye);right=vunit(np.cross(front,[0.,0.,1.]))
 up=vunit(np.cross(right,front))
 focal=960
 coords=[];bounds=0;auth_faces=0
 for pos,rgb,g,known in polys:
  p=np.asarray(pos,dtype=np.float64)-eye
  z=p@front
  if float(z.min())<=1.0:continue
  projected=np.empty((3,2))
  projected[:,0]=W/2+focal*(p@right)/z
  projected[:,1]=(H-44)/2-focal*(p@up)/z+35
  if (projected[:,0].max()<0 or projected[:,0].min()>W or
      projected[:,1].max()<45 or projected[:,1].min()>H):continue
  if float(np.abs(np.cross(projected[1]-projected[0],projected[2]-projected[0])))<.05:continue
  n=np.cross(pos[1]-pos[0],pos[2]-pos[0])
  n=vunit(n)
  shade=.70+.30*abs(float(n@vunit([.35,.25,.9])))
  color=tuple(int(max(0,min(255,c*shade))) for c in rgb)
  coords.append((float(z.mean()),projected,color,g,known))
  auth_faces+=known
 coords.sort(key=lambda q:-q[0])
 screen=Image.new('RGB',(W,H),(21,29,40))
 drawer=ImageDraw.Draw(screen)
 for depth,points,color,grp,known in coords:
  drawer.polygon([(int(x),int(y)) for x,y in points],fill=color)
 drawer.rectangle((0,0,W,48),fill=(16,24,33))
 drawer.text((17,15),desc+' | SOURCE 2010 C1L1 geometry + shader60 original PVR sampled flat-face preview',fill=(240,241,243))
 drawer.rectangle((0,H-43,W,H),fill=(16,24,33))
 drawer.text((17,H-30),'HOST SOURCE diagnostic, not real VitaGL screenshot. Per-triangle 1 UV sample; authored 2010 positions/materials. NO VPK.',fill=(211,220,227))
 out.parent.mkdir(parents=True,exist_ok=True)
 screen.save(out)
 return {'drawn_source_triangles_visible':len(coords),'visible_triangles_source_texture_color':auth_faces,
  'camera_center':list(center),'output_pixels':[W,H]}
def main(ipa,out):
 out.mkdir(parents=True,exist_ok=True)
 polygons,dense,stat=load_original(ipa)
 stats={}
 stats['g10_synthetic_world_origin']=draw(polygons,np.array([0.,0.,0.]),
   out/'G12_OWNER_C1L1_GAME_SOURCE_TEXTURING_AT_G10_SPAWN_0_0.png',
   'G10 current synthetic spawn world origin 0,0')
 stats['source_urban_densest_area']=draw(polygons,dense,
   out/'G12_OWNER_C1L1_CITY_DENSEST_AUTHORED_WORLD_TEXTURE_PREVIEW.png',
   'Actual source 2010 dense urban geometry candidate')
 report={**stat,'previews':stats,'all_original_source_22919_faces':True,
    'all_source_atlas_mat_link_from_true_BRES_60byte_prop':True,
    'original_level1_authored_player_spawn_STILL_NOT_PROVEN':True,
    'VitaGL_frame_NOT_captured':True}
 (out/'G12_ORIGINAL_C1L1_TEXTURED_HOST_WORLD_PREVIEW_DIAGNOSTIC.json').write_text(
   json.dumps(report,indent=2)+'\n')
 print('PASS original iOS 2010 C1L1 exact 22919 source faces 39 real original texture atlases host 3D screenshots: at synthetic G10 origin AND densest true authored urban source geometry, no VPK',report)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();main(a.ipa,a.out)
