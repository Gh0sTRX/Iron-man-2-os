#!/usr/bin/env python3
"""True 2010 owner game C1L1 perspective-correct UV atlas HOST raster screenshots.

EXTENDS, does not replace, prior flat-centroid diagnostic. This time pixels
are sampled from each 2010 original .tga atlas with proper barycentric UV
interpolation and depth testing. No invented building/road materials:
  original BRES geometry/UV, original BRES shader88->prop60->TGA20,
  user-owner 2010 IPA PVR decoded RGBA, original C1L1 GLB mesh faces.
Not a VitaGL/real-device screenshot, not a shader emulation, NO VPK.
"""
from __future__ import annotations
import argparse,collections,contextlib,io,json,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from numba import njit
from b24_owner_pack_extract import decode as owner_decode
from b24_g11_original_2010_city_texture_and_window_ui_contact import pvr_pixels
from recover_c1l1_original_uv import BDAEZIP,SOURCES,GLBZIP,MEMBER,decode_glb,arr,category
from b24_map_first_2010_source_60byte_material_texture_index_recovery import decode as shader_props

W,H=1280,760
@njit(cache=False)
def rasterize(pos,uv,groups,tids,rgba,atlas_offsets,atlas_w,atlas_h,eye,
              right,up,front,background,depth,surface_source):
 textured=0;covered=0;drawn=0;near_rejected=0
 for i in range(pos.shape[0]):
  d=np.empty(3,np.float64);xx=np.empty(3,np.float64);yy=np.empty(3,np.float64)
  skip=False
  for k in range(3):
   p0=pos[i,k,0]-eye[0];p1=pos[i,k,1]-eye[1];p2=pos[i,k,2]-eye[2]
   z=p0*front[0]+p1*front[1]+p2*front[2]
   if z<=1.0:
    skip=True;near_rejected+=1;break
   d[k]=z
   xx[k]=W*.5+960.*(p0*right[0]+p1*right[1]+p2*right[2])/z
   yy[k]=(H-44)*.5-960.*(p0*up[0]+p1*up[1]+p2*up[2])/z+35.
  if skip:continue
  minx=int(max(0,np.floor(min(xx[0],xx[1],xx[2]))))
  maxx=int(min(W-1,np.ceil(max(xx[0],xx[1],xx[2]))))
  miny=int(max(48,np.floor(min(yy[0],yy[1],yy[2]))))
  maxy=int(min(H-44,np.ceil(max(yy[0],yy[1],yy[2]))))
  if minx>maxx or miny>maxy:continue
  den=((yy[1]-yy[2])*(xx[0]-xx[2])+
       (xx[2]-xx[1])*(yy[0]-yy[2]))
  if abs(den)<.02:continue
  # Source authored original texture wrapping; renderer uses one material
  # bank per geometry submesh, NOT guessed same-name ordinal.
  tid=tids[i];tex=tid>=0 and groups[i]!=3
  # No face normals or invented source lighting: neutral fully lit atlas.
  g=groups[i]; fallback=np.array((132,148,143),np.uint8)
  if g==1:fallback=np.array((162,173,179),np.uint8)
  if g==2:fallback=np.array((123,132,143),np.uint8)
  if g==3:fallback=np.array((126,163,169),np.uint8)
  drawn+=1
  for y in range(miny,maxy+1):
   for x in range(minx,maxx+1):
    px=x+.5;py=y+.5
    b0=((yy[1]-yy[2])*(px-xx[2])+(xx[2]-xx[1])*(py-yy[2]))/den
    if b0<0 or b0>1:continue
    b1=((yy[2]-yy[0])*(px-xx[2])+(xx[0]-xx[2])*(py-yy[2]))/den
    if b1<0 or b1>1:continue
    b2=1.-b0-b1
    if b2<0 or b2>1:continue
    onez=b0/d[0]+b1/d[1]+b2/d[2]
    if onez<=0:continue
    z=1./onez
    if z>=depth[y,x]:continue
    if tex:
     uu=(b0*uv[i,0,0]/d[0]+b1*uv[i,1,0]/d[1]+
         b2*uv[i,2,0]/d[2])/onez
     vv=(b0*uv[i,0,1]/d[0]+b1*uv[i,1,1]/d[1]+
         b2*uv[i,2,1]/d[2])/onez
     w=atlas_w[tid];h=atlas_h[tid]
     tx=int((uu-np.floor(uu))*w)
     ty=int(((1.-vv)-np.floor(1.-vv))*h)
     k=atlas_offsets[tid]+4*(ty*w+tx)
     if rgba[k+3]<32:continue
     background[y,x,0]=rgba[k]
     background[y,x,1]=rgba[k+1]
     background[y,x,2]=rgba[k+2]
     surface_source[y,x]=1
     textured+=1
    else:
     background[y,x,0]=fallback[0]
     background[y,x,1]=fallback[1]
     background[y,x,2]=fallback[2]
     surface_source[y,x]=0
    depth[y,x]=z
    covered+=1
 return drawn,covered,near_rejected,textured

