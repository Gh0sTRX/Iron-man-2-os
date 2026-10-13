#!/usr/bin/env python3
"""B24-C1: exact original mesh triangles -> self-validating, Z-up, static runtime map.
B11 exported GLB positions are *already in original Z-up coordinates*; its root
node contains the -90-degree X Y-up correction. We read raw POSITION accessors
and intentionally do NOT apply this export-only root transform for B17's Z-up.
Authoring source: privately backed-up original Gameloft C1L1 BDAE 2010 model.
Original mission transform/spawn and full materials are NOT decoded.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import math
import pathlib
import struct
import zipfile
ROOT=pathlib.Path(__file__).resolve().parents[2]
ARCHIVE=ROOT/"research/B11_C1L1_Scene_GLBS.zip"
MEMBER="exports/IronMan2_C1L1_Environment_Geometry.glb"
FMT="<9fII"
STRIDE=struct.calcsize(FMT)
HEADER="<4sIII"
def data_parts(raw):
    magic,ver,sz=struct.unpack_from("<4sII",raw,0)
    assert (magic,ver,sz)==(b"glTF",2,len(raw))
    pos=12
    chunks={}
    while pos<len(raw):
        length,typ=struct.unpack_from("<I4s",raw,pos);pos+=8
        assert length%4==0 and pos+length<=len(raw)
        chunks[typ]=raw[pos:pos+length];pos+=length
    assert pos==len(raw) and b"JSON" in chunks and b"BIN\x00" in chunks
    return json.loads(chunks[b"JSON"].rstrip(b" \x00")),chunks[b"BIN\x00"]
def accessor(d,binary,i):
    a=d["accessors"][i]
    assert "sparse" not in a
    vw=d["bufferViews"][a["bufferView"]]
    kind={5121:"B",5123:"H",5125:"I",5126:"f"}[a["componentType"]]
    comp={"SCALAR":1,"VEC3":3,"VEC4":4}[a["type"]]
    fmt="<"+kind*comp
    size=struct.calcsize(fmt)
    stride=vw.get("byteStride",size)
    off=vw.get("byteOffset",0)+a.get("byteOffset",0)
    assert stride>=size
    assert off+(a["count"]-1)*stride+size <=len(binary)
    return [struct.unpack_from(fmt,binary,off+j*stride) for j in range(a["count"])]
def group_of(name):
    if name.startswith("C1L1_ground"):return 0
    if name.startswith("C1L1_obj"):return 1
    if name.startswith("C1L1_car"):return 2
    if name.startswith("C1L1_light"):return 3
    raise ValueError("unknown authentic C1L1 source: "+name)
def make(out,manifest):
    with zipfile.ZipFile(ARCHIVE) as z:
        assert z.testzip() is None
        raw=z.read(MEMBER)
    d,binary=data_parts(raw)
    assert len(d["meshes"])==370
    # GLB is the *environment only*; no duplicate demo Mark VI.
    names=[]
    payload=bytearray()
    bygroup=collections.Counter()
    xmax=ymax=-math.inf
    xmin=ymin=math.inf
    zmin=math.inf;zmax=-math.inf
    for mesh in d["meshes"]:
        name=mesh.get("name","")
        names.append(name)
        group=group_of(name)
        for prim in mesh["primitives"]:
            assert prim.get("mode",4)==4
            xyz=accessor(d,binary,prim["attributes"]["POSITION"])
            inds=accessor(d,binary,prim["indices"])
            col_idx=prim["attributes"].get("COLOR_0")
            cols=accessor(d,binary,col_idx) if col_idx is not None else None
            assert len(inds)%3==0
            for n in range(0,len(inds),3):
                ix=[int(inds[n+k][0]) for k in range(3)]
                assert all(0<=j<len(xyz) for j in ix)
                coords=[xyz[j] for j in ix]
                assert all(len(v)==3 and all(math.isfinite(c) for c in v) for v in coords)
                # Remove truly degenerate triangles; preserve all nondegenerate original surfaces.
                v0,v1,v2=coords
                cross=((v1[1]-v0[1])*(v2[2]-v0[2])-(v1[2]-v0[2])*(v2[1]-v0[1]),
                       (v1[2]-v0[2])*(v2[0]-v0[0])-(v1[0]-v0[0])*(v2[2]-v0[2]),
                       (v1[0]-v0[0])*(v2[1]-v0[1])-(v1[1]-v0[1])*(v2[0]-v0[0]))
                if sum(c*c for c in cross)<1e-12: continue
                if cols is not None:
                    rgb=cols[ix[0]][:3]
                    if all(0<=float(c)<=1 for c in rgb):
                        rgb=[int(max(0,min(255,round(float(c)*255)))) for c in rgb]
                    else:
                        rgb=[int(max(0,min(255,round(float(c))))) for c in rgb]
                else:
                    rgb=((98,112,115),(157,159,174),(168,113,78),(92,133,116))[group]
                color=(rgb[0]<<16)|(rgb[1]<<8)|rgb[2]
                flat=[float(x) for p in coords for x in p]
                payload.extend(struct.pack(FMT,*flat,color,group))
                bygroup[group]+=1
                xmin=min(xmin,*(c[0] for c in coords));xmax=max(xmax,*(c[0] for c in coords))
                ymin=min(ymin,*(c[1] for c in coords));ymax=max(ymax,*(c[1] for c in coords))
                zmin=min(zmin,*(c[2] for c in coords));zmax=max(zmax,*(c[2] for c in coords))
    count=len(payload)//STRIDE
    assert count>21000 and count<=22919
    binary_map=struct.pack(HEADER,b"C1M1",1,count,STRIDE)+payload
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(binary_map)
    result={"format":"B24-C1 original static map triangles Z-up","source":MEMBER,
            "source_sha256":hashlib.sha256(raw).hexdigest(),
            "map_sha256":hashlib.sha256(binary_map).hexdigest(),
            "triangles":count,"vertex_buffer_source":"original BDAE extracted through B11 GLB",
            "triangle_record_bytes":STRIDE,"binary_bytes":len(binary_map),
            "triangle_groups":{str(k):v for k,v in sorted(bygroup.items())},
            "bbox_z_up":[[xmin,ymin,zmin],[xmax,ymax,zmax]],
            "mission_spawn_known":False,"level1_bclara_instance_decoded":False,
            "materials_original_texture_complete":False,
            "test_origin":[0.0,0.0,1.0],"test_origin_is_original_spawn":False,
            "debug_lod_budget_per_group":[550,850,250,250],
            "renderer":"CPU original triangle test backend, NOT yet VitaGL"}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    return result
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--output",type=pathlib.Path,required=True)
    a.add_argument("--manifest",type=pathlib.Path,required=True)
    args=a.parse_args()
    make(args.output,args.manifest)
