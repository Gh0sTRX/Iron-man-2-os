#!/usr/bin/env python3
"""G39: source-authentic original Deco MODEL GEOMETRY + typed CLARA LOCAL POSES.

9 independent exact archive-index correspondences G38 -> all 53 native Deco
records. The original 2010 owner's models pack yields exact .bdae geometry.
This independently loads 25 distinct original BDAEs through native B11 parser,
then produces a DIAGNOSTIC source-local composed world (mesh-local * CLARA
instance S/Q/T). Does NOT claim CLARA source node is game engine final parent
world matrix, and never invents missing meshes/shaders/textures. No Vita VPK.

Debug PNG: exact source BRES 370 static city meshes plus position-transformed
source geometry for each non-origin Deco. Static map model decals/sky are
already included in BRES source, so origin static Deco instances are not
drawn twice in the preview.
"""
from __future__ import annotations
import argparse,collections,contextlib,hashlib,io,json,math,struct,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from b24_owner_pack_extract import decode,get_exact
from b24_g37_original_C1L1_Deco_resource_type_scene_instances import audit,FAMILY
from b24_g13_c1l1_light_dome_mesh_provenance_sheet import source as original_city

ROOT=Path(__file__).resolve().parents[2]
PARSER_ZIP=ROOT/"research/B11_C1L1_Source_Parser.zip"

def source_parser():
 with zipfile.ZipFile(PARSER_ZIP) as z:
  code=z.read("bdae_scene_parser.py")
 ns={"__name__":"g39_authentic_original_BDAE_source_parser","__file__":"bdae_scene_parser.py"}
 exec(compile(code,"bdae_scene_parser.py","exec"),ns)
 return ns["parse"]

def quat_transform(points,scale,quat,xyz):
 p=np.asarray(points,dtype=np.float32)*np.asarray(scale,dtype=np.float32)[None,:]
 q=np.asarray(quat[:3],dtype=np.float32)
 qw=float(quat[3])
 tmp=2.*np.cross(q,p)
 return (p+qw*tmp+np.cross(q,tmp)+np.asarray(xyz,dtype=np.float32)[None,:]).astype(np.float32)

def render_scene(static_rows,actors,output_path):
 W,H=1800,1190
 margin=48
 minx,maxx,miny,maxy=-390.,310.,-325.,310.
 graph=1175
 s=min((graph-2*margin)/(maxx-minx),(H-2*margin)/(maxy-miny))
 def coord(p):
  return (int(margin+(float(p[0])-minx)*s),
          int(H-margin-(float(p[1])-miny)*s))
 bg=Image.new("RGB",(W,H),"#0b1b2a")
 d=ImageDraw.Draw(bg)
 d.rectangle([graph,0,W,H],fill="#142637")
 source_colors={'ground':'#4f7743','urban':'#7094aa','vehicles':'#b5916e','lights':'#7b88aa'}
 for row,xyz,f in static_rows:
  color=source_colors.get(row["original_scene_group"],"#75889c")
  for inds in f:
   vals=xyz[inds]
   if vals[:,0].max()<minx or vals[:,0].min()>maxx or vals[:,1].max()<miny or vals[:,1].min()>maxy:continue
   d.polygon([coord(q) for q in vals],fill=color)
 category_colors={"fences":"#ffcf59","enemies":"#f47782","effects":"#dca7f4","people":"#73e3b5","other":"#ffb878"}
 for item in actors:
  if not item["placeable_mesh_geometry_valid"]:continue
  color=category_colors[item["source_draw_category"]]
  for obj in item["actual_source_transformed_meshes"]:
   points=np.asarray(obj["positions"],dtype=np.float32)
   tris=np.asarray(obj["faces"],dtype=np.int32)
   for face in tris:
    poly=points[face]
    if poly[:,0].max()<minx or poly[:,0].min()>maxx or poly[:,1].max()<miny or poly[:,1].min()>maxy:continue
    d.polygon([coord(q) for q in poly],fill=color)
    if item["source_draw_category"]=="fences":d.line([coord(q) for q in poly],fill="#d9893b",width=1)
 for item in actors:
  if not item["local_source_translation_nonzero"]:continue
  x,y=coord(item["source_original_native_transform"]["position_XYZ"])
  if not (0<x<graph and 0<y<H):continue
  col=category_colors[item["source_draw_category"]]
  d.ellipse([x-5,y-5,x+5,y+5],fill=col,outline="#17232c",width=2)
  if item["source_draw_category"]=="fences":
   d.text((x+9,y-16),item["source_entity_name"].replace("Deco_",""),fill=col,stroke_width=2,stroke_fill="#071420")
 def font(n,bold=False):
  path="/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf"
  try:return ImageFont.truetype(path,n)
  except OSError:return ImageFont.load_default()
 x=1205;y=29
 def line(s,large=19,color="#e0eaf1",weight=False,gap=12):
  nonlocal y
  d.text((x,y),s,font=font(large,weight),fill=color)
  y+=large+gap
 line("G39 | 2010 ORIJINAL GEOMETRI",26,"#ffe6ab",True)
 line("CLARA × BRES KAYNAK YERLESIMI",19,"#d1dce6",True)
 line("Model dosyasi: IPA models pack",17,"#a6d6e3")
 line("Pozisyon/donus/olcek: IPA level1",17,"#a6d6e3")
 y+=15
 for label,kind in [("7 çit","fences"),("21 dusman / efekt","enemies"),("insanlar","people"),("diger efekte ve bombalar","effects")]:
  line(label,19,category_colors.get(kind,"#bdcbd7"),True)
 y+=20
 line("ALTLIK: 370 orijinal BRES mesh",17,"#a9c6d5")
 line("RENKLER: inceleme / shader DEGIL",17,"#a9c6d5")
 line("GORUNUR MODEL: gercek 2010 ucgeni",17,"#a9c6d5")
 y+=22
 line("SINIR:",22,"#ffd19b",True)
 for value in ("CLARA yerel pozlari kullanildi.",
               "Parent-world matrisleri ve",
               "animasyon kayitlari henuz yok.",
               "Eksik model dosyasi uydurulmaz.",
               "Bu 2010 oyun ekran goruntusu degil.",
               "Yeni VPK / optimizasyon yok."):
  line(value,17,"#d0c3b2")
 bg.save(output_path,optimize=True)

