#!/usr/bin/env python3
"""Visualize proposed smooth transitions BETWEEN real baked source pose frames.

Inputs = user-original BRES triangle topology and exact already-baked original
2010 IM2V vertices. Intermediate 120ms blending is NEW engineering design, NOT
the original game's recovered transition timings. No Vita executable/VPK.
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


def read_im2v(path: Path, expected_nv: int):
    data = path.read_bytes()
    magic, nv, frames, fps, ms = struct.unpack_from("<4sIIII", data)
    if magic != b"IM2V" or nv != expected_nv or fps != 20 or ms < 1 or frames < 2:
        raise ValueError("not a validated source IM2V: " + path.name)
    if len(data) != 20 + nv*frames*12:
        raise ValueError("IM2V length mismatch: " + path.name)
    return np.frombuffer(data, dtype="<f4", offset=20).reshape(frames, nv, 3)


def draw_strip(armor, poses, faces, names, dst):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(14.3, 5.8), dpi=130, facecolor="#0b1424")
    fig.suptitle(f"G8 HOST TRANSITION PROTOTYPE — {armor.upper()}",
                 color="white", fontsize=13)
    allpts = np.concatenate(poses)
    origin = (allpts.min(axis=0)+allpts.max(axis=0))/2
    radius = max(float(np.ptp(allpts, axis=0).max())*.59,.2)
    for n,(p,alpha) in enumerate(zip(poses,(0.,.25925926,.74074074,1.))):
        ax=fig.add_subplot(1,4,n+1,projection="3d",facecolor="#101c2c")
        polys=p[faces[::2]]
        c="#9cb7be" if armor=="ironman" else "#a5aeb7"
        ax.add_collection3d(Poly3DCollection(polys,linewidths=.02,
                             edgecolors=(.1,.16,.21,.16),facecolors=c))
        for k,setlim in enumerate((ax.set_xlim,ax.set_ylim,ax.set_zlim)):
            setlim(float(origin[k]-radius),float(origin[k]+radius))
        ax.set_box_aspect((1,1,1))
        ax.view_init(elev=8,azim=-68)
        ax.set_axis_off()
        ax.set_title(f"New smooth transition {n}/3\n"
                     f"Blend weight {alpha:.1%}\n"
                     f"{'Original source L MOVE' if n==0 else 'Original source R ATTACK' if n==3 else 'Two verified source poses interpolated'}",
                     color="white",fontsize=7)
    fig.text(.5,.015,
             "OFF-CONSOLE geometry diagnostic | source endpoints authentic; "
             "120ms intermediate XYZ crossfade is a NEW prototype | no Vita runtime claim",
             color="#c8d6ed",ha="center",fontsize=8.5)
    dst.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(dst,bbox_inches="tight",facecolor=fig.get_facecolor())
    plt.close(fig)


def run(ipa: Path, source_dir: Path, out: Path):
    manifest=json.loads((source_dir/"B24_G8_ORIGINAL_40_HOVER_FIRE_MOTION_MANIFEST.json").read_text())
    rows={r["source_animation"].casefold():r for r in manifest["clips"]}
    with zipfile.ZipFile(ipa) as z:
        models=z.read("Payload/IronMan2.app/models")
    model_index=decode(models,".bdae")
    summaries=[]
    for armor,(model_name,nv) in TARGETS.items():
        raw=get_exact(models,model_index,model_name)
        candidates=[m for m in source_meshes(raw) if len(m["positions"])==nv]
        if len(candidates)!=1:
            raise ValueError("original BRES geometry mismatch: "+armor)
        faces=np.asarray(candidates[0]["faces"]).reshape(-1,3).astype(int)
        if faces.max()>=nv or faces.min()<0:
            raise ValueError("non-original triangle range")
        prefix="IronMan" if armor=="ironman" else "Warmachine"
        s1=(prefix+"_Aim_Float_move_L.anim").casefold()
        s2=(prefix+"_Aim_Float_move_R_Att.anim").casefold()
        if s1 not in rows or s2 not in rows:
            raise ValueError("missing certified original 2010 sources")
        a=read_im2v(source_dir/rows[s1]["output"],nv)
        b=read_im2v(source_dir/rows[s2]["output"],nv)
        left=np.array(a[len(a)//2],dtype=np.float64,copy=True)
        right=np.array(b[len(b)//2],dtype=np.float64,copy=True)
        poses=[]
        for t in (0.,1./3,2./3,1.):
            weight=t*t*(3.-2.*t)
            cur=left*(1.-weight)+right*weight
            if not np.isfinite(cur).all() or cur.shape!=(nv,3):
                raise ValueError("invalid interpolated real-source vertex")
            poses.append(cur)
        assert np.array_equal(poses[0],left) and np.array_equal(poses[-1],right)
        dest=out/f"HOST_G8_{armor}_ORIGINAL_Lmove_to_Rattack_4frame_transition.png"
        draw_strip(armor,poses,faces,(s1,s2),dest)
        displacements=[float(np.max(np.abs(p-left))) for p in poses]
        assert all(displacements[i]<=displacements[i+1]+1e-8
                   for i in range(len(displacements)-1))
        summaries.append({
            "armor":armor,"source_from":rows[s1]["source_animation"],
            "source_to":rows[s2]["source_animation"],
            "source_vertices":nv,"source_faces":len(faces),
            "proposed_transition_ms":120,
            "original_game_transition_timing_recovered":False,
            "original_source_baked_endpoints":True,
            "frames_generated":4,
            "max_vertex_displacement_from_left_pose":displacements,
            "preview":dest.name,
        })
        print("PASS 4 FRAME G8 ORIGINAL SOURCE BLEND",armor,"preview",dest.name,
              "max_move",displacements[-1])
    out.mkdir(parents=True,exist_ok=True)
    (out/"HOST_G8_SOURCE_TRANSITION_STRIP_MANIFEST.json").write_text(
        json.dumps(summaries,indent=2)+"\n")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ipa",required=True,type=Path)
    p.add_argument("--source-dir",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    run(a.ipa,a.source_dir,a.out)


if __name__=="__main__":
    main()
