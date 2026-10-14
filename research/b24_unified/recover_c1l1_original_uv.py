#!/usr/bin/env python3
"""Recover authentic C1L1 mesh UV0 candidates and source material names.

Inputs are the user's ORIGINAL 2010 Gameloft .bdae source archive and B11
exported geometry GLB, not generated approximations. Match EACH original BDAE
vertex against GLB POSITION before emitting UVs. C1G2 game vertex ordering is
exactly grouped B11 GLB mesh ordering: ground, urban, cars, lights.

Where original UV interpretation is uncertain, preserve source candidate but
mark material binding unverified. NO source texture mapped by visual guess.
Vehicles have independently reproduced B12 textured GLB with the original
C1L1_Vehicles texture, but original material pointer traversal is not solved.
No VPK or original asset upload.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import argparse,hashlib,json,math,re,struct,zipfile
import numpy as np
from export_b24_c1_gpu_mesh import decode_glb,arr,category,SOURCE as GLBZIP,MEMBER

ROOT=Path(__file__).resolve().parents[2]
BDAEZIP=ROOT/"research/B11_C1L1_Source_Parser.zip"
SOURCES=("C1L1_ground_001","C1L1_obj_001","C1L1_obj_002",
 "C1L1_obj_003","C1L1_obj_004","C1L1_car_01","C1L1_car_02",
 "C1L1_light_001","C1L1_light_002","C1L1_light_003")
GROUP_NAME=("ground","urban","vehicles","lights")
MAGIC=b"C1UV";VERSION=1
EXPECTED_VERTS=37946
EXPECTED_MESHES=370
def recover(out:Path,manifest:Path)->dict:
    with zipfile.ZipFile(GLBZIP) as z:
        if z.testzip():raise ValueError("B11 GLB zip corrupt")
        glbraw=z.read(MEMBER)
    d,binary=decode_glb(glbraw)
    assert len(d["meshes"])==EXPECTED_MESHES
    by_name={}
    with zipfile.ZipFile(BDAEZIP) as z:
        if z.testzip():raise ValueError("original BDAE zip corrupt")
        ns={"__name__":"b11_parser","__file__":"bdae_scene_parser.py"}
        code=z.read("bdae_scene_parser.py").decode()
        exec(compile(code,"bdae_scene_parser.py","exec"),ns)
        for filename in SOURCES:
            meshes,stats=ns["parse"](z.read("original_models/"+filename+".bdae"))
            if not meshes:raise ValueError("empty original "+filename)
            if stats and sum(int(v) for v in stats.values())>10:
                raise ValueError("unexpected source parser rejection "+filename)
            for i,mesh in enumerate(meshes):
                name=filename+"_"+str(i)
                if name in by_name:raise ValueError("duplicate "+name)
                by_name[name]=mesh
    if len(by_name)!=EXPECTED_MESHES:
        raise ValueError(f"original BDAE mesh count mismatch {len(by_name)}")
    records=bytearray()
    flags=bytearray()
    stats=Counter()
    all_mats=Counter()
    manifest_meshes=[]
    names_checked=set()
    # C1G2 vertex ordering is category-order then GLB original mesh ordering.
    for group in range(4):
        for mesh in d["meshes"]:
            name=mesh.get("name","")
            if category(name)!=group:continue
            if name in names_checked or name not in by_name:
                raise ValueError("missing/duplicate original matching "+name)
            names_checked.add(name)
            source=by_name[name]
            prim=mesh["primitives"]
            if len(prim)!=1 or "POSITION" not in prim[0]["attributes"]:
                raise ValueError("unsupported split B11 mesh: "+name)
            dest=np.asarray(arr(d,binary,prim[0]["attributes"]["POSITION"]),dtype=np.float32)
            orig=np.asarray(source["positions"],dtype=np.float32)
            uv=np.asarray(source["uv"],dtype=np.float32)
            if dest.shape!=orig.shape or orig.ndim!=2 or orig.shape[1]!=3:
                raise ValueError("BDAE/GLB vertex ordering/count drift: "+name)
            if uv.shape!=(orig.shape[0],2) or not np.isfinite(uv).all():
                raise ValueError("invalid original UV: "+name)
            deviation=float(np.max(np.abs(orig-dest)))
            if deviation>0.0001:
                raise ValueError(f"BDAE/GLB world positions don't align: {name} max delta={deviation}")
            index=np.asarray(arr(d,binary,prim[0]["indices"]),dtype=np.uint32).reshape(-1)
            faces=np.asarray(source["faces"],dtype=np.uint32).reshape(-1)
            if index.shape!=faces.shape:
                raise ValueError("BDAE/GLB face count mismatch "+name)
            # GLB exporter might reorder triangle winding, but indices must
            # reference the same original vertices. If it does, fail closed:
            # material submesh bindings require exact source alignment later.
            matching_indices=bool(np.array_equal(index,faces))
            if not matching_indices:
                raise ValueError("BDAE/GLB index ordering differs "+name)
            stride=int(source["stride"])
            has_coordinates=stride>=20 and np.any(uv!=0.0)
            if has_coordinates and float(np.max(np.abs(uv)))>500.0:
                raise ValueError("implausible UV range "+name)
            records.extend(uv.astype("<f4",copy=False).tobytes())
            flags.append(1 if has_coordinates else 0)
            submaterials=[{"source_name":str(s.get("material","")),
                "triangles":len(s["faces"])} for s in source["submeshes"]]
            if sum(q["triangles"] for q in submaterials)!=len(index)//3:
                raise ValueError("source material triangles don't sum "+name)
            for m in submaterials:all_mats[m["source_name"]]+=1
            row={"mesh":name,"source_bdae":name.rsplit("_",1)[0]+".bdae",
                "vertex_offset":len(records)//8-len(uv),
                "vertices":len(uv),"triangles":len(index)//3,
                "category":GROUP_NAME[group],"source_stride":stride,
                "uv_candidate":bool(has_coordinates),
                "max_world_position_mismatch":deviation,
                "faces_indices_match_original":matching_indices,
                "submesh_materials":submaterials,
                "diffuse_atlas_link_proven_from_material_pointer":False}
            if group==2:
                row["b12_independently_verified_texture_asset"]="C1L1_Vehicles.tga"
                stats["vehicle_meshes"]+=1
                stats["vehicle_tris"]+=len(index)//3
            stats["vertices"]+=len(uv);stats["triangles"]+=len(index)//3
            stats["mesh_count"]+=1;stats["category_"+GROUP_NAME[group]]+=1
            if has_coordinates:
                stats["meshes_uv_candidate"]+=1;stats["verts_uv_candidate"]+=len(uv)
            manifest_meshes.append(row)
    if len(names_checked)!=EXPECTED_MESHES or stats["vertices"]!=EXPECTED_VERTS or stats["triangles"]!=22919:
        raise ValueError("total C1G2/B11 source diverged "+str(stats))
    if stats["vehicle_meshes"]!=22:raise ValueError("must recover all original 22 car meshes")
    # 16 byte header, 370 per-mesh flags, 2*float32 per C1G2 vertex
    header=struct.pack("<4sIII",MAGIC,VERSION,EXPECTED_VERTS,EXPECTED_MESHES)
    payload=header+bytes(flags)+records
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(payload)
    metadata={
        "format":"C1UV v1 CPU-readable original BDAE UV candidates matching existing C1G2 exact vertex ordering",
        "source_game":"Gameloft Iron Man 2 iOS original C1L1 BRES/BDAE",
        "source_bdae_archive_sha256":hashlib.sha256(BDAEZIP.read_bytes()).hexdigest(),
        "source_geometry_glb_sha256":hashlib.sha256(glbraw).hexdigest(),
        "source_uv_sha256":hashlib.sha256(payload).hexdigest(),
        "original_material_pointer_to_diffuse_binding_recovered":False,
        "original_lightmap_binding_recovered":False,
        "fully_textured_C1L1":False,
        "vehicle_B12_texture_atlas_association":"C1L1_Vehicles.tga (from previously verified B12 real-textured 22-mesh GLB)",
        "texture_atlas_file_in_this_package":False,
        "number_of_distinct_material_labels":len(all_mats),
        "material_labels_and_source_submesh_occurrences":dict(sorted(all_mats.items())),
        "counts":dict(stats),"header_bytes":len(header),
        "mesh_uv_flag_bytes":len(flags),"uv_bytes":len(records),
        "total_bytes":len(payload),"exact_world_face_alignment":True,
        "meshes":manifest_meshes
    }
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps(metadata,indent=2,ensure_ascii=False)+"\n")
    print("PASS original C1L1 UV candidate: 370 meshes, 37946 verts, 22919 triangles, all POSITION + face indices match")
    print("VEHICLE",stats["vehicle_meshes"],"meshes",stats["vehicle_tris"],"triangles; B12 atlas C1L1_Vehicles")
    print("UV",stats["meshes_uv_candidate"],"source mesh candidates","MATERIAL LABELS",len(all_mats),"Source ONLY / NO VPK")
    return metadata
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--manifest",required=True,type=Path)
    a=p.parse_args()
    recover(a.out,a.manifest)
