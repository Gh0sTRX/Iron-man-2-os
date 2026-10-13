#!/usr/bin/env python3
"""Read B11 original C1L1 private archives to choose a geometry-faithful Vita test spawn."""
import json, struct, zipfile, pathlib, collections, math
root=pathlib.Path(__file__).resolve().parents[2]
with zipfile.ZipFile(root/"research/B11_C1L1_Scene_GLBS.zip") as z:
    raw=z.read("exports/IronMan2_C1L1_Environment_Geometry.glb")
magic,ver,total=struct.unpack_from("<4sII",raw); assert magic==b"glTF" and ver==2 and total==len(raw)
n,typ=struct.unpack_from("<I4s",raw,12); assert typ==b"JSON"
d=json.loads(raw[20:20+n]); off=20+n
bn,btyp=struct.unpack_from("<I4s",raw,off); assert btyp==b"BIN\0"
bin=raw[off+8:off+8+bn]
def acc(i):
 a=d["accessors"][i];v=d["bufferViews"][a["bufferView"]]; fmt={5126:"f",5125:"I",5123:"H",5121:"B"}[a["componentType"]]
 n={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4}[a["type"]]
 size=struct.calcsize(fmt)*n; stride=v.get("byteStride",size); start=v.get("byteOffset",0)+a.get("byteOffset",0)
 return [struct.unpack_from("<"+fmt*n,bin,start+j*stride) for j in range(a["count"])]
print("SCENE",len(d.get("scenes",[])),"NODES",len(d.get("nodes",[])),"MESH",len(d["meshes"]),"ACCESSOR",len(d["accessors"]))
print("FIRST NODES",repr(d.get("nodes",[])[:3])[:1700])
print("FIRST MESH",repr(d["meshes"][:1])[:1700])
info=[]
for mid,m in enumerate(d["meshes"]):
 p=m["primitives"][0]
 pos=acc(p["attributes"]["POSITION"]); ix=acc(p["indices"])
 xs=[v[0] for v in pos];ys=[v[1] for v in pos];zs=[v[2] for v in pos]
 box=[round(min(x),2) for x in (xs,ys,zs)]+[round(max(x),2) for x in (xs,ys,zs)]
 info.append((mid,m.get("name","?"),len(pos),len(ix)//3,box))
print("PRIMARY BOX SAMPLES")
for row in info[:9]+sorted(info,key=lambda row:row[3],reverse=True)[:20]:
 print(*row)
print("TOTAL AABB",[[min(r[4][i] for r in info),max(r[4][i+3] for r in info)] for i in range(3)])
zgroup=collections.Counter()
for _,name,nv,nt,box in info: zgroup[name.split("_")[0]]+=nt
print("groups",zgroup)
print("SCENES",repr(d.get("scenes",[])[:1])[:1000])
with zipfile.ZipFile(root/"research/B11_C1L1_Source_Parser.zip") as z:
  script=z.read("build_scene.py").decode()
  print("B11 BUILD SOURCE\n",script[:5000])
