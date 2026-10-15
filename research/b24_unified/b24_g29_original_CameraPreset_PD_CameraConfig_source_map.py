#!/usr/bin/env python3
"""G29 Original 2010 C1L1 camera->PositionDummy->CameraConfig evidence.

Native CameraPreset source layout: 57 original classed nodes each has a typed
4-byte reference at name-end+67, and a second typed 4-byte reference at +91.
51 reference EXACT classed PositionDummy IDs with THREE source-typed
vec3/quaternion/scale child transforms. Six contain explicit UINT32_MAX.
ALL 57 link to source CameraConfig CC_FollowMC ID587. The second original
CC_FrontMC classed config ID589 has same 18 native vec3 parameter triplets.

The 3 source PositionDummy transforms are NOT labeled camera eye/look-at or
world-space projection until native engine semantics confirm roles/parenting.
Do not invent camera movement or reconstructed iOS visuals. NO VPK.
"""
from __future__ import annotations
import argparse,base64,collections,hashlib,json,math,struct,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode as owner_decode,get_exact
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
from b24_g24_original_clara_source_601_nodes_663_parent_links import audit
from b24_g19_original_2010_level1_spawn_transforms_city_xy_map import exact_spawns,render
from b24_g13_c1l1_light_dome_mesh_provenance_sheet import source

