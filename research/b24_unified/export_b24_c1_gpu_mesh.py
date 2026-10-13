#!/usr/bin/env python3
"""C1L1 GPU indexed static scene export (original game geometry, no invented UVs).

SOURCE: privately held B11 original 2010 C1L1 environment GLB; GLB exported
root Y-up rotation, raw POSITION coordinates are original Z-up.
OUTPUT: C1G2 binary with uint16 index stream, 16-byte float3+RGBA8 vertices,
four category batches. No CPU pixel rasterization; caller must OWN one active
vitaGL 3D framebuffer and supply its Z-up view/projection matrix.

NO VPK: entirely host asset converter; does NOT imply actual Vita GPU driver
or correct texture/material mapping. The B11 GLB contains no UV attributes.
"""
from __future__ import annotations
from pathlib import Path
import argparse,collections,hashlib,json,math,struct,zipfile

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"research/B11_C1L1_Scene_GLBS.zip"
MEMBER="exports/IronMan2_C1L1_Environment_Geometry.glb"
HEADER_FMT="<4sIIIIII"             # 28-byte v2 header
VERT_FMT="<3fI"                     # 16-byte Z-up XYZ+RGBA
BATCH_FMT="<IIII6f"                 # 40-byte index group+local bbox
IDX_FMT="<H"
STRIDE=struct.calcsize(VERT_FMT)
NAMES=("ground","objects","vehicles","lights")

def decode_glb(raw):
    magic,version,n=struct.unpack_from("<4sII",raw)
    if (magic,version,n)!=(b"glTF",2,len(raw)):raise ValueError("not GLB2")
    chunks={};o=12
    while o<len(raw):
        n,kind=struct.unpack_from("<I4s",raw,o);o+=8
        if n%4 or n<0 or o+n>len(raw) or kind in chunks:raise ValueError("invalid GLB chunk")
        chunks[kind]=raw[o:o+n];o+=n
    if o!=len(raw):raise ValueError("GLB ends mid-chunk")
    d=json.loads(chunks[b"JSON"].rstrip(b"\x00 "))
    return d,chunks[b"BIN\x00"]

def arr(doc,binary,i):
    a=doc["accessors"][i]
    if "sparse" in a:raise ValueError("sparse accessor unsupported")
    fmt={5121:"B",5123:"H",5125:"I",5126:"f"}[a["componentType"]]
    size={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4}[a["type"]]
    view=doc["bufferViews"][a["bufferView"]]
    stride=view.get("byteStride",struct.calcsize(fmt)*size)
    n=struct.calcsize(fmt)*size
    start=view.get("byteOffset",0)+a.get("byteOffset",0)
    if stride<n or start<0 or start+(a["count"]-1)*stride+n>len(binary):
        raise ValueError("accessor OOB")
    return [struct.unpack_from("<"+fmt*size,binary,start+j*stride) for j in range(a["count"])]

def category(name):
    for prefix,i in (("C1L1_ground",0),("C1L1_obj",1),
                     ("C1L1_car",2),("C1L1_light",3)):
        if name.startswith(prefix):return i
    raise ValueError("unrecognized B11 C1L1 mesh "+name)

def asbyte(t):
    f=float(t)
    if not math.isfinite(f):raise ValueError("nonfinite color")
    return max(0,min(255,int(round((f*255 if f<=1 else f)))))

