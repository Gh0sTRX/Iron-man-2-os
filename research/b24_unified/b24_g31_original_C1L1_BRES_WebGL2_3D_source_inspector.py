#!/usr/bin/env python3
"""G31 authentic source original 2010 C1L1 BRES WebGL2 interactive 3D QA.

NO generated geometry. Encode ALL original 370 BRES meshes / 37946 vertices /
22919 triangles and genuine original source per-submesh material references
into standalone offline source viewer. Colors indicate evidence categories,
NOT original color/shader/diffuse texture fidelity. Include original CLARA
MC MainCharacter, 4 native Lights, and 57 CameraPreset PositionDummy reference
markers; local coordinates only, actual world matrix/camera roles not proven.

WebGL2 is for browser SOURCE PREVIEW, NOT iOS app GPU or PS VitaGL test. NO VPK.
"""
from __future__ import annotations
import argparse,base64,collections,hashlib,json,math,zipfile
from pathlib import Path
import numpy as np
from b24_owner_pack_extract import decode as owner_decode,get_exact
from b24_g13_c1l1_light_dome_mesh_provenance_sheet import source
from b24_g29_original_CameraPreset_PD_CameraConfig_source_map import decode as native_cameras
from b24_g30_original_C1L1_four_Sun_Light_source_native_fields import source_lights
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize

def make_geometry():
    records,_=source()
    vertices=[];indices=[];batches=[]
    verts_total=0;triangles_total=0
    for row,pos,face in records:
        if pos.ndim!=2 or pos.shape[1]!=3 or face.ndim!=2 or face.shape[1]!=3:
            raise ValueError("original BRES unexpected geometry schema")
        if not np.isfinite(pos).all() or np.min(face)<0 or np.max(face)>=len(pos):
            raise ValueError("original mesh bounds/position invalid")
        vertices.append(np.asarray(pos,dtype="<f4"))
        num_face=0
        for sub in row["original_BRES_authored_submesh_materials"]:
            tris=int(sub["source_original_faces"])
            if tris<0 or tris>len(face):raise ValueError("source per-material face count invalid")
            if not tris:continue
            begin=triangles_total*3
            indices.append((face[num_face:num_face+tris].astype("<u4")+verts_total).reshape(-1))
            verified_texture=bool(sub["authored_named_PVR"])
            has_uv=bool(row["genuine_original_uv_candidate"])
            expo=bool(sub["is_EXPO_nonprefix"])
            status=("expo" if expo and has_uv else
                    "source-texture-and-UV" if verified_texture and has_uv else
                    "source-texture-no-UV" if verified_texture else
                    "UV-no-source-diffuse" if has_uv else "unresolved")
            batches.append({
                "start":begin,"count":tris*3,"tris":tris,
                "mesh":row["source_mesh_name"],"group":row["original_scene_group"],
                "material":sub["original_material_name"],"tga":sub["original_shader_diffuse"],
                "status":status,"source_texture_named":verified_texture,
                "original_uv_mesh_positive":has_uv
            })
            num_face+=tris;triangles_total+=tris
        if num_face!=len(face):
            raise ValueError("native original BRES mesh material face count differs")
        verts_total+=len(pos)
    assert verts_total==37946 and triangles_total==22919 and len(records)==370
    flat_vertices=np.concatenate(vertices,axis=0)
    flat_indices=np.concatenate(indices,axis=0)
    assert len(flat_indices)==triangles_total*3 and max(flat_indices)<verts_total
    totals=collections.Counter()
    for b in batches:totals[b["status"]]+=b["tris"]
    assert sum(totals.values())==22919
    geometry={"vertices":verts_total,"source_meshes":len(records),
      "triangles":triangles_total,"material_draw_batches":len(batches),
      "source_material_triangle_status_summary":dict(totals),
      "source_does_not_add_missing_road_ground_facades":True,
      "positions_binary_float32_le_bytes":flat_vertices.nbytes,
      "source_indices_uint32_le_bytes":flat_indices.nbytes}
    return flat_vertices,flat_indices,batches,geometry

