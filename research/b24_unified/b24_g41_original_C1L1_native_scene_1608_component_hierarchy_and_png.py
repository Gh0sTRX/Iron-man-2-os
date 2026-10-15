#!/usr/bin/env python3
"""G41 original 2010 source-scene hierarchy, NOT guessed actor world matrices.

- Native Gameloft CLARA 1608 typed child→named-owner components (494 owners)
- Among them 685 tag 0x005c prefixes, 663 strictly valid XYZ/Q/scale
- 137 PositionDummy instances contain exactly THREE native transforms
- 53 native classed Deco have authentic 1-based models archive index and pose
- 57 CameraPreset have 51 source PositionDummy references, 6 null targets
- The native 1608 component IDs are NOT a graph of named actor parents.
No gameplay, no VPK. Produce source-authentic PNG using ORIGINAL BRES G39
geometry preview and G40 genuine decoded PVR image contact sheet.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,json,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from b24_owner_pack_extract import decode as owner_decode,get_exact
from b24_g24_original_clara_source_601_nodes_663_parent_links import audit as native_graph,native_names
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
from b24_g37_original_C1L1_Deco_resource_type_scene_instances import audit as native_deco,FAMILY
from b24_g29_original_CameraPreset_PD_CameraConfig_source_map import decode as native_cam
from b24_g39_original_C1L1_53_Deco_authentic_meshes_local_placement_map import main as source_map
from b24_g40_source_2010_first_level_Deco_authentic_BRES_PVR_shader_material_atlas_audit import analyze as source_pvr

def csvfile(path,items):
 with path.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)

def output_picture(map_png,atlas_png,report,png):
 W,H=2400,1350
 image=Image.new("RGB",(W,H),"#091728")
 d=ImageDraw.Draw(image)
 fonts=("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
 font=lambda sz,strong=False:ImageFont.truetype(fonts[bool(strong)],sz)
 def line(pos,text,size=23,color="#ddebf6",strong=False):
  d.text(pos,text,font=font(size,strong),fill=color)
 def frame(bounds):
  d.rounded_rectangle(bounds,radius=19,fill="#14293c",outline="#52718a",width=2)
 line((44,20),"IRON MAN 2 | LEVEL 1 | G41 GERCEK KAYNAK HARITA",41,"#ffe2ac",True)
 line((44,79),"2010 BRES / CLARA: gercek kaynak nesne ve alt bilesen baglantilari; final oyun kamerası degil",19,"#b9d1e4")
 frame((19,126,1253,1303));frame((1276,126,2377,636));frame((1276,655,2377,1303))
 # Original 2010 BRES polygons and 41 source-transformed authentic models:
 with Image.open(map_png) as src:
  inner=src.convert("RGB").crop((0,0,1175,1190)).resize((1194,1114),Image.Resampling.LANCZOS)
 image.paste(inner,(38,163))
 d=ImageDraw.Draw(image)
 d.rectangle((38,163,1000,212),fill="#10263a")
 line((59,173),"A — 370 BRES + 41 orijinal yerel model pozisyonu",25,"#ffe0a6",True)
 line((1307,145),"B — 25 gercek PVR doku atlasi",26,"#a0e8f0",True)
 with Image.open(atlas_png) as src:
  tex=src.convert("RGB");tex.thumbnail((1035,409),Image.Resampling.LANCZOS)
 image.paste(tex,(1307+(1035-tex.width)//2,190))
 d=ImageDraw.Draw(image)
 line((1307,675),"C — ORIJINAL SAHNE / KAYNAK HIYERARSISI",27,"#9bdde6",True)
 stats=[
  ("587", "dogrulanmis sinifli nesne"),
  ("1.608", "tipli parent → alt bilesen kenari"),
  ("663", "gercek XYZ + quaternion + scale"),
  ("53", "kaynak .bdae bagli Deco"),
  ("41", "yerel pozda cizilen gercek modeller"),
  ("57 / 51", "CameraPreset / PD kaynak baglantisi")
 ]
 y=727
 for num,desc in stats:
  line((1308,y),num,24,"#ffdfa9",True)
  line((1518,y+2),desc,21,"#d0e3ef")
  y+=52
 d.line((1305,1058,2341,1058),fill="#405b70",width=2)
 line((1308,1082),"Deco_fence1 → 0x004D #44 → models[43]",19,"#b7efda",True)
 line((1308,1115),"C2L1_fense.bdae + 0x005C yerel S/Q/T",19,"#dbe9f4")
 line((1308,1162),"NOT: 1.608 bilesen baginin hicbiri",19,"#ffcc9b")
 line((1308,1194),"baska isimli nesnenin ID'si degil.",19,"#ffcc9b")
 line((1308,1243),"Parent WORLD matrisi halen dogrulanmadi.",17,"#ffb8a4",True)
 line((44,1320),"Gercek 2010 oyun ekrani / shader degil. Kaynak pozlar ve orijinal 2010 BRES model ucgenleri. Yeni VPK yok.",15,"#b4cbd8")
 image.save(png,optimize=True)

def analyze(raw,modelpack,g39_json,g40_json,report_dir):
 report_dir.mkdir(parents=True,exist_ok=True)
 native=native_graph(raw)
 classes=summarize(raw)
 decoa=native_deco(raw)
 cameras=native_cam(raw)
 entry=owner_decode(modelpack)
 rows=classes["source_2010_typed_class_instances"]
 typed_byid={x["original_numeric_name_id"]:x for x in rows}
 assert len(typed_byid)==587
 names=native_names(raw)
 distinct_named_IDs={x["original_numeric_name_id"] for x in names}
 assert len(names)==601 and len(distinct_named_IDs)==594
 edges=native["original_source_static_parent_record_links"]
 transform=native["all_663_source_rigid_transforms_with_native_parent_child_name_ID_chain"]
 assert len(edges)==1608 and len(transform)==663
 assert len({x["original_child_id"] for x in edges})==1608
 assert len({x["original_parent_id"] for x in edges})==494
 assert not ({x["original_child_id"] for x in edges}&distinct_named_IDs)
 assert len({x["original_child_node_ID"] for x in transform})==663
 tags=collections.Counter(x["source_typed_record_field"] for x in edges)
 assert tags[92]==685
 # 22 extra tag 0x005c records do not carry fully validated rigid xyz/q/scale.
 assert tags[92]-len(transform)==22
 byparent=collections.defaultdict(list)
 for x in transform:byparent[x["original_named_parent_source_ID"]].append(x)
 pd_nodes=[x for x in rows if x["original_class_name"]=="PositionDummy"]
 assert len(pd_nodes)==137
 assert all(len(byparent[x["original_numeric_name_id"]])==3 for x in pd_nodes)
 modelrows=[]
 for x in decoa["source_decoded_native_Deco_0x4D_resource_fields_and_0x5C_transforms"]:
  key=x["native_raw_resource_type_uint32"]-1
  assert 0<=key<len(entry)
  res=entry[key]
  family=FAMILY.get(x["native_raw_resource_type_uint32"])
  if family and res.name.removesuffix(".bdae").casefold()!=family.casefold():
   raise ValueError("native CLARA source-model family original order changed")
  n=typed_byid[x["original_source_entity_ID"]]
  assert n["original_class_name"]=="Deco"
  links=byparent[n["original_numeric_name_id"]]
  assert len(links)==1 and links[0]["original_child_node_ID"]==n["original_numeric_name_id"]+3
  assert max(abs(a-b) for a,b in zip(links[0]["native_vec3_position"],[x["source_X"],x["source_Y"],x["source_Z"]]))<1e-6
  modelrows.append({"original_classed_node":x["source_Deco_name"],
      "source_entity_ID":x["original_source_entity_ID"],
      "native_resource_one_based_index":x["native_raw_resource_type_uint32"],
      "original_pack_model_index_zero_based":key,"actual_original_2010_model_filename":res.name,
      "native_type_0x005C_transform_component_ID":links[0]["original_child_node_ID"],
      "source_local_XYZ":links[0]["native_vec3_position"],
      "source_local_quaternion_xyzw":links[0]["native_quaternion_xyzw"],
      "source_local_scale_xyz":links[0]["native_vec3_scale"],
      "actual_runtime_world_matrix_recovered":False})
 assert len(modelrows)==53
 camrows=[]
 for c in cameras["source_original_CameraPreset_to_PositionDummy_and_CameraConfig_links"]:
  target=c["source_native_camera_target_id"]
  is_null=c["source_target_has_explicit_NULL_sentinel"]
  if not is_null:
   assert target in typed_byid and typed_byid[target]["original_class_name"]=="PositionDummy"
  camrows.append({"native_CameraPreset":c["source_CameraPreset_name"],
     "source_camera_entity_ID":c["source_camera_entity_ID"],
     "native_camera_PD_source_ID":target if not is_null else None,
     "source_PD_name":c["source_verified_target_PositionDummy_name"],
     "native_CameraConfig_ID":c["source_native_config_reference"],
     "has_original_PD_reference":not is_null,
     "real_game_camera_view_matrix_recovered":False})
 assert len(camrows)==57 and sum(x["has_original_PD_reference"] for x in camrows)==51
 # All available BRES and PVR images are separately treated as source evidence.
 assert g39_json["native_placed_nonorigin_Deco_model_geometry_count"]==41
 assert g39_json["native_placed_nonorigin_Deco_original_triangles"]==10379
 assert g40_json["source_owner_PVR_diffuse_png_decoded_count"]==25
 doc={"source_2010_owner_sha256":hashlib.sha256(raw).hexdigest(),
   "source_actual_named_classed_scene_nodes":587,
   "source_name_record_candidates":len(names),
   "source_name_candidate_distinct_IDs":len(distinct_named_IDs),
   "source_original_native_typed_child_component_edges":1608,
   "original_parent_named_node_IDs_owning_any_component":494,
   "source_original_0x005C_component_prefixes":685,
   "source_original_verified_0x005C_XYZ_quaternion_scale":663,
   "native_0x005C_other_records_with_unproven_rigid_pose":22,
   "native_component_child_IDs_are_unique_and_do_not_overlap_named_scene_actors":True,
   "source_classed_PositionDummy_three_native_transforms":len(pd_nodes),
   "source_original_CameraPreset_count":len(camrows),
   "source_camera_to_PD_exact_native_references":sum(x["has_original_PD_reference"] for x in camrows),
   "source_camera_explicit_NULL_refs":sum(not x["has_original_PD_reference"] for x in camrows),
   "original_C1L1_Deco_model_archive_index_links":len(modelrows),
   "original_2010_Deco_source_locally_transformed_mesh_instances":41,
   "original_source_Deco_local_instance_model_triangles":10379,
   "original_first_level_source_static_BRES_geometry_meshes":370,
   "original_first_level_source_static_BRES_geometry_triangles":22919,
   "source_authentic_2010_PVR_atlases_identified_in_active_Deco_materials":25,
   "source_typed_component_tag_histogram":{hex(k):v for k,v in sorted(tags.items())},
   "source_original_native_parent_world_matrices_NOT_PROVEN":True,
   "source_original_runtime_cutscene_visibility_NOT_PROVEN":True,
   "source_original_2010_renderer_shader_alpha_NOT_PROVEN":True,
   "source_no_performance_or_VPK_changes":True}
 report_dir.joinpath("G41_original_2010_component_hierarchy.json").write_text(
    json.dumps(doc,indent=2,ensure_ascii=False)+"\n")
 csvfile(report_dir/"G41_1608_original_typed_component_owners.csv",[
  {"source_tag_u16":e["source_typed_record_field"],
   "source_child_node_ID":e["original_child_id"],
   "source_component_owner_named_ID":e["original_parent_id"],
   "source_binary_offset":e["native_child_record_prefix_offset"]}
   for e in edges])
 csvfile(report_dir/"G41_663_authentic_rigid_XYZ_Q_S_parent_links.csv",transform)
 csvfile(report_dir/"G41_53_exact_Deco_BRES_models_and_poses.csv",modelrows)
 csvfile(report_dir/"G41_57_camera_PD_source_refs.csv",camrows)
 return doc

def main(args):
 with zipfile.ZipFile(args.ipa) as z:
  clev=z.read("Payload/IronMan2.app/clev")
  modelpack=z.read("Payload/IronMan2.app/models")
  raw=get_exact(clev,owner_decode(clev,".bclara"),"level1.bclara")
 args.out.mkdir(parents=True,exist_ok=True)
 g39path=args.out/"G41_g39_model_placement_structured.json"
 g39png=args.out/"G41_g39_original_geometry.png"
 source_map(args.ipa,g39path,g39png)
 g40path=args.out/"G41_g40_native_pvr_report.json"
 g40png=args.out/"G41_g40_original_PVR_contact.png"
 source_pvr(args.ipa,g40path,g40png)
 result=analyze(raw,modelpack,json.loads(g39path.read_text()),json.loads(g40path.read_text()),args.out)
 png=args.out/"G41_2010_C1L1_REAL_SOURCE_HIERARCHY_MAP_PREVIEW.png"
 output_picture(g39png,g40png,result,png)
 print("G41 PASS source original 2010 classed 587, 1608 typed components, 663 exact rigid components, 137 3-point PD and 53 Deco model source.")
 print("G41 PASS native component child IDs do not overlap any original named source node ID: NO inferred actor-world parent transformations.")
 print("G41 Native original map PNG",png,"original scene triangles / local actor instances: 22919 / 41; NO VPK.")

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 main(p.parse_args())