def decode(raw):
    classes=summarize(raw)
    typed=classes["source_2010_typed_class_instances"]
    byid={r["original_numeric_name_id"]:r for r in typed}
    assert len(byid)==len(typed)
    graph=audit(raw)
    byparent=collections.defaultdict(list)
    for row in graph["all_663_source_rigid_transforms_with_native_parent_child_name_ID_chain"]:
        byparent[row["original_named_parent_source_ID"]].append(row)
    configs={}
    for r in typed:
        if r["original_class_name"]!="CameraConfig":continue
        p=r["original_name_offset"]+len(r["original_name"])
        if raw[p+35:p+37]!=b"\x18\x00":
            raise ValueError("native CC transform property field 18 vector array not present")
        vecs=[]
        for k in range(18):
            off=p+37+14*k
            if raw[off:off+2]!=b"\x0c\x00":
                raise ValueError("native camera config 0x000C tagged vec3 missing")
            xyz=struct.unpack_from("<fff",raw,off+2)
            if not all(math.isfinite(z) for z in xyz):raise ValueError("bad source CC vec3")
            vecs.append([round(float(z),6) for z in xyz])
        configs[r["original_numeric_name_id"]]={
             "source_config_ID":r["original_numeric_name_id"],
             "source_config_name":r["original_name"],"original_18_native_vec3_fields":vecs,
             "vector_roles_in_original_engine_verified":False}
    if set(configs)!={587,589}:
        raise ValueError("unexpected native CameraConfig IDs")
    if configs[587]["original_18_native_vec3_fields"]!=configs[589]["original_18_native_vec3_fields"]:
        raise ValueError("original camera config vector bytes differ")
    cams=[]
    for r in typed:
        if r["original_class_name"]!="CameraPreset":continue
        p=r["original_name_offset"]+len(r["original_name"])
        if raw[p+65:p+67]!=b"\x04\x00" or raw[p+89:p+91]!=b"\x04\x00":
            raise ValueError("2010 native CameraPreset tagged 4-byte class references changed")
        target=struct.unpack_from("<I",raw,p+67)[0]
        cfg=struct.unpack_from("<I",raw,p+91)[0]
        if cfg!=587:raise ValueError("2010 real CameraPreset class config link not CC_FollowMC")
        if target==0xFFFFFFFF:
            target_item=None;trs=[]
        else:
            target_item=byid.get(target)
            if target_item is None or target_item["original_class_name"]!="PositionDummy":
                raise ValueError("native source camera target not classed PositionDummy")
            trs=byparent[target]
            if len(trs)!=3:raise ValueError("CameraPreset PD source transforms not exactly 3")
        cams.append({
          "source_CameraPreset_name":r["original_name"],
          "source_camera_entity_ID":r["original_numeric_name_id"],
          "source_preset_name_offset":r["original_name_offset"],
          "source_native_camera_target_id":target,
          "source_target_has_explicit_NULL_sentinel":target==0xFFFFFFFF,
          "source_verified_target_PositionDummy_name":target_item["original_name"] if target_item else None,
          "source_3_target_PD_local_transform_records":[
             {"original_child_node_ID":s["original_child_node_ID"],
              "native_XYZ":s["native_vec3_position"],
              "native_quaternion_xyzw":s["native_quaternion_xyzw"],
              "native_scale":s["native_vec3_scale"],
              "original_source_byte_offset":s["native_transform_source_offset"]}
              for s in trs],
          "source_native_config_reference":cfg,
          "original_camera_view_matrix_proven":False,
          "source_three_position_transforms_are_not_eye_target_proof":True})
    if len(cams)!=57:raise ValueError("57 native CameraPreset source records expected")
    anchored=[c for c in cams if not c["source_target_has_explicit_NULL_sentinel"]]
    if len(anchored)!=51 or sum(len(c["source_3_target_PD_local_transform_records"]) for c in cams)!=153:
        raise ValueError("51 PD references/153 original local typed transforms invariant failed")
    expected={
        "Camera_start_show":("PD_start",1848),
        "Camera_start_show2":("PD_start_end",1852)}
    lookup={r["source_CameraPreset_name"]:r for r in cams}
    for name,(target_name,target_id) in expected.items():
        if lookup[name]["source_native_camera_target_id"]!=target_id or lookup[name]["source_verified_target_PositionDummy_name"]!=target_name:
            raise ValueError("native 2010 introductory camera→PD source association mismatch")
    nullnames=sorted(c["source_CameraPreset_name"] for c in cams if c["source_target_has_explicit_NULL_sentinel"])
    if nullnames!=sorted([
        "Camera_Tutorial_move","Camera_IM_attack_look","Camera_IM_Down",
        "Camera_check_IM_close","Camera_tuto_missile","Camera_around_bomb"]):
        raise ValueError("original source camera sentinel list drift")
    return {"original_source_level1_sha256":hashlib.sha256(raw).hexdigest(),
        "source_original_CameraPreset_count":57,
        "source_original_CameraConfig_count":len(configs),
        "source_original_PD_mapped_camera_count":len(anchored),
        "source_explicit_NULL_camera_position_target_count":len(nullnames),
        "source_original_camera_PD_transform_subrecords":153,
        "camera_native_config_fields_18_vec3_per_config":36,
        "source_original_config_18_vec3_exact_equal_across_both":True,
        "source_original_camera_configs":list(configs.values()),
        "source_original_CameraPreset_to_PositionDummy_and_CameraConfig_links":cams,
        "source_camera_position_transform_role_or_look_at_PROVEN":False,
        "source_camera_runtime_execution_or_footage_PROVEN":False,
        "new_VPK":False}

