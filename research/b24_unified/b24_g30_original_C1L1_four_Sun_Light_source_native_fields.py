#!/usr/bin/env python3
"""G30 original owner 2010 C1L1 light placement and typed raw properties.

Decode exactly four original class Light nodes Sun001..Sun004 with genuine
source child/parent transform and native raw Light parameters; display only
source position/quaternion. ARGB-looking raw UINT32=0xFFBEAEFF and native
float-like value 0.3/1.0 are source parameters, NOT proven shader light color
or brightness. Scene renderer has not used these lights (no false visuals).
"""
from __future__ import annotations
import argparse,base64,hashlib,json,math,struct,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode as owner_decode,get_exact
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
from b24_g24_original_clara_source_601_nodes_663_parent_links import audit
from b24_g19_original_2010_level1_spawn_transforms_city_xy_map import exact_spawns,render
from b24_g13_c1l1_light_dome_mesh_provenance_sheet import source

def source_lights(raw):
    s=summarize(raw);g=audit(raw)
    children=g["all_663_source_rigid_transforms_with_native_parent_child_name_ID_chain"]
    names=[x for x in s["source_2010_typed_class_instances"] if x["original_class_name"]=="Light"]
    if len(names)!=4 or set(n["original_name"] for n in names)!={"Sun001","Sun002","Sun003","Sun004"}:
        raise ValueError("original 4 typed Light nodes changed")
    rows=[]
    for n in names:
        links=[x for x in children if x["original_named_parent_source_ID"]==n["original_numeric_name_id"]]
        if len(links)!=1:raise ValueError("original Light no unique typed transform")
        p=n["original_name_offset"]+len(n["original_name"])
        if struct.unpack_from("<H",raw,p+160)[0]!=16:
            raise ValueError("Light native numeric group tag changed")
        numtags=[struct.unpack_from("<H",raw,p+off)[0] for off in (162,168,174)]
        if numtags!=[4,4,4]:raise ValueError("Light typed numbers not real source 4-byte fields")
        raw_lamp_param=[struct.unpack_from("<I",raw,p+off)[0] for off in (164,170,176)]
        if raw_lamp_param[1]!=0 or raw_lamp_param[2]!=0x42480000:
            raise ValueError("Light native raw parameter pattern differs")
        if [struct.unpack_from("<H",raw,p+off)[0] for off in (276,282,288,294,300)]!=[4]*5:
            raise ValueError("Light trailing 5×4 original 2010 numeric fields mismatch")
        intensity_candidate=struct.unpack_from("<f",raw,p+278)[0]
        packed=struct.unpack_from("<I",raw,p+284)[0]
        if packed!=0xFFBEAEFF or not (0<intensity_candidate<=1.01):
            raise ValueError("original source color-like and scalar native bytes drift")
        row={
            "source_class":"Light","source_name":n["original_name"],
            "original_source_class_id":n["original_class_id"],
            "original_source_named_entity_id":n["original_numeric_name_id"],
            "original_local_translation_xyz":links[0]["native_vec3_position"],
            "original_local_quaternion_xyzw":links[0]["native_quaternion_xyzw"],
            "original_local_scale_xyz":links[0]["native_vec3_scale"],
            "original_transform_child_id":links[0]["original_child_node_ID"],
            "raw_u32_fields_after_native_0x0010":[hex(v) for v in raw_lamp_param],
            "source_2010_unknown_float_property_at_name_plus_278":round(intensity_candidate,6),
            "source_2010_RGBA_like_u32_at_name_plus_284":f"0x{packed:08X}",
            "source_light_render_type_intensity_alpha_semantics_PROVEN":False,
            "source_original_light_color_shading_effect_PROVEN":False}
        rows.append(row)
    if len([r for r in rows if r["raw_u32_fields_after_native_0x0010"][0]=="0x2"])!=3:
        raise ValueError("expected 3 original native Light type raw value two")
    if len([r for r in rows if r["raw_u32_fields_after_native_0x0010"][0]=="0x0"])!=1:
        raise ValueError("expected 1 original native Light type raw value zero")
    return rows