def export(path,manifest):
    with zipfile.ZipFile(SOURCE) as z:
        if z.testzip():raise ValueError("B11 ZIP CRC failed")
        raw=z.read(MEMBER)
    d,bb=decode_glb(raw)
    if len(d["meshes"])!=370:raise ValueError("unexpected source mesh count")
    # World parent node encodes export-only Z-up->Y-up rotation. Child mesh
    # nodes are expected to be identity, not secretly displaced. Fail closed.
    nodes=d["nodes"]
    if not nodes or nodes[0].get("name")!="world":raise ValueError("world root missing")
    child_meshes=[x for x in nodes[1:] if "mesh" in x]
    if len(child_meshes)!=370:raise ValueError("mesh-node count mismatch")
    for n in child_meshes:
        for key in ("matrix","translation","rotation","scale"):
            if key in n:
                v=n[key]
                expected={"translation":[0.,0.,0.],"rotation":[0.,0.,0.,1.],
                          "scale":[1.,1.,1.],
                          "matrix":[1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]}[key]
                if len(v)!=len(expected) or any(abs(float(a)-b)>1e-4 for a,b in zip(v,expected)):
                    raise ValueError("nonidentity child transform, bake required "+str(n.get("name")))
    V=bytearray();I=bytearray();B=bytearray();verts=0;inds=0;total=0
    ranges=[]
    origins=[]
    color0=0; uvcount=0
    # Four batches preserve source category in a single global uint16 index buffer.
    for group in range(4):
        first=inds
        lo=[math.inf]*3;hi=[-math.inf]*3;count=0
        for m in d["meshes"]:
            if category(m.get("name",""))!=group:continue
            for p in m["primitives"]:
                if p.get("mode",4)!=4:raise ValueError("nontriangle prim")
                if "TEXCOORD_0" in p["attributes"]:uvcount+=1
                pp=arr(d,bb,p["attributes"]["POSITION"])
                cc=arr(d,bb,p["attributes"]["COLOR_0"]) if "COLOR_0" in p["attributes"] else None
                ii=arr(d,bb,p["indices"])
                if len(ii)%3:raise ValueError("index stream not triangular")
                if verts+len(pp)>65535:raise ValueError("global uint16 range exceeded, must chunk")
                for j,x in enumerate(pp):
                    if len(x)!=3 or not all(math.isfinite(z) and abs(z)<100000 for z in x):
                        raise ValueError("invalid source vertex")
                    c=(asbyte(cc[j][0]),asbyte(cc[j][1]),asbyte(cc[j][2])) if cc else (120,120,120)
                    if cc:color0+=1
                    rgba=c[0]|c[1]<<8|c[2]<<16|255<<24
                    V.extend(struct.pack(VERT_FMT,*x,rgba))
                    for k in range(3):
                        lo[k]=min(lo[k],x[k]);hi[k]=max(hi[k],x[k])
                for t in ii:
                    val=int(t[0])
                    if val>=len(pp):raise ValueError("index outside accessor")
                    I.extend(struct.pack(IDX_FMT,verts+val))
                    inds+=1
                total+=len(ii)//3
                verts+=len(pp);count+=1
        if inds==first:raise ValueError("empty scene category "+str(group))
        B.extend(struct.pack(BATCH_FMT,group,first,inds-first,count,*(lo+hi)))
        ranges.append({"name":NAMES[group],"first_index":first,
                       "indices":inds-first,"meshes":count,"bbox":[lo,hi]})
    if verts!=37946 or total!=22919 or inds!=68757:
        raise ValueError(f"source corruption: verts={verts}, triangles={total}, indices={inds}")
    if uvcount:raise ValueError("B11 unexpectedly contains UV, revisit parser")
    header=struct.pack(HEADER_FMT,b"C1G2",2,STRIDE,verts,inds,4,struct.calcsize(BATCH_FMT))
    data=header+B+V+I
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)
    doc={"status":"GPU INDEXED SOURCE MESH, NOT VITA GPU INTEGRATION",
         "source":"B11 original C1L1 GLB (user-owned iOS backup)",
         "source_sha256":hashlib.sha256(raw).hexdigest(),"gpu_mesh_sha256":hashlib.sha256(data).hexdigest(),
         "geometry":"Z-up XYZ, original indexed 16-bit triangles",
         "header_bytes":len(header),"batch_stride":struct.calcsize(BATCH_FMT),
         "vertex_stride":STRIDE,"vertices":verts,"indices":inds,"triangles":total,
         "batches":ranges,"submeshes":370,"has_uv0":False,"has_real_textures":False,
         "has_original_spawn":False,"measured_vita_gpu_fps":None,
         "vita_context_attached":False,"vita_armor_mesh_attached":False}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n")
    print("PASS authentic C1G2 source: 37946 vertices / 68757 uint16 indices / 22919 triangles / 4 draw batches")
    print("NOT a Vita renderer, no UV, not a playable scene, no VPK")
    return doc

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--manifest",required=True,type=Path)
    a=p.parse_args()
    export(a.out,a.manifest)
