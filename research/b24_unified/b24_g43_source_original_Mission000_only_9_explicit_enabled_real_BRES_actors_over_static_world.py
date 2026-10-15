#!/usr/bin/env python3
"""G43 source-authored first mission prologue actor geometry scene snapshot.

Uses 2010 original BRES triangles, actual original CLARA 0x005C local
poses, exact original models archive one-based refs, AND G42 native Lua51
original 12 unconditional prebranch Enable/Disable calls to form the nine
EXPLICITLY Enabled actor geometry objects. The other 44 Deco states are NOT
assumed invisible: unknown/not-asserted items are not included in this
MINIMUM-SCRIPT-EVIDENCE actor preview (not the full original runtime scene).
Static 370 original environment BRES triangles are drawn. NOT original
2010 engine frame; shader color and world parent remain unproven.

Creates 2200x1238 PNG and JSON/CSV with actual 2010 source triangles.
"""
from __future__ import annotations
import argparse,collections,contextlib,io,json,math,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from b24_owner_pack_extract import decode as decode_pack
from b24_g37_original_C1L1_Deco_resource_type_scene_instances import audit as deco_audit
from b24_g39_original_C1L1_53_Deco_authentic_meshes_local_placement_map import source_parser,quat_transform
from b24_g42_original_2010_C1L1_Mission000_prebranch_Deco_stage_visibility import inspect as g42
from b24_g13_c1l1_light_dome_mesh_provenance_sheet import source as static_source

PALETTE={"ground":"#789a53","urban":"#8fb4c6","vehicles":"#c39c79","lights":"#8b9cb7"}
def font(n,b=False):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
 except OSError:return ImageFont.load_default()

def render(city,actors,disabled,out):
 W,H=2200,1238
 im=Image.new("RGB",(W,H),"#091827")
 dr=ImageDraw.Draw(im)
 dr.text((36,17),"IRON MAN 2 — C1L1 | ORIGINAL GOREV 000 KAYNAK SAHNESI",font=font(34,True),fill="#f6daa8")
 dr.text((37,73),"2010 BRES poligonlar + 2010 CLARA yerel XYZ/Q/olcek + Lua Mission000_OnStart",font=font(20),fill="#b7cfdd")
 source_panel=(20,119,1450,1191)
 dr.rounded_rectangle(source_panel,radius=13,outline="#4b6d84",fill="#0d2030",width=2)
 right=(1474,119,2181,1191)
 dr.rounded_rectangle(right,radius=13,outline="#4b6d84",fill="#162c3d",width=2)
 minx,maxx,miny,maxy=-390,310,-325,310
 x0,y0=source_panel[0]+35,source_panel[1]+45
 xx=1340/(maxx-minx);yy=965/(maxy-miny);scale=min(xx,yy)
 def mapxy(p):return (round(x0+(p[0]-minx)*scale),round(source_panel[3]-30-(p[1]-miny)*scale))
 for row,pts,faces in city:
  color=PALETTE.get(row["original_scene_group"],"#91abc0")
  for f in faces:
   poly=pts[f]
   if poly[:,0].max()<minx or poly[:,0].min()>maxx or poly[:,1].max()<miny or poly[:,1].min()>maxy:continue
   dr.polygon([mapxy(p) for p in poly],fill=color)
 for actor in actors:
  for points,faces in actor["authentic_source_placed_parts"]:
   for face in faces:
    tri=points[face]
    if tri[:,0].max()<minx or tri[:,0].min()>maxx or tri[:,1].max()<miny or tri[:,1].min()>maxy:continue
    dr.polygon([mapxy(pt) for pt in tri],fill="#ffcd7d" if actor["source_original_node"]=="Deco004" else "#9befbc")
 for actor in actors:
  x,y=mapxy(actor["source_xyz"])
  if x0<x<source_panel[2] and source_panel[1]<y<source_panel[3]:
   dr.ellipse((x-6,y-6,x+6,y+6),fill="#62ffae",outline="#0a1b28",width=2)
   dr.text((x+10,y-10),actor["source_original_node"].replace("Deco_",""),font=font(15,True),fill="#aaf5cb",stroke_width=2,stroke_fill="#0a1b28")
 for actor in disabled:
  x,y=mapxy(actor["source_original_native_XYZ"])
  if x0<x<source_panel[2] and source_panel[1]<y<source_panel[3]:
   dr.line((x-7,y-7,x+7,y+7),fill="#f39494",width=4)
   dr.line((x-7,y+7,x+7,y-7),fill="#f39494",width=4)
   if actor["original_node"] in ("Deco005",):
    dr.text((x+11,y+6),actor["original_node"]+" DISABLE",font=font(16),fill="#f5a5a5",stroke_width=2,stroke_fill="#091827")
 rx=right[0]+30;ry=right[1]+33
 def label(t,n=22,c="#dbeafa",b=False,space=11):
  nonlocal ry
  dr.text((rx,ry),t,font=font(n,b),fill=c)
  ry+=n+space
 label("GOREV 000 — ORIJINAL KANIT",26,"#ffe0a4",True);ry+=14
 label("ILK KOSULLU LUA OP: PC 73",20,"#a9d4e2",True)
 label("PC<73 ENABLE: 9 Deco model",22,"#9debba",True)
 label("PC<73 DISABLE: 3 Deco model",22,"#f4a5ab",True)
 ry+=23
 label("Kaynak geometri:",24,"#f1dbaa",True)
 label("370 sabit kaynak BRES mesh",20)
 label("22.919 sabit ucgen",20)
 label(f"{len(actors)} ilk-komut ENABLE modeli",20)
 label(f"{sum(a['source_original_triangle_count'] for a in actors):,} kaynak actor instance ucgeni",20)
 ry+=30
 label("YALNIZCA KANITLI ALT KATMAN",24,"#f1dbaa",True)
 for line in ["Kirmizi carpi: Disable komutu","Yesil: Enable komutu","Diger 41 Deco: durumu bilinmiyor","Sabit C1L1 sahnesi: Lua'da","gizlenme komutu yok","", "MODELLERE SAHTE OFFSET YOK", "2010 shader/alpha dogrulanmadi", "Dunya parent matrisi bulunmadi", "Gercek oyun ekran goruntusu degil"]:
  if line:label(line,19,"#c9dfec")
  else:ry+=8
 dr.text((38,1202),"Original kaynak verisini zorla yeniden dizmeyen teknik map preview; motorun tum runtime komutlarini calistirmiyor.",font=font(17),fill="#a8bdcc")
 im.save(out,optimize=True)