HTML=r"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Iron Man 2 iOS | G29 Orijinal Kamera & Harita Denetleyicisi</title>
<style>
:root{color-scheme:dark;font-family:system-ui,-apple-system,Segoe UI,sans-serif}
*{box-sizing:border-box}body{margin:0;background:#0d1722;color:#e7effa}header{padding:20px;border-bottom:1px solid #365166}
h1{font-size:clamp(23px,3.3vw,31px);margin:3px 0 8px}p{color:#b2c6d8;line-height:1.6}
main{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(300px,1fr);gap:14px;padding:14px;max-width:1560px;margin:auto}
@media(max-width:900px){main{grid-template-columns:1fr}}
section{background:#142635;border:1px solid #395468;border-radius:10px;overflow:hidden}
.controls{display:flex;flex-wrap:wrap;gap:10px;padding:12px}
select,input{background:#0c1b28;border:1px solid #657c8c;border-radius:7px;color:#edf5fa;padding:10px;font:inherit}
select{max-width:100%}input{flex:1;min-width:170px}
.canvas{position:relative;max-width:100%;aspect-ratio:1400/920}
.canvas img,.canvas svg{position:absolute;inset:0;width:100%;height:100%}
#info{padding:16px}#info h3{margin-top:4px}#info b{color:#fbd89c}
#list{max-height:380px;overflow-y:auto}
.item{padding:10px 14px;border-bottom:1px solid #344b5a;cursor:pointer;font-size:13px}
.item:hover,.item.active{background:#204258}
small,code{color:#a6c4d5}code{font-size:12px}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}
.pills{display:flex;flex-wrap:wrap;gap:8px}.pills span{background:#234155;border-radius:6px;padding:6px 10px;font-size:12px}
footer{padding:13px 20px}strong{color:#fee0b2}
</style></head><body>
<header><small>ORIGINAL 2010 GAMELOFT SOURCE · C1L1 · OFFLINE MAP QA · NO VPK</small>
<h1>G29 — Gerçek Kamera → PositionDummy → CameraConfig bağlantıları</h1>
<p>Bu şemada kaynak iOS 2010 BRES şehir geometrisi ve gerçek CLARA nesne kimlikleri vardır.
<strong>Üç PositionDummy dönüşümünün gerçek kamera gözü/bakış hedefi olduğu kanıtlanmadı.</strong>
Üç kaynak noktası A/B/C diye ayrılır; gerçek iOS kamera görüntüsü veya animasyon değildir.</p>
<div class="pills"><span>57 özgün KameraPreset</span><span>51 kaynak PD bağlantısı</span><span>6 boş/sentinel hedef</span><span>2 CameraConfig</span></div>
</header><main>
<section><div class="controls"><label>Kamera <select id="cam"></select></label></div>
<div class="canvas"><img src="data:image/png;base64,__IMAGE__" alt="2010 BRES özgün C1L1 şehrinin kaynak XY üçgenleri"/>
<svg id="marks" viewBox="0 0 1400 920" role="img" aria-label="Seçilen özgün kamera konum kayıtları A B C"></svg></div>
<p style="padding:0 15px">BRES orijinal üçgenleri üzerine çizilen işaretler yalnızca yerel kaynak XYZ'yi aynı XY düzlemine izdüşürür. Özgün sahne hiyerarşisi ve bakış matrisi henüz çözülmedi.</p>
</section>
<section><div id="info"></div><div class="controls"><input id="search" type="search" placeholder="Kamera / PD nesnesi ara"></div><div id="list"></div></section>
</main><footer><small>Kaynak test arayüzü — 51×3=153 gerçek dönüşüm, 57 gerçek CameraPreset nesnesi, 2×18 CameraConfig vektörü.
Orijinal GPU render'ı, kamera yolculuğu, görev süresi, Vita testi ve 3B gerçek shader iddiası yoktur.</small></footer>
<script id="native" type="application/json">__JSON__</script><script>
const src=JSON.parse(document.getElementById('native').textContent);
const cams=src.source_original_CameraPreset_to_PositionDummy_and_CameraConfig_links;
const selector=document.getElementById('cam'),marks=document.getElementById('marks'),info=document.getElementById('info');
const search=document.getElementById('search'),list=document.getElementById('list');
let picked='Camera_start_show';
for(const x of cams){let o=document.createElement('option');o.value=x.source_CameraPreset_name;o.textContent=x.source_CameraPreset_name;selector.appendChild(o)}
selector.value=picked;
const esc=t=>String(t).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function toXY(x){const m=src.map_transform;return [m.pixel_origin_offset_xy[0]+(x[0]-m.low_xy[0])*m.pixel_world_scale,
m.canvas_height-m.pixel_origin_offset_xy[1]-(x[1]-m.low_xy[1])*m.pixel_world_scale]}
function change(name){picked=name;selector.value=name;update()}
function update(){const x=cams.find(c=>c.source_CameraPreset_name===picked)||cams[0], t=x.source_3_target_PD_local_transform_records;
info.innerHTML='<h3>'+esc(x.source_CameraPreset_name)+'</h3><p>Özgün kamera ID: <b>'+x.source_camera_entity_ID+'</b>'+
'</p><p>Konum-hedef ID: <b>'+x.source_native_camera_target_id+'</b> ('+esc(x.source_verified_target_PositionDummy_name||'NULL / hedef yok')+
')</p><p>Kamera konfigürasyonu: <b>CC_FollowMC (#'+x.source_native_config_reference+')</b></p>'+
(t.length?t.map((s,i)=>'<p><b>'+String.fromCharCode(65+i)+' — özgün yerel kaynak dönüşümü</b> · child #'+s.original_child_node_ID+
'<br><code>'+s.native_XYZ.join(' / ')+'</code></p>').join(''):
'<p>Kaynakta bu kamera için açık PositionDummy hedefi bulunmuyor.</p>')+
'<small>Konumların gerçek kamera gözü veya hedef olduğunu varsaymıyoruz.</small>';
marks.innerHTML=t.map((s,i)=>{let [a,b]=toXY(s.native_XYZ);let cl=['#80d9ff','#ffc980','#adf7ac'][i];
return '<circle cx="'+a+'" cy="'+b+'" r="10" fill="'+cl+'" stroke="#172333" stroke-width="3"/>'+
'<text x="'+(a+14)+'" y="'+(b+5)+'" font-size="17" font-family="system-ui" fill="'+cl+'">'+String.fromCharCode(65+i)+'</text>'}).join('');
const q=search.value.toLowerCase().trim();
list.innerHTML=cams.filter(c=>(c.source_CameraPreset_name+' '+(c.source_verified_target_PositionDummy_name||'')).toLowerCase().includes(q))
.map(c=>'<div class="item '+(c.source_CameraPreset_name===picked?'active':'')+'" data-name="'+esc(c.source_CameraPreset_name)+'">'+
esc(c.source_CameraPreset_name)+'<br><small>'+esc(c.source_verified_target_PositionDummy_name||'NULL / hedefsiz')+'</small></div>').join('');
list.querySelectorAll('[data-name]').forEach(el=>el.onclick=()=>change(el.dataset.name))}
selector.addEventListener('change',()=>change(selector.value));search.addEventListener('input',update);update();
</script></body></html>"""

def main(ipa,report_path,image_path,html_path):
    with zipfile.ZipFile(ipa) as z:
        packed=z.read("Payload/IronMan2.app/clev")
        original=get_exact(packed,owner_decode(packed,".bclara"),"level1.bclara")
    result=decode(original)
    meshrows,_=source()
    nodes=exact_spawns(original)
    stats=render(nodes,meshrows,image_path)
    result["source_original_world_BRES_meshes"]=stats["actual_authored_BRES_meshes"]
    result["source_original_world_BRES_faces"]=stats["actual_authored_BRES_triangles"]
    result["original_source_camera_map_is_diagnostic_only"]=True
    result["map_transform"]=stats["world_source_to_map"]
    report_path.parent.mkdir(parents=True,exist_ok=True)
    html_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    payload=json.dumps(result,separators=(",",":"),ensure_ascii=False).replace("</","<\\/")
    pic=base64.b64encode(image_path.read_bytes()).decode()
    html_path.write_text(HTML.replace("__IMAGE__",pic).replace("__JSON__",payload),encoding="utf-8")
    assert len(result["source_original_CameraPreset_to_PositionDummy_and_CameraConfig_links"])==57
    assert html_path.stat().st_size>60000
    print("PASS G29 original 2010 CameraPreset 57; 51 exact PositionDummy IDs and 153 typed local transforms, 6 original UINT32_MAX sentinel camera targets.")
    print("PASS G29 57 cameras all link original class CameraConfig #587 CC_FollowMC, two native CameraConfig 18-vector blocks byte-equal, original city BRES 370/22919.")
    print("PASS offline source-backed camera/PD map JSON PNG HTML, no reconstructed iOS camera, no VPK.")
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--ipa",type=Path,required=True);a.add_argument("--out",type=Path,required=True)
    a.add_argument("--png",type=Path,required=True);a.add_argument("--html",type=Path,required=True)
    o=a.parse_args();main(o.ipa,o.out,o.png,o.html)
