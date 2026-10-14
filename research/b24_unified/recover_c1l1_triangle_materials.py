#!/usr/bin/env python3
"""Recover ORIGINAL per-triangle material labels for C1L1 without inventing
material->diffuse texture bindings.

B11 original BDAE parser returned ordered material-specific submesh faces.
C1G2 GPU index order was built from SAME original B11 exported GLB faces.
Assert EXACT triangle/index alignment before writing material IDs. Both
individual source BDAE file and material name form the stable identity
(the same generic Standard_* name need not mean the same texture in all files).

Format C1MA v1, little endian:
  <4sIIIIII> magic, version, nvertices, ntriangles, nmesh, nmaterial, dictbytes
  370 * <IIIII> group, first_vert, vertcount, first_tri, tricount
  22919 * <H> assigned original material-id per source triangle
  material dictionary nmaterial of
    <H> byte_length and UTF-8 "C1L1_obj_001.bdae:MaterialName"

NO texture byte, atlas, geometry or user copyrighted source is committed.
NO VPK. Strictly source metadata and provenance only.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, struct, zipfile
from pathlib import Path
import numpy as np
from export_b24_c1_gpu_mesh import SOURCE, MEMBER, decode_glb, arr, category
from recover_c1l1_original_uv import BDAEZIP, SOURCES

ROOT=Path(__file__).resolve().parents[2]
FMT="<4sIIIIII"
RECORD="<IIIII"
def generate(out:Path, manifest:Path):
    with zipfile.ZipFile(SOURCE) as z:
        assert z.testzip() is None
        doc,binbuf=decode_glb(z.read(MEMBER))
    by_name={}
    with zipfile.ZipFile(BDAEZIP) as z:
        assert z.testzip() is None
        code=z.read("bdae_scene_parser.py").decode()
        ns={"__name__":"original_bdae_materials","__file__":"bdae_scene_parser.py"}
        exec(compile(code,"bdae_scene_parser.py","exec"),ns)
        for basename in SOURCES:
            originals,_=ns["parse"](z.read("original_models/"+basename+".bdae"))
            for i,original in enumerate(originals):
                key=basename+"_"+str(i)
                if key in by_name:raise ValueError("duplicate original mesh "+key)
                by_name[key]=(basename+".bdae",original)
    if len(by_name)!=370:raise ValueError("expected 370 BDAE objects")
    mat_ids={};material_names=[]
    face_ids=[];ranges=[];names=set()
    triangle=vertex=0
    groups=collections.Counter()
    mat_face_counts=collections.Counter()
    for grp in range(4):
        for mesh in doc["meshes"]:
            name=mesh.get("name","")
            if category(name)!=grp:continue
            if name not in by_name or name in names:raise ValueError("mismatched BDAE mesh "+name)
            names.add(name)
            filename,orig=by_name[name]
            primitives=mesh["primitives"]
            if len(primitives)!=1:raise ValueError("multi-primitive GLB "+name)
            prim=primitives[0]
            positions=arr(doc,binbuf,prim["attributes"]["POSITION"])
            indices=np.asarray(arr(doc,binbuf,prim["indices"]),dtype=np.uint32).reshape(-1)
            original_index=np.asarray(orig["faces"],dtype=np.uint32).reshape(-1)
            if not np.array_equal(indices,original_index):
                raise ValueError("SOURCE face reorder in "+name)
            if len(positions)!=len(orig["positions"]):
                raise ValueError("SOURCE vertex count mismatch "+name)
            if len(indices)%3:raise ValueError("invalid GLB triangle count")
            material_faces=[]
            for sub in orig["submeshes"]:
                label=str(sub.get("material","")).strip()
                if not label:raise ValueError("original empty material name "+name)
                src_faces=np.asarray(sub["faces"],dtype=np.uint32).reshape(-1)
                if len(src_faces)%3:raise ValueError("broken submesh faces "+name)
                material_key=filename+":"+label
                if material_key not in mat_ids:
                    mat_ids[material_key]=len(material_names)
                    material_names.append(material_key)
                index=mat_ids[material_key]
                material_faces.extend([index]*(len(src_faces)//3))
                mat_face_counts[material_key]+=len(src_faces)//3
            if len(material_faces)!=len(indices)//3:
                raise ValueError("submesh material face count differs "+name)
            # Per-submesh face arrays may be view slices, prove exact order
            # rather than assume material buckets preserve original faces.
            ordered=np.concatenate([np.asarray(sub["faces"],dtype=np.uint32).reshape(-1)
                                    for sub in orig["submeshes"]]) if orig["submeshes"] else np.array([],dtype=np.uint32)
            if not np.array_equal(ordered,indices):
                raise ValueError("original material submesh face ranges not contiguous: "+name)
            ranges.append((grp,vertex,len(positions),triangle,len(material_faces)))
            face_ids.extend(material_faces)
            groups[("mesh",grp)]+=1
            groups[("triangles",grp)]+=len(material_faces)
            vertex+=len(positions);triangle+=len(material_faces)
    if len(names)!=370 or vertex!=37946 or triangle!=22919:
        raise ValueError(f"C1MA original scene mismatch meshes={len(names)} vertices={vertex} triangles={triangle}")
    if len(material_names)>65535:raise ValueError("material ID overflow")
    labels=bytearray()
    for name in material_names:
        encoded=name.encode("utf-8")
        if len(encoded)>255:raise ValueError("material name too long")
        labels.extend(struct.pack("<H",len(encoded)))
        labels.extend(encoded)
    hdr=struct.pack(FMT,b"C1MA",1,vertex,triangle,len(ranges),len(material_names),len(labels))
    binary=bytearray(hdr)
    for item in ranges:binary.extend(struct.pack(RECORD,*item))
    for ident in face_ids:binary.extend(struct.pack("<H",ident))
    binary.extend(labels)
    out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(binary)
    result={"format":"C1MA v1 original BDAE source triangle->material labels, no texture link",
       "source_content":"USER ORIGINAL BDAE",
       "sha256":hashlib.sha256(binary).hexdigest(),
       "vertices":vertex,"triangles":triangle,"meshes":len(ranges),
       "unique_file_scoped_materials":len(material_names),
       "material_dictionary_bytes":len(labels),
       "mesh_records_bytes":len(ranges)*struct.calcsize(RECORD),
       "triangle_material_bytes":len(face_ids)*2,
       "all_source_glb_faces_and_material_ranges_verified":True,
       "diffuse_texture_links_proven":False,
       "lightmap_texture_links_proven":False,
       "vehicle_original_atlas_verified_separately":True,
       "group_counts":{str(k):v for k,v in groups.items()},
       "materials":[{"id":i,"source_material":name,"triangles":mat_face_counts[name]}
                    for i,name in enumerate(material_names)]}
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(f"PASS C1MA real material-to-TRIANGLE map: {len(ranges)} meshes, "
          f"{triangle} source faces, {len(material_names)} filename-scoped material labels")
    print("GROUPS",dict(groups))
    print("NO diffuse assignments invented; no raw asset export; no VPK")
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    a=p.parse_args()
    generate(a.out,a.manifest)