def main(ipa,out):
 out.mkdir(parents=True,exist_ok=True)
 stage=g42(ipa)
 acts=stage["source_pre_branch_decoded_Deco_actions"]
 enabled=[a for a in acts if a["original_lua_global_call"]=="Enable"]
 disabled=[a for a in acts if a["original_lua_global_call"]=="Disable"]
 assert len(enabled)==9 and len(disabled)==3
 with zipfile.ZipFile(ipa) as z:
  models=z.read("Payload/IronMan2.app/models")
  packed=z.read("Payload/IronMan2.app/clev")
 from b24_owner_pack_extract import get_exact
 level=get_exact(packed,decode_pack(packed,".bclara"),"level1.bclara")
 records=deco_audit(level)["source_decoded_native_Deco_0x4D_resource_fields_and_0x5C_transforms"]
 byname={r["source_Deco_name"]:r for r in records}
 archive=decode_pack(models)
 parse=source_parser()
 actor_rows=[]
 jsonrows=[]
 for a in enabled:
  r=byname[a["original_CLARA_Deco_name"]]
  idnum=r["native_raw_resource_type_uint32"]
  descriptor=archive[idnum-1]
  with contextlib.redirect_stdout(io.StringIO()):
   meshes,metadata=parse(models[descriptor.start:descriptor.end])
  parts=[]
  for mesh in meshes:
   vertices=np.asarray(mesh["positions"],dtype=np.float32)
   faces=np.asarray(mesh["faces"],dtype=np.int32)
   if not len(vertices) or not len(faces):continue
   placed=quat_transform(vertices,r["source_scale_xyz"],r["source_quat_xyzw"],[r["source_X"],r["source_Y"],r["source_Z"]])
   parts.append((placed,faces))
  count=sum(len(faces) for _,faces in parts)
  assert count>0
  actor_rows.append({"source_original_node":r["source_Deco_name"],
   "source_original_model":descriptor.name,"source_original_triangle_count":count,
   "source_xyz":[r["source_X"],r["source_Y"],r["source_Z"]],
   "authentic_source_placed_parts":parts})
  jsonrows.append({"original_node":r["source_Deco_name"],"original_model_file":descriptor.name,
   "source_XYZ":[r["source_X"],r["source_Y"],r["source_Z"]],"source_authentic_transformed_triangles":count,
   "source_2010_enable_native_lua_PC":a["original_source_bytecode_PC"],
   "engine_runtime_visibility_not_fully_proven":True})
 disabledrows=[]
 for a in disabled:
  r=byname[a["original_CLARA_Deco_name"]]
  disabledrows.append({"original_node":r["source_Deco_name"],
    "source_original_native_XYZ":[r["source_X"],r["source_Y"],r["source_Z"]],
    "source_original_lua_disable_PC":a["original_source_bytecode_PC"]})
 static_city,_=static_source()
 image=out/"G43_ILK_GOREV_ORIGINAL_KAYNAK_GEOMETRI_9_ENABLE_3_DISABLE_HARITA.png"
 render(static_city,actor_rows,disabledrows,image)
 report={
   "original_source_true_static_C1L1_BRES_meshes":370,
   "original_source_true_static_C1L1_BRES_triangles":22919,
   "original_stage_Mission000_first_branch_PC":73,
   "original_stage_first_unconditional_explicit_Enable_Deco_count":len(actor_rows),
   "original_stage_first_unconditional_explicit_Disable_Deco_count":len(disabledrows),
   "original_native_genuine_placed_actor_triangles":sum(a["source_original_triangle_count"] for a in actor_rows),
   "source_2010_exact_native_9_enabled_original_model_geometry":jsonrows,
   "source_2010_exact_native_3_disabled_source_instances":disabledrows,
   "stage_preview_other_41_Deco_visibility_default_not_assumed":True,
   "game_original_static_geometry_parent_root_matrix_not_proven":True,
   "actual_original_game_camera_shading_and_cutscene_engine_not_reconstructed":True,
   "no_native_Vita_VPK_or_performance_changes":True}
 assert len(actor_rows)+len(disabledrows)==12
 (out/"G43_2010_LEVEL1_NATIVE_STAGE_9_MODEL_GEOMETRY_PROOF.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G43 authentic original 2010 mission first prologue, actual original 9 source models",[(a["source_original_node"],a["source_original_triangle_count"]) for a in actor_rows])
 print("G43 placed authentic source actor triangles",report["original_native_genuine_placed_actor_triangles"],"plus 370 BRES static original meshes / 22919 faces")
 print("G43 preview",image,"no VPK, no invented parent or source texture")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();main(a.ipa,a.out)
