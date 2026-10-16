#!/usr/bin/env python3
"""G64 source-verified material rebind for G57 C1L1 WebGL2 + GLB.
No invented BRES UV, no gameplay/Vita claims; 74 unlinked meshes remain hidden.
"""
import argparse,base64,collections,io,json,re
from pathlib import Path
import numpy as np
from PIL import Image
import trimesh
from trimesh.visual.material import PBRMaterial
from b24_g64_source_original_C1L1_BRES_40_60_shader_sampler_recovery import main as native_proof

def tag(html,name):
    x=re.search(r'<script id="'+re.escape(name)+r'"[^>]*>(.*?)</script>',html,re.S)
    if not x:raise ValueError("G57 missing "+name)
    return x.group(1)

def run(html_path,bres_zip,output):
    output.mkdir(parents=True,exist_ok=True)
    native_proof(bres_zip,output/"G64_AUTHENTIC_ORIGINAL_SHADER40_60_NATIVE_PROVENANCE.json")
    html=html_path.read_text(encoding="utf8")
    old=tag(html,"payload")
    data=json.loads(old)
    assert len(data["batches"])==386
    assert sum(x["tris"] for x in data["batches"])==22441
    edits=[]
    for b in data["batches"]:
        if b["material"]!="c1l1_3building" or b["status"]!="UV-no-source-diffuse":continue
        assert b["original_uv_mesh_positive"] and not b["tga"]
        b["tga"]="c1l1_building.tga"
        b["status"]="source-texture-and-UV"
        b["source_texture_named"]=True
        edits.append((b["mesh"],b["tris"]))
    assert sum(n for _,n in edits)==1683 and len(edits)==11
    atlas={x["name"].lower():Image.open(io.BytesIO(base64.b64decode(x["base64"]))).convert("RGBA") for x in data["originalPVRs"]}
    assert len(atlas)==24 and "c1l1_building.tga" in atlas
    total=sum(b["tris"] for b in data["batches"] if b["original_uv_mesh_positive"] and (b["tga"] or "").lower() in atlas)
    assert total==20457
    data["original_source_PVR_textured_faces"]=total
    data["G64_NATIVE_SHADER_40B_NEW_BUILDING_TEXTURED_FACES"]=1683
    data["G64_GLOBE_MATERIAL20_21_UV_SHADER_REBUILT"]=False
    data["G64_NATIVE_ORIGINAL_REMAINING_NOT_UV_TEXTURED"]=1984
    data["NO_VPK"]=True
    updated=html.replace(old,json.dumps(data,separators=(",",":"),ensure_ascii=False),1)
    label=('<p style="padding:12px;background:#123529;border-left:4px solid #5db98e">'
       '<b>G64 gerçek BRES doku eşlemesi:</b> 7 özgün kaynak dosyasında 40B shader'
       'property tablosu ile bulunan <code>c1l1_building.tga</code> 1683 üçgene bağlandı.'
       ' 20.457 / 22.441 mesh üçgeni artık kaynak UV + özgün doku taşıyor.'
       ' Küre UV/shader ve gizli 74 özel mesh henüz çözülmedi. VPK yapılmadı.</p>')
    assert "<body>" in updated
    updated=updated.replace("<body>","<body>"+label,1)
    (output/"G64_SOURCE_REAL_UV_PVR_RECOVERED_VIEWER.html").write_text(updated,encoding="utf8")
    pos=np.frombuffer(base64.b64decode(tag(html,"rawpositions")),dtype="<f4").reshape(-1,3)
    uv=np.frombuffer(base64.b64decode(tag(html,"rawuv")),dtype="<f4").reshape(-1,2)
    faces=np.frombuffer(base64.b64decode(tag(html,"rawindices")),dtype="<u4").reshape(-1,3)
    assert pos.shape==(37946,3) and uv.shape==(37946,2) and faces.shape==(22919,3)
    groups=collections.defaultdict(lambda:[[],[]])
    for b in data["batches"]:
        ids=faces[b["start"]//3:b["start"]//3+b["tris"]].reshape(-1)
        k=(b["tga"] or "").lower() if b["original_uv_mesh_positive"] else ""
        if k not in atlas:k="__unknown_"+b["group"]
        groups[k][0].append(pos[ids])
        groups[k][1].append(uv[ids])
    scene=trimesh.Scene()
    colors={"ground":[109,147,117,255],"urban":[142,159,176,255],
            "vehicles":[188,150,102,255],"lights":[163,154,168,255]}
    for i,(k,(v,t)) in enumerate(sorted(groups.items())):
        v=np.concatenate(v);t=np.concatenate(t)
        m=trimesh.Trimesh(vertices=v,faces=np.arange(len(v)).reshape(-1,3),process=False)
        if k in atlas:
            mat=PBRMaterial(baseColorTexture=atlas[k],metallicFactor=0,roughnessFactor=.93,doubleSided=True)
            m.visual=trimesh.visual.TextureVisuals(uv=t,material=mat)
        else:m.visual.face_colors=colors[k.removeprefix("__unknown_")]
        scene.add_geometry(m,geom_name=f"G64_{i}_{k.replace('.tga','')}")
    dest=output/"G64_ORIGINAL_NATIVE_20457_TEXTURED_SCENE.glb"
    scene.export(str(dest))
    reloaded=trimesh.load(dest,force="scene",process=False)
    assert sum(len(g.faces) for g in reloaded.geometry.values())==22441
    report={"stage":"G64","source_meshes":296,"source_triangles":22441,
      "old_native_textured_faces":18774,"new_shader40_texture_recovery_faces":1683,
      "current_source_UV_PVR_textured_faces":20457,"remaining_non_source_textured_faces":1984,
      "native_40B_shader_bound_to_correct_atlas":True,"globe_native_UV_shader_proven":False,
      "source_geometry_or_world_transforms_modified":False,
      "Vita_runtime_executed_in_this_job":False,"no_new_VPK":True}
    (output/"G64_MATERIAL_SCENE_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
    print("PASS G64: 20457 exact native UV/PVR triangles and 1683 newly source-verified building faces; 698 sphere special faces still require true UV/shader.")
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--g57html",type=Path,required=True)
    ap.add_argument("--b11zip",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args();run(a.g57html,a.b11zip,a.out)