HTML=r"""<!doctype html><html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Iron Man 2 (2010) G31 — Gerçek BRES 3B Harita Test Arayüzü</title>
<style>
:root{color-scheme:dark;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
*{box-sizing:border-box}body{margin:0;background:#07111d;color:#e8f2fa}
header{padding:16px 22px;border-bottom:1px solid #324d64;background:#102334}
header h1{font-size:clamp(22px,3.2vw,31px);margin:2px 0 8px}
p{color:#b4ccdd;line-height:1.52}
small,code{color:#9fbfce}code{font-size:12px}
.kpis{display:flex;gap:8px;flex-wrap:wrap}
.kpis span{padding:7px 10px;border:1px solid #456378;border-radius:6px;background:#1a3245;font-size:12px}
main{display:grid;grid-template-columns:minmax(0,2fr) minmax(290px,1fr);gap:12px;max-width:1750px;padding:12px;margin:auto}
@media(max-width:930px){main{grid-template-columns:1fr}}
.card{background:#122537;border:1px solid #34516a;border-radius:11px;overflow:hidden}
.controls{padding:10px;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
select,input{font:inherit;background:#0b1b2a;color:#e7f2fa;padding:9px;border:1px solid #58768c;border-radius:7px;max-width:100%}
input[type=search]{flex:1;min-width:160px}
canvas{display:block;width:100%;height:auto;touch-action:none;cursor:grab;background:#0a1724}
.canvas{position:relative;aspect-ratio:16/10}
.canvas canvas,.canvas svg{position:absolute;width:100%;height:100%;inset:0}
.canvas svg{pointer-events:none}
.side{max-height:77vh;overflow-y:auto;padding:14px}
#meshList{max-height:270px;overflow-y:auto;margin-top:10px}
.mesh{border-top:1px solid #294558;padding:8px 0;font-size:12px}
.mesh b{color:#e8f0fa}#info{background:#172e43;border-radius:7px;padding:10px;margin:8px 0}
footer{padding:8px 17px;font-size:12px;max-width:1700px;margin:auto}
button{background:#243f55;border:1px solid #60819a;padding:9px 13px;color:white;border-radius:6px;cursor:pointer}
button:hover{background:#36536a}
label{font-size:12px;color:#cbdfeb}
#fail{color:#f7b6b6}
</style></head><body>
<header><small>2010 GAMELOFT SOURCE → HOST WEBGL2 DIAGNOSTIC · SOURCE PROVENANCE · NO VPK</small>
<h1>G31 — Orijinal ilk haritanın gerçek 3B geometri inceleyicisi</h1>
<p>Şehirdeki <b>37.946 özgün köşe</b>, <b>22.919 gerçek BRES üçgeni</b> ve <b>370 mesh</b> — geometri yeniden çizilmedi.
Malzeme renkleri yalnızca kaynak kanıt durumunu gösterir; <b>orijinal iOS dokuları/ışıklandırması veya oyunun kamera hareketi değildir.</b>
Parmağınla çevir, iki parmakla yakınlaş veya fareyle döndür ve tekerlekle uzaklaş.</p>
<div class="kpis"><span>370 özgün mesh</span><span>22.919 gerçek üçgen</span><span>37.946 özgün köşe</span><span>57 kamera preset referansı</span><span>4 özgün Light</span></div>
</header><main><section class="card">
<div class="controls">
<label>Konum odağı <select id="focus"><option value="mc">MC · MainCharacter</option><option value="all">Haritanın tümü</option><option value="start">İlk kamera PositionDummy</option></select></label>
<label>Mesh grubu <select id="group"><option value="">Tümü</option><option value="ground">Zemin</option><option value="urban">Şehir</option><option value="vehicles">Araçlar</option><option value="lights">Işık modelleri</option></select></label>
<label>Materyal durumu <select id="mat"><option value="">Hepsi</option><option value="source-texture-and-UV">PVR + UV</option><option value="expo">Expo · özel özgün PVR</option><option value="source-texture-no-UV">PVR var, UV yok</option><option value="UV-no-source-diffuse">UV var, PVR bağlantısı yok</option><option value="unresolved">UV/PVR çözümsüz</option></select></label>
</div>
<div class="canvas"><canvas id="game" aria-label="370 kaynak mesh üçgenli özgün şehir 3B görüntüleyici"></canvas><svg id="markers"></svg></div>
<div class="controls"><label><input type="checkbox" id="shade"> Deneysel yönlü gölgeleme (özgün değil)</label><label><input type="checkbox" id="marker" checked> Kaynak konum işaretlerini göster</label><button id="reset">Görünümü sıfırla</button></div>
<div style="padding:0 12px"><p id="status"></p><p id="fail"></p></div>
</section><aside class="card side">
<h3 style="margin-top:0">Sahne ve orijinal materyal kanıtı</h3>
<p><b style="color:#72d3ae">Yeşil:</b> kaynak PVR adı ve UV adayı bulundu.<br>
<b style="color:#e4b16d">Sarı:</b> özgün Expo PVR bağlantısı.<br>
<b style="color:#db9369">Turuncu:</b> PVR var ama UV yok.<br>
<b style="color:#83acda">Mavi:</b> UV var, doğrulanmış PVR bağlanmadı.<br>
<b style="color:#96a1a9">Gri:</b> ikisi de yok.</p>
<label>Özgün CameraPreset <select id="camera"></select></label>
<div id="info"></div>
<label>Kaynak mesh/materyal ara <input id="search" type="search" placeholder="Expo, Material__20, C1L1_light..."></label>
<div id="meshList"></div>
</aside></main><footer><p>Bu <b>3B WebGL2 görüntüsü gerçek 2010 BRES geometri</b> kullanır; 2010 oyun kodu, gerçek shader, per-pixel PVR doku örneklemesi, orijinal cutscene, collider, mesh parent dünya dönüşümü veya PS Vita GPU performans testinin yerine geçmez.
Kamera PositionDummy A/B/C, MC ve Sun işaretleri özgün yerel CLARA pozisyonlarından gelir; işlevlerinin nihai anlamı çözümlenmedi.</p></footer>
<script id="payload" type="application/json">__DATA__</script>
<script id="rawpositions" type="text/plain">__POSITIONS__</script>
<script id="rawindices" type="text/plain">__INDICES__</script>
<script>
"use strict";
const d=JSON.parse(document.getElementById("payload").textContent);
const can=document.getElementById("game"),svg=document.getElementById("markers"),status=document.getElementById("status"),fail=document.getElementById("fail");
const group=document.getElementById("group"),mat=document.getElementById("mat"),focus=document.getElementById("focus"),shade=document.getElementById("shade"),marker=document.getElementById("marker"),search=document.getElementById("search");
const camselect=document.getElementById("camera"),info=document.getElementById("info"),meshes=document.getElementById("meshList");
const gl=can.getContext("webgl2",{antialias:true,alpha:false,depth:true});
if(!gl){fail.textContent="Bu tarayıcıda WebGL2 bulunamadı. Materyal/nesne kayıtlarını sağdaki listeden yine inceleyebilirsin."}
let az=-1.2,el=0.56,dist=145,center=d.mc_xyz.slice(),pointer=null,lastTouchDist=0;
const sourceColors={"source-texture-and-UV":[.36,.78,.63],"expo":[.96,.75,.35],"source-texture-no-UV":[.91,.56,.34],"UV-no-source-diffuse":[.41,.65,.88],"unresolved":[.51,.59,.65]};
const esc=t=>String(t).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function b64(id){let s=document.getElementById(id).textContent.trim(),decoded=atob(s),b=new Uint8Array(decoded.length);for(let i=0;i<decoded.length;i++)b[i]=decoded.charCodeAt(i);return b.buffer}
function shader(type,src){const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s}
function program(){const p=gl.createProgram();gl.attachShader(p,shader(gl.VERTEX_SHADER,\`#version 300 es
layout(location=0) in vec3 position;uniform mat4 projection,view;out vec3 worldP;
void main(){worldP=position;gl_Position=projection*view*vec4(position,1.);}\`));
gl.attachShader(p,shader(gl.FRAGMENT_SHADER,\`#version 300 es
precision highp float;in vec3 worldP;uniform vec3 baseColor;uniform float diagShade;out vec4 outColor;
void main(){float s=1.;if(diagShade>0.5){vec3 n=normalize(cross(dFdx(worldP),dFdy(worldP)));s=0.48+0.52*abs(dot(n,normalize(vec3(0.35,0.55,0.78))));}outColor=vec4(baseColor*s,1.);}\`));
gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));return p}
let pr=null,projU=null,viewU=null,colorU=null,shadeU=null,indexTotal=0;
if(gl)try{pr=program();gl.useProgram(pr);projU=gl.getUniformLocation(pr,"projection");viewU=gl.getUniformLocation(pr,"view");colorU=gl.getUniformLocation(pr,"baseColor");shadeU=gl.getUniformLocation(pr,"diagShade");
const vao=gl.createVertexArray();gl.bindVertexArray(vao);
const vb=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,vb);let pos=new Float32Array(b64("rawpositions"));gl.bufferData(gl.ARRAY_BUFFER,pos,gl.STATIC_DRAW);
gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,3,gl.FLOAT,false,0,0);
const ib=gl.createBuffer();gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,ib);let ind=new Uint32Array(b64("rawindices"));indexTotal=ind.length;gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,ind,gl.STATIC_DRAW);
if(pos.length!==d.vertices*3||indexTotal!==d.triangles*3)throw Error("Özgün kaynak geometri byte boyutları uyuşmuyor");
gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.clearColor(.035,.076,.12,1);
}catch(err){fail.textContent="Kaynak WebGL yükleme hatası: "+err.message;pr=null}
const vecnorm=v=>{let n=Math.hypot(...v)||1;return v.map(q=>q/n)};
function cross(a,b){return[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]}
function lookAt(eye,target,up){let z=vecnorm(eye.map((x,i)=>x-target[i])),x=vecnorm(cross(up,z)),y=cross(z,x);return new Float32Array([
x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,
-x.reduce((v,q,i)=>v+q*eye[i],0),-y.reduce((v,q,i)=>v+q*eye[i],0),-z.reduce((v,q,i)=>v+q*eye[i],0),1])}
function perspective(a,r,n,f){let v=1/Math.tan(a/2);return new Float32Array([v/r,0,0,0,0,v,0,0,0,0,(f+n)/(n-f),-1,0,0,2*f*n/(n-f),0])}
function matmul(a,b){let o=new Float32Array(16);for(let c=0;c<4;c++)for(let r=0;r<4;r++)for(let k=0;k<4;k++)o[c*4+r]+=a[k*4+r]*b[c*4+k];return o}
function proj3(p,m,w,h){let t=[0,0,0,0];for(let r=0;r<4;r++)t[r]=m[r]*p[0]+m[4+r]*p[1]+m[8+r]*p[2]+m[12+r];return t[3]<=0?null:[(t[0]/t[3]+1)*w/2,(1-t[1]/t[3])*h/2]}
function getCam(){return d.cameras.find(x=>x.source_CameraPreset_name===camselect.value)||d.cameras[0]}
function markers(view,proj,w,h){if(!marker.checked){svg.innerHTML="";return}let m=matmul(proj,view);
let items=[{p:d.mc_xyz,name:"MC",clr:"#ffe89a"}];
for(const sun of d.suns)items.push({p:sun.original_local_translation_xyz,name:sun.source_name,clr:"#d3a7ff"});
let ca=getCam();for(let i=0;i<ca.source_3_target_PD_local_transform_records.length;i++){let tr=ca.source_3_target_PD_local_transform_records[i];items.push({p:tr.native_XYZ,name:"PD "+String.fromCharCode(65+i),clr:"#79e4dc"})}
svg.setAttribute("viewBox","0 0 "+w+" "+h);svg.innerHTML=items.map(v=>{let p=proj3(v.p,m,w,h);return !p?'':'<circle cx="'+p[0]+'" cy="'+p[1]+'" r="6" fill="'+v.clr+'" stroke="#152233" stroke-width="2"/><text x="'+(p[0]+9)+'" y="'+(p[1]+5)+'" font-size="13" fill="'+v.clr+'" font-family="system-ui">'+esc(v.name)+'</text>'}).join("")}
function matches(b){let s=search.value.toLowerCase().trim();return (!group.value||b.group===group.value)&&(!mat.value||b.status===mat.value)&&(!s||(b.mesh+" "+b.material+" "+(b.tga||"")).toLowerCase().includes(s))}
function refreshList(){let arr=d.batches.filter(matches),tot=arr.reduce((a,b)=>a+b.tris,0);
status.textContent="Seçili özgün üçgen: "+tot.toLocaleString('tr-TR')+" / "+d.triangles.toLocaleString('tr-TR')+" • "+arr.length+" materyal çizim grubu.";
meshes.innerHTML=arr.slice(0,70).map(x=>'<div class="mesh"><b>'+esc(x.mesh)+'</b><br>'+esc(x.material)+' · '+x.tris+' üçgen<br><small>'+esc(x.tga||"Kaynak diffuse PVR yok")+'</small></div>').join('')+(arr.length>70?'<p><small>İlk 70 eşleşme gösteriliyor; aramayla daralt.</small></p>':'')}
function render(){if(!gl||!pr)return;let w=Math.max(2,can.clientWidth),h=Math.max(2,can.clientHeight);let dpi=Math.min(2,window.devicePixelRatio||1);
let dw=Math.floor(w*dpi),dh=Math.floor(h*dpi);if(can.width!==dw||can.height!==dh){can.width=dw;can.height=dh;gl.viewport(0,0,dw,dh)}
el=Math.max(-1.38,Math.min(1.38,el));dist=Math.max(5,Math.min(5500,dist));
let eye=[center[0]+dist*Math.cos(el)*Math.cos(az),center[1]+dist*Math.cos(el)*Math.sin(az),center[2]+dist*Math.sin(el)];
let v=lookAt(eye,center,[0,0,1]),p=perspective(Math.PI/3,w/h,.3,9000);
gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.useProgram(pr);gl.uniformMatrix4fv(projU,false,p);gl.uniformMatrix4fv(viewU,false,v);gl.uniform1f(shadeU,shade.checked?1:0);
for(const batch of d.batches){if(!matches(batch))continue;gl.uniform3fv(colorU,sourceColors[batch.status]);gl.drawElements(gl.TRIANGLES,batch.count,gl.UNSIGNED_INT,batch.start*4)}
markers(v,p,w,h)}
let active=false,lastx=0,lasty=0;
can.addEventListener('pointerdown',ev=>{active=true;lastx=ev.clientX;lasty=ev.clientY;can.setPointerCapture(ev.pointerId)});
can.addEventListener('pointerup',()=>active=false);can.addEventListener('pointercancel',()=>active=false);
can.addEventListener('pointermove',ev=>{if(!active)return;az+=(ev.clientX-lastx)*.007;el+=(ev.clientY-lasty)*.006;lastx=ev.clientX;lasty=ev.clientY;render()});
can.addEventListener('wheel',ev=>{ev.preventDefault();dist*=Math.exp(ev.deltaY*.001);render()},{passive:false});
function setFocus(){if(focus.value==="all"){center=d.map_center.slice();dist=1400}else if(focus.value==="start"){center=d.pd_start_xyz.slice();dist=95}else{center=d.mc_xyz.slice();dist=145}az=-1.2;el=.56;render()}
for(let x of [focus,group,mat,shade,marker])x.addEventListener('change',()=>{if(x===focus)setFocus();else{refreshList();render()}});
search.addEventListener('input',()=>{refreshList();render()});
document.getElementById('reset').onclick=()=>{focus.value="mc";group.value="";mat.value="";search.value="";shade.checked=false;setFocus();refreshList()};
for(const x of d.cameras){let o=document.createElement("option");o.value=x.source_CameraPreset_name;o.textContent=x.source_CameraPreset_name;camselect.append(o)}
camselect.value="Camera_start_show";
function updateCam(){let x=getCam();info.innerHTML='<b>'+esc(x.source_CameraPreset_name)+'</b><p>Özgün hedef: '+esc(x.source_verified_target_PositionDummy_name||"NULL / hedefsiz")+' (ID '+x.source_native_camera_target_id+')</p>'+
'<small>A/B/C işaretleri orijinal kaynak yerel PositionDummy kayıtlarıdır. Kamera gözü/look-at oldukları bilinmiyor.</small>';render()}
camselect.addEventListener('change',updateCam);window.addEventListener('resize',render);
refreshList();updateCam();setFocus();
</script></body></html>"""

