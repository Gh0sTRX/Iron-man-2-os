#!/usr/bin/env python3
"""G46 original 2010 C1L1: genuine negative-Z PositionDummy vs real city BRES faces.

Find any original CLARA PositionDummy source 0x005C transform records with Z<-20.
Find nearest true ORIGINAL C1L1_obj urban triangle center in 3D; do not use
asset-name guesses or arbitrary +36 Z "fix". This falsifies treating raw urban
negative-Z as proof of a broken scene root. PD nested-child vector semantics
remain unknown (eye/target/command position), so don't assert playable route.

Output independent real source BRES polygon 16:9 ground+urban/PD visualization,
JSON exact raw source world references and CSV. No VPK.
"""
from __future__ import annotations
import argparse,collections,csv,json,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from b24_owner_pack_extract import decode,get_exact
from b24_g24_original_clara_source_601_nodes_663_parent_links import audit
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
from b24_g13_c1l1_light_dome_mesh_provenance_sheet import source

def native(ipa):
 with zipfile.ZipFile(ipa) as z:pack=z.read("Payload/IronMan2.app/clev")
 raw=get_exact(pack,decode(pack,".bclara"),"level1.bclara")
 original=audit(raw)
 types=summarize(raw)["source_2010_typed_class_instances"]
 lookup={x["original_numeric_name_id"]:x for x in types}
 records=original["all_663_source_rigid_transforms_with_native_parent_child_name_ID_chain"]
 low=[]
 for row in records:
  parent=lookup.get(row["original_named_parent_source_ID"])
  if not parent or parent["original_class_name"]!="PositionDummy":continue
  xyz=row["native_vec3_position"]
  if xyz[2]<-20.:
   low.append({"original_native_PD_name":parent["original_name"],
    "original_native_PD_source_entity_ID":row["original_named_parent_source_ID"],
    "source_child_transform_entity_ID":row["original_child_node_ID"],
    "source_native_XYZ":[float(a) for a in xyz],
    "original_source_transform_byte_offset":row["native_transform_source_offset"],
    "original_CLARA_PD_transform_function_semantics_not_proven":True})
 if len(low)!=5:raise ValueError("original low-level PD source count drift")
 known={"PD_check_enemy_go","PD_check_enemy_go_goal","PD_fly_away_goal",
        "PD_enemy_away_1","PD_tutorial_missile_goal"}
 if {r["original_native_PD_name"] for r in low}!=known:
  raise ValueError("original negative-Z source names changed")
 return low

def font(n,b=False):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
 except OSError:return ImageFont.load_default()

def preview(rows,png):
 W,H=2400,1350
 im=Image.new("RGB",(W,H),"#07182a");d=ImageDraw.Draw(im)
 def text(x,y,t,n=21,color="#e9f0fa",bold=False):
  d.text((x,y),t,font=font(n,bold),fill=color)
 text(40,17,"G46 — ORIJINAL C1L1: Z<0 KATMANINDA SAHNE KONUM KANITI",35,"#f9dfaa",True)
 text(40,69,"2010 CLARA PositionDummy + GERCEK 2010 BRES ucgenleri. G44'teki -36 Z bulgusu tek basina HATA kaniti degil.",20,"#b9d2e0")
 d.rounded_rectangle((18,120,1428,1316),radius=14,fill="#132737",outline="#56758a",width=2)
 d.rounded_rectangle((1453,120,2380,1316),radius=14,fill="#132737",outline="#56758a",width=2)
 xmin,xmax,ymin,ymax=-390.,310.,-325.,310.
 scale=min(1304/(xmax-xmin),1080/(ymax-ymin))
 def pt(v):return (int(46+(float(v[0])-xmin)*scale),int(1240-(float(v[1])-ymin)*scale))
 meshes,_=source()
 for mesh,xyz,faces in meshes:
  if mesh["original_scene_group"]!="ground":continue
  for face in faces:
   p=xyz[face]
   if p[:,0].max()<xmin or p[:,0].min()>xmax or p[:,1].max()<ymin or p[:,1].min()>ymax:continue
   d.polygon([pt(a) for a in p],fill="#416647")
 # The source city geometry is UNDER ground in raw Z. Overlay x/y as a
 # DIAGNOSTIC only: DO NOT call this original game occlusion/render result.
 for mesh,xyz,faces in meshes:
  if mesh["original_scene_group"]!="urban":continue
  p=xyz[faces].mean(axis=1)
  for tri in p:
   x,y=pt(tri)
   if 50<=x<=1370 and 150<=y<=1270 and tri[2]<-20:
    d.point((x,y),fill="#f0aa79")
 for i,r in enumerate(rows):
  x,y=pt(r["source_native_XYZ"]);col="#8ee5fd"
  d.ellipse((x-11,y-11,x+11,y+11),fill=col,outline="#0b1826",width=3)
  text(x+16,y-25,f"PD {i+1}",19,col,True)
 text(44,143,"A — ZEMIN AYAK IZI VE NEGATIF-Z SEHIR UCLARI",22,"#ffdda7",True)
 text(1474,151,"B — 5 ORIJINAL PD KAYDI",25,"#ffe0a7",True)
 y=211
 for i,r in enumerate(rows,1):
  name=r["original_native_PD_name"]
  text(1480,y,str(i)+". "+name,20,"#b4effa",True);y+=36
  text(1500,y,"PD XYZ "+", ".join(f"{v:+.2f}" for v in r["source_native_XYZ"]),17);y+=28
  text(1500,y,"Yakin sehir: "+r["nearest_original_city_mesh"],17,"#fbcba4");y+=28
  text(1500,y,f"3D uzaklik: {r['source_nearest_city_centroid_3d_distance']:.2f} birim",17);y+=66
 d.line((1480,1065,2334,1065),fill="#54758a",width=2)
 text(1484,1084,"UYARI — HARITAYI OYNATMADIK",20,"#ffcf9d",True)
 text(1484,1130,"Bu PD kayitlari kaynak koordinatidir.",17)
 text(1484,1162,"PD = kesin oyuncu konumu DENEMEZ.",17)
 text(1484,1194,"BRES root/dunya matrisi hala bilinmiyor.",17)
 text(1484,1226,"Tum sehri +36 Z KAYDIRMAK KANITSIZ.",17,"#ffa9a6")
 text(40,1320,"Kaynak meshleri ve 5 ayri PD gercek oyun IPA verisinden. Isik, alpha ve kamera oyunun gercek render'i degildir.",15,"#b8cbdc")
 png.parent.mkdir(parents=True,exist_ok=True)
 im.save(png,optimize=True)

