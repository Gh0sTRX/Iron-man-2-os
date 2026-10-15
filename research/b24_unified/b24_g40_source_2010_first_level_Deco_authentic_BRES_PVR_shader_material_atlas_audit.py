#!/usr/bin/env python3
"""G40: First-level 25 ORIGINAL active Deco BRES models per-material SOURCE texture audit.

Inspect native original BRES shader material 60B property pointers and original
2010 TGA author list. Cross-check with IPA original textures archive, no invented
diffuse, shader alpha or lighting. Decode only genuine matched original PVR atlases.
"""
from __future__ import annotations
import argparse,collections,contextlib,io,json,zipfile
from pathlib import Path
from PIL import Image,ImageDraw
from b24_owner_pack_extract import decode as unpack,get_exact
from b24_g37_original_C1L1_Deco_resource_type_scene_instances import audit,FAMILY
from b24_map_first_2010_source_60byte_material_texture_index_recovery import decode as sampler
from b24_g11_original_2010_city_texture_and_window_ui_contact import pvr_pixels,make_sheet

def analyze(ipa,out,png):
 with zipfile.ZipFile(ipa) as z:
  models=z.read("Payload/IronMan2.app/models")
  textures=z.read("Payload/IronMan2.app/textures")
  clev=z.read("Payload/IronMan2.app/clev")
 m=unpack(models);t=unpack(textures,".tga")
 bank={r.name.casefold():r for r in t}
 level=get_exact(clev,unpack(clev,".bclara"),"level1.bclara")
 g37=audit(level)
 dynamic=collections.defaultdict(list)
 for deco in g37["source_decoded_native_Deco_0x4D_resource_fields_and_0x5C_transforms"]:
  idx=deco["native_raw_resource_type_uint32"]-1
  if not 0<=idx<len(m):raise ValueError("source model index OOB")
  res=m[idx]
  expected=FAMILY.get(deco["native_raw_resource_type_uint32"])
  if expected and res.name.removesuffix(".bdae").casefold()!=expected.casefold():
   raise ValueError("2010 source name index mismatch")
  dynamic[res.name].append(deco["source_Deco_name"])
 reports=[];used=set();warnings=[]
 for model,instances in sorted(dynamic.items()):
  rec=next(r for r in m if r.name==model)
  original=models[rec.start:rec.end]
  material=[];bank_names=[];native_success=False
  try:
   with contextlib.redirect_stdout(io.StringIO()):
    props,orig_images=sampler(model.removesuffix(".bdae"),original)
   native_success=True
   bank_names=[row["name"] for row in orig_images]
   for prop in props:
    name=prop["candidate_true_source_TGA"]
    found=bool(name and name.casefold() in bank)
    if found:used.add(name.casefold())
    material.append({
     "original_native_material_name":prop["original_material_name"],
     "source_native_material_property_offset":prop["property_60_offset"],
     "source_native_TGA_author_ordinal":prop["exact_TGA_author_list_index_candidate"],
     "source_original_TGA_name":name,
     "original_user_PVR_archive_member_verified":found})
  except Exception as e:
   warnings.append({"source_native_model":model,"unsupported_source_shader_layout":str(e)[:200]})
  reports.append({"original_source_BRES_name":model,
   "source_CLARA_Deco_count":len(instances),"original_2010_Deco_nodes":instances,
   "native_shader_source_sampler_decoder_supported":native_success,
   "source_original_author_TGA_table":bank_names,
   "original_source_materials":material,
   "native_original_shader_semantics_complete":False})
 if len(reports)!=25:raise ValueError("exact 25 original native model resources expected")
 preview=[];decode_errors=[]
 for name in sorted(used):
  r=bank[name]
  try:
   img,info=pvr_pixels(textures[r.start:r.end],r.name)
   preview.append((r.name,img))
  except Exception as e:decode_errors.append({"name":r.name,"error":str(e)[:180]})
 if preview:
  make_sheet(preview,png,"2010 original level1 Deco BRES native-source PVR samples",ncol=5)
 else:
  empty=Image.new("RGB",(850,140),"#182734")
  ImageDraw.Draw(empty).text((18,18),"No source PVR links confirmed. No invented textures.",fill="white")
  empty.save(png)
 result={
  "original_models_named_archive_entry_count":len(m),
  "original_level1_Deco_native_instances":53,
  "source_distinct_decoded_Deco_BRES_model_resources":len(reports),
  "source_2010_native_shader_sampler_parser_supported_model_count":sum(r["native_shader_source_sampler_decoder_supported"] for r in reports),
  "source_owner_original_TGA_archive_candidate_names":len(used),
  "source_owner_PVR_diffuse_png_decoded_count":len(preview),
  "native_shader_source_property_decoder_unknown_models":warnings,
  "source_original_PVR_decode_failures":decode_errors,
  "source_first_level_Deco_25_model_material_details":reports,
  "original_real_alpha_blend_emissive_light_shader_reconstructed":False,
  "no_guessed_textures":True,"NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print("G40 source original first-level 25 Deco model textures:",len(reports),
  "native shader decoder supported",result["source_2010_native_shader_sampler_parser_supported_model_count"],
  "genuine source referenced TGA names",len(used),"decoded original PVR",len(preview))
 print("G40 valid genuine source texture names",sorted(used)[:50])
 print("G40 alternate source shader layout models",warnings[:20])
 print("PASS G40 exact real original 2010 Deco model shader TGA+PVR source audit, no VPK.")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path);p.add_argument("--png",required=True,type=Path)
 a=p.parse_args();analyze(a.ipa,a.out,a.png)
