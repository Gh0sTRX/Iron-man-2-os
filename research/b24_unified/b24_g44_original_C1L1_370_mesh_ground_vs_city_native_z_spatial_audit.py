#!/usr/bin/env python3
"""G44 2010 C1L1: source-native height inversion / ground occupancy audit.

Based on exact original BRES 370 meshes, 22919 triangles. Nothing translated.
Source ground mesh raw local Z is approximately zero; a very large majority
of authored city BRES polygon triangle centroids are BELOW that reference.
This is physical source raw vertex data; NOT proof that original engine draws
city underground (model/root transforms, draw masks and shader unproven).

Produces independent 16:9 chart + JSON/CSV, without VPK or invented fixes.
--html optional: preexisting certified G32 original-data self-contained HTML;
otherwise reads original 2010 B11 source .bdae ZIP private repo.
"""
from __future__ import annotations
import argparse,base64,collections,csv,io,json,math,re
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont

def load(authentic_html=None):
 if authentic_html:
  s=authentic_html.read_text(encoding="utf-8")
  def tag(name):
   m=re.search(r'<script id="'+name+r'"[^>]*>(.*?)</script>',s,re.S)
   if not m:raise ValueError("G32 self-contained source payload missing "+name)
   return m.group(1)
  j=json.loads(tag("payload"))
  xyz=np.frombuffer(base64.b64decode(tag("rawpositions")),dtype="<f4").reshape(-1,3)
  faces=np.frombuffer(base64.b64decode(tag("rawindices")),dtype="<u4").reshape(-1,3)
  rows=[]
  for b in j["batches"]:
   i=int(b["start"])//3;n=int(b["tris"])
   rows.append((b["mesh"],b["group"],xyz,faces[i:i+n]))
  assert len(xyz)==37946 and len(faces)==22919 and len(set(r[0] for r in rows))==370
  return rows
 from b24_g13_c1l1_light_dome_mesh_provenance_sheet import source
 meshes,_=source()
 return [(r["source_mesh_name"],r["original_scene_group"],pts,faces)
         for r,pts,faces in meshes]

