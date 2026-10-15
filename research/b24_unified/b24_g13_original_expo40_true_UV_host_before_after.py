#!/usr/bin/env python3
"""Actual 2010 G12 39 PVR vs G13 40 including original CAHP01 Expo compare.

GPU-less host diagnostic, not real iOS/Vita scene nor a guessed city. Exact
B11 exported source GLB positions/index triangle winding + original BRES
UV + authentic original iOS 2010 PVR atlas sampler; the ONLY changed asset
is originally-referenced CAHP01_c_expo_building.tga for 206 authored faces.
"""
from __future__ import annotations
import argparse,json,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops,ImageDraw
from b24_g12_original_C1L1_true_uv_pixel_raster import original_data,preview,H,W
from recover_c1l1_original_uv import BDAEZIP
def get_expo_center():
 with zipfile.ZipFile(BDAEZIP) as z:
  ns={'__name__':'G13_EXPO_TRUE_SOURCE','__file__':'bdae_scene_parser.py'}
  exec(compile(z.read('bdae_scene_parser.py'),'bdae_scene_parser.py','exec'),ns)
  rows,_=ns['parse'](z.read('original_models/C1L1_obj_002.bdae'))
  m=rows[4]
  if len(m['faces'])!=206 or len(m['submeshes'])!=1 or (
      m['submeshes'][0]['material']!='orig_07___Default'):
   raise ValueError('Original 2010 exact Expo mesh 206 source faces not aligned')
  pos=np.asarray(m['positions'],dtype=np.float32)
  return ((pos.min(axis=0)+pos.max(axis=0))/2.).astype(np.float64)

def main(ipa:Path,out:Path):
 out.mkdir(parents=True,exist_ok=True)
 center=get_expo_center()
 original=original_data(ipa,include_expo=False)
 extended=original_data(ipa,include_expo=True)
 if original[-1]['source_texture_atlas_count']!=39 or extended[-1]['source_texture_atlas_count']!=40:
  raise ValueError('authentic source PVR atlas bank changed')
 if not np.array_equal(original[0],extended[0]):
  raise ValueError('original 2010 BRES world positions changed between preview versions')
 if not np.array_equal(original[1],extended[1]):
  raise ValueError('original source authored BRES UV coordinates changed')
 if not np.array_equal(original[2],extended[2]):
  raise ValueError('original source mesh category changed')
 old_png=out/'G13_2010_EXPO_ORIGINAL_G12_TEXTURE_FILTER_BEFORE.png'
 new_png=out/'G13_2010_EXPO_GENUINE_40TH_PVR_AFTER.png'
 a=preview(original,center,
   'BEFORE G12 missing exact original Expo 2010 PVR',
   old_png)
 b=preview(extended,center,
   'AFTER G13 original Expo owner PVR included',
   new_png)
 before=np.array(Image.open(old_png).convert('RGB'))
 after=np.array(Image.open(new_png).convert('RGB'))
 view_a=before[48:H-44]
 view_b=after[48:H-44]
 delta=np.abs(view_a.astype(np.int16)-view_b.astype(np.int16))
 change=np.any(delta>8,axis=2)
 nchanged=int(change.sum())
 heat=np.zeros_like(after)
 heat[:]=[22,35,45]
 heat[48:H-44][change]=[254,187,57]
 heatim=Image.fromarray(heat,'RGB')
 draw=ImageDraw.Draw(heatim)
 draw.text((20,16),'YELLOW = pixel change from adding ONLY the authentic 2010 Expo PVR',fill='white')
 draw.text((20,H-30),'SOURCE test, NOT VitaGL capture; no 3D model/camera/other material changes.',fill='white')
 heatim.save(out/'G13_2010_EXPO_ONLY_CHANGED_PIXEL_MASK.png')
 page="""<!DOCTYPE html><html lang='tr'><meta charset='utf-8'>
<title>G13 Original 2010 Expo haritası — Önce/Sonra UV</title>
<style>body{background:#14202b;color:#d9ebf4;font:16px system-ui;margin:25px auto;max-width:1280px}
h1{font-size:23px}p{line-height:1.45}.frame{position:relative;aspect-ratio:1280/760;overflow:hidden;border:1px solid #557;}
.frame img{position:absolute;top:0;left:0;width:100%;height:100%;display:block;}
#clip{clip-path:inset(0 50% 0 0)}input{width:100%}small{color:#a5bac5}
</style>
<h1>Iron Man 2 iOS (2010) C1L1 — Eksik özgün Expo dokusu</h1>
<p>Sol: G12 orijinal 39 PVR. Sağ: G13, özgün 40. PVR de eklendi.
Kaydırıcıyı hareket ettirerek yalnız bu materyal farkını incele.</p>
<div class='frame'><img src='G13_2010_EXPO_ORIGINAL_G12_TEXTURE_FILTER_BEFORE.png'>
<img id='clip' src='G13_2010_EXPO_GENUINE_40TH_PVR_AFTER.png'></div>
<input id='range' type='range' min='0' max='100' value='50' aria-label='G13 before-after slider'>
<small>Gerçek kaynak BRES 3B geometri/UV ve gerçek iOS 2010 PVR'den CPU ile üretilmiştir. Bu gerçek VitaGL ekran görüntüsü değildir; sahne yerleşimi orijinal oyunla eşitliği kanıtlanmadı.</small>
<script>const r=document.getElementById('range'),c=document.getElementById('clip');
r.addEventListener('input',()=>{c.style.clipPath='inset(0 '+(100-Number(r.value))+'% 0 0)'})</script>
</html>"""
 (out/'G13_2010_EXPO_BEFORE_AFTER_SOURCE_UV_COMPARE.html').write_text(page)
 report={'owner_source_exact_2010_Original_ExpoBRES_mesh':'C1L1_obj_002_4',
   'source_2010_shader_material':'orig_07___Default',
   'exact_source_original_faces_corrected':206,
   'source_expo_geometry_world_bbox_center':center.tolist(),
   'source_g10_before':a,'source_g13_after':b,
   'only_source_PVR_atlas_difference':True,
   'source_color_pixel_changes_in_scene_not_header':nchanged,
   'source_geometry_UV_bitidentical_before_after':True,
   'NOT_VITA_IN_GAME_SCREENSHOT':True,'VPK_GENERATED':False}
 (out/'G13_2010_EXPO_PER_PIXEL_REAL_SOURCE_DIFFERENCE_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS G13 2010 original Expo 206-faces PVR per-pixel host renderer old39 vs real40, authored BRES UV AND ORIGINAL mesh identical, final actual source image pixel differences',nchanged,'NO VPK')
 return report

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--ipa',required=True,type=Path)
 p.add_argument('--out',required=True,type=Path)
 a=p.parse_args();main(a.ipa,a.out)
