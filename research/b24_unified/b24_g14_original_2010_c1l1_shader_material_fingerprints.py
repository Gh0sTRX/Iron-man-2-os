#!/usr/bin/env python3
"""G14: real 2010 C1L1 material/shader fingerprint investigation (NO VPK).

Source: exact 10 owner BRES archives committed privately as the B11 source
ZIP, plus the already verified 370 BRES mesh provenance. This tool DOES NOT
interpret shader constants as a color, blend mode or lightmaps until an
independent native format relationship proves that semantic meaning.

Focus: Material__20 curved light/dome surfaces and c1l1_3building arches.
Deliverable: searchable, offline HTML and auditable JSON with original mesh
names, face counts, UV evidence, 2010 shader property words and source PVR
references (if any).
"""
from __future__ import annotations

import argparse
import collections
import contextlib
import html
import io
import json
import struct
import zipfile
from pathlib import Path

from b24_g13_c1l1_light_dome_mesh_provenance_sheet import source as meshes_source
from b24_map_first_source_BRES_real_relocation_materials import (
    BDAEZIP, SOURCES, load, string, u
)
from b24_map_first_2010_source_60byte_material_texture_index_recovery import (
    decode as decode_60
)

TARGETS = {"material__20", "c1l1_3building",
           "standard_16dd", "orig_07___default"}
TOTAL_MESHES = 370
TOTAL_FACES = 22919


def shader_fields(name: str, blob: bytes):
    info = load(name, blob)
    with contextlib.redirect_stdout(io.StringIO()):
        properties, textures = decode_60(name, blob)
    by64 = {r["original_BRES_material_name"]: r
            for r in info["materials"]}
    assert len(by64) == len(info["materials"])
    known = {}
    for row in properties:
        label = row["original_material_name"]
        if label in known:
            raise ValueError(f"duplicate shader name in {name}: {label}")
        off = row["shader_88_offset"]
        shader88 = [u(blob, off + i * 4) for i in range(22)]
        mat64 = by64.get(label)
        if mat64 is None:
            raise ValueError(f"no native 64B material for {name}: {label}")
        raw60 = row["property_60_original_15_u32"]
        # candidate UI strings are not auto-interpreted as color / blend modes.
        pfields = info["materials"][mat64["material_index"]]["relocated_real_pointer_fields"]
        known[label] = {
            "source_file": name + ".bdae",
            "original_material_name": label,
            "material_64_offset": mat64["source_record_offset"],
            "shader_88_offset": off,
            "shader_88_words_hex": [f"0x{x:08X}" for x in shader88],
            "property_60_offset": row["property_60_offset"],
            "property_60_exists": bool(raw60),
            "property_60_words_hex": [f"0x{x:08X}" for x in raw60],
            "property_60_texture_index_candidate": row["exact_TGA_author_list_index_candidate"],
            "authored_20byte_TGA_name": row["candidate_true_source_TGA"],
            "relocated_64byte_pointer_strings": [
                {"field_off": p["field_off"], "string": p["string"]}
                for p in pfields if p.get("string")
            ],
            "possible_native_float_color_OR_other_flags": [
                {
                    "words_start": i,
                    "values": [round(struct.unpack("<f", struct.pack("<I", w))[0], 6)
                               for w in shader88[i:i + 4]]
                }
                for i in range(4, 19)
                if all(0 <= struct.unpack("<f", struct.pack("<I", w))[0] <= 1.0
                       for w in shader88[i:i + 4])
                and any(shader88[i:i + 4])
            ][:12],
            "color_semantics_proven": False,
            "blend_semantics_proven": False,
        }
    return known


