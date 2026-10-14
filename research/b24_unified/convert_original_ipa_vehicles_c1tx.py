#!/usr/bin/env python3
"""Original Gameloft iOS 2010 C1L1_Vehicles.tga PVRTC atlas -> Vita C1TX.
Uses owner-provided ORIGINAL IPA, never replacement/generated imagery.
B12 independently established 22 source car meshes share this atlas; 512x512.
texture2ddecoder returns BGRA, calibrated against original B9 Mark V native
RGBA model texture (MAE=0.0854 over 1,048,576 bytes; CI 38574410509).
No new material assignments inferred for unrelated ground/buildings.
"""
from __future__ import annotations
import argparse,hashlib,json,struct,zipfile
from pathlib import Path
import numpy as np
import texture2ddecoder
from b24_owner_pack_extract import decode,get_exact
TEX='C1L1_Vehicles.tga'
def convert(ipa:Path,out:Path,manifest:Path):
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("original IPA CRC failure")
  packed=z.read("Payload/IronMan2.app/textures")
 pvr=get_exact(packed,decode(packed,'.tga'),TEX)
 # Original 2010 Vehicles PVR contains the 512x512 base image plus its
 # mip chain (unlike MC_SuitCase.tga). Vita uploads only level zero.
 base_bytes=512*512//2
 if len(pvr)<52+base_bytes or len(pvr)>52+base_bytes*2:
  raise ValueError(f"original PVRTC source total file length unexpected {len(pvr)}")
 size,height,width=struct.unpack_from("<III",pvr)
 if (size,width,height)!=(52,512,512):
  raise ValueError(f"original PVR header drift {(size,width,height)}")
 decoded=texture2ddecoder.decode_pvrtc(pvr[52:],width,height)
 if len(decoded)!=width*height*4:raise ValueError("PVRTC decoder returned wrong RGBA size")
 bgra=np.frombuffer(decoded,dtype=np.uint8).reshape(-1,4)
 rgba=np.ascontiguousarray(bgra[:,[2,1,0,3]]).tobytes()
 header=struct.pack("<4sIIII",b"C1TX",1,512,512,0)
 data=header+rgba
 assert len(data)==20+512*512*4
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_bytes(data)
 meta={"format":"C1TX v1","source":TEX,
       "source_ipa_sha256":hashlib.sha256(ipa.read_bytes()).hexdigest(),
       "source_pvr_sha256":hashlib.sha256(pvr).hexdigest(),
       "c1tx_sha256":hashlib.sha256(data).hexdigest(),
       "original_vehicle_meshes_verified":22,
       "pixel_swizzle":"BGRA-to-RGBA; original B9 Mark V reference MAE=0.0854",
       "row_flip":False,
       "not_full_city_material_recovery":True,
       "texture_oriented_on_ps_vita":False,
       "source_only_no_vpk_in_this_script":True,
       "bytes":len(data)}
 manifest.parent.mkdir(parents=True,exist_ok=True)
 manifest.write_text(json.dumps(meta,sort_keys=True,indent=2)+"\n")
 print("PASS B24 authentic original C1L1_Vehicles 512x512 RGBA C1TX",len(data),"bytes (original B12 22 mesh atlas; no other city textures)")
 return meta
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 p.add_argument("--manifest",type=Path,required=True)
 x=p.parse_args();convert(x.ipa,x.out,x.manifest)
