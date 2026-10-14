#!/usr/bin/env python3
"""2010 original warmachine.bdae shoulder weapon socket forensic metadata.

No assumption that a source rig Shoulder joint is the actual machine gun
muzzle or left rocket pod. Extract original named nodes and candidate gun
strings; only authentic bound scene graph pointers could prove mount sockets.
No VPK, no dummy gun transforms, no generic hardpoint promoted to original.
"""
from __future__ import annotations
import argparse,json,re,tempfile,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact
from b24_hover_fire_authentic_pose_preview import source_meshes
from b24_underwater_source_34_im2v_bake import load_original_b13

PATTERN=re.compile(r"shoulder|rocket|missile|muzzle|gatl|gun|barrel|weapon|turret|m134|launch|fire|aim",re.I)
def run(ipa,out):
    with zipfile.ZipFile(ipa) as z:
        models=z.read("Payload/IronMan2.app/models")
    raw=get_exact(models,decode(models,".bdae"),"warmachine.bdae")
    with tempfile.TemporaryDirectory(prefix="b24_wm_2010_socket_source_") as temp:
        b13=load_original_b13(Path(temp))
        nodes=b13.parse_rig(raw)
        rest_world=b13.worlds(nodes)
    names=[]
    for n in nodes:
        v=n.get("name")
        if isinstance(v,str):
            names.append(v)
    candidates=[{"name":name,"kind":"rig_node_name_only"}
                for name in names if PATTERN.search(name)]
    fields=[{"name":name,"kind":"source_asset_ascii_string_only",
             "occurrences":[m.start() for m in re.finditer(re.escape(name.encode()),raw)][:8]}
             for name in sorted(set(
              m.group(0).decode("ascii",errors="ignore")
              for m in re.finditer(rb"[A-Za-z][A-Za-z0-9_ .-]{3,65}",raw)
              if PATTERN.search(m.group(0).decode("ascii",errors="ignore"))
             ))[:90]]
    meshes=source_meshes(raw)
    source_rest=[]
    for node in nodes:
        name=node.get("name","")
        if not isinstance(name,str) or not PATTERN.search(name):
            continue
        world=rest_world.get(name)
        if world is None:
            raise ValueError("original gun scene rig world transform missing: "+name)
        import numpy as np
        matrix=np.asarray(world,dtype=np.float64)
        if matrix.shape!=(4,4) or not np.isfinite(matrix).all():
            raise ValueError("bad genuine B13 world transform for "+name)
        translation=[float(matrix[i,3]) for i in range(3)]
        source_rest.append({
            "name":name,
            "original_bres_record_offset":node.get("offset"),
            "node_data_keys":sorted(node),
            "original_world_translation_xyz":translation,
            "original_world_matrix_4x4":matrix.tolist(),
            "source_parent_relation_proven":False,
            "verified_particle_emitter":False,
        })
    rest_by_name={x["name"]:x for x in source_rest}
    proposed_pairs=[]
    for side in ("L","R"):
        a=rest_by_name.get("Dummy_Gun_"+side+"-node")
        b=rest_by_name.get("DummyE_Gun_"+side+"-node")
        if a and b:
            import math
            p=a["original_world_translation_xyz"]
            q=b["original_world_translation_xyz"]
            distance=math.sqrt(sum((q[i]-p[i])**2 for i in range(3)))
            proposed_pairs.append({
                "original_name_side":side,
                "original_dummy_node":a["name"],
                "original_dummyE_node":b["name"],
                "world_distance":distance,
                "E_label_is_author_verified_emitter":False,
            })
    summary={
      "owner_2010_source_file":"warmachine.bdae",
      "original_scene_rig_node_count":len(nodes),
      "original_source_meshes":[{"name":m.get("name",""),"vertices":len(m["positions"])}
                                for m in meshes],
      "named_rig_socket_candidates":candidates,
      "rest_pose_weapon_node_transforms":source_rest,
      "source_dummy_to_dummyE_deltas":proposed_pairs,
      "source_ascii_name_candidates":fields,
      "G8_verified_2010_skin_vertex_count":1292,
      "left_rocket_socket_proven":False,
      "right_gatling_socket_proven":False,
      "physical_2010_attachment_scene_graph_resolved":False,
      "note":"A shoulder bone/label is not automatically the gun barrel exit; no invented port offsets.",
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(summary,indent=2)+"\n")
    print("WM_2010_BRES_RIG_NODE_COUNT",len(nodes))
    print("WM_2010_MESH_COUNTS",summary["original_source_meshes"])
    print("WM_2010_SHOULDER_NAMED_CANDIDATES",candidates[:30])
    print("WM_2010_ORIGINAL_REST_WORLD_WEAPON_NODES",[(i["name"],i["original_world_translation_xyz"],i["original_bres_record_offset"]) for i in source_rest])
    print("WM_2010_ORIGINAL_DUMMY_TO_DUMMYE_DISTANCE",proposed_pairs)
    print("WM_2010_SOURCE_ASCII_WEAPON_NAMES",[(x["name"],x["occurrences"]) for x in fields[:50]])
    print("PASS original model 2010 shoulder mount forensic SOURCE_ONLY; two muzzle transforms UNPROVEN")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--ipa",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    run(a.ipa,a.report)
