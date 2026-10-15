#!/usr/bin/env python3
"""G19: 16 genuine 2010 level1.bclara SpawnPoint transform triples and BRES map plan.

Each source SpawnPoint has length-tagged 12B Position + 16B quaternion-like
Rotation + 12B Scale at SAME +107 offset from its exact 13-byte node name.
This is stronger than G11's unrelated-nearby-float heuristics: all sixteen
records validate, rotation magnitude unity and scales exactly (1,1,1).
The original game's PLAYER START / mission role is NOT inferred.

Offline HTML and screenshot use only true source BRES polygons, plus exact
2010 BCLARA binary node transforms. NO invented roads/geometry/texture/shader.
The overlay is a diagnostic in common numerical X/Y coordinates; BCLARA
node parent transforms and true game scene graph are NOT yet verified.
"""
from __future__ import annotations
import argparse,base64,hashlib,io,json,math,re,struct,zipfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from b24_owner_pack_extract import decode,get_exact
from b24_g13_c1l1_light_dome_mesh_provenance_sheet import source

MARKER=re.compile(rb"SpawnPoint(\d{3})(?!_)")
SOURCE_SIZE=339733
def exact_spawns(raw:bytes)->list[dict]:
    if len(raw)!=SOURCE_SIZE:raise ValueError("Wrong original 2010 level1 scene size")
    records={}
    for m in MARKER.finditer(raw):
        name=m.group().decode("ascii")
        if name in records:raise ValueError("duplicate original node "+name)
        base=m.start()+107
        if raw[base:base+2]!=b"\x0c\x00" or raw[base+14:base+16]!=b"\x10\x00" or raw[base+32:base+34]!=b"\x0c\x00":
            raise ValueError("source native tagged vec3/quaternion/vec3 schema fails "+name)
        position=struct.unpack_from("<3f",raw,base+2)
        quat=struct.unpack_from("<4f",raw,base+16)
        scale=struct.unpack_from("<3f",raw,base+34)
        if not all(math.isfinite(v) for v in position+quat+scale):
            raise ValueError("nonfinite source transform "+name)
        norm=sum(v*v for v in quat)
        if abs(norm-1.0)>0.002:
            raise ValueError("native quaternion not unit "+name)
        if max(abs(v-1.0) for v in scale)>0.0001:
            raise ValueError("original spawn default scale differs from one "+name)
        if max(abs(v) for v in position)>3000:raise ValueError("invalid native world position")
        records[name]={
            "node":name,"native_clara_file_offset":m.start(),
            "native_transform_tag_offset":base,
            "position_XYZ":[round(float(x),6) for x in position],
            "quaternion_xyzw":[round(float(v),6) for v in quat],
            "scale_XYZ":[round(float(x),6) for x in scale],
            "quaternion_length":round(math.sqrt(norm),6),
            "native_tagged_value_sizes":[12,16,12],
            "this_is_original_source_node_transform":True,
            "is_original_player_spawn_proven":False
        }
    if sorted(records)!=["SpawnPoint%03d"%i for i in range(16)]:
        raise ValueError("original level1 has incomplete 000-015 spawn names")
    return [records["SpawnPoint%03d"%i] for i in range(16)]