def audit(rows):
 bounds=(-1300.,500.,-1150.,600.)
 xmin,xmax,ymin,ymax=bounds
 scale=2
 W,H=int((xmax-xmin)*scale),int((ymax-ymin)*scale)
 xy=lambda pts: np.rint(np.stack(((pts[...,0]-xmin)*scale,
                           (ymax-pts[...,1])*scale),axis=-1)).astype(np.int32)
 mask=Image.new("1",(W,H),0)
 draw=ImageDraw.Draw(mask)
 for name,kind,pts,faces in rows:
  if kind!="ground":continue
  for inds in faces:
   draw.polygon([tuple(x) for x in xy(pts[inds])],fill=1)
 raster=np.asarray(mask,dtype=bool)
 groups=collections.defaultdict(lambda:dict(centroids=[],inside=0,count=0,belowzero=0,belowminus3=0))
 meshes=collections.defaultdict(lambda:dict(kind="",count=0,inside=0,belowzero=0,
                                         centroid_z=[],xsum=0.,ysum=0.))
 for name,kind,pts,faces in rows:
  center=pts[faces].mean(axis=1)
  ix=xy(center)
  ok=(ix[:,0]>=0)&(ix[:,0]<W)&(ix[:,1]>=0)&(ix[:,1]<H)
  inside=np.zeros(len(center),dtype=bool)
  inside[ok]=raster[ix[ok,1],ix[ok,0]]
  group=groups[kind]
  group["centroids"].append(center)
  group["inside"]+=int(inside.sum())
  group["count"]+=len(faces)
  group["belowzero"]+=int((center[:,2]<0).sum())
  group["belowminus3"]+=int((center[:,2]<-3).sum())
  m=meshes[name]
  m["kind"]=kind;m["count"]+=len(faces)
  m["inside"]+=int(inside.sum())
  m["belowzero"]+=int((center[:,2]<0).sum())
  m["centroid_z"].extend(float(x) for x in center[:,2])
  m["xsum"]+=float(center[:,0].sum());m["ysum"]+=float(center[:,1].sum())
 summary={};allcent={}
 for kind,g in sorted(groups.items()):
  z=np.concatenate(g["centroids"],axis=0)
  allcent[kind]=z
  summary[kind]={"native_source_triangles":g["count"],"original_triangle_Z_centroid_min":round(float(z[:,2].min()),4),
     "median":round(float(np.median(z[:,2])),4),"max":round(float(z[:,2].max()),4),
     "triangles_source_Z_centroid_below_0":g["belowzero"],
     "triangles_source_Z_centroid_below_minus_3":g["belowminus3"],
     "triangles_XY_centroid_inside_original_projected_ground_footprint":g["inside"],
     "triangles_XY_centroid_OUTSIDE_original_projected_ground_footprint":g["count"]-g["inside"]}
 assert sum(x["native_source_triangles"] for x in summary.values())==22919
 assert len(meshes)==370
 assert summary["urban"]["native_source_triangles"]==11141
 assert summary["ground"]["native_source_triangles"]==3280
 assert summary["vehicles"]["native_source_triangles"]==5116
 assert summary["lights"]["native_source_triangles"]==3382
 assert summary["urban"]["triangles_source_Z_centroid_below_0"]==11048
 assert summary["urban"]["triangles_XY_centroid_inside_original_projected_ground_footprint"]>=7500
 meshrows=[{"original_mesh_name":name,"original_source_group":m["kind"],"original_triangles":m["count"],
   "triangles_Z_centroid_below_zero":m["belowzero"],
   "original_source_median_Z":round(float(np.median(m["centroid_z"])),4),
   "triangles_XY_centroid_projected_to_original_ground":m["inside"],
   "triangles_XY_centroid_OUTSIDE_original_ground_footprint":m["count"]-m["inside"],
   "source_triangle_centroid_average_X":round(m["xsum"]/m["count"],4),
   "source_triangle_centroid_average_Y":round(m["ysum"]/m["count"],4),
   "real_original_runtime_parent_world_transform_PROVEN":False}
   for name,m in meshes.items()]
 assert sum(m["original_triangles"] for m in meshrows)==22919
 out=dict(original_2010_C1L1_BRES_370_meshes=370,
   original_2010_C1L1_BRES_22919_faces=22919,
   original_source_ground_height_reference_is_static_raw_Z_not_runtime_world=True,
   source_native_height_and_footprint_groups=summary,
   original_source_urban_centroids_below_Z0=11048,
   original_source_urban_triangle_centroids_total=11141,
   original_source_city_polygon_median_Z=summary["urban"]["median"],
   source_original_C1L1_environment_Deco_actor_transform_identity_previously_verified=True,
   original_engine_internal_BRES_node_root_matrix_recovered=False,
   original_game_camera_render_depth_compositing_OR_terrain_contact_PROVEN=False,
   no_mesh_repositioning_and_no_VPK=True)
 return out,meshrows,allcent,raster,bounds,scale

