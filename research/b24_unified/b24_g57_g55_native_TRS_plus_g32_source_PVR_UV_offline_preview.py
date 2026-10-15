#!/usr/bin/env python3
"""G57 source-only: join G55 real native C1L1 parent→pivot mesh positions
to G32 independently source-verified PVR diffuse/UV. NO runtime shader,
touchHLE frame, Vita device proof or VPK. The 74 unlinked meshes stay hidden.
Input archives are downloaded from verified private GH Actions artifacts.
"""
from __future__ import annotations
import argparse,base64,collections,contextlib,io,json,re,zipfile
from pathlib import Path
import numpy as np
from PIL import Image

STEMS=["C1L1_ground_001","C1L1_obj_001","C1L1_obj_002","C1L1_obj_003",
       "C1L1_obj_004","C1L1_light_001","C1L1_light_002",
       "C1L1_light_003","C1L1_car_01","C1L1_car_02"]

def tag(html,name):
    m=re.search(r'<script id="'+re.escape(name)+r'"[^>]*>(.*?)</script>',html,re.S)
    if m is None:raise ValueError("G32 source HTML missing "+name)
    return m.group(1)

def replace_once(s,a,b):
    if s.count(a)!=1:raise ValueError("expected exactly one template field "+a[:60])
    return s.replace(a,b)

