#!/usr/bin/env python3
"""Original owner 2010 War Machine gun channel kinematic forensic.

World matrices are reconstructed from authentic BRES parent hierarchy and
source .anim tracks via the original B13 evaluator. Source-only, no VPK.
Gun01–Gun04 labels are not yet verified as exact weapon emitter sockets.
"""
from __future__ import annotations
import argparse,json,tempfile,zipfile
from pathlib import Path
import numpy as np
from b24_owner_pack_extract import decode,get_exact
from b24_underwater_source_34_im2v_bake import load_original_b13

GUNS=("Gun01-node","Gun02-node","Gun03-node","Gun04-node",
      "Dummy_Green_Gun-node","DummyE_Green_Gun-node",
      "Dummy_Gun_L-node","DummyE_Gun_L-node",
      "Dummy_Gun_R-node","DummyE_Gun_R-node")
ANIMATIONS=(
 "Warmachine_Aim_Float_idle.anim",
 "Warmachine_Aim_Float_move_R_Att.anim",
 "Warmachine_Aim_M_Float_move_L_Att.anim",
 "Warmachine_Aim_Fly_M.anim",
 "Warmachine_Attack_Float_move_R.anim",
 "Warmachine_Aim_Ground_move_R_Att.anim",
)

def parent_path(name,nodes):
    out=[]
    while name:
        if name not in nodes or name in out:
            raise ValueError("invalid original parent graph")
        out.append(name)
        name=nodes[name]["parent"]
    return out

def matrix(value):
    a=np.asarray(value,dtype=np.float64)
    if a.shape!=(4,4) or not np.isfinite(a).all() or np.max(np.abs(a))>1e5:
        raise ValueError("invalid original authored node matrix")
    return a

