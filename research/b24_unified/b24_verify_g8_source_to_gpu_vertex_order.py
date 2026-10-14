#!/usr/bin/env python3
"""Check real G8 textured IM2T topology against actual 2010 BRES skin order.

A byte-valid IM2V does NOT prove suitability for G8 unless each skin vertex
index refers to the SAME original vertex as the GPU IM2T triangle index.
Fail closed if source->IM2T vertex ordering differs; never fake compatibility.
"""
from __future__ import annotations
import argparse
import json
import struct
import zipfile
from pathlib import Path
import numpy as np
from b24_hover_fire_authentic_pose_preview import TARGETS, source_meshes
from b24_owner_pack_extract import decode, get_exact

G8_MODELS={"ironman":"mark6.im2t","warmachine":"warmachine.im2t"}

def run(ipa:Path,model_dir:Path,out:Path):
    with zipfile.ZipFile(ipa) as z:
        source=z.read("Payload/IronMan2.app/models")
    index=decode(source,".bdae")
    report={}
    for armor,(bdae,nv) in TARGETS.items():
        raw=get_exact(source,index,bdae)
        matches=[m for m in source_meshes(raw) if len(m["positions"])==nv]
        if len(matches)!=1:raise ValueError("ambiguous original BRES geometry")
        original_xyz=np.asarray(matches[0]["positions"],dtype=np.float64)
        original_faces=np.asarray(matches[0]["faces"]).reshape(-1,3).astype(np.uint16)
        binary=(model_dir/G8_MODELS[armor]).read_bytes()
        magic,model_nv,model_nt,tw,th=struct.unpack_from("<4sIIII",binary)
        if magic!=b"IM2T" or model_nv!=nv:raise ValueError("G8 GPU model header mismatch")
        g8_vertices=np.frombuffer(binary,dtype="<f4",count=nv*5,offset=20).reshape(nv,5)
        xyz=np.asarray(g8_vertices[:,:3],dtype=np.float64)
        face_start=20+nv*20
        faces=np.frombuffer(binary,dtype="<u2",count=model_nt*3,offset=face_start).reshape(-1,3)
        err=np.linalg.norm(xyz-original_xyz,axis=1)
        max_err=float(np.max(err))
        mean_err=float(np.mean(err))
        same_faces=bool(faces.shape==original_faces.shape and
                        np.array_equal(faces,original_faces))
        # Check material-independent ordered XYZ. Real original rig weights refer
        # to BRES vertex indices; never apply to arbitrary reordered IM2T.
        max_coordinate_allowed=1e-3
        compatible=max_err<=max_coordinate_allowed and same_faces
        report[armor]={
            "2010_source_model":bdae,"G8_IM2T":G8_MODELS[armor],
            "vertices":nv,"source_triangles":len(original_faces),
            "G8_triangles":model_nt,"max_xyz_index_order_error":max_err,
            "average_xyz_index_order_error":mean_err,
            "exact_triangle_indices_match":same_faces,
            "SAFE_source_skin_to_G8_IM2T_vertex_mapping":compatible,
            "original_2010_rig_bind_after_animated_retarget_verified":False,
        }
        print("G8_ORIGINAL_TOPOLOGY",armor,"vertices",nv,"faces",model_nt,
              "max_xyz_error",max_err,"triangles_same",same_faces,
              "SAFE_SKIN_INDICES",compatible,flush=True)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    if not all(x["SAFE_source_skin_to_G8_IM2T_vertex_mapping"] for x in report.values()):
        print("REJECT original source animation applying to G8 IM2T; requires index/order mapping",flush=True)
        return False
    print("PASS authentic 2010 GPU model vertex index and source skin order",flush=True)
    return True

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--ipa",type=Path,required=True)
    p.add_argument("--models",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if not run(a.ipa,a.models,a.out):raise SystemExit(2)
