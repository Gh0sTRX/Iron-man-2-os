#!/usr/bin/env python3
"""G47 offline image of two AUTHENTIC 2010 BRES geometry layers, no fake layout.

Input G32 source-generated standalone 3D HTML embeds exact 370 original
BRES meshes, 22919 triangles, source original UVs and 24 source PVR atlases.
G46 source-derived 5 original CLARA negative-Z PD coordinates are plotted.
Both panels share identical diagnostic 3D camera:
  A all 370 source static BRES meshes (the raw M1-style overlap)
  B all urban, vehicle, light meshes; ground temporarily hidden FOR INSPECTION.
No vertex moves, no unproven parent/root/scaling, no claimed game visibility.
Colors sample source PVR texel at per-triangle UV centroid (not texture mapped
per pixel / original PVR native shader); non-PVR color is neutral evidence grey.
Uses host CPU painter projection ONLY for a static PNG; NO Vita performance.
"""
from __future__ import annotations
import argparse,base64,io,json,re
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
def font(n,b=False):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
 except OSError:return ImageFont.load_default()
def run(html,report,out):
 s=html.read_text(encoding="utf-8")
 def tag(n):
  m=re.search(r'<script id="'+n+r'"[^>]*>(.*?)</script>',s,re.S)
  if not m:raise ValueError("G32 original WebGL proof HTML missing source "+n)
  return m.group(1)
 source=json.loads(tag("payload"))
 pos=np.frombuffer(base64.b64decode(tag("rawpositions")),dtype="<f4").reshape(-1,3)
 faces=np.frombuffer(base64.b64decode(tag("rawindices")),dtype="<u4").reshape(-1,3)
 uv=np.frombuffer(base64.b64decode(tag("rawuv")),dtype="<f4").reshape(-1,2)
 if len(source["originalPVRs"])!=24 or len(pos)!=37946 or len(faces)!=22919 or len(uv)!=37946 or len(source["batches"])!=460:
  raise ValueError("G32 actual original BRES+PVR source invariant failed")
 imgs={r["name"].casefold():np.asarray(Image.open(io.BytesIO(base64.b64decode(r["base64"]))).convert("RGB"))
      for r in source["originalPVRs"]}
 cols=np.tile(np.array([118,146,163],dtype=np.uint8),(len(faces),1))
 isground=np.zeros(len(faces),dtype=bool)
 for b in source["batches"]:
  begin=b["start"]//3;end=begin+b["tris"]
  if b["group"]=="ground":isground[begin:end]=True
  tex=imgs.get(str(b.get("tga") or "").casefold())
  if tex is None or not b.get("original_uv_mesh_positive"):continue
  t=uv[faces[begin:end]].mean(axis=1)
  xx=np.rint((t[:,0]%1)*(tex.shape[1]-1)).astype(np.int32)
  yy=np.rint(((1-t[:,1])%1)*(tex.shape[0]-1)).astype(np.int32)
  cols[begin:end]=tex[yy,xx]
 assert isground.sum()==3280
 az=-1.04;el=.64
 front=np.array([np.cos(az)*np.cos(el),np.sin(az)*np.cos(el),np.sin(el)])
 right=np.cross([0.,0.,1.],-front);right/=np.linalg.norm(right)
 up=np.cross(-front,right);up/=np.linalg.norm(up)
 center=np.array([-65.,-47.,-17.])
 xyz=pos.astype(np.float64)-center
 projected=np.stack((xyz@right,xyz@up),axis=1)
 screen=np.rint(np.stack((635+projected[faces,:,0]*2.14,570-projected[faces,:,1]*2.14),axis=-1)).astype(np.int32)
 distances=(xyz@front)[faces].mean(axis=1)
 order=np.argsort(distances)
 pts3=pos[faces].astype(np.float64)
 normal=np.cross(pts3[:,1]-pts3[:,0],pts3[:,2]-pts3[:,0])
 normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-5)
 shade=.68+.32*np.abs(normal@np.array([.27,-.35,.90]))
 cols=np.clip(cols.astype(np.float64)*shade[:,None],0,255).astype(np.uint8)
 pd=json.loads(report.read_text())["source_low_Z_author_transforms_around_real_source_city_meshes"]
 assert len(pd)==5
 def px(v):
  q=np.array(v)-center
  return int(635+q@right*2.14),int(570-q@up*2.14)
 def render(no_ground):
  img=Image.new("RGB",(1270,1040),"#122237");draw=ImageDraw.Draw(img)
  n=0
  for k in order:
   if no_ground and isground[k]:continue
   poly=[tuple(q) for q in screen[k]]
   if max(q[0] for q in poly)<0 or min(q[0] for q in poly)>=1270 or max(q[1] for q in poly)<0 or min(q[1] for q in poly)>=1040:continue
   draw.polygon(poly,fill=tuple(int(c) for c in cols[k]));n+=1
  if no_ground:
   for i,rec in enumerate(pd):
    x,y=px(rec["source_native_XYZ"])
    if 12<x<1255 and 12<y<1030:
     draw.ellipse((x-7,y-7,x+7,y+7),fill="#8cf0ff",outline="#142433",width=2)
     draw.text((x+10,y-10),"PD "+str(i+1),fill="#b1f8ff",font=font(22,True),stroke_width=2,stroke_fill="#081c30")
  return img,n
 all_img,count_all=render(False)
 layers_img,count_layers=render(True)
 im=Image.new("RGB",(2600,1260),"#091723")
 d=ImageDraw.Draw(im)
 d.text((32,18),"G47 | ORIJINAL 2010 C1L1 - AYNI KAMERA, IKI KAYNAK KATMANI",font=font(37,True),fill="#f2dfae")
 d.text((34,81),"22.919 gercek BRES ucgeni / 24 orijinal PVR atlas UV orneklemesi / SIFIR mesh tasima",font=font(22),fill="#bbd1df")
 im.paste(all_img,(20,164));im.paste(layers_img,(1310,164))
 d=ImageDraw.Draw(im)
 for x,t in ((33,"A - TUM KAYNAK GEOMETRISI"),(1323,"B - ZEMIN GIZLI: SEHIR + 5 PD")):
  d.rounded_rectangle((x-10,124,x+1250,162),radius=5,fill="#203c4c")
  d.text((x,127),t,font=font(24,True),fill="#e8d6a8")
 d.text((33,1211),"B: zemin SADECE kaynak incelemesinde gizlendi. Original oyun runtime gorunurlugu kanitlanmadi; painter host gorunumu / native shader DEGIL.",font=font(18),fill="#b5cada")
 out.mkdir(parents=True,exist_ok=True)
 im.save(out/"G47_C1L1_2010_ORIGINAL_BRES_PVR_3D_GROUND_ON_OFF.png",optimize=True)
 layers_img.save(out/"G47_2010_C1L1_REAL_SOURCE_LOWER_CITY_3D.png",optimize=True)
 evidence=dict(source_original_BRES_meshes=370,source_original_triangles=22919,
   source_native_ground_triangles=3280,source_authentic_original_PVRs=24,
   source_native_PD_negative_Z_count=5,source_3D_diagnostic_camera_same_between_panels=True,
   original_source_vertices_relocated=False,
   original_native_shader_camera_or_root_matrix_recovered=False,
   original_runtime_visibility_claimed=False,
   source_PVR_is_triangle_centroid_sample_not_per_pixel_uv_shading=True,
   no_VPK_and_no_performance_changes=True,
   image_source_triangle_bounding_box_qualifying_polygons_painter_all=count_all,
   image_source_triangle_bounding_box_qualifying_polygons_painter_non_ground=count_layers)
 (out/"G47_ORIGINAL_2010_TWO_LAYER_3D_PROVENANCE.json").write_text(json.dumps(evidence,indent=2)+"\n")
 print("PASS G47 real 2010 BRES/PVR 370/22919+24 source triangles and native 5 CLARA PD; zero source model placement changed; no VPK.")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--g32-html",type=Path,required=True)
 p.add_argument("--g46-json",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();run(a.g32_html,a.g46_json,a.out)
