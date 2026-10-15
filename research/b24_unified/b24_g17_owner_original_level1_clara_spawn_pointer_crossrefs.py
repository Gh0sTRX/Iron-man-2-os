#!/usr/bin/env python3
"""G17 genuinely source-constrained CLARA level1 spawn cross-reference atlas.

Avoid the G11 false assumption that a plausible float triplet near a string
is the real original player location. Search original owner 2010 level1 data
for a *structural* reference chain (literal node -> pointer table -> numeric
record). All candidate floats remain explicitly unverified. No engine edits.
"""
from __future__ import annotations
import argparse,collections,hashlib,html,json,math,re,struct,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact

NEEDLES=[rb"SpawnPoint[0-9_]{0,14}",rb"Position\x00",
         rb"NodeMaterials\x00",rb"Rotation\x00",
         rb"Translation\x00",rb"Scale\x00",
         rb"UseDefaultGPMaterials\x00"]
def names(data:bytes):
    records=[]
    for term in NEEDLES:
        for m in re.finditer(term,data):
            records.append({"offset":m.start(),"source_ascii":m.group(0).rstrip(b"\x00").decode("latin1"),
                            "literal_source_length":len(m.group(0))})
    return sorted(records,key=lambda q:q["offset"])

def scan(data:bytes):
    n=len(data); named=names(data)
    target_to_nodes=collections.defaultdict(list)
    for node in named:target_to_nodes[node["offset"]].append(node)
    # Object identifiers may repeat; match all exact byte offsets.
    targets=set(target_to_nodes)
    xrefs=collections.defaultdict(list)
    for location in range(0,n-3,4):
        unsigned=struct.unpack_from("<I",data,location)[0]
        signed=struct.unpack_from("<i",data,location)[0]
        interpretations=(
           ("exact_2010_file_absolute_LE_u32",unsigned),
           ("relative_positive_LE_u32",location+unsigned),
           ("relative_signed_LE_i32",location+signed),
           ("relative_from_next_LE_i32",location+4+signed),
        )
        for kind,dest in interpretations:
            if dest in targets and len(xrefs[(dest,kind)])<32:
                xrefs[(dest,kind)].append(location)
    def plausible(xyz):
        return (all(math.isfinite(v) and abs(v)<1500 for v in xyz)
                and any(abs(v)>1 for v in xyz)
                and sum(abs(v)>.02 for v in xyz)>=2)
    out=[]
    for node in named:
        at=node["offset"]
        references=[{"type":k,"source_referencing_u32_word_positions":positions}
                    for (dest,k),positions in sorted(xrefs.items())
                    if dest==at]
        # Full float candidate sample around proven ptr use; also literal nearby
        # for forensic context, never labeled original authored coordinates.
        sample_sites={at: "literal_name_context"}
        for obj in references:
            for loc in obj["source_referencing_u32_word_positions"][:8]:
                sample_sites[loc]="pointer_reference_context"
        candid=[]
        for site,kind in sorted(sample_sites.items()):
            first=max(0,(site-64+3)//4*4);last=min(n-12,site+64)
            for p in range(first,last+1,4):
                xyz=struct.unpack_from("<fff",data,p)
                if plausible(xyz):
                    candid.append({"potential_raw_float3_at_file_offset":p,
                       "nearest_provenance_context":kind,
                       "candidate_xyz":[round(z,5) for z in xyz],
                       "confidence":"UNKNOWN_NOT_LINKED_TO_CLARA_TYPED_NODE"})
                if len(candid)>=24:break
            if len(candid)>=24:break
        out.append({**node,
            "matching_native_u32_reference_patterns":references,
            "pointer_count":sum(len(q["source_referencing_u32_word_positions"]) for q in references),
            "nearby_float_triplets_unverified":candid[:24]})
    return {"original_level1_file_size":n,"original_level1_sha256":hashlib.sha256(data).hexdigest(),
         "raw_original_file_first_96_bytes_hex":data[:96].hex(),
         "actual_source_named_strings":out,
         "unique_real_SpawnPoint_literal_names":sorted(set(
             r["source_ascii"] for r in out if r["source_ascii"].startswith("SpawnPoint"))),
         "source_string_absolute_pointer_hits":sum(
             len(s["source_referencing_u32_word_positions"]) for r in out
             for s in r["matching_native_u32_reference_patterns"]
             if s["type"]=="exact_2010_file_absolute_LE_u32"),
         "source_genuine_player_spawn_xyz_confirmed":False,
         "source_structure_SpawnPoint_to_typed_Position_link_confirmed":False,
         "source_level1_parent_node_transforms_confirmed":False,
         "never_use_triplet_near_string_as_actual_spawn":True,
         "no_map_gameplay_or_VPK_modifications":True}

HTML=r"""<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Iron Man 2 G17 — Orijinal C1L1 sahne adları</title>
<style>body{max-width:960px;margin:auto;padding:18px;background:#101923;color:#eaf1fa;font-family:system-ui;line-height:1.5}
small,p{color:#c0cbd8}details{padding:12px;margin:10px 0;border:1px solid #526574;border-radius:7px}
summary{cursor:pointer}code{color:#96d9da;font-size:12px}input{width:95%;padding:12px;font-size:16px;background:#192938;color:white;border:1px solid #789;border-radius:7px}
pre{white-space:pre-wrap;overflow-wrap:anywhere}b{color:#eebd7b}
</style></head><body>
<h1>G17 — Özgün ilk bölümün SpawnPoint incelemesi</h1>
<p>Yalnızca Gameloft 2010 kaynak <code>level1.bclara</code> dosyasındaki adlar ve ham adreslere bakar.
<strong>Gerçek oyuncu başlangıç koordinatı henüz kanıtlanmadı.</strong>
Yakındaki sayılar tahmini adaydır; oyuna uygulanmaz. Yeni VPK kurulumu gerektirmez.</p>
<input id="q" placeholder="SpawnPoint000, Position, NodeMaterials …">
<p id="status"></p><div id="list"></div>
<script id="raw" type="application/json">__PAYLOAD__</script>
<script>
const source=JSON.parse(document.getElementById('raw').textContent);
const q=document.getElementById('q');const list=document.getElementById('list');
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function draw(){let term=q.value.toLowerCase();let rows=source.actual_source_named_strings.filter(x=>x.source_ascii.toLowerCase().includes(term));
document.getElementById('status').textContent=rows.length+' orijinal isim konumu / '+source.actual_source_named_strings.length;
list.innerHTML=rows.map(r=>'<details><summary><code>'+esc(r.source_ascii)+'</code> — özgün bayt '+r.offset+' — adres referansı '+r.pointer_count+'</summary>'+
'<p>Buradaki hiçbir XYZ orijinal oyuncu spawn koordinatı olarak doğrulanmadı.</p>'+
'<pre>'+esc(JSON.stringify(r.matching_native_u32_reference_patterns,null,2))+'</pre>'+
'<p>Yakın alandaki olası sayısal üçlü sayısı: '+r.nearby_float_triplets_unverified.length+'</p></details>').join('')}
q.addEventListener('input',draw);draw();
</script></body></html>"""

def main(ipa:Path,out:Path,preview:Path):
    with zipfile.ZipFile(ipa) as z:
        clev=z.read("Payload/IronMan2.app/clev")
        raw=get_exact(clev,decode(clev,".bclara"),"level1.bclara")
    report=scan(raw)
    assert report["original_level1_file_size"]==339733
    assert report["unique_real_SpawnPoint_literal_names"]
    out.parent.mkdir(parents=True,exist_ok=True)
    preview.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    payload=json.dumps({"actual_source_named_strings":report["actual_source_named_strings"]},
                       ensure_ascii=False,separators=(",",":")).replace("</","<\\/")
    preview.write_text(HTML.replace("__PAYLOAD__",payload),encoding="utf-8")
    assert preview.stat().st_size>3000
    print("G17 authentic source level1 size",report["original_level1_file_size"])
    print("G17 original SpawnPoint identifiers",report["unique_real_SpawnPoint_literal_names"][:32])
    print("G17 source exact native 32bit absolute pointer hits",report["source_string_absolute_pointer_hits"])
    for row in report["actual_source_named_strings"]:
        if row["source_ascii"].startswith("SpawnPoint"):
            print("G17 SPAWN-NAME",row["source_ascii"],
                  "at",row["offset"],"reference patterns",row["matching_native_u32_reference_patterns"],
                  "candidate_float_count_NOT_PLAYER_SPAWN",len(row["nearby_float_triplets_unverified"]))
    print("PASS G17 original 2010 BCLARA byte/refs contact inspection; no proven real spawn, no VPK")
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--ipa",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    a.add_argument("--html",type=Path,required=True)
    p=a.parse_args();main(p.ipa,p.out,p.html)