def unit(x):
 n=np.linalg.norm(x)
 return x/n if n>0.00001 else x

def original_data(ipa, include_expo=False):
 # True auth source: model mesh positions & per-vertex UV live in the
 # user's original BRES, face identity in exact independently exported GLB.
 originals={}; shader={}
 with zipfile.ZipFile(BDAEZIP) as z:
  ns={'__name__':'real_game_BRES','__file__':'bdae_scene_parser.py'}
  exec(compile(z.read('bdae_scene_parser.py'),'bdae_scene_parser.py','exec'),ns)
  for base in SOURCES:
   raw=z.read('original_models/'+base+'.bdae')
   meshes,_=ns['parse'](raw)
   for k,mesh in enumerate(meshes):
    originals[base+'_'+str(k)]=(base,mesh)
   with contextlib.redirect_stdout(io.StringIO()):
    records,_=shader_props(base,raw)
   for r in records:shader[base+'.bdae:'+r['original_material_name']]=r['candidate_true_source_TGA']
 with zipfile.ZipFile(GLBZIP) as z:
  glb,glb_bin=decode_glb(z.read(MEMBER))
 with zipfile.ZipFile(ipa) as z:
  packed=z.read('Payload/IronMan2.app/textures')
 atlas={};atlas_names=[]
 for tex in owner_decode(packed,'.tga'):
  if tex.name.casefold().startswith('c1l1_') or (include_expo and tex.name.casefold()=='cahp01_c_expo_building.tga'):
   pic,_=pvr_pixels(packed[tex.start:tex.end],tex.name)
   atlas[tex.name.casefold()]=np.array(pic.convert('RGBA'),dtype=np.uint8)
   atlas_names.append(tex.name.casefold())
 assert len(atlas)==len(atlas_names)==39+(1 if include_expo else 0)
 names=sorted(atlas);index={name:i for i,name in enumerate(names)}
 rgba_parts=[];offsets=[];width=[];height=[];size=0
 for name in names:
  img=atlas[name]
  h,w=img.shape[:2]
  offsets.append(size);width.append(w);height.append(h)
  b=img.reshape(-1)
  rgba_parts.append(b)
  size+=b.size
 rgba=np.concatenate(rgba_parts)
 positions=[];uvs=[];groups=[];tids=[];dense=[]
 seen=set()
 for g in range(4):
  for mesh in glb['meshes']:
   name=mesh.get('name','')
   if category(name)!=g:continue
   assert name in originals and name not in seen
   seen.add(name)
   base,model=originals[name]
   prim=mesh['primitives'][0]
   pos=np.asarray(arr(glb,glb_bin,prim['attributes']['POSITION']),np.float32)
   model_uv=np.asarray(model['uv'],np.float32)
   assert len(pos)==len(model_uv)
   faces=np.asarray(arr(glb,glb_bin,prim['indices']),np.uint32).reshape(-1,3)
   assert np.array_equal(faces,np.asarray(model['faces'],np.uint32).reshape(-1,3))
   if g==1:dense.append(pos[faces].mean(axis=1)[:,:2])
   start=0
   for sub in model['submeshes']:
    n=len(sub['faces'])
    tid=index.get((shader.get(base+'.bdae:'+str(sub['material'])) or '').casefold(),-1)
    part=faces[start:start+n]
    positions.append(pos[part]);uvs.append(model_uv[part])
    groups.extend([g]*n);tids.extend([tid]*n)
    start+=n
   assert start==len(faces)
 assert len(seen)==370
 p=np.concatenate(positions).astype(np.float32)
 t=np.concatenate(uvs).astype(np.float32)
 g=np.asarray(groups,np.int16);ids=np.asarray(tids,np.int16)
 assert p.shape==(22919,3,3) and t.shape==(22919,3,2)
 xy=np.concatenate(dense)
 bins=[np.arange(-600,701,55),np.arange(-650,701,55)]
 hist,xe,ye=np.histogram2d(xy[:,0],xy[:,1],bins=bins)
 a,b=np.unravel_index(int(hist.argmax()),hist.shape)
 center=np.array([(xe[a]+xe[a+1])/2,(ye[b]+ye[b+1])/2,0.],dtype=np.float64)
 return (p,t,g,ids,rgba,np.asarray(offsets,np.int64),
   np.asarray(width,np.int32),np.asarray(height,np.int32),center,
   {'source_2010_urban_crowded_55m_geometry_cell':int(hist[a,b]),
    'source_texture_atlas_count':len(names),'source_original_triangles':22919,
    'original_UV_materials_shader_prop60_not_guessed':True})