def render(nodes,meshrows,output:Path)->dict:
    pos=np.concatenate([p for _,p,_ in meshrows],axis=0)
    if not np.isfinite(pos).all():raise ValueError("source original BRES nonfinite positions")
    assert sum(int(r["source_faces"]) for r,_,_ in meshrows)==22919
    source_xy=pos[:,:2]
    nodes_xy=np.asarray([r["position_XYZ"][:2] for r in nodes],dtype=np.float32)
    # Use BOTH sources for viewport. AABB membership is not proof of world/parent
    # transform semantics, only a useful source-coordinate diagnostic.
    low_source=source_xy.min(axis=0);high_source=source_xy.max(axis=0)
    low=np.minimum(low_source,nodes_xy.min(axis=0))
    high=np.maximum(high_source,nodes_xy.max(axis=0))
    # Symmetrical margin preserves natural aspect ratio.
    width,height=1400,920;margin=65
    wmax=max(1.,float(high[0]-low[0]));hmax=max(1.,float(high[1]-low[1]))
    scale=min((width-2*margin)/wmax,(height-2*margin)/hmax)
    offsetx=(width-wmax*scale)/2
    offsety=(height-hmax*scale)/2
    def screen(point):
        return (offsetx+(float(point[0])-float(low[0]))*scale,
                height-offsety-(float(point[1])-float(low[1]))*scale)
    image=Image.new("RGB",(width,height),"#091724")
    draw=ImageDraw.Draw(image)
    # Explicitly just a diagnostic wireframe, no surface shaders.
    colors={"ground":"#2e5764","urban":"#3f6674",
            "vehicles":"#816949","lights":"#536979"}
    for row,p,f in meshrows:
        col=colors[row["original_scene_group"]]
        xy=[screen(v) for v in p[:,:2]]
        for tri in f:
            vertices=[xy[int(idx)] for idx in tri]
            draw.line(vertices+[vertices[0]],fill=col,width=1)
    # top-down axes cross and authentic spawn points
    for node in nodes:
        x,y=screen(node["position_XYZ"])
        draw.ellipse([x-5,y-5,x+5,y+5],fill="#ffcf6d",outline="#172334",width=2)
        draw.text((x+7,y-10),node["node"][-3:],fill="#ffe4a0")
    draw.text((20,10),"IRON MAN 2 2010 | ORIGINAL C1L1 BRES 370 MESH + BCLARA 16 SPAWNPOINTS",fill="#e8f0f8")
    draw.text((20,29),"TOP-DOWN SOURCE XY / NOT IN-GAME CAMERA OR CONFIRMED PLAYER START",fill="#d5a66e")
    draw.text((20,height-32),"Authentic 2010 BRES geometry / raw CLARA source transform values | Shader, parenting & scene order unverified",fill="#bccbd5")
    output.parent.mkdir(parents=True,exist_ok=True)
    image.save(output,optimize=True)
    within=sum(bool(np.all(n>=low_source) and np.all(n<=high_source))
               for n in nodes_xy)
    return {
        "source_bres_bbox_min_XYZ":np.min(pos,axis=0).tolist(),
        "source_bres_bbox_max_XYZ":np.max(pos,axis=0).tolist(),
        "nodes_inside_untransformed_source_BRES_AABB_XY":within,
        "total_real_original_vertices":len(pos),
        "actual_authored_BRES_meshes":len(meshrows),
        "actual_authored_BRES_triangles":sum(r["source_faces"] for r,_,_ in meshrows),
        "projection":"X horizontal; Y vertical; Z retained as spawn altitude metadata",
        "world_source_to_map": {
            "low_xy":low.tolist(),"high_xy":high.tolist(),
            "pixel_world_scale":float(scale),
            "pixel_origin_offset_xy":[float(offsetx),float(offsety)],
            "canvas_width":width,"canvas_height":height},
        "map_world_source_mesh_node_parent_transform_recovered":False,
        "map_is_diagnostic_true_source_polygon_wireframe":True}

