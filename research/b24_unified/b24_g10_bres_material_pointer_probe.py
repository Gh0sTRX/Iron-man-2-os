#!/usr/bin/env python3
"""Reverse engineer 2010 BRES material (per-face) -> original exact TGA pointer.

Original .bdae contains file-qualified submesh material labels and TGA strings.
DO NOT promote mere occurrence/name similarity to verified texture binding.
"""
from __future__ import annotations
import argparse,collections,json,re,struct,zipfile
from pathlib import Path
from recover_c1l1_original_uv import BDAEZIP,SOURCES

def inspect():
 with zipfile.ZipFile(BDAEZIP) as z:
  src=z.read("bdae_scene_parser.py").decode()
  parser={"__name__":"authored_2010_materials","__file__":"bdae_scene_parser.py"}
  exec(compile(src,"bdae_scene_parser.py","exec"),parser)
  samples=[]
  for name in SOURCES:
   raw=z.read("original_models/"+name+".bdae")
   meshes,stats=parser["parse"](raw)
   mats=collections.Counter()
   bymaterial={}
   for mesh in meshes:
    sd=struct.unpack_from("<I",raw,mesh["mesh_descriptor"]+28)[0]
    for i,sub in enumerate(mesh["submeshes"]):
     label=sub["material"]
     mats[label]+=len(sub["faces"])
     p=sd+56*i
     buf=struct.unpack_from("<14I",raw,p)
     matches=[]
     for off in buf:
      if 0<off<len(raw)-2:
       end=raw.find(b"\x00",off,min(len(raw),off+100))
       if end>=0:
        b=raw[off:end]
        if 3<=len(b)<90 and all(32<=x<=126 for x in b):
         matches.append({"pointer":off,"value":b.decode("ascii")})
     if label not in bymaterial:
      bymaterial[label]={"submesh_56byte_words":buf,"pointed_to_real_strings":matches,
                          "submesh_record_offset":p,"original_face_count":len(sub["faces"])}
   tga_refs=[(m.start(),m.group(0).decode("latin1")) for m in
             re.finditer(rb"[a-zA-Z0-9_./\\-]{3,120}\.tga",raw,re.I)]
   report={
      "original_bres_model":name+".bdae","mesh_count":len(meshes),
      "submesh_unique_names":len(mats),"material_face_counts":dict(mats),
      "one_exact_authoring_record_per_material":bymaterial,
      "actual_tga_name_bytes_count":len(tga_refs),
      "material_to_texture_verified":False,
   }
   samples.append(report)
   print("BRES_TRUE_C1L1_MATERIAL_FREQ",name,dict(mats))
   for key,entry in list(bymaterial.items())[:5]:
     print("BRES_TRUE_AUTHOR_SUBMESH_POINTERS",name,key,entry)
 return samples

def main(out):
 report=inspect()
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps({"source_2010_original_10_scene_BRES_materials":report,
  "verified_per_material_texture_sampler":False},indent=2)+"\n")
 print("PASS actual 2010 BRES/GLB 10 source original per-submesh material records and candidate pointer graph NO fictitious sampler, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);a=p.parse_args();main(a.out)
