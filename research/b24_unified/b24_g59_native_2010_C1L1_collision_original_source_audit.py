#!/usr/bin/env python3
"""G59 source-faithful collision intake for a future C1L1 playable slice.
Only BRES native XY/XYZ and face indices. No claim of authentic Gameloft
physics settings, runtime transform roots, player contact or Vita FPS.
"""
from __future__ import annotations
import argparse,contextlib,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np
import trimesh
SOURCES=("C1L1_floor_001","C1L1_col_01","C1L1_building_col")
COLORS=([70,175,120,145],[250,166,91,145],[104,141,237,145])

def run(zpath,outjson,outglb):
    scene=trimesh.Scene()
    out=[]
    nmesh=ntri=nvert=horiz=slope=walls=0
    with zipfile.ZipFile(zpath) as z:
        env={"__name__":"g59_original_collision_reader","__file__":"bdae_scene_parser.py"}
        exec(compile(z.read("bdae_scene_parser.py"),"bdae_scene_parser.py","exec"),env)
        for stem,rgba in zip(SOURCES,COLORS):
            raw=z.read("original_models/"+stem+".bdae")
            with contextlib.redirect_stdout(io.StringIO()):
                meshes,_=env["parse"](raw)
            parts=[]
            for m in meshes:
                xyz=np.asarray(m["positions"],dtype=np.float32)
                faces=np.asarray(m["faces"],dtype=np.int64).reshape(-1,3)
                assert xyz.ndim==2 and xyz.shape[1]==3
                assert len(faces)>0 and faces.min()>=0 and faces.max()<len(xyz)
                obj=trimesh.Trimesh(vertices=xyz,faces=faces,process=False)
                obj.visual.face_colors=np.asarray(rgba,dtype=np.uint8)
                scene.add_geometry(obj,geom_name=stem+"__"+m["name"])
                nz=np.abs(obj.face_normals[:,2])
                hh=int(np.count_nonzero(nz>=.8))
                ss=int(np.count_nonzero((nz>=.35)&(nz<.8)))
                ww=int(np.count_nonzero(nz<.35))
                horiz+=hh;slope+=ss;walls+=ww
                nmesh+=1;ntri+=len(faces);nvert+=len(xyz)
                parts.append({"original_source_mesh":m["name"],"original_triangles":len(faces),
                              "host_horizontal_normals":hh,"host_sloped_normals":ss,
                              "host_vertical_normals":ww})
            out.append({"original_BRES":stem,
                        "SHA256":hashlib.sha256(raw).hexdigest(),
                        "source_meshes":len(meshes),
                        "source_triangles":sum(x["original_triangles"] for x in parts),
                        "original_member_mesh_data":parts})
    assert len(SOURCES)==3 and nmesh==19 and ntri==1910
    assert horiz+slope+walls==ntri
    report={
        "stage":"G59","source_original_collision_meshes":nmesh,
        "source_original_collision_triangles":ntri,"source_original_collision_vertices":nvert,
        "source_native_collision_BRES_file_count":3,
        "host_diagnostic_abs_face_normal_up_ge_0_8":horiz,
        "host_diagnostic_sloping_face_count":slope,
        "host_diagnostic_wall_face_count":walls,
        "per_original_C1L1_collision_source":out,
        "source_original_mesh_transforms_rewritten":False,
        "source_native_walkable_logic_proven":False,
        "source_native_gameplay_collision_engine_recovered":False,
        "Vita_C1L1_demo_playable_or_tested":False,
        "NO_VPK":True}
    outjson.parent.mkdir(parents=True,exist_ok=True);outglb.parent.mkdir(parents=True,exist_ok=True)
    outjson.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    scene.export(outglb)
    print("PASS G59 original 19 collision meshes 1910 triangles; no native physics claim",
          {"horizontal":horiz,"sloped":slope,"walls":walls})
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zip",type=Path,required=True)
    p.add_argument("--json",type=Path,required=True)
    p.add_argument("--glb",type=Path,required=True)
    a=p.parse_args()
    run(a.zip,a.json,a.glb)