PAGE=r"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Iron Man 2 — G30 özgün ışık kaynakları</title>
<style>
:root{color-scheme:dark;font-family:system-ui}*{box-sizing:border-box}
body{background:#091725;color:#e9f0fb;margin:0 auto;max-width:1400px;padding:16px}
h1{font-size:clamp(24px,4vw,34px)}p{color:#b8cbda;line-height:1.6}
main{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(275px,1fr);gap:14px}
@media(max-width:840px){main{grid-template-columns:1fr}}
section{background:#132639;border:1px solid #37576e;border-radius:9px;overflow:hidden}
.viewport{position:relative;aspect-ratio:1400/920}
.viewport img,.viewport svg{position:absolute;inset:0;width:100%;height:100%}
article{padding:18px}button{padding:11px 13px;border-radius:7px;background:#1f3a52;color:#f6f3ea;border:1px solid #6b889a;font:inherit;cursor:pointer;margin:3px}
button.active{background:#6e5162}code{color:#99dce7;font-size:12px}b{color:#ffda9f}
</style></head><body>
<h1>G30 — Gameloft 2010 özgün ışık nesneleri</h1>
<p>Bu görünüm gerçek C1L1 BRES şehir geometrisinin kaynak XY planını ve özgün
<code>Light</code> sınıfındaki dört <code>Sun</code> nesnesinin CLARA konumlarını gösterir.
Kaynakta renk gibi görünen <code>0xFFBEAEFF</code> değeri var;
<strong>gerçek GPU shader rengi ya da ışık yoğunluğu olarak henüz doğrulanmadı.</strong></p>
<main><section><div class="viewport"><img src="data:image/png;base64,__IMAGE__" alt="Orijinal 2010 C1L1 BRES şehir geometri planı"/><svg id="pins" viewBox="0 0 1400 920"></svg></div>
<p style="padding:0 16px">Nesnelerin işaretleri orijinal yerel kaynak koordinatlarıdır; gerçek dünyadaki gölgeleme etkisi veya ışık yarıçapı görselleştirilmez.</p></section>
<section><article><div id="buttons"></div><h2 id="name"></h2><div id="facts"></div></article></section></main>
<p><small>4 sınıflandırılmış özgün Light nesnesi; üç tanesinde ham sayısal tür alanı 2, birinde 0. Gerçek ışık tipi, materyal-gölge etkileşimi, orijinal 2010 render sonucu ve Vita GPU testi henüz kanıtlanmadı. VPK gerektirmez.</small></p>
<script id="src" type="application/json">__DATA__</script><script>
let report=JSON.parse(document.getElementById('src').textContent),data=report.original_2010_Light_source_nodes,chosen=0;
const svg=document.getElementById('pins'),btns=document.getElementById('buttons'),fact=document.getElementById('facts');
const cam=report.source_map_coordinate_transform;
function point(v){return [cam.pixel_origin_offset_xy[0]+(v[0]-cam.low_xy[0])*cam.pixel_world_scale,
cam.canvas_height-cam.pixel_origin_offset_xy[1]-(v[1]-cam.low_xy[1])*cam.pixel_world_scale]}
btns.innerHTML=data.map((x,i)=>'<button data-i="'+i+'">'+x.source_name+'</button>').join('');
function draw(){document.getElementById('name').textContent=data[chosen].source_name;
svg.innerHTML=data.map((x,i)=>{let [px,py]=point(x.original_local_translation_xyz),color=chosen===i?'#fff4b3':'#7dd8fa';
return '<circle cx="'+px+'" cy="'+py+'" r="'+(chosen===i?12:7)+'" fill="'+color+'" stroke="#0a1b2b" stroke-width="3"/><text x="'+(px+12)+'" y="'+(py+4)+'" font-family="sans-serif" fill="'+color+'" font-size="15">'+x.source_name+'</text>'}).join('');
document.querySelectorAll('[data-i]').forEach(b=>b.classList.toggle('active',Number(b.dataset.i)===chosen));
let l=data[chosen];fact.innerHTML='<p>Orijinal sınıf: <b>'+l.source_class+'</b> · ID '+l.original_source_named_entity_id+
'</p><p>Yerel XYZ: <code>'+l.original_local_translation_xyz.join(' / ')+'</code></p>'+
'<p>Yerel quaternion: <code>'+l.original_local_quaternion_xyzw.join(' / ')+'</code></p>'+
'<p>Ham parametreler: <code>'+l.raw_u32_fields_after_native_0x0010.join(' / ')+'</code></p>'+
'<p>Kaynak sayısal alanı: <code>'+l.source_2010_unknown_float_property_at_name_plus_278+'</code></p>'+
'<p>Renk-benzeri ham 32 bit: <code>'+l.source_2010_RGBA_like_u32_at_name_plus_284+'</code></p>'+
'<p><small>Bu sayısal alanların gerçek render anlamı bilinmiyor.</small></p>'}
btns.querySelectorAll('button').forEach(b=>b.onclick=()=>{chosen=Number(b.dataset.i);draw()});draw();
</script></body></html>"""

def main(ipa,out,png,preview):
    with zipfile.ZipFile(ipa) as z:
        raw=z.read("Payload/IronMan2.app/clev")
        level=get_exact(raw,owner_decode(raw,".bclara"),"level1.bclara")
    lights=source_lights(level)
    shapes,_=source()
    background=render(exact_spawns(level),shapes,png)
    stats={"game":"Original Gameloft Iron Man 2 iOS 2010 level1.bclara",
      "source_original_level1_sha256":hashlib.sha256(level).hexdigest(),
      "native_classed_2010_Light_source_node_count":4,
      "source_original_Light_nodes_with_unique_native_transform":len(lights),
      "original_2010_Light_source_nodes":lights,
      "source_map_coordinate_transform":background["world_source_to_map"],
      "source_real_BRES_city_triangles":background["actual_authored_BRES_triangles"],
      "source_light_color_type_intensity_in_2010_engine_PROVEN":False,
      "source_original_light_caster_geometry_or_shadow_shader_PROVEN":False,
      "source_lightmap_gpu_renderer_verified":False,"NO_VPK":True}
    out.parent.mkdir(parents=True,exist_ok=True);preview.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(stats,ensure_ascii=False,indent=2)+"\n")
    payload=json.dumps(stats,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")
    preview.write_text(PAGE.replace("__IMAGE__",base64.b64encode(png.read_bytes()).decode()).replace("__DATA__",payload),encoding="utf-8")
    assert len(lights)==4 and preview.stat().st_size>60000
    for r in lights:
        print("G30 original 2010 classed Light",r["source_name"],r["original_local_translation_xyz"],
              "type raw",r["raw_u32_fields_after_native_0x0010"],
              "raw scalar",r["source_2010_unknown_float_property_at_name_plus_278"],
              "ARGB-like raw",r["source_2010_RGBA_like_u32_at_name_plus_284"])
    print("PASS G30 4 genuine iOS 2010 first-level class Light positions/rotations, typed raw native numeric/ARGB-looking fields, BRES polygons map, NO renderer color guess or VPK.")
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--ipa",type=Path,required=True);a.add_argument("--out",type=Path,required=True)
    a.add_argument("--png",type=Path,required=True);a.add_argument("--html",type=Path,required=True)
    o=a.parse_args();main(o.ipa,o.out,o.png,o.html)
