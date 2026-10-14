#!/usr/bin/env python3
"""Authentic ORIGINAL C1L1 COLLISION meshes, NOT heuristic visual triangles.

Reads *existing private B11 archive* C1L1_col_01.bdae and
C1L1_building_col.bdae; exact 631 SOURCE triangles. C1L1_floor_001.bdae
has 4 vertices and 0 parsed triangle faces and cannot truthfully be used
as a floor yet. Output C1WC v1 is for B14 CPU collision integration.

Binary header little endian: <4sIIII> C1WC, version1, 631 triangles,
two source BDAE files, stride40. Records <9fI> original Z-up vertices
and 0/1 original collision source ID. Never silently invent geometry.
"""
from __future__ import annotations
import argparse,hashlib,json,struct,zipfile
from pathlib import Path
import numpy as np
SOURCES=("C1L1_col_01","C1L1_building_col")
EXPECTED=(230,401)
HEADER="<4sIIII"
TRI="<9fI"
def convert(archive:Path,out:Path,manifest:Path):
 with zipfile.ZipFile(archive) as z:
  if z.testzip():raise ValueError("original B11 CRC failure")
  code=z.read("bdae_scene_parser.py").decode()
  ns={"__name__":"original_c1_collision","__file__":"bdae_scene_parser.py"}
  exec(compile(code,"bdae_scene_parser.py","exec"),ns)
  raw={n:z.read("original_models/"+n+".bdae") for n in SOURCES}
 tri=bytearray()
 counts={}
 steep=0
 for group,name in enumerate(SOURCES):
  meshes,_=ns['parse'](raw[name])
  count=0
  for m in meshes:
   positions=np.asarray(m['positions'],dtype=np.float64)
   indices=np.asarray(m['faces'],dtype=np.int64).reshape(-1)
   if positions.ndim!=2 or positions.shape[1]!=3 or not np.isfinite(positions).all():
    raise ValueError("original collision vertex invalid "+name)
   if len(indices)%3 or np.any(indices<0) or np.any(indices>=len(positions)):
    raise ValueError("original collision index corrupt "+name)
   for a,b,c in indices.reshape(-1,3):
    v=positions[[a,b,c]]
    d1=v[1]-v[0];d2=v[2]-v[0]
    normal=np.cross(d1,d2)
    norm=float(np.linalg.norm(normal))
    if norm<1e-5:raise ValueError("source contains zero area collision face: "+name)
    if abs(float(normal[2]))/norm<.58:steep+=1
    tri.extend(struct.pack(TRI,*[float(x) for x in v.flat],group))
    count+=1
  if count!=EXPECTED[group]:raise ValueError(f"original collision {name} faces {count} not {EXPECTED[group]}")
  counts[name]={"meshes":len(meshes),"triangles":count,"raw_sha256":hashlib.sha256(raw[name]).hexdigest()}
 header=struct.pack(HEADER,b'C1WC',1,sum(EXPECTED),len(SOURCES),struct.calcsize(TRI))
 data=header+tri
 assert len(data)==struct.calcsize(HEADER)+sum(EXPECTED)*struct.calcsize(TRI)
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_bytes(data)
 result={"format":"C1WC v1 source-authentic original 2010 BDAE collision triangles, original Z-up",
  "triangles":sum(EXPECTED),"steep_candidates":steep,
  "stride":struct.calcsize(TRI),"bytes":len(data),
  "sha256":hashlib.sha256(data).hexdigest(),
  "sources":counts,"floor_C1L1_floor_001_parsed_triangles":0,
  "cpu_collision_runtime_enabled":False,"device_collision_verified":False}
 manifest.parent.mkdir(parents=True,exist_ok=True)
 manifest.write_text(json.dumps(result,indent=2)+"\n")
 print("PASS 631 TRUE C1L1 2010 collision faces, without heuristic visual-only walls; no VPK:",result)
 return result
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument('--archive',type=Path,default=Path("research/B11_C1L1_Source_Parser.zip"))
 parser.add_argument('--out',type=Path,required=True)
 parser.add_argument('--manifest',type=Path,required=True)
 a=parser.parse_args()
 convert(a.archive,a.out,a.manifest)