def analyze(ipa,out,figure):
    with zipfile.ZipFile(ipa) as z:
        packed=z.read("Payload/IronMan2.app/models")
        packed_animations=z.read("Payload/IronMan2.app/anims")
    raw=get_exact(packed,decode(packed,".bdae"),"warmachine.bdae")
    animations=decode(packed_animations,".anim")
    with tempfile.TemporaryDirectory(prefix="g8_wm_original_gun_") as temp:
        b13=load_original_b13(Path(temp))
        nodes=b13.parse_rig(raw)
        by_name={n["name"]:n for n in nodes}
        if len(nodes)!=112 or len(by_name)!=112 or any(n not in by_name for n in GUNS):
            raise ValueError("original source War Machine 112-node graph drift")
        rest=b13.worlds(nodes)
        children={n["name"]:[] for n in nodes}
        for n in nodes:
            if n["parent"]:
                children[n["parent"]].append(n["name"])
        record={
           "source":"2010 owner IPA warmachine.bdae and authored .anim",
           "rig_count":112,"parent_graph_verified":True,
           "muzzle_side_or_particle_emitter_proven":False,
           "Vita_GPU_animation_verified":False,
           "nodes":{},"animations":{}
        }
        for key in GUNS:
            n=by_name[key];m=matrix(rest[key])
            record["nodes"][key]={
                "offset":n["offset"],"parent":n["parent"],
                "ancestry_to_root":parent_path(key,by_name),
                "authentic_child_nodes":children[key],
                "source_rest_world_xyz":m[:3,3].tolist(),
                "source_rest_matrix":m.tolist()
            }
        for name in ANIMATIONS:
            source=get_exact(packed_animations,animations,name)
            a=b13.decode_anim(source)
            ms=a.duration_ms
            if not 0<ms<10000:raise ValueError("original authored animation duration")
            times=sorted(set((0,ms//4,ms//2,ms*3//4,ms)))
            source_channels=set(a.names)
            matrices={key:[] for key in GUNS}
            # Compute entire original hierarchy once at each timestamp, not
            # one pose-per-node. This preserves authored parent movement.
            for t in times:
                w=b13.worlds(nodes,a,t)
                for key in GUNS:
                    m=matrix(w[key])
                    matrices[key].append({
                        "t_ms":t,"world_xyz":m[:3,3].tolist(),
                        "world_basis":m[:3,:3].tolist(),
                    })
            entries={}
            for key in GUNS:
                sample=matrices[key]
                positions=np.asarray([s["world_xyz"] for s in sample])
                basis=np.asarray([s["world_basis"] for s in sample])
                entries[key]={
                    "authored_direct_track":key.removesuffix("-node") in source_channels,
                    "max_world_displacement":float(np.linalg.norm(positions-positions[0],axis=1).max()),
                    "max_world_orientation_delta":float(np.abs(basis-basis[0]).max()),
                    "samples":sample,
                }
            base=matrices["Dummy_Green_Gun-node"]
            tip=matrices["DummyE_Green_Gun-node"]
            vectors=[]
            for b,e in zip(base,tip):
                v=np.asarray(e["world_xyz"])-np.asarray(b["world_xyz"])
                distance=float(np.linalg.norm(v))
                if not np.isfinite(distance) or distance<1.e-7:
                    raise ValueError("original gun marker source vector degeneracy")
                vectors.append({
                    "time_ms":b["t_ms"],
                    "original_Dummy_to_DummyE_distance":distance,
                    "original_Dummy_to_DummyE_unit_direction":(v/distance).tolist(),
                    "original_tip_model_space_xyz":e["world_xyz"],
                })
            record["animations"][name]={
                "gun03_source_marker_direction_candidate":vectors,
                "candidate_markers_are_proven_muzzle":False,
                "duration_ms":ms,"authored_channel_count":len(a.names),
                "samples_t_ms":times,"gun_nodes":entries
            }
            print("2010_WM_GUN_WORLD",name,
                  [(key,round(entries[key]["max_world_displacement"],6),
                    round(entries[key]["max_world_orientation_delta"],6),
                    entries[key]["authored_direct_track"]) for key in GUNS[:4]],flush=True)
        print("2010_WM_GUN04_TRUE_CHILD_NODES",children["Gun04-node"])
        print("2010_WM_GUN03_SOURCE_MARKER_SEPARATION",
              {clip:round(entry["gun03_source_marker_direction_candidate"][0]["original_Dummy_to_DummyE_distance"],6)
               for clip,entry in record["animations"].items()})
        print("2010_WM_GUN_PARENT_LINKS",
             {k:record["nodes"][k]["parent"] for k in GUNS},flush=True)
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(record,indent=2)+"\n")
        if figure:
            draw(record,figure)
        print("PASS 2010 genuine 112-node source 6-clip animated gun transforms. Muzzle event sockets UNPROVEN. NO VPK.",flush=True)

def draw(record,figure):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    motions=list(record["animations"])
    colors=("#86caf4","#f9b57b","#86d4b1","#e5a3de")
    fig=plt.figure(figsize=(14,9),dpi=125,facecolor="#0c1828")
    for i,clip in enumerate(motions):
        ax=fig.add_subplot(2,3,i+1,projection="3d",facecolor="#142036")
        pts_all=[]
        for k in range(1,5):
            key="Gun%02d-node"%k
            frames=record["animations"][clip]["gun_nodes"][key]["samples"]
            pts=np.asarray([s["world_xyz"] for s in frames])
            pts_all.extend(pts.tolist())
            ax.plot(pts[:,0],pts[:,1],pts[:,2],"-o",color=colors[k-1],
                    linewidth=2,markersize=3,label="Gun%02d"%k)
        allp=np.array(pts_all)
        center=allp.mean(axis=0)
        radius=max(.07,float(np.ptp(allp,axis=0).max())*.7)
        ax.set_xlim(center[0]-radius,center[0]+radius)
        ax.set_ylim(center[1]-radius,center[1]+radius)
        ax.set_zlim(center[2]-radius,center[2]+radius)
        ax.set_box_aspect((1,1,1))
        ax.view_init(elev=24,azim=-62)
        ax.tick_params(labelsize=6,colors="#bdcadb")
        ax.set_title(clip.removeprefix("Warmachine_").removesuffix(".anim"),
                     fontsize=9,color="white")
        if i==0:ax.legend(loc="upper left",fontsize=7)
    fig.suptitle("TRUE 2010 WAR MACHINE GUN01–04 ANIMATED WORLD NODES",
                 color="white",fontsize=14,y=.98)
    fig.text(.5,.014,
        "Host forensic: original BRES scene + B13 animation keyframes at 0/25/50/75/100%. "
        "NOT muzzle emitter assignment or Vita screenshot.",
        ha="center",color="#cbd8e8",fontsize=8.4)
    figure.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(figure,bbox_inches="tight",facecolor=fig.get_facecolor())
    plt.close(fig)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--ipa",required=True,type=Path)
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--image",type=Path)
    a=p.parse_args()
    analyze(a.ipa,a.report,a.image)
