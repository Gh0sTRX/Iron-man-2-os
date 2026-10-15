#!/usr/bin/env python3
"""G32: source authentic 2010 C1L1 original PVR diffuse and BRES UV in 3D.

EXTENDS G31 (identical actual 370 BRES geometry, no invented triangles)
with per-vertex original native BRES UVs and 2010 owner PVR v2 atlas RGBA.
Source-authored per-material links are used, including exact non-C1L1
CAHP01_c_expo_building.tga. Unproven shader-only material surfaces remain
explicitly diagnostic colors, never guessed textures. This browser-rendered
GLSL is NOT a restored Gameloft shader, render-state, camera or VitaGL.
Alpha/blending/emissive/lighting semantics remain unverified. NO VPK.
"""
from __future__ import annotations
import argparse,base64,collections,contextlib,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np
from PIL import Image
from b24_owner_pack_extract import decode as owner_decode,get_exact
from b24_g11_original_2010_city_texture_and_window_ui_contact import pvr_pixels
from recover_c1l1_original_uv import BDAEZIP,SOURCES
from b24_g13_c1l1_light_dome_mesh_provenance_sheet import source
from b24_g31_original_C1L1_BRES_WebGL2_3D_source_inspector import make_geometry,HTML as BASE
from b24_g29_original_CameraPreset_PD_CameraConfig_source_map import decode as cameras
from b24_g30_original_C1L1_four_Sun_Light_source_native_fields import source_lights
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize

def exact_source_uv():
    lookup={}
    with zipfile.ZipFile(BDAEZIP) as z:
        ns={"__name__":"g32_real_original_uv_parser","__file__":"bdae_scene_parser.py"}
        exec(compile(z.read("bdae_scene_parser.py"),"bdae_scene_parser.py","exec"),ns)
        for stem in SOURCES:
            models,_=ns["parse"](z.read("original_models/"+stem+".bdae"))
            for i,m in enumerate(models):
                name=stem+"_"+str(i)
                lookup[name]=m
    rows,_=source()
    vectors=[]
    for r,vertices,faces in rows:
        m=lookup.pop(r["source_mesh_name"],None)
        if m is None:raise ValueError("source BRES UV mesh not found")
        original_xyz=np.asarray(m["positions"],dtype=np.float32)
        original_face=np.asarray(m["faces"],dtype=np.uint32).reshape(-1,3)
        uv=np.asarray(m["uv"],dtype="<f4")
        if not np.array_equal(original_xyz,np.asarray(vertices,dtype=np.float32)):
            raise ValueError("source BRES vertices mismatch real native UV frame")
        if not np.array_equal(original_face,np.asarray(faces,dtype=np.uint32)):
            raise ValueError("source BRES triangle order doesn't match source original UV")
        if uv.shape!=(len(vertices),2) or not np.isfinite(uv).all():
            raise ValueError("2010 original UV stream corrupt")
        vectors.append(uv)
    if lookup:raise ValueError("unvisited real original source meshes")
    array=np.concatenate(vectors,axis=0)
    assert array.shape==(37946,2)
    return array

def real_source_PVRs(ipa,source_used):
    with zipfile.ZipFile(ipa) as z:
        pack=z.read("Payload/IronMan2.app/textures")
    registry={r.name.lower():r for r in owner_decode(pack,".tga")}
    all_c1=[s for s in registry if s.startswith("c1l1_")]
    assert len(all_c1)==39
    assert "cahp01_c_expo_building.tga" in registry
    if any(n not in registry for n in source_used):
        raise ValueError("original source 2010 shader names not all present in owner PVR archive")
    atlases=[];sizes={}
    for name in sorted(source_used):
        entry=registry[name]
        im,info=pvr_pixels(pack[entry.start:entry.end],entry.name)
        if not isinstance(im,Image.Image) or im.width<8:
            raise ValueError("original native PVR decode failed")
        buf=io.BytesIO()
        im.save(buf,format="PNG",optimize=True)
        png=buf.getvalue()
        sizes[name]={"source_rgba_size":[im.width,im.height],
            "original_PVR_native_SHA256":info["pixel_payload_sha256"],
            "preview_png_encoded_bytes":len(png)}
        atlases.append({"name":name,"base64":base64.b64encode(png).decode("ascii")})
    return atlases,sizes,{"original_user_owner_C1L1_tga_atlases":len(all_c1),
                          "original_user_owner_expo_tga_one_present":True}

def replace_once(text,before,after):
    if text.count(before)!=1:raise ValueError("G31 HTML template changed: "+before[:70])
    return text.replace(before,after)

