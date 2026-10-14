#!/usr/bin/env python3
"""Build *user-owned original* underwater .im2t from exact original IPA.
Never guess mesh topology. Underwater is unique 840-vertex skinned topology;
its original 43 named animations need separate decoded bake (not included).
Input IPA is private, outputs for owner's PS Vita build only.
The source archive may not exist in public/CI without user's permission.
"""
from __future__ import annotations
import argparse,hashlib,io,json,struct,sys,zipfile
from pathlib import Path
import numpy as np
from b24_owner_pack_extract import decode,get_exact

MODEL_NAME="LC_MC_UnderWater.bdae"
ATLAS_NAME="MC_UnderWater.tga"
EXPECTED_VERTS=840
EXPECTED_TRIS=359
def source(ipa:Path):
 with zipfile.ZipFile(ipa) as z:
  path='Payload/IronMan2.app/'
  packed={x:z.read(path+x) for x in ('models','textures','anims')}
 if len(packed['models'])<1000:raise ValueError("IPA models missing")
 resources={x:decode(packed[x],'.bdae' if x=='models' else '.tga' if x=='textures' else '.anim') for x in packed}
 bres=get_exact(packed['models'],resources['models'],MODEL_NAME)
 atlas=get_exact(packed['textures'],resources['textures'],ATLAS_NAME)
 return bres,atlas,resources,packed
def decode_bres(data:bytes,parser_archive:Path):
 with zipfile.ZipFile(parser_archive) as z:
  code=z.read("bdae_scene_parser.py").decode()
 namespace={"__name__":"2010_original_underwater_bres","__file__":"bdae_scene_parser.py"}
 exec(compile(code,"bdae_scene_parser.py","exec"),namespace)
 meshes,stats=namespace['parse'](data)
 if len(meshes)!=2:raise ValueError(f"Underwater original mesh count {len(meshes)} != 2")
 vertices=sum(len(m['positions']) for m in meshes)
 triangles=sum(len(m['faces'])//3 for m in meshes)
 if (vertices,triangles)!=(EXPECTED_VERTS,EXPECTED_TRIS):
  raise ValueError(f"Underwater source topology drift {(vertices,triangles)}")
 packed=bytearray()
 faces=bytearray()
 base=0
 for m in meshes:
  p=np.asarray(m['positions'],dtype='<f4')
  uv=np.asarray(m['uv'],dtype='<f4')
  idx=np.asarray(m['faces'],dtype=np.int64).reshape(-1)
  if p.shape[1:]!=(3,) or uv.shape!=(len(p),2) or not np.isfinite(p).all() or not np.isfinite(uv).all():
   raise ValueError("original source geometry / UV invalid")
  if len(idx)%3 or np.any(idx<0) or np.any(idx>=len(p)):
   raise ValueError("original source triangles invalid")
  # Same IM2T v1 layout verified from ORIGINAL B9 629-vertex model.
  packed.extend(np.concatenate((p,uv),axis=1).astype('<f4',copy=False).tobytes())
  faces.extend((idx+base).astype('<u2').tobytes())
  base+=len(p)
 return bytes(packed),bytes(faces),meshes
def decode_pvr(pvr:bytes):
 if len(pvr)<52:raise ValueError("original PVR truncated")
 hsize,height,width=struct.unpack_from('<III',pvr,0)
 if hsize!=52 or (width,height)!=(512,512) or len(pvr)!=52+131072:
  raise ValueError(f"original Underwater PVR unexpected {hsize,width,height,len(pvr)}")
 import texture2ddecoder
 pixels=texture2ddecoder.decode_pvrtc(pvr[52:],512,512)
 if len(pixels)!=512*512*4:raise ValueError("PVRTC decoder wrong output size")
 return pixels
def build(ipa:Path,parser_archive:Path,out:Path,manifest:Path):
 bres,atlas,rs,packed=source(ipa)
 verts,faces,meshes=decode_bres(bres,parser_archive)
 pixels=decode_pvr(atlas)
 # Pixel byte-order MUST be calibrated against the existing B9 original
 # suit: imagecodecs/texture2ddecoder may output BGRA.
 # Until independently verified don't assign output to a live release.
 if len(verts)!=EXPECTED_VERTS*20 or len(faces)!=EXPECTED_TRIS*6:
  raise ValueError("underwater mesh layout")
 header=struct.pack('<4sIIII',b'IM2T',EXPECTED_VERTS,EXPECTED_TRIS,512,512)
 data=header+verts+faces+pixels
 assert len(data)==20+EXPECTED_VERTS*20+EXPECTED_TRIS*6+512*512*4
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_bytes(data)
 meta={"model":MODEL_NAME,"atlas":ATLAS_NAME,"source_model_sha256":hashlib.sha256(bres).hexdigest(),
   "source_atlas_sha256":hashlib.sha256(atlas).hexdigest(),"im2t_sha256":hashlib.sha256(data).hexdigest(),
   "vertices":EXPECTED_VERTS,"triangles":EXPECTED_TRIS,"bytes":len(data),
   "original_animation_count":len([x for x in rs['anims'] if "underwater" in x.name.lower()]),
   "pvrtc_output_byte_order_calibrated":False,
   "original_skin_weights_or_animations_decoded_here":False,"g7_device_verified":False}
 manifest.write_text(json.dumps(meta,indent=2)+"\n")
 print("PASS ORIGINAL Underwater BRES 840 vertices 359 triangles + PVR atlas, IM2T v1 source format",
    len(data),"bytes; COLOR ORDER UNVERIFIED - DO NOT SHIP AS COMPLETE ARMOR")
 return meta
if __name__=='__main__':
 a=argparse.ArgumentParser()
 a.add_argument('--ipa',type=Path,required=True)
 a.add_argument('--parser',type=Path,default=Path('research/B11_C1L1_Source_Parser.zip'))
 a.add_argument('--out',type=Path,required=True)
 a.add_argument('--manifest',type=Path,required=True)
 c=a.parse_args()
 build(c.ipa,c.parser,c.out,c.manifest)