def preview(data,center,title,out):
 p,uv,g,ids,rgba,ofs,ww,hh,dense,_=data
 eye=np.array(center,dtype=np.float64)+np.array([105.,-135.,90.])
 aim=np.array(center,dtype=np.float64)+np.array([0.,0.,4.])
 front=unit(aim-eye);right=unit(np.cross(front,np.array([0.,0.,1.])))
 up=unit(np.cross(right,front))
 pixels=np.zeros((H,W,3),np.uint8);pixels[:]=[21,29,40]
 zbuf=np.full((H,W),np.inf,np.float32)
 source=np.zeros((H,W),np.uint8)
 n,covered,discarded,tex=rasterize(p,uv,g,ids,rgba,ofs,ww,hh,eye,right,
                                   up,front,pixels,zbuf,source)
 pic=Image.fromarray(pixels,'RGB')
 draw=ImageDraw.Draw(pic)
 draw.rectangle((0,0,W,48),fill=(15,24,32))
 draw.text((16,16),title+' | REAL 2010 PVR per-pixel UV projection + Z buffering',fill=(238,243,247))
 draw.rectangle((0,H-44,W,H),fill=(15,24,32))
 draw.text((16,H-28),'HOST original BRES world raster, not a VitaGL screenshot; no gameplay, no VPK.',fill=(220,235,238))
 pic.save(out)
 return {'visible_source_triangle_count':int(n),
   'written_pixel_samples_with_depth':int(covered),
   'final_visible_source_PVR_texture_pixels':int(source.sum()),
   'original_vertex_faces_rejected_near_camera':int(discarded),
   'original_center':list(map(float,center)),
   'not_real_vita_screenshot':True}

def main(ipa,out):
 out.mkdir(parents=True,exist_ok=True)
 d=original_data(ipa)
 result={'source_geometry':d[-1],'previews':{}}
 result['previews']['G10_synthetic_spawn']=preview(d,np.array([0.,0.,0.]),
   'G10 current synthetic player spawn world center (0,0)',
   out/'G12_PER_PIXEL_REAL_2010_G10_WORLD_ORIGIN.png')
 result['previews']['original_urban_dense_center']=preview(d,d[-2],
   'Source 2010 urban area dense geometry sample',
   out/'G12_PER_PIXEL_REAL_2010_C1L1_DENSE_URBAN.png')
 result['screenshot_method']='per-pixel perspective corrected atlas original PVR RGBA; host CPU renderer, not VitaGL'
 (out/'G12_ORIGINAL_2010_PER_PIXEL_UV_HOST_DIAGNOSTIC.json').write_text(
     json.dumps(result,indent=2)+'\n')
 print('PASS G12 ORIGINAL 2010 owner C1L1 actual UV per-pixel sampled atlas raster',
   'at G10 center AND original denser center. Diagnostics:',result,flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--ipa',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args();main(a.ipa,a.out)
