#!/usr/bin/env python3
"""Original C1L1 scene ground/atlas coverage independent source forensic.

Uses B11 owner original GLB (2010 BDAE exported), UV/material archives and
temporary owner IPA texture name index. No invented surface or texture link.
"""
from __future__ import annotations
import argparse,collections,json,math,zipfile
from pathlib import Path
import numpy as np
from export_b24_c1_gpu_mesh import SOURCE,MEMBER,decode_glb,arr,category
from b24_owner_pack_extract import decode

def in_tri(px,py,a,b,c):
    d=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(d)<1e-12:return None
    u=((b[1]-c[1])*(px-c[0])+(c[0]-b[0])*(py-c[1]))/d
    v=((c[1]-a[1])*(px-c[0])+(a[0]-c[0])*(py-c[1]))/d
    w=1-u-v
    if min(u,v,w)<-1e-5:return None
    return u*a[2]+v*b[2]+w*c[2]

def report(owner_ipa,out):
    with zipfile.ZipFile(SOURCE) as z:
        doc,binary=decode_glb(z.read(MEMBER))
    categories=collections.Counter()
    tris={}
    xy_ranges={}
    face_normals={}
    for mesh in doc["meshes"]:
        name=mesh["name"]
        group=category(name)
        p=mesh["primitives"][0]
        pos=np.asarray(arr(doc,binary,p["attributes"]["POSITION"]),dtype=np.float64)
        idx=np.asarray(arr(doc,binary,p["indices"]),dtype=np.uint32).reshape(-1,3)
        triangle=pos[idx]
        if len(triangle)==0:continue
        categories[group]+=len(triangle)
        if group not in tris:tris[group]=[]
        tris[group].append(triangle)
    samples=[]
    for grp in (0,1,2,3):
        tr=np.concatenate(tris[grp])
        norm=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0])
        magnitude=np.linalg.norm(norm,axis=1)
        steep=(magnitude>1.e-5)&(np.abs(norm[:,2])/np.maximum(magnitude,1.e-6)<.58)
        upward=(magnitude>1.e-5)&(np.abs(norm[:,2])/np.maximum(magnitude,1.e-6)>.75)
        face_normals[str(grp)]={"faces":len(tr),"near_horizontal":int(upward.sum()),
            "steep":int(steep.sum()),"min_xyz":tr.reshape(-1,3).min(axis=0).tolist(),
            "max_xyz":tr.reshape(-1,3).max(axis=0).tolist()}
    g=np.concatenate(tris[0])
    for x,y in ((0,0),(0,8),(8,0),(30,30),(-20,-20),(-100,0),(0,-100)):
        matching=[]
        for t in g:
            z=in_tri(x,y,*t)
            if z is not None:matching.append(round(float(z),4))
        samples.append({"xy":[x,y],"original_ground_z_candidates":sorted(matching),
                        "has_real_floor_surface":bool(matching)})
    with zipfile.ZipFile(owner_ipa) as z:
        textures=z.read("Payload/IronMan2.app/textures")
    rows=decode(textures,".tga")
    names=sorted(x["name"] for x in rows.values()) if isinstance(rows,dict) else []
    # name-only texture index, no raw original PVR texture contents in report
    city=[n for n in names if "C1L1" in n.upper() or "CITY" in n.upper()
          or "BUILD" in n.upper() or "ROAD" in n.upper()]
    reticles=[n for n in names if any(t in n.upper() for t in
       ("RETIC","TARGET","CROSS","CURSOR","LOCK","AIM","HUD","SIGHT","VISOR"))]
    result={"2010_original_glb_groups":face_normals,"city_z_ground_samples":samples,
         "2010_packed_texture_total":len(names),"city_texture_name_candidates":city,
         "2010_reticle_texture_name_candidates":reticles,
         "note":"Asset name alone is NOT confirmed per-surface material pointer or in-game reticle binding"}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print("C1L1_FACE_GROUPS",face_normals)
    print("C1L1_GROUND_Z_AT_PLAYER",samples)
    print("C1L1_TEXTURE_NAMED_CANDIDATES",city[:100])
    print("C1L1_RETICLE_NAMED_CANDIDATES",reticles[:80])
    print("C1L1_TOTAL_ORIGINAL_TEXTURES",len(names))
    print("PASS original city source ground geometry coverage and user-owned true game texture name inventory, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True);a=p.parse_args()
 report(a.ipa,a.out)
