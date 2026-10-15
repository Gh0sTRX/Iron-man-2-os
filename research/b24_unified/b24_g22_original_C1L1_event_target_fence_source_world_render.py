#!/usr/bin/env python3
"""G22 source-authored 2010 CLARA mission event target transform map.

Proven graph: SpawnPoint012 --Enable--> SpawnPoint015;
SpawnPoint014 --Disable--> Deco_fence2;
SpawnPoint015 --Disable--> Deco_fence6.
Two fence target nodes have exact native length-tagged 12B xyz, 16B
quaternion and 12B scale record at source-name +184 (vs SpawnPoint +107).
This is a source-authored static graph, NOT executed gameplay or camera.
"""
from __future__ import annotations
import argparse,base64,hashlib,json,math,struct,zipfile
from pathlib import Path
from PIL import Image,ImageDraw
from b24_owner_pack_extract import decode,get_exact
from b24_g19_original_2010_level1_spawn_transforms_city_xy_map import exact_spawns,render
from b24_g13_c1l1_light_dome_mesh_provenance_sheet import source
from b24_g21_original_C1L1_clara_OnDestroy_action_real_node_id_links import link

FENCE_NAMES=("Deco_fence2","Deco_fence6")
def target_deco(raw, source_row):
    at=source_row["source_text_offset"]
    label=source_row["record_source_name"]
    if label not in FENCE_NAMES or raw[at:at+len(label)]!=label.encode():
        raise ValueError("original 2010 fence source name/offset mismatch")
    base=at+184
    if raw[base:base+2]!=b"\x0c\x00" or raw[base+14:base+16]!=b"\x10\x00" or raw[base+32:base+34]!=b"\x0c\x00":
        raise ValueError("original fence native transform tag sequence mismatch")
    pos=struct.unpack_from("<3f",raw,base+2)
    quat=struct.unpack_from("<4f",raw,base+16)
    scl=struct.unpack_from("<3f",raw,base+34)
    if not all(math.isfinite(v) for v in pos+quat+scl):
        raise ValueError("source fence transform nonfinite")
    if abs(sum(q*q for q in quat)-1)>0.002:raise ValueError("source fence quaternion invalid")
    return {
        "node":label,"source_name_offset":at,
        "source_native_typed_transform_data_offset":base,
        "real_original_position_XYZ":[round(float(v),6) for v in pos],
        "source_quaternion_xyzw":[round(float(v),6) for v in quat],
        "source_scale_XYZ":[round(float(v),6) for v in scl],
        "typed_field_lengths":[12,16,12],"source_native_scene_mesh_parent_transforms_UNVERIFIED":True
    }

