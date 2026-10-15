#!/usr/bin/env python3
"""G56: classify exactly 74 special C1L1 light meshes missing source PIVOT.
Do not guess transforms from native canonical -node only; some original
vertex buffers are centered and others already contain nonzero offsets.
"""
from __future__ import annotations
import argparse,collections,contextlib,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np
from b24_g55_2010_C1L1_true_native_BRES_parent_pivot_scene_reconstruction import SOURCES,find_native_nodes
EPS=0.01

def source_center_class(positions):
    v=np.asarray(positions,dtype=np.float64)
    if v.ndim!=2 or v.shape[1]!=3 or not len(v) or not np.isfinite(v).all():
        raise ValueError("Invalid original XYZ array")
    lo=v.min(axis=0);hi=v.max(axis=0);c=(lo+hi)/2
    return ("source_bbox_origin_centered" if np.linalg.norm(c)<=EPS
            else "source_bbox_baked_nonzero"),c,lo,hi

def run(zpath:Path,out:Path):
    count=collections.Counter();records=[]
    with zipfile.ZipFile(zpath) as z:
        env={"__name__":"g56_owned_BRES_parser","__file__":"bdae_scene_parser.py"}
        exec(compile(z.read("bdae_scene_parser.py"),"bdae_scene_parser.py","exec"),env)
        for stem in SOURCES:
            raw=z.read("original_models/"+stem+".bdae")
            nodes=find_native_nodes(raw)
            byname=collections.defaultdict(list)
            for n in nodes.values():byname[n["name"]].append(n)
            with contextlib.redirect_stdout(io.StringIO()):
                meshes,_=env["parse"](raw)
            missing=[]
            for m in meshes:
                name=m["name"];base=name.removesuffix("-mesh")
                par=byname.get(base+"-node",[])
                pivot=byname.get(base+"-node_PIVOT",[])
                edges=[(a,b) for a in par for b in pivot
                       if a["native_child_count"]>0 and a["native_child_ptr"]==b["offset"]]
                count["all_original_meshes"]+=1
                if len(edges)==1:
                    count["G55_source_parent_pivot_links"]+=1
                    continue
                kind,center,lo,hi=source_center_class(m["positions"])
                count["unresolved_special_meshes"]+=1
                count["unresolved_original_triangles"]+=len(m["faces"])
                count[kind]+=1
                count["canonical_node_present" if par else "canonical_node_missing"]+=1
                missing.append({
                    "original_source_mesh":name,
                    "original_BRES":stem,
                    "original_source_triangles":len(m["faces"]),
                    "original_source_vertex_count":int(m["vertex_count"]),
                    "source_bbox_center":[round(float(x),6) for x in center],
                    "source_bbox_min":[round(float(x),6) for x in lo],
                    "source_bbox_max":[round(float(x),6) for x in hi],
                    "original_vertex_position_family":kind,
                    "native_canonical_node_record_offsets":[n["offset"] for n in par],
                    "native_canonical_node_XYZ":[[round(float(x),6) for x in n["xyz"]] for n in par],
                    "native_pivot_records":[n["offset"] for n in pivot],
                    "proven_full_parent_pivot_mesh_edges":len(edges),
                    "runtime_world_placement_proven":False,
                })
            if missing:
                records.append({"source_BRES":stem,"sha256":hashlib.sha256(raw).hexdigest(),
                                "unresolved_original_meshlists":missing})
                print("G56",stem,"missing",len(missing),
                      "origin",sum(r["original_vertex_position_family"]=="source_bbox_origin_centered" for r in missing),
                      "nonzero",sum(r["original_vertex_position_family"]=="source_bbox_baked_nonzero" for r in missing))
    assert count["all_original_meshes"]==370
    assert count["G55_source_parent_pivot_links"]==296
    assert count["unresolved_special_meshes"]==74
    assert count["unresolved_original_triangles"]==478
    assert count["canonical_node_present"]==74
    assert count["source_bbox_origin_centered"]==49
    assert count["source_bbox_baked_nonzero"]==25
    report={"stage":"G56_source_only","original_2010_BRES_source_count":10,
            "original_source_center_epsilon":EPS,"counts":dict(count),
            "unresolved_light_original_BRES":records,
            "zero_center_is_NOT_proof_parent_only_transform":True,
            "nonzero_center_is_NOT_proof_source_world_coordinates":True,
            "no_speculative_special_light_mesh_placement":True,
            "no_original_mesh_edits":True,"NO_VPK_OR_VITA_DEVICE_TEST":True}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print("PASS G56",dict(count),"74 special BRES source billboard meshes NOT guessed into map")

def test():
    a,center,_,_=source_center_class([[-2,-1,-3],[2,1,3]])
    assert a=="source_bbox_origin_centered" and np.linalg.norm(center)==0
    a,center,_,_=source_center_class([[10,11,-3],[14,13,3]])
    assert a=="source_bbox_baked_nonzero" and np.linalg.norm(center)>10
    print("PASS G56 deterministic synthetic raw source mesh classifications")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--zip",type=Path)
    p.add_argument("--out",type=Path);p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:test()
    elif a.zip and a.out:run(a.zip,a.out)
    else:p.error("Need --zip and --out for genuine sources")