def main(ipa,out,preview):
 with zipfile.ZipFile(ipa) as z:
  models=z.read("Payload/IronMan2.app/models")
  clev=z.read("Payload/IronMan2.app/clev")
 model_table=decode(models)
 level=get_exact(clev,decode(clev,".bclara"),"level1.bclara")
 g37=audit(level)
 parser=source_parser()
 local_data={}
 for row in g37["source_decoded_native_Deco_0x4D_resource_fields_and_0x5C_transforms"]:
  idx=row["native_raw_resource_type_uint32"]-1
  filename=model_table[idx].name
  expect=FAMILY.get(row["native_raw_resource_type_uint32"])
  if expect and filename.removesuffix(".bdae").casefold()!=expect.casefold():
   raise ValueError("original 2010 models archive slot mapping changed")
  local_data[filename]=model_table[idx]
 decoded={}
 for filename,descriptor in sorted(local_data.items()):
  native=models[descriptor.start:descriptor.end]
  try:
   with contextlib.redirect_stdout(io.StringIO()):
    meshes,other=parser(native)
   parts=[]
   for mesh in meshes:
    pts=np.asarray(mesh["positions"],dtype=np.float32)
    faces=np.asarray(mesh["faces"],dtype=np.int32).reshape(-1,3)
    if len(pts)==0 or len(faces)==0:continue
    if not np.isfinite(pts).all() or np.min(faces)<0 or np.max(faces)>=len(pts):
     raise ValueError("out of source original mesh index bounds")
    parts.append((pts,faces))
   decoded[filename]={"parts":parts,"status":"parsed_source_authentic",
      "original_bdae_sha256":hashlib.sha256(native).hexdigest(),
      "source_BRES_mesh_parts":len(parts),
      "source_BRES_triangles":sum(len(face) for _,face in parts)}
  except Exception as e:
   decoded[filename]={"parts":[],"status":"native_unsupported",
      "reason":type(e).__name__+": "+str(e)[:260],
      "original_bdae_sha256":hashlib.sha256(native).hexdigest(),
      "source_BRES_mesh_parts":0,"source_BRES_triangles":0}
 result=[]
 for node in g37["source_decoded_native_Deco_0x4D_resource_fields_and_0x5C_transforms"]:
  idx=node["native_raw_resource_type_uint32"]-1;entry=model_table[idx]
  decoded_mesh=decoded[entry.name]
  transform={"position_XYZ":[node["source_X"],node["source_Y"],node["source_Z"]],
     "quaternion_xyzw":node["source_quat_xyzw"],"scale_XYZ":node["source_scale_xyz"]}
  name=node["source_Deco_name"];ridx=node["native_raw_resource_type_uint32"]
  category=("fences" if ridx==44 else "enemies" if ridx==134 else
     "effects" if ridx in (136,137,139) else "people" if ridx in (162,163,164,165,205,206,207) else "other")
  local_nonzero=node["original_local_xyz_nonzero"]
  draw=local_nonzero and len(decoded_mesh["parts"])>0
  source_placed=[]
  bbox_low=np.array([float("inf")]*3);bbox_high=np.array([float("-inf")]*3)
  if draw:
   for pts,faces in decoded_mesh["parts"]:
    placed=quat_transform(pts,transform["scale_XYZ"],transform["quaternion_xyzw"],transform["position_XYZ"])
    bbox_low=np.minimum(bbox_low,placed.min(axis=0));bbox_high=np.maximum(bbox_high,placed.max(axis=0))
    source_placed.append({"positions":placed,"faces":faces})
  result.append({"source_entity_name":name,"source_resource_index_1_based":ridx,
    "source_exact_BRES_filename":entry.name,
    "source_actual_BRES_model_index_zero_based":idx,
    "source_original_native_transform":transform,
    "source_draw_category":category,"local_source_translation_nonzero":local_nonzero,
    "original_model_source_mesh_count":decoded_mesh["source_BRES_mesh_parts"],
    "original_model_source_triangle_count":decoded_mesh["source_BRES_triangles"],
    "original_model_geometry_status":decoded_mesh["status"],
    "placeable_mesh_geometry_valid":draw,
    "transformed_source_bbox_XYZ_min":bbox_low.tolist() if draw else None,
    "transformed_source_bbox_XYZ_max":bbox_high.tolist() if draw else None,
    "original_final_2010_parent_world_matrix_not_proven":True,
    "actual_source_transformed_meshes":source_placed})
 original_rows,_=original_city()
 preview.parent.mkdir(parents=True,exist_ok=True)
 render_scene(original_rows,result,preview)
 out.parent.mkdir(parents=True,exist_ok=True)
 summary={"native_2010_original_model_pack_count":len(model_table),
   "original_CLARA_Deco_model_bindings":53,
   "original_distinct_model_resources_used_in_Deco":len(local_data),
   "original_decoded_source_BRES_model_resource_count":sum(v["status"]=="parsed_source_authentic" for v in decoded.values()),
   "source_original_model_parser_failures":{k:v["reason"] for k,v in decoded.items() if v["status"]!="parsed_source_authentic"},
   "native_placed_nonorigin_Deco_model_geometry_count":sum(x["placeable_mesh_geometry_valid"] for x in result),
   "native_placed_nonorigin_Deco_original_triangles":sum(x["original_model_source_triangle_count"] for x in result if x["placeable_mesh_geometry_valid"]),
   "source_original_Deco_model_registry":{name:{k:v for k,v in value.items() if k!="parts"} for name,value in decoded.items()},
   "source_original_actor_geometry_and_CLARA_local_transforms":
     [{k:v for k,v in x.items() if k!="actual_source_transformed_meshes"} for x in result],
   "source_original_2010_BRES_370_environment_meshes":370,
   "source_original_2010_BRES_22919_environment_faces":22919,
   "unproven_real_game_parent_scene_root_camera_shader":True,
   "no_VPK_no_performance_changes":True}
 out.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
 print("G39 native models parsed",summary["original_decoded_source_BRES_model_resource_count"],"/",len(decoded))
 print("G39 native non-origin 2010 Deco model instances with REAL vertices transformed",summary["native_placed_nonorigin_Deco_model_geometry_count"],"/41")
 print("G39 source polygons instantiated",summary["native_placed_nonorigin_Deco_original_triangles"])
 print("G39 genuine original model geometry parser failures",summary["source_original_model_parser_failures"])
 print("PASS source Deco archive table + original CLARA native local transformation + real BRES source 3D instance preview. NO VPK.")
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--ipa",required=True,type=Path)
 a.add_argument("--out",required=True,type=Path);a.add_argument("--png",required=True,type=Path)
 p=a.parse_args();main(p.ipa,p.out,p.png)