def emit(ipa,out,png,preview):
    with zipfile.ZipFile(ipa) as z:
        packed=z.read("Payload/IronMan2.app/clev")
        level=get_exact(packed,decode(packed,".bclara"),"level1.bclara")
    linked=link(level)
    edges=linked["source_real_CLARA_OnDestroy_action_named_event_edges"]
    native=linked["source_named_type1_CLARA_id_registry"]
    fence_registry={r["record_source_name"]:r for r in native if r["record_source_name"] in FENCE_NAMES}
    if set(fence_registry)!=set(FENCE_NAMES):raise ValueError("source fence nodes missing")
    fences={name:target_deco(level,fence_registry[name]) for name in FENCE_NAMES}
    nodes=exact_spawns(level)
    srcpos={n["node"]:n["position_XYZ"] for n in nodes}
    allpos={**srcpos,**{f:row["real_original_position_XYZ"] for f,row in fences.items()}}
    complete=[]
    for edge in edges:
        a=edge["source_node"];b=edge["resolved_original_source_destination_node"]
        if a not in allpos or b not in allpos:raise ValueError("original action source/target has no backed coordinates")
        p=allpos[a];q=allpos[b]
        xy=math.hypot(p[0]-q[0],p[1]-q[1])
        complete.append({**edge,
            "source_authored_XYZ":p,"destination_authored_XYZ":q,
            "raw_source_XY_distance":round(xy,4),
            "both_endpoints_native_source_transform_typed":True,
            "genuine_scene_node_parent_transform_applied":False})
    rows,_=source()
    geometry=render(nodes,rows,png)
    # Add real authored event arrows over original mesh city wireframe image
    im=Image.open(png).convert("RGB");pen=ImageDraw.Draw(im)
    m=geometry["world_source_to_map"]
    def project(xyz):
        return (m["pixel_origin_offset_xy"][0]+(xyz[0]-m["low_xy"][0])*m["pixel_world_scale"],
                m["canvas_height"]-m["pixel_origin_offset_xy"][1]-(xyz[1]-m["low_xy"][1])*m["pixel_world_scale"])
    for edge in complete:
        p=project(edge["source_authored_XYZ"]);q=project(edge["destination_authored_XYZ"])
        color="#fcac63" if edge["original_source_named_action"]=="Disable" else "#9de3a0"
        pen.line([p,q],fill=color,width=4)
        ang=math.atan2(q[1]-p[1],q[0]-p[0]);length=15
        left=(q[0]-length*math.cos(ang-0.6),q[1]-length*math.sin(ang-0.6))
        right=(q[0]-length*math.cos(ang+0.6),q[1]-length*math.sin(ang+0.6))
        pen.line([left,q,right],fill=color,width=4)
        pen.ellipse((q[0]-6,q[1]-6,q[0]+6,q[1]+6),outline=color,width=3)
    im.save(png,optimize=True)
    report={
        "source_owner_original_level1_sha256":hashlib.sha256(level).hexdigest(),
        "source_16_clara_SpawnPoint_names_and_typed_transforms":nodes,
        "original_fence2_fence6_native_scene_transforms":fences,
        "three_native_source_onDestroy_Enable_Disable_links_with_both_authored_positions":complete,
        "source_real_2010_clara_event_edges":3,
        "source_fence_typed_transform_records":2,
        "original_authored_BRES_city_meshes":geometry["actual_authored_BRES_meshes"],
        "original_authored_BRES_city_triangles":geometry["actual_authored_BRES_triangles"],
        "original_player_start_confirmed":False,
        "original_2010_trigger_runtime_execution_verified":False,
        "source_city_parent_transforms_all_verified":False,
        "no_gameplay_or_VPK_build":True}
    out.parent.mkdir(parents=True,exist_ok=True)
    preview.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    data=json.dumps({"edges":complete},separators=(",",":"),ensure_ascii=False).replace("</","<\\/")
    picture=base64.b64encode(png.read_bytes()).decode()
    page=r"""<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Iron Man 2 — özgün 2010 ilk bölüm olay haritası G22</title>
<style>body{margin:auto;max-width:1280px;padding:18px;font-family:system-ui;background:#0a1622;color:#eef2fa}
h1{font-size:clamp(23px,4vw,32px)}p{color:#b9cadb;line-height:1.65}.preview{border:1px solid #455e73;border-radius:10px;overflow:hidden}.preview img{display:block;width:100%}
.panel{border:1px solid #415a72;padding:16px;border-radius:10px;background:#162738;margin:15px 0}
select{color:white;background:#203548;border:1px solid #6a869b;border-radius:8px;padding:12px;font:inherit}
strong{color:#ffd89c}small{color:#b5cbdc}code{color:#8fd6ef}
</style></head><body><h1>Iron Man 2 (2010) — özgün görev olayları</h1>
<p>Haritadaki 370 mesh ve 22.919 üçgen, orijinal iOS oyunundan geri kazanılmış BRES geometrisidir.
Oklar, gerçek CLARA node-ID eşleşmelerinden kurtarılan üç özgün olay kaydını gösterir:
yeşil <strong>Enable</strong>, turuncu <strong>Disable</strong>.
Orijinal oyun motorundaki görev yürütme, oyuncunun başlangıç noktası ve gerçek kamera henüz doğrulanmadı.</p>
<div class="preview"><img src="data:image/png;base64,__IMG__" alt="Gerçek BRES geometri üzerinden özgün üç CLARA olay oku"></div>
<div class="panel"><label>Kaynak bağlantıyı incele: <select id="pick"></select></label><div id="facts"></div></div>
<p><small>Çevrimdışı HTML kaynak ön izlemesidir; oyun/simülasyon veya Vita ekran görüntüsü değildir. Yalnızca kaynak ham numaralar ve source mesh XY kullanılır.</small></p>
<script id="evidence" type="application/json">__DATA__</script><script>
const e=JSON.parse(document.getElementById("evidence").textContent).edges;
const sel=document.getElementById("pick");e.forEach((x,i)=>{let o=document.createElement("option");o.value=i;o.textContent=x.source_node+" → "+x.original_source_named_action+" → "+x.resolved_original_source_destination_node;sel.append(o)});
function draw(){const x=e[Number(sel.value)||0];document.getElementById("facts").innerHTML="<p><strong>"+x.source_node+"</strong> ("+x.source_authored_XYZ.join(", ")+")"+
" → "+x.original_source_named_action+" → <strong>"+x.resolved_original_source_destination_node+"</strong> ("+x.destination_authored_XYZ.join(", ")+")</p>"+
"<p>Kaynak XY uzaklık: "+x.raw_source_XY_distance.toFixed(3)+" birim. Bu sayılar gerçek kaynak konumlarıdır; oyundaki yürütme ve parent transform etkisi doğrulanmadı.</p>"}
sel.addEventListener("change",draw);draw();</script></body></html>"""
    preview.write_text(page.replace("__IMG__",picture).replace("__DATA__",data),encoding="utf-8")
    assert preview.stat().st_size>10000
    for e in complete:
        print("G22 TRUE SOURCE EVENT",e["source_node"],e["original_source_named_action"],
              e["resolved_original_source_destination_node"],"source XY distance",e["raw_source_XY_distance"])
    print("PASS G22 real 2010 BRES city + 16 Spawn transforms + two authentic Deco_fence transform records and three target-backed mission edges; NO VPK")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--ipa",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--png",required=True,type=Path)
    p.add_argument("--html",required=True,type=Path)
    a=p.parse_args();emit(a.ipa,a.out,a.png,a.html)