def html_page(nodes,geometry,background,out):
    png=base64.b64encode(background.read_bytes()).decode("ascii")
    j=json.dumps({"nodes":nodes,"map":geometry["world_source_to_map"]},separators=(",",":"))
    page=r"""<!doctype html><html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Iron Man 2 — 2010 özgün 16 SpawnPoint ve şehir planı</title>
<style>
:root{color-scheme:dark;font-family:system-ui}
body{max-width:1300px;margin:0 auto;background:#0b1520;color:#f0f3fa;padding:15px}
h1{font-size:clamp(22px,4vw,32px)}p{color:#bdd0de;line-height:1.65}
.wrap{position:relative;width:100%;overflow:hidden;border:1px solid #3c5b72;border-radius:10px}
.wrap img{width:100%;height:auto;display:block}
#overlay{position:absolute;width:100%;height:100%;inset:0;pointer-events:auto}
.controls{display:flex;gap:10px;flex-wrap:wrap;margin:15px 0}
select{background:#152c3d;color:#e8f1fa;border:1px solid #698ba0;padding:12px;border-radius:8px;font:inherit}
.panel{border:1px solid #34485a;background:#152638;border-radius:8px;padding:15px;margin-top:16px}
strong{color:#ffdb9d}small{color:#b5c8d8}
</style></head><body>
<h1>Iron Man 2 (2010) — ilk bölümün özgün yerleşim noktaları</h1>
<p>Haritanın çizgileri 2010 tarihli gerçek BRES şehir modelinin üçgenleridir.
16 işaret gerçek <code>level1.bclara</code> SpawnPoint konum kaydından geldi.
Çizim, kaynak koordinatlarını aynı XY düzleminde gösteren teknik
karşılaştırmadır. <strong>Oyuncunun hangi noktada başladığı hâlâ bilinmiyor.</strong>
Bu özgün oyunun ekran görüntüsü veya tamamlanmış Vita haritası değil.</p>
<div class="controls"><label>Özgün düğüm:
<select id="pick"></select></label></div>
<div class="wrap"><img src="data:image/png;base64,__PNG__" alt="2010 BRES özgün şehir üçgen tel-kafes plan görünüşü"/><svg id="overlay" viewBox="0 0 1400 920" aria-label="SpawnPoint vurgusu"></svg></div>
<div class="panel" id="info"></div>
<p><small>G19 kaynak testi: 16 özgün isim, 16 × (12 bayt XYZ + 16 bayt quaternion + 12 bayt ölçek) doğrulandı.
Görüntüde kaynak mesh üst hiyerarşi dönüşümleri ve orijinal ışıklandırma uygulanmadı.</small></p>
<script id="records" type="application/json">__DATA__</script>
<script>
"use strict";
const data=JSON.parse(document.getElementById("records").textContent);
const sel=document.getElementById("pick"),svg=document.getElementById("overlay");
const info=document.getElementById("info");
data.nodes.forEach(n=>{const o=document.createElement("option");o.value=n.node;o.textContent=n.node;sel.append(o)});
function project(n){let m=data.map;return [
m.pixel_origin_offset_xy[0]+(n.position_XYZ[0]-m.low_xy[0])*m.pixel_world_scale,
m.canvas_height-m.pixel_origin_offset_xy[1]-(n.position_XYZ[1]-m.low_xy[1])*m.pixel_world_scale
]}
function draw(){let n=data.nodes.find(x=>x.node===sel.value)||data.nodes[0];
let [x,y]=project(n);
svg.innerHTML='<circle cx="'+x+'" cy="'+y+'" r="22" fill="none" stroke="#ffde74" stroke-width="3"/>'+
'<circle cx="'+x+'" cy="'+y+'" r="8" fill="#ffecb0"/>';
info.innerHTML='<strong>'+n.node+'</strong><p>Konum (X, Y, Z): '+n.position_XYZ.join(' / ')+
'</p><p>Quaternion (x, y, z, w): '+n.quaternion_xyzw.join(' / ')+
'</p><p>Ölçek: '+n.scale_XYZ.join(' / ')+
'</p><small>Özgün CLARA dönüştürme verisi; gerçek oyuncu başlangıcı olduğuna dair kanıt yok.</small>'}
sel.addEventListener("change",draw);draw();
</script></body></html>"""
    out.write_text(page.replace("__PNG__",png).replace("__DATA__",j.replace("</","<\\/")),encoding="utf-8")
    assert out.stat().st_size>100000

def main(ipa:Path,out:Path,png:Path,preview:Path):
    with zipfile.ZipFile(ipa) as z:
        clev=z.read("Payload/IronMan2.app/clev")
        raw=get_exact(clev,decode(clev,".bclara"),"level1.bclara")
    nodes=exact_spawns(raw)
    meshrows,_=source()
    extra=render(nodes,meshrows,png)
    result={
      "game":"Gameloft Iron Man 2 iOS 2010 (original owner assets)",
      "original_level1_bclara_sha256":hashlib.sha256(raw).hexdigest(),
      "original_level1_bytes":len(raw),
      "source_native_16_named_spawnpoints":nodes,
      "source_original_spawn_nodes_valid":16,
      "source_all_native_tagged_transform_lengths_are_12_16_12":True,
      "source_quaternion_norm_and_unit_scales_verified":True,
      "original_player_start_node_identified":False,
      "original_mission_node_to_actor_mapping_decoded":False,
      "no_fabricated_source_geometry_or_textures":True,
      "no_Vita_game_build_or_test":True,
      **extra}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    html_page(nodes,extra,png,preview)
    print("G19 2010 original C1L1 authentic 16 source SpawnPoint transforms",[(n["node"],n["position_XYZ"]) for n in nodes])
    print("G19 city native bbox",extra["source_bres_bbox_min_XYZ"],extra["source_bres_bbox_max_XYZ"])
    print("G19 genuine nodes inside original raw mesh XY AABB",extra["nodes_inside_untransformed_source_BRES_AABB_XY"],"/16")
    print("PASS original 16 CLARA source vec3+quaternion+scale + 370 BRES mesh 22919 triangles 2D top-down per-source preview; NO VPK")
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--ipa",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    a.add_argument("--png",type=Path,required=True)
    a.add_argument("--html",type=Path,required=True)
    args=a.parse_args();main(args.ipa,args.out,args.png,args.html)
