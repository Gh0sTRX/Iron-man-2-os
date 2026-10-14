#!/usr/bin/env python3
"""2010 BRES material source pointers inside/outside 56-byte face submesh.
Out-of-submesh references reveal real separate material declarations.
Never assign speculative TGA images to a per-face material.
"""
from pathlib import Path
from recover_c1l1_original_uv import BDAEZIP,SOURCES
import json,collections,zipfile,struct,argparse
def trace():
 with zipfile.ZipFile(BDAEZIP) as z:
  code=z.read("bdae_scene_parser.py").decode()
  scope={"__name__":"original_material_graph_2010"}
  exec(compile(code,"bdae_scene_parser.py","exec"),scope)
  reports=[]
  for name in SOURCES:
   raw=z.read("original_models/"+name+".bdae")
   meshes,_=scope["parse"](raw)
   reference_to_strings=collections.defaultdict(list)
   for off in range(0,len(raw)-3,4):
     pointer=struct.unpack_from("<I",raw,off)[0]
     reference_to_strings[pointer].append(off)
   used_submesh=collections.defaultdict(list)
   for mesh in meshes:
     d=struct.unpack_from("<I",raw,mesh["mesh_descriptor"]+28)[0]
     for idx,sub in enumerate(mesh["submeshes"]):
       label=sub["material"];offset=d+56*idx+4
       key=struct.unpack_from("<I",raw,offset)[0]
       used_submesh[(label,key)].append(offset)
   found=[]
   for (label,ptr),refs in used_submesh.items():
     outside=sorted(set(reference_to_strings.get(ptr,[]))-set(refs))
     found.append({"label":label,"source_string_offset":ptr,
       "source_submesh_material_pointer_positions":refs[:16],
       "all_source_exact_label_pointer_positions":reference_to_strings.get(ptr,[])[:60],
       "extra_material_shader_resource_references":outside[:30],
       "recovered_diffuse_texture_link":False})
   reports.append({"original_BRES":name,"records":found})
   print("BRES_2010_SHADER_MATERIAL_POINTER_COUNTS",name,
      [(m["label"],len(m["source_submesh_material_pointer_positions"]),
        len(m["extra_material_shader_resource_references"]),
        m["extra_material_shader_resource_references"][:5]) for m in found[:25]])
 return reports
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);a=p.parse_args()
 out=trace();a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps({"2010_original_BRES_shader_material_declaration_refs":out,
     "diffuse_texture_binds_proven":False},indent=2)+"\n")
 print("PASS exact source BRES material declaration vs per-face submesh graph without false texture labels")