def audit() -> dict:
    rows, prior = meshes_source()
    if len(rows) != TOTAL_MESHES or sum(r["source_faces"] for r, _, _ in rows) != TOTAL_FACES:
        raise ValueError("original mesh/triangle provenance invariant failed")
    per_source = {}
    with zipfile.ZipFile(BDAEZIP) as archive:
        if archive.testzip():
            raise ValueError("source BRES archive CRC failure")
        for stem in SOURCES:
            per_source[stem + ".bdae"] = shader_fields(
                stem, archive.read("original_models/" + stem + ".bdae"))
    summary = collections.defaultdict(lambda: {
        "faces": 0, "uv_positive_faces": 0, "known_PVR_faces": 0,
        "meshes": 0, "members": []
    })
    mesh_out = []
    for r, _, _ in rows:
        remapped = dict(r)
        parts = []
        for sub in r["original_BRES_authored_submesh_materials"]:
            mat = sub["original_material_name"]
            native = per_source[r["source_file"]].get(mat)
            if native is None:
                raise ValueError(f"missing original material {r['source_file']}:{mat}")
            count = int(sub["source_original_faces"])
            case = {
                "original_material_name": mat,
                "faces": count,
                "source_2010_UV_candidate": r["genuine_original_uv_candidate"],
                "source_2010_PVR": native["authored_20byte_TGA_name"],
                "shader_record_offset": native["shader_88_offset"],
                "source_shader_property60_exists": native["property_60_exists"],
                "surface_color_unverified": True,
                "shader_effect_unverified": True,
            }
            parts.append(case)
            key = (r["original_scene_group"], mat)
            s = summary[key]
            s["faces"] += count
            s["uv_positive_faces"] += count if r["genuine_original_uv_candidate"] else 0
            s["known_PVR_faces"] += count if native["authored_20byte_TGA_name"] else 0
            s["meshes"] += 1
            s["members"].append(r["source_mesh_name"])
        remapped["source_material_shading_evidence"] = parts
        remapped.pop("not_proven_to_be_dome", None)
        mesh_out.append(remapped)
    if sum(s["faces"] for s in summary.values()) != TOTAL_FACES:
        raise ValueError("material face accounting invariant failed")
    named = []
    for (group, mat), entry in sorted(summary.items()):
        named.append({"group": group, "material": mat, **entry})
    for focus in TARGETS:
        if not any(x["material"].casefold() == focus for x in named):
            raise ValueError("target original native shader missing: " + focus)
    light_uv_and_tex = sum(
        item["faces"] for r in mesh_out if r["original_scene_group"] == "lights"
        for item in r["source_material_shading_evidence"]
        if item["source_2010_UV_candidate"] and item["source_2010_PVR"]
    )
    if light_uv_and_tex != 0:
        # Earlier G13 source-proof gives ZERO intersection, fail on regression.
        raise ValueError("G13 source light UV+diffuse zero-intersection drift")
    focus_rows = [r for r in named if r["material"].casefold() in TARGETS]
    return {
        "tool": "G14 C1L1 original native BRES shader/material forensic",
        "original_source": "2010 owner-recovered BRES (10 original files)",
        "mesh_count": len(mesh_out),
        "face_count": TOTAL_FACES,
        "source_BRES_files": list(per_source),
        "source_material_tables": per_source,
        "meshes": mesh_out,
        "source_group_material_face_summary": named,
        "priority_materials": focus_rows,
        "g13_light_true_source_UV_AND_proven_diffuse_faces": light_uv_and_tex,
        "old_G13_group_counts": dict(prior),
        "original_source_shader_semantic_lighting_decoded": False,
        "original_source_vertex_colors_decoded": False,
        "original_source_real_game_spawn_decoded": False,
        "forbid_guessed_shader_colors_or_clay_fix": True,
        "diagnostic_only_NOT_VitaGPU_or_original_iOS_screenshot": True,
        "no_VPK": True,
    }