def visual(summary,cent,mask,bounds,scale,path):
 W,H=2400,1350
 p=Image.new("RGB",(W,H),"#0b1929")
 d=ImageDraw.Draw(p)
 def ft(n,b=False):
  try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
  except OSError:return ImageFont.load_default()
 def text(x,y,t,n=22,color="#dbe9f2",bold=False):
  d.text((x,y),t,fill=color,font=ft(n,bold))
 text(36,20,"G44 | ORIGINAL 2010 C1L1: SEHIR YER YUZUNUN ALTINDA MI?",37,"#f7dfab",True)
 text(39,73,"Gercek 22.919 BRES ucgen merkezi, kaynak ham XYZ. Hicbir mesh hareket ettirilmedi.",21,"#b7cedd")
 d.rounded_rectangle((16,122,1339,1312),radius=13,fill="#112b3a",outline="#54758e",width=2)
 d.rounded_rectangle((1360,122,2385,1312),radius=13,fill="#152b3d",outline="#54758e",width=2)
 text(35,144,"A — ORIJINAL ZEMIN AYAK IZI + SEHIR UCLARI",24,"#e8d8b4",True)
 xmin,xmax,ymin,ymax=bounds
 world=(-500.,490.,-570.,570.)
 x1,x2,y1,y2=world
 side_x0,side_y0=50,235
 side_width,side_height=1240,990
 def point(x,y):return (int(side_x0+(x-x1)/(x2-x1)*side_width),
                       int(side_y0+(y2-y)/(y2-y1)*side_height))
 from PIL import Image as PILImage
 # Actual raster projection of all ORIGINAL ground triangles, not a synthetic level footprint.
 px0=int((x1-xmin)*scale);px1=int((x2-xmin)*scale)
 py0=int((ymax-y2)*scale);py1=int((ymax-y1)*scale)
 fp=PILImage.fromarray((mask[py0:py1,px0:px1].astype("uint8")*255),"L")
 fp=fp.resize((side_width,side_height),Image.Resampling.NEAREST)
 panel=PILImage.new("RGB",(side_width,side_height),"#102334")
 panel.paste("#3e6d4c",(0,0,side_width,side_height),fp)
 p.paste(panel,(side_x0,side_y0))
 d=ImageDraw.Draw(p)
 def dots(kind,color,step=1):
  pts=cent[kind][::step]
  for x,y,z in pts:
   if x1<=x<=x2 and y1<=y<=y2:
    xx,yy=point(x,y)
    d.point((xx,yy),fill=color)
 # Source 2010 polygon centroids, no approximated meshes
 dots("urban","#f4a16d",2)
 dots("vehicles","#c6c1e9",2)
 dots("lights","#76d3e7",2)
 for xx,t,col in [(55,"ZEMIN XY","#78c996"),(322,"SEHIR","#f4a16d"),(525,"ARACLAR","#c6c1e9"),(755,"ISIKLAR","#76d3e7")]:
  text(xx,1250,t,20,col,True)
 text(1380,158,"B — ORIJINAL KAYNAK Z DAGILIMI",25,"#e8d8b4",True)
 z0line=1800
 right_x0=1470;right_x1=2290
 def xpos(z):return int(right_x0+(z+50)/100*(right_x1-right_x0))
 d.line((xpos(0),245,xpos(0),910),fill="#fafaf0",width=3)
 text(xpos(0)+10,225,"Z = 0 (zemin civari)",17,"#f6f0da")
 layers=[("ground","ZEMIN","#8ec593"),("urban","SEHIR","#ffad7d"),("vehicles","ARACLAR","#baa8f3"),("lights","ISIK","#86d4e9")]
 for i,(kind,label,col) in enumerate(layers):
  y=310+i*144
  text(1390,y,label,22,col,True)
  vals=cent[kind]
  step=max(1,len(vals)//2200)
  for j,z in enumerate(vals[::step,2]):
   x=xpos(float(z))
   jitter=((j*134775813)&255)%51-25
   if right_x0-10<=x<=right_x1+10:d.ellipse((x-1,y+57+jitter,x+1,y+59+jitter),fill=col)
  med=summary[kind]["median"]
  text(1395,y+103,f"median Z={med:+.2f}  |  Z<0: {summary[kind]['triangles_source_Z_centroid_below_0']:,}/{len(vals):,}",17,"#c4d6e2")
 for z in [-40,-20,0,20,40]:
  x=xpos(z);text(x-18,940,str(z),18,"#bbd0dd")
 d.line((1384,995,2345,995),fill="#537088",width=2)
 text(1390,1014,"ORIJINAL VERIDE:",22,"#f5dca5",True)
 text(1390,1062,"11.048 / 11.141 sehir ucgeni",21,"#ffad7d",True)
 text(1390,1093,"Z=0 seviyesinin altinda.",21,"#ffad7d",True)
 text(1390,1150,"Engine ic root/donus bilinmiyor.",17,"#d0e3ee")
 text(1390,1180,"Burada model/Z offset UYDURULMADI.",17,"#d0e3ee")
 text(39,1318,"KAYNAK KOORDINAT KANITI — orijinal oyun ekran goruntusu veya tamamlanmis sehir sahnesi degil.",16,"#c0d3e0")
 path.parent.mkdir(parents=True,exist_ok=True)
 p.save(path,optimize=True)

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--html",type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args()
 rows=load(a.html)
 summary,meshrows,cent,mask,bounds,scale=audit(rows)
 a.out.mkdir(parents=True,exist_ok=True)
 (a.out/"G44_NATIVE_2010_GROUND_URBAN_HEIGHT_AND_XY.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
 with (a.out/"G44_370_MESH_ORIGINAL_Z_AND_GROUND_FOOTPRINT.csv").open("w",newline="",encoding="utf-8-sig") as f:
  writer=csv.DictWriter(f,fieldnames=list(meshrows[0]));writer.writeheader();writer.writerows(meshrows)
 visual(summary["source_native_height_and_footprint_groups"],cent,mask,bounds,scale,
        a.out/"G44_ORIGINAL_LEVEL1_KAYNAK_GEOMETRI_YUKSEKLIK_16_9.png")
 print("PASS G44 source BRES original 370 meshes 22919 real polygons, no invented transformations")
 print("G44 original true authored coordinate distribution",json.dumps(summary["source_native_height_and_footprint_groups"]))
 print("G44 11048/11141 native city triangles below flat ground Z=0 reference; source model-local, world root unknown; NO VPK")
if __name__=="__main__":main()
