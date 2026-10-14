#!/usr/bin/env python3
"""Original 2010 iOS 6MB 'sprites' archive exact 13 u32 offsets / 12 blobs.

This is NOT the named owner asset model pack and must not be decoded as one.
Extract only verified source PVR subrecords, texture mark.tga and metadata.
Do not assert crosshair identity before source pixel graphic is inspected.
"""
from __future__ import annotations
import argparse,hashlib,json,struct,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact
from b24_g11_original_2010_city_texture_and_window_ui_contact import pvr_pixels

def inspect(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  sprites=z.read('Payload/IronMan2.app/sprites')
  tex=z.read('Payload/IronMan2.app/textures')
 if struct.unpack_from('<H',sprites)[0]!=13:raise ValueError('2010 sprites count changed')
 starts=struct.unpack_from('<13I',sprites,2)
 base=2+13*4
 assert starts[0]==0 and starts[-1]==len(sprites)-base
 assert all(x<y for x,y in zip(starts,starts[1:]))
 out.mkdir(parents=True,exist_ok=True)
 report=[]
 for i,(start,end) in enumerate(zip(starts,starts[1:])):
  blob=sprites[base+start:base+end]
  hashes={'crc_32_start_hex':blob[:64].hex(),
    'raw_size':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),
    'PNG_magic_count':blob.count(b'\x89PNG\r\n\x1a\n'),
    'PVR_header_tag_count':blob.count(b'PVR!'),
    'JPEG_SOI_count':blob.count(b'\xff\xd8\xff'),
    'DDS_signature_count':blob.count(b'DDS '),
    'zlib_78_9c_count':blob.count(b'\x78\x9c')}
  # Validate native PVR 2.0 header from source "PVR!" offset -44
  valid=[]
  cursor=0
  while True:
   tag=blob.find(b'PVR!',cursor)
   if tag<0:break
   start_p=tag-44
   if start_p>=0 and start_p+52<len(blob):
    part=blob[start_p:]
    try:
     img,meta=pvr_pixels(part,'SpriteBlob'+str(i)+'_'+str(tag))
     png=out/f'ORIGINAL_2010_sprites_blob{i:02}_PVR_{tag}.png'
     img.save(png)
     valid.append({'offset':start_p,'png':png.name,'meta':meta})
    except Exception as e:
     valid.append({'offset':start_p,'decode_error':str(e)[:160]})
   cursor=tag+4
  hashes['source_pvr_candidates']=valid
  # Even-numbered author blobs are the compact atlas sprite rectangle
  # descriptors for the following genuine PVR. Archiving six small source
  # descriptor records (not full IPA nor bulk original binaries) permits
  # deterministic local reverse engineering of the ORIGINAL HUD UV cells.
  if i%2==0:
   descriptor=out/f'G11_ORIGINAL_2010_SPRITE_RECT_DESCRIPTOR_{i:02}.bin'
   descriptor.write_bytes(blob)
   hashes['source_sprite_rect_descriptor']=descriptor.name
   hashes['descriptor_magic_hex']=blob[:4].hex()
   hashes['descriptor_2010_record_count_u16_at_6']=struct.unpack_from('<H',blob,6)[0] if len(blob)>=8 else None
  report.append(hashes)
  print('2010_GENUINE_SPRITES12_ARCHIVE',i,
        'bytes',len(blob),'PNG',hashes['PNG_magic_count'],
        'PVR',hashes['PVR_header_tag_count'],'JPEG',hashes['JPEG_SOI_count'],
        'JPEG+PVR headers',valid[:5],'first64',blob[:64].hex(),flush=True)
 original=get_exact(tex,decode(tex,'.tga'),'mark.tga')
 img,meta=pvr_pixels(original,'mark.tga')
 img.save(out/'G11_ORIGINAL_2010_IOS_MARK_TGA_AUTHOR_TEXTURE.png')
 result={'original_game_sprites_records':len(report),
   'original_archive_size':len(sprites),
   'original_archive_has_correct_sentinel_offsets':True,
   'original_native_blobs':report,
   'original_mark_pvr':meta,
   'original_crosshair_identity_verified':False,
   'sprites_proprietary_source_blobs_NOT_PNG':True,
   'not_gameplay_gpu_screenshot':True}
 (out/'G11_AUTHENTIC_2010_IOS_SPRITE_RECORDS_AND_MARK_PVR.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PASS original user-owned 2010 iOS Sprites archive 12 true records and source mark.TGA pixel preview; no crosshair identity assumption')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();inspect(a.ipa,a.out)