HTML = r"""<!doctype html><html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Iron Man 2 — G14 Orijinal Materyal İncelemesi</title>
<style>
:root{color-scheme:dark;font-family:system-ui,-apple-system,sans-serif}
body{background:#0c1420;color:#e8f1fa;margin:0 auto;padding:16px;max-width:1150px}
h1{font-size:clamp(22px,4vw,32px);margin-bottom:6px}
p,small{color:#abbfd0;line-height:1.6}
.panel{border:1px solid #30485b;background:#142333;border-radius:10px;padding:16px;margin:18px 0}
.controls{display:flex;gap:12px;flex-wrap:wrap}
input,select{background:#0b1924;color:#e8f1fa;border:1px solid #608399;
border-radius:6px;padding:10px;font:inherit}
input{flex:1;min-width:210px}
table{border-collapse:collapse;width:100%;font-size:13px}
td,th{padding:10px 8px;border-bottom:1px solid #27394b;text-align:left}
th{color:#b8d3e6}code{font-size:11px}
.tag{color:#edd4a5}.yes{color:#9cdeb8}.no{color:#e8a7a7}
.viewport{overflow-x:auto}
details{margin:9px 0;padding:9px;border:1px solid #2c4052;border-radius:6px}
summary{cursor:pointer}.stats{font-variant-numeric:tabular-nums}
</style></head><body>
<h1>Iron Man 2 (2010) — G14 materyal kaynak incelemesi</h1>
<p><strong>Orijinal BRES verisi, oyun ekran görüntüsü değil.</strong> 370 gerçek mesh,
22.919 üçgen. Düz turkuaz kubbeler, kayıp UV'ler ve özgün shader semantiği
arasındaki farkı dosya ve materyal seviyesinde incelemek için hazırlandı.
Renk/ışık tahmini yapılmadı; hiçbir VPK gerekmez.</p>
<div class="panel"><div class="controls">
<input id="q" aria-label="Mesh veya materyal ara" placeholder="Material__20, c1l1_3building, C1L1_light_002_87…">
<select id="grp" aria-label="Geometri grubu">
<option value="">Tüm gruplar</option><option>lights</option><option>urban</option>
<option>ground</option><option>vehicles</option></select>
<select id="uv" aria-label="UV durumu"><option value="">Tüm UV</option>
<option value="yes">UV var</option><option value="no">UV yok</option></select>
</div><p id="count" class="stats"></p>
<div class="viewport"><table><thead><tr><th>Gerçek 2010 BRES mesh</th><th>Grup</th>
<th>Üçgen</th><th>UV</th><th>Orijinal materyaller / kaynak PVR</th></tr></thead>
<tbody id="out"></tbody></table></div></div>
<div class="panel"><h3>Öncelikli materyal istatistikleri</h3>
<div id="priority"></div></div>
<p><small>Önemli: BRES içinde standart diffuse doku adı bulunmaması,
malzemenin özgün oyunda renksiz olduğu anlamına gelmez.
Özgün oyun shader, vertex color, ışık ve blending bilgileri henüz çözülmedi.</small></p>
<script id="payload" type="application/json">__DATA__</script>
<script>
"use strict";
const data=JSON.parse(document.getElementById("payload").textContent);
const query=document.getElementById("q"), group=document.getElementById("grp");
const uv=document.getElementById("uv"), out=document.getElementById("out");
const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function draw(){
 const q=query.value.toLowerCase().trim(),g=group.value,u=uv.value;
 const list=data.meshes.filter(m=>(!g||m.original_scene_group===g)
 &&(!u||(m.genuine_original_uv_candidate?"yes":"no")===u)
 &&(!q||(m.source_mesh_name+" "+m.source_file+" "+m.source_material_shading_evidence.map(s=>s.original_material_name+" "+(s.source_2010_PVR||"")).join(" ")).toLowerCase().includes(q)));
 document.getElementById("count").textContent=list.length+" / "+data.meshes.length+
 " gerçek mesh • "+list.reduce((a,m)=>a+m.source_faces,0)+" / "+data.face_count+" üçgen";
 out.innerHTML=list.map(m=>"<tr><td><code>"+esc(m.source_mesh_name)+"</code></td><td>"+
 esc(m.original_scene_group)+"</td><td>"+m.source_faces+"</td><td class="+
 (m.genuine_original_uv_candidate?"yes":"no")+">"+
 (m.genuine_original_uv_candidate?"VAR":"YOK")+"</td><td>"+
 m.source_material_shading_evidence.map(s=>"<div>"+esc(s.original_material_name)+
 " ("+s.faces+") → <span class="+(s.source_2010_PVR?"yes":"tag")+">"+
 esc(s.source_2010_PVR||"standart diffuse bağlantısı yok")+"</span></div>").join("")+"</td></tr>").join("");
}
for(const el of [query,group,uv])el.addEventListener("input",draw);
document.getElementById("priority").innerHTML=data.priority_materials.map(m=>
 "<details><summary><strong>"+esc(m.material)+"</strong> / "+esc(m.group)+
 " — "+m.faces+" üçgen; "+m.uv_positive_faces+" UV aday yüz; "+
 m.known_PVR_faces+" diffuse bağlantılı yüz</summary><p>"+
 m.members.map(esc).join(", ")+"</p></details>").join("");
draw();
</script></body></html>"""


def main(out: Path, preview: Path) -> None:
    report = audit()
    out.parent.mkdir(parents=True, exist_ok=True)
    preview.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    # Self-contained local HTML; escape a possible script end sequence.
    payload = json.dumps({
        "meshes": report["meshes"], "priority_materials": report["priority_materials"],
        "face_count": report["face_count"],
    }, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    preview.write_text(HTML.replace("__DATA__", payload), encoding="utf-8")
    assert report["mesh_count"] == 370 and report["face_count"] == 22919
    assert report["g13_light_true_source_UV_AND_proven_diffuse_faces"] == 0
    assert "Material__20" in preview.read_text(encoding="utf-8")
    assert preview.stat().st_size > 20000
    print("PASS G14 real 2010 BRES 370 meshes / 22919 faces / shader88+property60+material64.")
    for p in report["priority_materials"]:
        print("TARGET", p["group"], p["material"], "faces", p["faces"],
              "UV faces", p["uv_positive_faces"], "diffuse-pointer faces", p["known_PVR_faces"])
    print("PASS original light mesh native UV AND diffuse intersection ZERO.")
    print("PASS searchable independent single-file offline G14 source material preview.")
    print("NOT original iOS render, NOT VitaGL or real PS Vita game test, NO VPK.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--html", type=Path, required=True)
    args = parser.parse_args()
    main(args.out, args.html)