def main(g32_html,sourcezip,g55glb,out):
    import trimesh
    from trimesh.visual.material import PBRMaterial
    out.mkdir(parents=True,exist_ok=True)
    html=g32_html.read_text(encoding="utf8")
    raw=tag(html,"payload")
    payload=json.loads(raw)
    pos=np.frombuffer(base64.b64decode(tag(html,"rawpositions")),dtype="<f4").reshape(-1,3).copy()
    uv=np.frombuffer(base64.b64decode(tag(html,"rawuv")),dtype="<f4").reshape(-1,2)
    faces=np.frombuffer(base64.b64decode(tag(html,"rawindices")),dtype="<u4").reshape(-1,3)
    assert len(pos)==len(uv)==37946 and len(faces)==22919 and len(payload["batches"])==460
    with zipfile.ZipFile(sourcezip) as za:
        ctx={"__name__":"g57_authentic_BRES_source","__file__":"bdae_scene_parser.py"}
        exec(compile(za.read("bdae_scene_parser.py"),"bdae_scene_parser.py","exec"),ctx)
        original=[]
        for stem in STEMS:
            with contextlib.redirect_stdout(io.StringIO()):
                meshes,_=ctx["parse"](za.read("original_models/"+stem+".bdae"))
            for i,m in enumerate(meshes):
                original.append((stem+"_"+str(i),stem+"__"+m["name"],m))
    assert len(original)==370
    original_bymesh=collections.defaultdict(list)
    for b in payload["batches"]:original_bymesh[b["mesh"]].append(b)
    g55=trimesh.load(g55glb,force="scene",process=False)
    source_xyz=pos.copy()
    valid=set();check_tri=check_v=0
    for key,gname,m in original:
        batch=original_bymesh[key]
        ti=batch[0]["start"]//3
        tj=(batch[-1]["start"]+batch[-1]["count"])//3
        fv=np.asarray(m["faces"],dtype=np.uint32).reshape(-1,3)
        v=np.asarray(m["positions"],dtype=np.float32)
        assert tj-ti==len(fv)
        vi=int(faces[ti:tj].min())
        assert np.array_equal(faces[ti:tj],fv+vi),(key,"face index changed")
        assert np.array_equal(pos[vi:vi+len(v)],v),(key,"source XYZ changed")
        if gname in g55.geometry:
            mg=g55.geometry[gname]
            world=np.asarray(mg.vertices,dtype=np.float32)
            assert len(world)==len(v) and np.array_equal(mg.faces,fv)
            source_xyz[vi:vi+len(v)]=world
            valid.add(key)
            check_tri+=len(fv)
            check_v+=len(v)
    assert len(valid)==296 and check_tri==22441 and check_v==37089
    batches=[b for b in payload["batches"] if b["mesh"] in valid]
    assert sum(b["tris"] for b in batches)==22441
    atlas={a["name"].lower():Image.open(io.BytesIO(base64.b64decode(a["base64"]))).convert("RGBA")
           for a in payload["originalPVRs"]}
    assert len(atlas)==24
    groups=collections.defaultdict(lambda:[[],[]])
    textured=0
    for b in batches:
        candidate=str(b.get("tga") or "").lower()
        verified=bool(b.get("original_uv_mesh_positive") and candidate in atlas)
        k=candidate if verified else ("__UNKNOWN_"+b["group"])
        i=b["start"]//3
        ids=faces[i:i+b["tris"]].reshape(-1)
        groups[k][0].append(source_xyz[ids])
        groups[k][1].append(uv[ids])
        if verified:textured+=b["tris"]
    assert textured==18774
    outscene=trimesh.Scene()
    fallback={"ground":[109,147,117,255],"urban":[142,159,176,255],
              "vehicles":[188,150,102,255],"lights":[163,154,168,255]}
    for i,(k,(v,u)) in enumerate(sorted(groups.items())):
        v=np.concatenate(v)
        u=np.concatenate(u)
        obj=trimesh.Trimesh(vertices=v,
                           faces=np.arange(len(v),dtype=np.int64).reshape(-1,3),process=False)
        if k in atlas:
            mat=PBRMaterial(baseColorTexture=atlas[k],metallicFactor=0,
                            roughnessFactor=.93,doubleSided=True)
            obj.visual=trimesh.visual.TextureVisuals(uv=u,material=mat)
        else:
            obj.visual.face_colors=fallback[k.removeprefix("__UNKNOWN_")]
        outscene.add_geometry(obj,geom_name="G57_"+str(i)+"_"+k.replace(".tga",""))
    glb=out/"G57_C1L1_TRUE_NATIVE_2010_PVR_UV_TEXTURED.glb"
    outscene.export(str(glb))
    payload["batches"]=batches
    payload["G57_native_meshes"]=296
    payload["G57_native_triangles"]=22441
    payload["G57_true_PVR_uv_faces"]=18774
    payload["G57_unresolved_74_hidden"]=True
    native=np.concatenate([q for v,_ in groups.values() for q in v],axis=0)
    payload["map_center"]=((native.min(axis=0)+native.max(axis=0))/2).tolist()
    html=replace_once(html,raw,json.dumps(payload,ensure_ascii=False,separators=(",",":")))
    html=replace_once(html,tag(html,"rawpositions"),base64.b64encode(source_xyz.astype("<f4").tobytes()).decode())
    html=replace_once(html,"370 özgün mesh</span><span>22.919 gerçek üçgen",
                        "296 kaynak node zincirli mesh</span><span>22.441 özgün dönüşümlü üçgen")
    html=replace_once(html,"let az=-1.2,el=0.56,dist=145,center=d.mc_xyz.slice()",
                        "let az=-1.2,el=0.70,dist=1400,center=d.map_center.slice()")
    html=replace_once(html,'<option value="mc">MC · MainCharacter</option><option value="all">Haritanın tümü</option>',
                        '<option value="mc">MC · MainCharacter</option><option value="all" selected>G57 source harita</option>')
    html=replace_once(html,'focus.value="mc";group.value','focus.value="all";group.value')
    html=replace_once(html,"<div class=\"kpis\">",
       '<p style="padding:10px;border:1px solid #b38b51"><b>G57 özgün oyun veri önizlemesi:</b> 296 kaynak TRS zincirli mesh, 22.441 gerçek üçgen, 24 gerçek PVR ve 18.774 UV-dokulu üçgen. Kalan 74 küçük mesh gizlidir. Orijinal Gameloft iOS shader/visibility/root veya Vita oyunu değildir.</p><div class="kpis">')
    html_file=out/"G57_C1L1_ORIGINAL_BRES_TRS_PVR_UV_INTERACTIVE_OFFLINE.html"
    html_file.write_text(html,encoding="utf8")
    report={"stage":"G57","source_meshes_exact_G55_G32":len(valid),
            "native_node_chain_triangles":22441,"matched_vertices":check_v,
            "PVR_atlas_count":len(atlas),"authentic_per_pixel_UV_PVR_triangles":textured,
            "untextured_material_triangle_count":22441-textured,
            "unlinked_meshes_hidden":74,
            "native_iOS_game_shader_visibility_root_verified":False,
            "real_Vita_fps_test":False,"new_VPK":False}
    (out/"G57_C1L1_SOURCE_EVIDENCE.json").write_text(json.dumps(report,indent=2)+"\n")
    print("PASS G57",report)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--g32html",type=Path,required=True)
    p.add_argument("--b11zip",type=Path,required=True)
    p.add_argument("--g55glb",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    main(a.g32html,a.b11zip,a.g55glb,a.out)