def main(ipa,html_path,manifest):
    with zipfile.ZipFile(ipa) as z:
        packed=z.read("Payload/IronMan2.app/clev")
        raw=get_exact(packed,owner_decode(packed,".bclara"),"level1.bclara")
    verts,indices,batches,g=make_geometry()
    src_cam=native_cameras(raw)
    lights=source_lights(raw)
    mc=summarize(raw)["source_exact_MC_native_parent_child_transform"]["native_vec3_position"]
    bnd_min=verts.min(axis=0);bnd_max=verts.max(axis=0)
    first=next(c for c in src_cam["source_original_CameraPreset_to_PositionDummy_and_CameraConfig_links"] if c["source_CameraPreset_name"]=="Camera_start_show")
    pd_start=first["source_3_target_PD_local_transform_records"][0]["native_XYZ"]
    scene={**g,"batches":batches,
      "mc_xyz":mc,"map_center":((bnd_min+bnd_max)/2).tolist(),
      "pd_start_xyz":pd_start,
      "suns":lights,
      "cameras":src_cam["source_original_CameraPreset_to_PositionDummy_and_CameraConfig_links"],
      "owner_2010_level1_sha256":hashlib.sha256(raw).hexdigest(),
      "source_geometry_is_original_BRES":True,
      "original_material_diffuse_PVR_pixels_actually_rendered":False,
      "original_WorldMatrix_Parenting_rendered":False,
      "actual_iOS_2010_camera_or_shading_recreated":False,
      "browser_WebGL2_diagnostic_only":True,
      "source_camera_PD_markers_not_real_lookat_claim":True,
      "NO_VPK":True}
    packed_json=json.dumps(scene,separators=(",",":"),ensure_ascii=False).replace("</","<\\/")
    p64=base64.b64encode(verts.tobytes()).decode("ascii")
    i64=base64.b64encode(indices.tobytes()).decode("ascii")
    manifest.parent.mkdir(parents=True,exist_ok=True);html_path.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text(json.dumps({k:v for k,v in scene.items() if k not in ("batches","cameras","suns")},indent=2)+"\n",encoding="utf-8")
    html_path.write_text(HTML.replace("__POSITIONS__",p64).replace("__INDICES__",i64).replace("__DATA__",packed_json),encoding="utf-8")
    if html_path.stat().st_size<850000:raise ValueError("real 3D source WebGL geometry payload too small")
    assert sum(x["tris"] for x in batches)==22919
    print("G31 AUTHENTIC BRES real original 370 mesh / 37946 vertices / 22919 source triangle data +",len(batches),"material batches")
    print("G31 source material status triangles",g["source_material_triangle_status_summary"])
    print("G31 HTML bytes",html_path.stat().st_size,"Browser WebGL2 source diagnostic, 57 real camera refs + 4 original Light + exact MC local position")
    print("PASS native 2010 original polygon/face/index/submesh invariants; no made-up source geometry, no original shader/camera/gameplay, NO VPK.")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--ipa",required=True,type=Path)
    p.add_argument("--html",required=True,type=Path);p.add_argument("--manifest",required=True,type=Path)
    args=p.parse_args();main(args.ipa,args.html,args.manifest)