def updated_HTML():
    h=BASE
    h=replace_once(h,
      "layout(location=0) in vec3 position;uniform mat4 projection,view;out vec3 worldP;",
      "layout(location=0) in vec3 position;layout(location=1) in vec2 uv;uniform mat4 projection,view;out vec3 worldP;out vec2 sourceUV;")
    h=replace_once(h,
      "void main(){worldP=position;gl_Position=projection*view*vec4(position,1.);}",
      "void main(){sourceUV=uv;worldP=position;gl_Position=projection*view*vec4(position,1.);}")
    h=replace_once(h,
      "precision highp float;in vec3 worldP;uniform vec3 baseColor;uniform float diagShade;out vec4 outColor;",
      "precision highp float;in vec3 worldP;in vec2 sourceUV;uniform vec3 baseColor;uniform float diagShade;uniform sampler2D originalPVR;uniform float enableOriginalPVR;out vec4 outColor;")
    h=replace_once(h,
      "outColor=vec4(baseColor*s,1.);}",
      "vec4 src=enableOriginalPVR>0.5?texture(originalPVR,sourceUV):vec4(baseColor,1.);outColor=vec4(src.rgb*s,1.);}")
    h=replace_once(h,
      "let pr=null,projU=null,viewU=null,colorU=null,shadeU=null,indexTotal=0;",
      "let pr=null,projU=null,viewU=null,colorU=null,shadeU=null,indexTotal=0,samplerU=null,usePVRU=null;const nativePVRTextures={};")
    h=replace_once(h,
      'shadeU=gl.getUniformLocation(pr,"diagShade");',
      'shadeU=gl.getUniformLocation(pr,"diagShade");samplerU=gl.getUniformLocation(pr,"originalPVR");usePVRU=gl.getUniformLocation(pr,"enableOriginalPVR");')
    h=replace_once(h,
      "if(pos.length!==d.vertices*3||indexTotal!==d.triangles*3)",
      'const uvr=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,uvr);let uv=new Float32Array(b64("rawuv"));gl.bufferData(gl.ARRAY_BUFFER,uv,gl.STATIC_DRAW);gl.enableVertexAttribArray(1);gl.vertexAttribPointer(1,2,gl.FLOAT,false,0,0);if(uv.length!==d.vertices*2)throw Error("Native original BRES UV count mismatch");\nif(pos.length!==d.vertices*3||indexTotal!==d.triangles*3)')
    h=replace_once(h,
      'for(const batch of d.batches){if(!matches(batch))continue;gl.uniform3fv(colorU,sourceColors[batch.status]);gl.drawElements(gl.TRIANGLES,batch.count,gl.UNSIGNED_INT,batch.start*4)}',
      'for(const batch of d.batches){if(!matches(batch))continue;const tex=batch.tga?nativePVRTextures[batch.tga.toLowerCase()]:null;const original=!!(tex&&batch.original_uv_mesh_positive&&document.getElementById("togglePVR").checked);gl.uniform1f(usePVRU,original?1:0);if(original){gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,tex);gl.uniform1i(samplerU,0);}gl.uniform3fv(colorU,sourceColors[batch.status]);gl.drawElements(gl.TRIANGLES,batch.count,gl.UNSIGNED_INT,batch.start*4)}')
    h=replace_once(h,
      "let active=false,lastx=0,lasty=0;",
      '''if(gl&&pr){let atlasLoaded=0;for(const asset of d.originalPVRs){const img=new Image();img.onload=()=>{try{let texture=gl.createTexture();gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,texture);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,img);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.REPEAT);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.REPEAT);nativePVRTextures[asset.name.toLowerCase()]=texture;atlasLoaded++;document.getElementById("pvrstate").textContent="Kaynak PVR atlasları: "+atlasLoaded+" / "+d.originalPVRs.length;render();}catch(e){fail.textContent="PVR GPU texture yükleme hatası "+e.message}};img.onerror=()=>fail.textContent="Kaynak PVR PNG açılamadı: "+asset.name;img.src="data:image/png;base64,"+asset.base64;}}
let active=false,lastx=0,lasty=0;''')
    h=replace_once(h,
      '<label><input type="checkbox" id="shade"> Deneysel yönlü gölgeleme (özgün değil)</label>',
      '<label><input type="checkbox" id="togglePVR" checked> Orijinal PVR+UV dokularını çiz</label><label><input type="checkbox" id="shade"> Deneysel yönlü gölgeleme (özgün değil)</label>')
    h=replace_once(h,
      '<div style="padding:0 12px"><p id="status"></p><p id="fail"></p></div>',
      '<div style="padding:0 12px"><p id="pvrstate">Orijinal PVR atlasları yükleniyor…</p><p id="status"></p><p id="fail"></p></div>')
    h=replace_once(h,
      'for(let x of [focus,group,mat,shade,marker])',
      'for(let x of [focus,group,mat,shade,marker,document.getElementById("togglePVR")])')
    h=replace_once(h,
      '<script id="rawindices" type="text/plain">__INDICES__</script>',
      '<script id="rawindices" type="text/plain">__INDICES__</script>\n<script id="rawuv" type="text/plain">__UV__</script>')
    h=replace_once(h,
      'Şehirdeki <b>37.946 özgün köşe</b>, <b>22.919 gerçek BRES üçgeni</b> ve <b>370 mesh</b> — geometri yeniden çizilmedi.',
      'Şehirdeki <b>37.946 özgün köşe</b>, <b>22.919 gerçek BRES üçgeni</b> ve <b>370 mesh</b> — geometri yeniden çizilmedi. Kaynak PVR+UV eşleşmesi olan yüzeyler artık <b>özgün 2010 PVR diffuse atlası</b> ile örneklenir.')
    h=replace_once(h,
      'Malzeme renkleri yalnızca kaynak kanıt durumunu gösterir; <b>orijinal iOS dokuları/ışıklandırması veya oyunun kamera hareketi değildir.</b>',
      'Orijinal kaynak diffuse+UV bağlantısı bulunmayan yüzeyler tanısal renktedir; <b>özgün oyun ışıklandırması/alpha/emissive ve kamera hareketi değildir.</b>')
    h=replace_once(h,
      'Bu <b>3B WebGL2 görüntüsü gerçek 2010 BRES geometri</b> kullanır; 2010 oyun kodu, gerçek shader, per-pixel PVR doku örneklemesi, orijinal cutscene, collider, mesh parent dünya dönüşümü veya PS Vita GPU performans testinin yerine geçmez.',
      'Bu <b>3B WebGL2 görüntüsü gerçek 2010 BRES geometri, özgün UV ve mevcut olan orijinal kaynak PVR diffuse piksellerini</b> kullanır. Bu, özgün shader/ışıklandırma/alpha-blend, eksik materyaller, camera/world-parent, cutscene, collider veya VitaGL testi anlamına gelmez.')
    return h

