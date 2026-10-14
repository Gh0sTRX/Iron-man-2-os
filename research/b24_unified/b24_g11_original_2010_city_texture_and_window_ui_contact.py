#!/usr/bin/env python3
"""True 2010 C1L1 city diffuse atlases + WINDOW source PNG contact sheets.

Only source-owned 2010 iOS TGA/PVR and PNG records, not generated guesses.
Determine exact PVR 2.0 pixel format header before decoding textures.
Do not claim material->texture assignment, or original reticle identity.
"""
from __future__ import annotations
import argparse, hashlib, io, json, math, struct, zipfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from b24_owner_pack_extract import decode
import texture2ddecoder

def pvr_pixels(raw:bytes, name:str):
    if len(raw)<52:raise ValueError('PVR header truncated')
    size,height,width,mips,flags,data_len,bpp,r,g,b,a,magic,surfaces=struct.unpack_from('<13I',raw)
    fmt=flags & 0xff
    if size!=52 or width<8 or width>2048 or height<8 or height>2048 or magic!=0x21525650:
        raise ValueError('original PVR v2 header invalid')
    stride=int(width*height*bpp//8)
    if stride<=0 or stride>len(raw)-52:raise ValueError('PVR first mip exceeds source bytes')
    meta={'filename':name,'width':width,'height':height,'mips':mips,
      'pvr_flags':flags,'pvr_format_low':fmt,'bpp':bpp,'payload_bytes':len(raw)-52,
      'header_data_length':data_len,'pixel_payload_sha256':hashlib.sha256(raw[52:52+stride]).hexdigest()}
    if fmt==25 and bpp==4:
        decoded=texture2ddecoder.decode_pvrtc(raw[52:52+stride],width,height)
        rgba=np.frombuffer(decoded,dtype=np.uint8).reshape((height,width,4))[:,:, [2,1,0,3]].copy()
        img=Image.fromarray(rgba,'RGBA')
    elif fmt==24 and bpp==2:
        decoded=texture2ddecoder.decode_pvrtc(raw[52:52+stride],width,height)
        rgba=np.frombuffer(decoded,dtype=np.uint8).reshape((height,width,4))[:,:, [2,1,0,3]].copy()
        img=Image.fromarray(rgba,'RGBA')
    elif bpp==16 and fmt in (0x10,0x11,0x12,0x13,0x14):
        # PVR2 explicitly stores exact channel masks in its 52-byte header.
        # Critically, the authentic 2010 'sprites' atlases use RGBA4444
        # (0x0f00/0x00f0/0x000f/0xf000) — not RGB565. Guessing distorted
        # the original C1L1_map mini-map preview too. Decode SOURCE masks.
        channel_masks=(r,g,b,a)
        bits_union=0
        for mask in channel_masks:
            if mask<0 or mask>0xffff or mask&bits_union:
                raise ValueError('original PVR overlapping/bad 16bit channel masks')
            bits_union|=mask
        if not all((r,g,b)):
            raise ValueError('original PVR missing RGB channel mask')
        native=np.frombuffer(raw[52:52+stride],dtype='<u2').reshape((height,width))
        channels=[]
        for i,mask in enumerate(channel_masks):
            if not mask:
                if i!=3:raise ValueError('missing non-alpha source channel')
                channels.append(np.full((height,width),255,dtype=np.uint8))
                continue
            shift=(mask&-mask).bit_length()-1
            bitcount=mask.bit_count()
            expected=((1<<bitcount)-1)<<shift
            if mask!=expected:raise ValueError('original PVR noncontiguous channel mask')
            src=(native&mask)>>shift
            dst=(src.astype(np.uint32)*255//((1<<bitcount)-1)).astype(np.uint8)
            channels.append(dst)
        rgba=np.stack(channels,axis=2)
        img=Image.fromarray(rgba,'RGBA')
        meta['actual_native_source_rgba_channel_masks']=[hex(q) for q in channel_masks]
    else:
        raise ValueError(f'unsupported original texel type PVR flags={hex(flags)} bpp={bpp} fmt={fmt}')
    return img,meta

def make_sheet(images:list[tuple[str,Image.Image]], output:Path, title:str, ncol:int=5):
    w,h=195,180
    rows=(len(images)+ncol-1)//ncol
    sheet=Image.new('RGB',(ncol*w,max(1,rows)*h+36),(23,29,40))
    draw=ImageDraw.Draw(sheet)
    draw.text((12,12),title,fill='white')
    for i,(name,img) in enumerate(images):
        x=(i%ncol)*w;y=(i//ncol)*h+36
        alpha=img.convert('RGBA')
        alpha.thumbnail((180,135),Image.Resampling.NEAREST)
        if 'A' in alpha.getbands():
            bg=Image.new('RGBA',alpha.size,(62,67,78,255));bg.alpha_composite(alpha); alpha=bg
        sheet.paste(alpha.convert('RGB'),(x+(w-alpha.width)//2,y+4))
        clean=name if len(name)<=27 else name[:24]+'...'
        draw.text((x+5,y+143),clean,fill=(232,235,243))
        draw.text((x+5,y+157),f'{img.width} x {img.height}',fill=(163,186,212))
    output.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(output)

def main(ipa:Path,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(ipa) as z:
        textures=z.read('Payload/IronMan2.app/textures')
        window=z.read('Payload/IronMan2.app/window')
    rows=decode(textures,'.tga')
    city=[r for r in rows if r.name.casefold().startswith('c1l1_')]
    city.sort(key=lambda r:r.name.casefold())
    pre=[];metadata=[];failed=[]
    for r in city:
        original=textures[r.start:r.end]
        try:
            img,info=pvr_pixels(original,r.name)
            pre.append((r.name,img))
            metadata.append(info)
            img.save(out/f'CITY_SOURCE_{r.name[:-4].replace("/","_")}.png')
            print('G11_NATIVE_ORIGINAL_PVR',r.name,info,flush=True)
        except Exception as e:
            failed.append({'name':r.name,'error':str(e),
              'original_bytes':len(original),
              'header_52_hex':original[:52].hex()})
            print('G11_ORIGINAL_ATLAS_UNSUPPORTED',r.name,str(e),flush=True)
    if not pre:raise ValueError('no genuine original 2010 city textures decoded')
    make_sheet(pre,out/'G11_ORIGINAL_2010_C1L1_CITY_TEXTURE_ATLAS_CONTACT.png',
               'Original 2010 C1L1 author PVR diffuse atlas samples — NOT yet material-mapped')
    p=0; original_ui=[];ui_rows=[]
    while p+4<=len(window):
        n=struct.unpack_from('<I',window,p)[0]
        if not 45<=n<=len(window)-p-4 or window[p+4:p+12]!=b'\x89PNG\r\n\x1a\n':
            raise ValueError('original window png sequence corrupted')
        raw=window[p+4:p+4+n]
        with Image.open(io.BytesIO(raw)) as im:
            im.load();im=im.convert('RGBA').copy()
        label=f'window_png_{len(original_ui):02d}'
        original_ui.append((label,im))
        ui_rows.append({'record_index':len(ui_rows),'source_offset':p+4,
                        'source_bytes':n,'original_size':[im.width,im.height],
                        'original_png_sha256':hashlib.sha256(raw).hexdigest(),
                        'authentic_crosshair_verified':False})
        p+=4+n
    if p!=len(window) or len(ui_rows)!=23:raise ValueError('UI source records not exact')
    make_sheet(original_ui,out/'G11_ORIGINAL_2010_IOS_WINDOW_UI_23_SPRITES_CONTACT.png',
               'Source original 2010 UI WINDOW 23 actual PNG records — reticle identity UNKNOWN',ncol=5)
    doc={'city_source_tga_total':len(city),'city_source_decoded':len(pre),
         'city_source_failed_format':failed,'city_source_png_rows':metadata,
         'ui_true_source_png_count':len(ui_rows),'ui_original_png_meta':ui_rows,
         'authoritative_material_to_diffuse_link_proven':False,
         'original_crosshair_sprite_identity_proven':False,
         'original_2010_ipa_uploaded':False,'host_previews_NOT_VITA_GPU_screenshots':True}
    (out/'G11_CITY_PVR_AND_IOS_SOURCE_UI_AUTHENTIC_PREVIEW_REPORT.json').write_text(
        json.dumps(doc,indent=2)+'\n')
    print('PASS G11 ORIGINAL iOS genuine first-level texture atlases',len(pre),
          'out of',len(city),'and 23 original WINDOW UI sprites host preview NO VPK',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ipa',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();main(a.ipa,a.out)
