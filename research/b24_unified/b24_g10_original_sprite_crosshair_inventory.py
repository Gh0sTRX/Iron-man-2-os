#!/usr/bin/env python3
"""Forensic 2010 original sprite archive crosshair/lock reticle indexing.
Does not invent a replacement HUD image or publish private whole archives.
"""
import argparse,collections,json,re,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode

def run(ipa,out):
 with zipfile.ZipFile(ipa) as z:
  sprites=z.read("Payload/IronMan2.app/sprites")
  names=z.namelist()
  extras=[x for x in names if x.rsplit(".",1)[-1].lower()
     in ("bclara","xml","png","spr","ui","gui","pal","atlas")]
 result={"sprite_bytes":len(sprites),"sprite_packed_names_valid":False,
         "decoded_names":[],"crosshair_keyword_candidates":[],
         "sprite_archive_first_64_bytes_hex":sprites[:64].hex(),
         "other_original_IPA_gui_scene_file_candidates":extras[:120],
         "reticle_identity_from_this_evidence_proven":False}
 try:
  entries=decode(sprites)
  result["sprite_packed_names_valid"]=True
  result["sprite_records"]=len(entries)
  result["decoded_names"]=[x.name for x in entries]
 except Exception as exc:
  result["decode_error"]=str(exc)
  strs=set(v.group(0).decode("latin1","replace")
    for v in re.finditer(rb"[ -~]{5,95}",sprites))
  result["embedded_named_ascii"]=[
    s for s in sorted(strs) if any(t in s.casefold()
     for t in ("cross","aim","hud","retic","lock","crosshair","target","mark"))][:140]
 if result["sprite_packed_names_valid"]:
  result["crosshair_keyword_candidates"]=[
    x for x in result["decoded_names"]
    if any(t in x.casefold() for t in
       ("cross","retic","lock","hud","aim","target","marker","cursor","sight"))]
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2)+"\n")
 print("ORIGINAL_IPA_2010_SPRITES_META",len(sprites),result["sprite_packed_names_valid"])
 print("ORIGINAL_2010_SPRITES_SOURCE_TARGET_NAMES",result["crosshair_keyword_candidates"][:100])
 print("ORIGINAL_2010_SPRITES_NAMES_SAMPLE",result["decoded_names"][:85])
 print("ORIGINAL_2010_SPRITES_EMBEDDED_ASCII",result.get("embedded_named_ascii",[])[:80])
 print("ORIGINAL_2010_RELATED_UI_FILES",extras[:90])
 print("PASS authentic original iOS sprites indexing attempt — reticle binding still unproven")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args();run(a.ipa,a.out)
