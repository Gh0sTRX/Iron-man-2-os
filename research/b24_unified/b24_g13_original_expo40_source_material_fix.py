#!/usr/bin/env python3
"""G13 MAP-ONLY: restore the PROVEN missing original iOS 2010 Expo building.

G12's C1MT atlas filter was incorrectly restricted to C1L1_* filenames.
The genuine C1L1_obj_002.bdae shader property points to
CAHP01_c_expo_building.tga, actually present in owner `textures` pack.
Do not alter any other original shader mapping, geometry, animation or
world transform. Rebuild G12 source-verified C1MT then append exactly one
original asset as 40th bank entry. No guessed UV, no new VPK.

Staging ZIP paths: maps/C1L1_environment.c1mt (94, 40),
maps/c1l1_*.c1tx (G12 23 actually used), and
maps/cahp01_c_expo_building.c1tx (ORIGINAL missing Expo).
"""
from __future__ import annotations
import argparse,contextlib,hashlib,io,json,struct,tempfile,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode
from b24_g11_original_2010_city_texture_and_window_ui_contact import pvr_pixels
from b24_g12_pack_only_source_used_original_C1L1_map_textures import build as g12_package

EXPO='cahp01_c_expo_building.tga'
EXPO_ASSET='cahp01_c_expo_building.c1tx'
HEADER=struct.Struct('<4sIIII')
def parse_bank(data):
 magic,version,count,natlas,namesize=HEADER.unpack_from(data)
 if (magic,version,count,natlas)!=(b'C1MT',1,94,39):
  raise ValueError('G12 exact original 94x39 material-source header changed')
 numbers=list(struct.unpack_from('<94H',data,20))
 start=20+94*2
 names=[]
 off=start
 while off<len(data):
  n=data[off];off+=1
  names.append(data[off:off+n].decode('ascii'));off+=n
 if off!=len(data) or len(names)!=39 or len(data)-start!=namesize:
  raise ValueError('G12 39 original C1MT atlas strings corrupt')
 return numbers,names