def run(ipa,out):
 low=native(ipa)
 meshes,_=source()
 candidates=[]
 for row,p,f in meshes:
  if row["original_scene_group"]=="urban":
   centers=p[f].mean(axis=1)
   candidates.append((row["source_mesh_name"],centers))
 for item in low:
  pos=np.asarray(item["source_native_XYZ"],dtype=np.float32)
  best=None
  for name,tri in candidates:
   delta=tri-pos
   dist=np.sum(delta*delta,axis=1)
   k=int(np.argmin(dist));score=float(dist[k])
   if best is None or score<best[0]:best=(score,name,tri[k].tolist())
  item["nearest_original_city_mesh"]=best[1]
  item["source_nearest_city_centroid_XYZ"]=[round(float(x),6) for x in best[2]]
  item["source_nearest_city_centroid_3d_distance"]=round(float(np.sqrt(best[0])),6)
  item["original_game_path_or_camera_target_function_PROVEN"]=False
 assert max(x["source_nearest_city_centroid_3d_distance"] for x in low)<20.
 assert sum(x["source_nearest_city_centroid_3d_distance"]<10 for x in low)==4
 report={"original_game":"Gameloft Iron Man 2 iOS 2010 C1L1",
  "source_original_low_Z_PositionDummy_count":5,
  "source_low_Z_author_transforms_around_real_source_city_meshes":low,
  "source_negative_2010_PD_near_original_city_within_10_world_coordinate_units":4,
  "source_all_five_PD_near_original_city_within_20_world_coordinate_units":True,
  "source_G44_city_negative_Z_does_not_alone_prove_bad_game_scene_root":True,
  "source_BRES_original_scene_root_world_matrix_resolved":False,
  "source_PD_three_transform_semantics_and_runtime_position_resolved":False,
  "no_original_mesh_moved_and_NO_VPK":True}
 out.mkdir(parents=True,exist_ok=True)
 (out/"G46_original_2010_low_Z_PD_vs_BRES_city.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 with (out/"G46_5_PD_real_negative_Z_city_nearest_mesh.csv").open("w",newline="",encoding="utf-8-sig") as f:
  w=csv.DictWriter(f,fieldnames=[k for k in low[0]]);w.writeheader();w.writerows(low)
 preview(low,out/"G46_ORIGINAL_2010_ALT_SEVIYE_SAHNE_PD_HARITASI_16_9.png")
 print("G46 TRUE ORIGINAL negative-Z PD count",len(low))
 print("G46 raw native nearest original source urban 3D triangle distances",[(r["original_native_PD_name"],r["nearest_original_city_mesh"],r["source_nearest_city_centroid_3d_distance"]) for r in low])
 print("PASS G46 5 source CLARA PD at negative-Z near original native city BRES geometry; NO invented building shift or VPK.")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();run(a.ipa,a.out)
