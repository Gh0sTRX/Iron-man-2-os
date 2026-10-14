#!/usr/bin/env python3
"""2010 ORIGINAL 39 first-level source C1L1 textures -> true Vita C1TX RGBA bank.

One C1TX per source TGA, exact original PVRTC/16bit PVR header and masks.
No surface/material assignment guessed. UV C1UV/C1MA genuine authored source
remains separate; no extra GPU draw command or VPK produced here.
"""
from __future__ import annotations
import argparse, hashlib, json, re, struct, zipfile
from pathlib import Path
from b24_owner_pack_extract import decode
from b24_g11_original_2010_city_texture_and_window_ui_contact import pvr_pixels
from PIL import Image

HEADER=struct.Struct('<4sIIII')
def build(ipa:Path,out:Path):
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError('2010 owner IPA zip CRC failed')
  packed=z.read('Payload/IronMan2.app/textures')
 rows=decode(packed,'.tga')
 city=sorted((r for r in rows if r.name.casefold().startswith('c1l1_')),
             key=lambda r:r.name.casefold())
 if len(city)!=39:raise ValueError('expected genuine 39 original C1L1 source images')
 out.mkdir(parents=True,exist_ok=True)
 generated=[]; seen=set()
 for r in city:
  png,meta=pvr_pixels(packed[r.start:r.end],r.name)
  filename=r.name[:-4].casefold()+'.c1tx'
  if not re.fullmatch(r'[a-z0-9_]+\.c1tx',filename):
   raise ValueError('original PVR filename is unsafe for Vita bank: '+r.name)
  if filename in seen:raise ValueError('case-colliding author texture '+r.name)
  seen.add(filename)
  rgba=png.convert('RGBA').tobytes()
  width,height=png.size
  data=HEADER.pack(b'C1TX',1,width,height,0)+rgba
  if len(data)!=20+4*width*height:
   raise ValueError('bad true author RGBA C1TX length')
  p=out/filename;p.write_bytes(data)
  generated.append({'authentic_original_2010_texture':r.name,
    'source_2010_pvr_sha256':hashlib.sha256(packed[r.start:r.end]).hexdigest(),
    'source_pvr_flags':meta['pvr_flags'],
    'original_pvr_base_pixel_sha256':meta['pixel_payload_sha256'],
    'actual_rgba_source_width':width,'actual_rgba_source_height':height,
    'output_exact_c1tx':filename,'output_bytes':len(data),
    'output_c1tx_sha256':hashlib.sha256(data).hexdigest(),
    'ground/building/sky_material_link_proven':False})
 total=sum(x['output_bytes'] for x in generated)
 summary={'genuine_2010_C1L1_TGA':39,'genuine_VitaGPU_C1TX_output_count':len(generated),
   'raw_pvr_source_from_original_user_ipa':True,
   'atlas_to_original_material_bindings_verified':False,
   'shader_textures_enabled_in_live_G10':False,
   'original_B12_vehicle_C1TX_unchanged_compare_required':True,
   'gpu_bank_uncompressed_total_bytes':total,
   'entries':generated,'full_owner_IPA_exported':False}
 (out/'G11_ORIGINAL_2010_C1L1_39_GPU_TEXTURES_MANIFEST.json').write_text(
    json.dumps(summary,indent=2)+'\n')
 if total<1_000_000 or total>100_000_000:raise ValueError('unexpected native GPU bank size')
 print('PASS 39 original 2010 user-owned C1L1 native GPU-ready RGBA C1TX source files,',
       total,'uncompressed bytes. NO VPK; NO invented material assignments.')
 return summary
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',type=Path,required=True)
 p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();build(a.ipa,a.out)