def run(ipa:Path,output:Path,report:Path):
 with tempfile.TemporaryDirectory(prefix='owner_G13_EXPO40_') as temp:
  root=Path(temp)
  original_zip=root/'G12_USED_SOURCE_ONLY.zip'
  g12_json=root/'G12_USED_SOURCE_ONLY.json'
  with contextlib.redirect_stdout(io.StringIO()):
   g12=g12_package(ipa,original_zip,g12_json)
  if g12['actual_used_atlases_staged']!=23:
   raise ValueError('G12 original 23 used-source atlas invariant changed')
  with zipfile.ZipFile(original_zip) as z:
   payload={name:z.read(name) for name in z.namelist()}
  old=payload['maps/C1L1_environment.c1mt']
  ids,names=parse_bank(old)
  with zipfile.ZipFile(ipa) as z:
   packed=z.read('Payload/IronMan2.app/textures')
  matches=[r for r in decode(packed,'.tga') if r.name.casefold()==EXPO]
  if len(matches)!=1:
   raise ValueError('EXACT original Expo asset not found in user iOS 2010 source pack')
  original=packed[matches[0].start:matches[0].end]
  png,pvr=pvr_pixels(original,matches[0].name)
  rgba=png.convert('RGBA').tobytes()
  w,h=png.size
  if w<8 or h<8 or len(rgba)!=4*w*h:
   raise ValueError('original Expo PVR source decoded size not plausible')
  raw=HEADER.pack(b'C1TX',1,w,h,0)+rgba
  # G12 original manifest is the independently verified 2010 BRES
  # shader88 -> property60 -> TGA20 relation. Only the originally-proven
  # Expo 206 faces are modified. All others remain exactly G12.
  # G12 manifest isn't bundled in G12 data zip: reproduce deterministically
  # using same original owner source workflow and require explicit source
  # record only, no filename or material guess.
  from b24_map_first_original_2010_C1MT_source_verified_material_bank import build as source_bres
  source_manifest=root/'G12_BRES_MATERIAL_NAMES.json'
  with contextlib.redirect_stdout(io.StringIO()):
   source=source_bres(ipa,root/'recheck_g12.c1mt',source_manifest)
  if (root/'recheck_g12.c1mt').read_bytes()!=old:
   raise ValueError('G12 source original bank material order was not reproducible')
  source_expo=[row for row in source['materials'] if
      (row['2010_verified_20byte_named_diffuse'] or '').casefold()==EXPO]
  if len(source_expo)!=1 or source_expo[0]['source_original_triangles']!=206 or (
       source_expo[0]['material']!='C1L1_obj_002.bdae:orig_07___Default'):
   raise ValueError('G13 Expo source material identity not proven EXACTLY')
  idx=source_expo[0]['C1MA_2010_source_mat_id']
  if ids[idx]!=65535 or EXPO_ASSET in names:
   raise ValueError('G12 already mapped owner Expo source unexpectedly')
  ids[idx]=39
  names.append(EXPO_ASSET)
  encoded=bytearray()
  for name in names:
   b=name.encode('ascii')
   if len(b)>75 or not all(x in b'abcdefghijklmnopqrstuvwxyz0123456789_.' for x in b):
    raise ValueError('invalid genuine original C1TX bank filename')
   encoded.append(len(b));encoded+=b
  new=HEADER.pack(b'C1MT',1,94,40,len(encoded))+struct.pack('<94H',*ids)+encoded
  payload['maps/C1L1_environment.c1mt']=new
  payload['maps/'+EXPO_ASSET]=raw
  output.parent.mkdir(parents=True,exist_ok=True)
  with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for name,data in sorted(payload.items()):
    z.writestr(name,data)
  included_tex=sum(name.endswith('.c1tx') for name in payload)
  assert included_tex==24 and len(payload)==25
  summary={
   'source':'genuine user-owned iOS 2010 original Gameloft IronMan2',
   'source_author_material':'C1L1_obj_002.bdae:orig_07___Default',
   'source_material_id':idx,'source_original_triangles_newly_textured':206,
   'source_expo_2010_pvr_original_name':matches[0].name,
   'source_pvr2_decoded_width':w,'source_pvr2_decoded_height':h,
   'source_pvr2_metadata':pvr,
   'source_expo_original_PVR_sha256':hashlib.sha256(original).hexdigest(),
   'source_expo_native_C1TX_sha256':hashlib.sha256(raw).hexdigest(),
   'output_G13_C1MT_original_material_count':94,
   'output_G13_C1MT_original_atlas_count':40,
   'output_G13_C1MT_mapped_source_material_count':sum(v!=65535 for v in ids),
   'actual_authored_source_C1TX_textures_packed':included_tex,
   'all_other_material_indices_identical_to_proven_G12':all(
       n==v for i,(n,v) in enumerate(zip(ids,parse_bank(old)[0])) if i!=idx),
   'original_2010_immutable_world_positions_winding_unchanged':True,
   'raw_RGBA_original_expo_bytes':len(raw),
   'output_ZIP_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
   'ZIP_contains_only_authored_source_map_data_not_VPK':True,
   'hardware_PS_Vita_G13_tested':False,
   'files_sha256':{name:hashlib.sha256(b).hexdigest() for name,b in sorted(payload.items())},
  }
  report.parent.mkdir(parents=True,exist_ok=True)
  report.write_text(json.dumps(summary,indent=2,default=str)+'\n')
  print('PASS G13 exact source original Expo PVR no prefix omission; 206 genuine BRES urban faces now map to original 40th C1TX source, G12 other 93 original shader material records byte identical; map ZIP 24 authentic C1TX, NOT VPK.')
  return summary

if __name__=='__main__':
 ap=argparse.ArgumentParser()
 ap.add_argument('--ipa',required=True,type=Path)
 ap.add_argument('--output',required=True,type=Path)
 ap.add_argument('--report',required=True,type=Path)
 a=ap.parse_args();run(a.ipa,a.output,a.report)
