#!/usr/bin/env python3
"""2010 source-animated Iron Man/War Machine contact sheets (not Vita images).

Original 2010 BRES triangles + the 304-clip source skin bake frames. Diagnostic
untextured clay view; no procedural/AI poses and no screen capture claims.
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

SELECT={
 "ironman":[
  "IronMan_Walk_F.anim","Ironman_Fly_F.anim","Ironman_Fly_F_RUSH.anim",
  "IronMan_Aim_Float_move_L_Att.anim","IronMan_Aim_Float_Beam1.anim",
  "IronMan_Ground_Combo_1.anim","IronMan_Air_CounterAtt.anim",
  "IronMan_Air_land_s_start.anim"],
 "warmachine":[
  "Warmachine_Aim_Float_idle.anim",
  "Warmachine_Aim_Float_move_R_Att.anim",
  "Warmachine_Aim_Fly_M.anim",
  "Warmachine_Fly_Att_s.anim",
  "Warmachine_Aim_Ground_move_F.anim",
  "Warmachine_Aim_M_Float_move_L_Att.anim",
  "Warmachine_Attack_Float_move_R.anim",
  "Warmachine_Fly_Att_ready.anim"],
}

def read_mid(path,nv):
    b=path.read_bytes()
    magic,n,frames,fps,duration=struct.unpack_from("<4sIIII",b)
    if magic!=b"IM2V" or n!=nv or fps!=20 or frames<1 or len(b)!=20+nv*frames*12:
        raise ValueError(f"invalid source original skin animation stream {path.name}")
    frame_no=(frames-1)//2
    return np.frombuffer(b,dtype="<f4",count=nv*3,
                         offset=20+frame_no*nv*12).reshape(nv,3).astype(np.float64)

def draw(armor,frames,faces,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig=plt.figure(figsize=(16,9.2),dpi=125,facecolor="#0b1424")
    fig.suptitle("IRON MAN 2 (2010) ORIGINAL SOURCE POSES | "+armor.upper(),
                 color="white",fontsize=16,y=.99)
    all_xyz=np.concatenate([f["xyz"] for f in frames])
    center=(all_xyz.min(axis=0)+all_xyz.max(axis=0))*.5
    radius=max(.15,float(np.ptp(all_xyz,axis=0).max())*.58)
    for i,row in enumerate(frames):
        ax=fig.add_subplot(2,4,i+1,projection="3d",facecolor="#101c2c")
        facecolor="#b7c1cc" if armor=="warmachine" else "#b3abb0"
        ax.add_collection3d(Poly3DCollection(row["xyz"][faces[::2]],linewidths=.01,
                           edgecolors=(.05,.07,.1,.07),facecolors=facecolor))
        for index,setter in enumerate((ax.set_xlim,ax.set_ylim,ax.set_zlim)):
            setter(float(center[index]-radius),float(center[index]+radius))
        ax.set_box_aspect((1,1,1))
        ax.view_init(elev=8,azim=-68)
        ax.set_axis_off()
        ax.set_title(f"{row['name']}\n{row['duration_ms']}ms | {row['frames']} samples",
                     color="white",fontsize=8)
    fig.text(.5,.015,
             "HOST DIAGNOSTIC ONLY: authentic BRES geometry + source animation frames, "
             "clay material (not restored textures), NOT G8 Vita gameplay",
             ha="center",color="#c7d1e4",fontsize=10)
    fig.savefig(out,bbox_inches="tight",facecolor=fig.get_facecolor())
    plt.close(fig)

def run(ipa,assets,out):
    meta=json.loads((assets/"B24_ORIGINAL_304_SOURCE_BAKE_COVERAGE.json").read_text())
    if meta["processed"]!=304 or meta["baked"]!=304:
        raise ValueError("not fully converted original source 304 catalog")
    records={r["source_animation"].casefold():r for r in meta["records"]}
    with zipfile.ZipFile(ipa) as z:
        packed=z.read("Payload/IronMan2.app/models")
    index=decode(packed,".bdae")
    out.mkdir(parents=True,exist_ok=True)
    summary=[]
    for armor,(source_name,nv) in TARGETS.items():
        raw=get_exact(packed,index,source_name)
        source=[m for m in source_meshes(raw) if len(m["positions"])==nv]
        if len(source)!=1:raise ValueError(f"wrong source BRES geometry for {armor}")
        faces=np.asarray(source[0]["faces"]).reshape(-1,3).astype(int)
        if faces.max()>=nv or faces.min()<0:raise ValueError("source face range")
        chosen=[]
        for name in SELECT[armor]:
            row=records.get(name.casefold())
            if not row or row["status"]!="SOURCE_SKINNED_BAKED":
                raise ValueError("required real source pose not converted: "+name)
            xyz=read_mid(assets/row["im2v_filename"],nv)
            chosen.append({"name":row["source_animation"],"xyz":xyz,
                           "frames":row["frame_count"],
                           "duration_ms":row["duration_ms"]})
        name=f"B24_G8_HOST_ORIGINAL_{armor}_8_flight_combat_pose_comparison.png"
        draw(armor,chosen,faces,out/name)
        summary.append({"armor":armor,"source_BRES":source_name,
                        "original_vertices":nv,
                        "original_triangle_count":len(faces),
                        "real_2010_source_pose_names":[c["name"] for c in chosen],
                        "source_preview":name,"Vita_runtime_verified":False})
        print("PASS ORIGINAL 8-PANEL SOURCE CHARACTER PREVIEW",armor,
              "triangles",len(faces),"image",name)
    (out/"B24_304_HOST_POSE_PREVIEW_MANIFEST.json").write_text(
        json.dumps(summary,indent=2)+"\n")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ipa",type=Path,required=True)
    p.add_argument("--assets",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.ipa,a.assets,a.out)

if __name__=="__main__":
    main()
