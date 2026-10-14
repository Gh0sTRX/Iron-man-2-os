#!/usr/bin/env python3
"""Owner 2010 C1L1 BDAE model material name->texture pointer and HUD archives.

Strictly forensic: real original bytes and original texture dimensions/names;
no speculative road/building atlas bindings. No raw IPA uploaded.
"""
import argparse,collections,json,re,struct,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact
from recover_c1l1_original_uv import SOURCES
def main(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  file_names=z.namelist()
  packed_models=z.read("Payload/IronMan2.app/models")
  packed_tex=z.read("Payload/IronMan2.app/textures")
 mr=decode(packed_models,".bdae")
 tr=decode(packed_tex,".tga")
 original_names=[x.name for x in tr]
 image_dimensions={}
 for r in tr:
  if r.name.casefold().startswith("c1l1_") or r.name.casefold().startswith("c1l1"):
   raw=packed_tex[r.start:r.end]
   if len(raw)>=52:
    h,w1,w2=struct.unpack_from("<III",raw)
    image_dimensions[r.name]={"file_bytes":len(raw),"pvr_header":h,
                                 "height":w1,"width":w2,
                                 "pixel_payload_bytes":len(raw)-52}
 model_ref_report={}
 for name in SOURCES:
  raw=get_exact(packed_models,mr,name+".bdae")
  texture_ref_strings=sorted(set(
   m.group(0).decode("latin1") for m in re.finditer(
     rb"[a-zA-Z0-9_./\\-]{3,110}\.tga",raw,re.I)))
  ascii_mat_samples=[m.group(0).decode("ascii","ignore") for m in
      re.finditer(rb"[a-zA-Z][a-zA-Z0-9_]{5,45}",raw)
      if any(t in m.group(0).lower() for t in (b"standard",b"material",b"c1l1",b"diffuse",b"tex"))]
  model_ref_report[name]={
      "genuine_source_BDAE_file_bytes":len(raw),
      "embedded_literal_TGA_names":texture_ref_strings,
      "embedded_source_material_keyword_samples":sorted(set(ascii_mat_samples))[:30],
      "model_contains_exact_source_TGA_ref":len(texture_ref_strings)>0,
  }
 members=[n for n in file_names if any(t in n.casefold() for t in
           ("scen","hud","ui","sprite","bclara","gui","atlas","common","resource"))]
 ui_names=[n for n in original_names if n.casefold().startswith(("ui","hud","gui","button","weap","main","icon","radar","aim","mark","sprite","cross","target","lock","shot","ret"))]
 outcome={
   "original_C1L1_PVR_texture_dimensions":image_dimensions,
   "BDAE_original_direct_embedded_texture_pointer_forensics":model_ref_report,
   "IPA_other_potential_scene_HUD_archive_filenames":members[:200],
   "original_UI_glyph_texture_name_candidates":ui_names,
   "source_warning":"A model string and name alone cannot prove actual material to texture sampler binding."
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(outcome,indent=2)+"\n")
 print("C1L1_ORIGINAL_TEXTURE_DIMENSIONS",image_dimensions)
 print("C1L1_BDAE_ORIGINAL_EMBEDDED_TEXTURE_POINTERS",{k:v["embedded_literal_TGA_names"] for k,v in model_ref_report.items()})
 print("C1L1_BDAE_ORIGINAL_MODEL_MATERIAL_NAMES",{k:v["embedded_source_material_keyword_samples"] for k,v in model_ref_report.items()})
 print("2010_HUD_UI_ARCHIVE_MEMBER_CANDIDATES",members[:100])
 print("2010_ORIGINAL_UI_TEXTURE_NAME_CANDIDATES",ui_names)
 print("PASS original scene/material and crosshair source byte/name investigation NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();main(a.ipa,a.out)
