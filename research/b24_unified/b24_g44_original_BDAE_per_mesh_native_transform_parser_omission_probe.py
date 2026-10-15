#!/usr/bin/env python3
"""G44 forensic: Does 2010 BDAE source carry per-mesh scene transforms the
existing B11 geometry parser omitted? Inspect REAL original bundled 2010
BRES assets and parser raw returned mesh+metadata, as well as decoder code.
This is exploratory source fingerprint, not an engine transform solution.
"""
from __future__ import annotations
import argparse,ast,contextlib,io,json,re,zipfile
from pathlib import Path
import numpy as np
def safe(v,depth=0):
 if depth>4:return {"type":type(v).__name__,"too_deep":True}
 if isinstance(v,dict):return {str(k):safe(z,depth+1) for k,z in list(v.items())[:35]}
 if isinstance(v,(list,tuple)):
  if len(v)>15:return {"type":type(v).__name__,"length":len(v),"first":safe(v[0],depth+1),"last":safe(v[-1],depth+1)}
  return [safe(x,depth+1) for x in v]
 if isinstance(v,np.ndarray):
  return {"kind":"numpy","dtype":str(v.dtype),"shape":list(v.shape),
   "min":float(np.min(v)) if v.size and np.issubdtype(v.dtype,np.number) else None,
   "max":float(np.max(v)) if v.size and np.issubdtype(v.dtype,np.number) else None}
 if isinstance(v,(str,int,float,bool,type(None))):return v
 return {"type":type(v).__name__,"repr":repr(v)[:150]}
def main(zip_path,out):
 with zipfile.ZipFile(zip_path) as z:
  original=z.read("bdae_scene_parser.py").decode("utf-8")
  ns={"__name__":"g44_source_BRES_parser","__file__":"bdae_scene_parser.py"}
  exec(compile(original,"bdae_scene_parser.py","exec"),ns)
  func=ns["parse"]
  allpaths=z.namelist()
  names=["C1L1_ground_001","C1L1_obj_001","C1L1_obj_002","C1L1_obj_003","C1L1_obj_004",
    "C1L1_light_001","C1L1_light_002","C1L1_light_003","C1L1_car_01","C1L1_car_02"]
  parsed=[]
  for basename in names:
   with contextlib.redirect_stdout(io.StringIO()):
    meshes,metadata=func(z.read("original_models/"+basename+".bdae"))
   kinds={}
   for mesh in meshes:
    for key,value in mesh.items():
     if key not in kinds:kinds[key]={"type":type(value).__name__,"one_sample":safe(value,2)}
   first=meshes[0]
   rows=[]
   for i,m in enumerate(meshes):
    pos=np.asarray(m["positions"],dtype=np.float32)
    rows.append({"index":i,"source_original_vertices":len(pos),
      "raw_bbox_min":pos.min(axis=0).tolist(),"raw_bbox_max":pos.max(axis=0).tolist(),
      "mesh_extra_source_fields":{k:safe(v) for k,v in m.items() if k not in ("positions","uv","faces","submeshes")}})
   parsed.append({"original_BRES":basename,"meshes":len(meshes),
      "native_parser_second_return_type":type(metadata).__name__,
      "native_parser_second_return_source_fields":safe(metadata),
      "native_parser_individual_mesh_return_field_examples":kinds,
      "original_raw_mesh_bbox_and_additional_attributes":rows})
 tree=ast.parse(original)
 sourcefn=[{"line":f.lineno,"name":f.name} for f in ast.walk(tree) if isinstance(f,(ast.FunctionDef,ast.AsyncFunctionDef))]
 keywords=("transform","matrix","quaternion","parent","world","node","position","rotation","scale","translation","hierarchy","scene")
 hit_lines=[{"line":i,"content":line.strip()[:240]} for i,line in enumerate(original.splitlines(),1)
            if any(w in line.casefold() for w in keywords)]
 report={
  "source_archive":"OWNER_ORIGINAL_2010_C1L1_B11_Source_Parser_ZIP",
  "native_2010_static_environment_BRES_model_count":len(parsed),
  "native_source_parsed_BRES_models":parsed,
  "parser_file_SHA256":__import__("hashlib").sha256(original.encode()).hexdigest(),
  "python_parser_source_function_table":sourcefn,
  "source_parser_lines_referencing_node_matrix_transform_or_root":hit_lines,
  "source_parser_interpretation_and_original_game_runtime_world_mat_NOT_YET_PROVEN":True,
  "no_original_game_shader_or_source_poly_movement_assumed":True,
  "no_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G44 parser SHA",report["parser_file_SHA256"],"source parser named functions",sourcefn)
 print("G44 SOURCE BRES native return metadata",[(x["original_BRES"],x["meshes"],x["native_parser_second_return_type"],str(x["native_parser_second_return_source_fields"])[:750]) for x in parsed])
 print("G44 SOURCE parser matrix/transform keyword lines",hit_lines[:55])
 print("PASS G44 real original C1L1 BDAE decoder transform metadata inventory; no model relocation.")
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--parser-bdae-zip",required=True,type=Path);a.add_argument("--out",required=True,type=Path)
 x=a.parse_args();main(x.parser_bdae_zip,x.out)