def main(ipa,html_path,report_path):
    with zipfile.ZipFile(ipa) as z:
        pack=z.read("Payload/IronMan2.app/clev")
        level=get_exact(pack,owner_decode(pack,".bclara"),"level1.bclara")
    pos,tri,batches,g=make_geometry()
    uv=exact_source_uv()
    if len(pos)!=len(uv):raise ValueError("G32 true BRES source UV drift")
    used={b["tga"].lower() for b in batches if b["tga"] and b["original_uv_mesh_positive"]}
    images,pvrmeta,bank=real_source_PVRs(ipa,used)
    cams=cameras(level)
    lights=source_lights(level)
    mc=summarize(level)["source_exact_MC_native_parent_child_transform"]["native_vec3_position"]
    rows={**g,"batches":batches,"mc_xyz":mc,
         "map_center":((pos.min(axis=0)+pos.max(axis=0))/2).tolist(),
         "pd_start_xyz":next(c for c in cams["source_original_CameraPreset_to_PositionDummy_and_CameraConfig_links"] if c["source_CameraPreset_name"]=="Camera_start_show")["source_3_target_PD_local_transform_records"][0]["native_XYZ"],
         "suns":lights,
         "cameras":cams["source_original_CameraPreset_to_PositionDummy_and_CameraConfig_links"],
         "originalPVRs":images,
         "original_used_source_PVR_TGA_count":len(images),
         "source_original_PVR_bank":bank,
         "native_original_2010_BRES_mesh_uv_float32_pairs":len(uv),
         "original_source_PVR_textured_faces":sum(b["tris"] for b in batches if b["tga"] and b["original_uv_mesh_positive"]),
         "original_owner_level1_sha256":hashlib.sha256(level).hexdigest(),
         "source_original_BRES_PVR_UV_atlases_rendered_when_WebGL2_enabled":True,
         "source_original_shader_lighting_alpha_blend_emissive_rebuilt":False,
         "source_world_parent_matrix_camera_motion_rebuilt":False,
         "source_bare_unknown_material_not_fake_textured":True,
         "NO_VPK":True}
    html=updated_HTML()
    payload=json.dumps(rows,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")
    html=html.replace("__POSITIONS__",base64.b64encode(pos.tobytes()).decode("ascii")).replace(
        "__INDICES__",base64.b64encode(tri.tobytes()).decode("ascii")).replace(
        "__UV__",base64.b64encode(uv.tobytes()).decode("ascii")).replace("__DATA__",payload)
    if "__POSITIONS__" in html or "__UV__" in html:raise ValueError("original source HTML template payload not expanded")
    html_path.parent.mkdir(parents=True,exist_ok=True);report_path.parent.mkdir(parents=True,exist_ok=True)
    html_path.write_text(html,encoding="utf-8")
    report={k:v for k,v in rows.items() if k not in ("batches","originalPVRs","cameras","suns")}
    report["original_PVR_atlases_name_sizes_hashes"]=pvrmeta
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    assert rows["original_source_PVR_textured_faces"]==18774
    assert len(used)==len(images)
    assert html_path.stat().st_size>1000000
    print("G32 PASS source 2010 real 370 BRES, 22919 triangles, 37946 native original vertices and UV0.")
    print("G32 real original PVR owner atlas count all C1L1",bank["original_user_owner_C1L1_tga_atlases"],"used/source-authored",len(images),
          "true original PVR+UV triangles",rows["original_source_PVR_textured_faces"])
    print("G32 standalone source HTML bytes",html_path.stat().st_size)
    print("PASS actual owner PVR decode exact texture names, native BRES per-pixel WebGL2 diffuse UV stream, no invented materials/lighting or VPK.")
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--ipa",required=True,type=Path);a.add_argument("--html",required=True,type=Path)
    a.add_argument("--report",required=True,type=Path);args=a.parse_args()
    main(args.ipa,args.html,args.report)
