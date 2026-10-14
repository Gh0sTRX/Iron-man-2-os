#!/usr/bin/env python3
"""B24 original C1L1 material->texture pointer graph forensic audit.

Reads only user's original B11 archived BDAE bytes. Identifies independently
validated (material name, -fx) and (texture name, alias, historical path)
records, and explores how their STRUCT ADDRESSES are referenced.

This deliberately DOES NOT assign a diffuse texture from proximity, name
resemblance, UV range or adjacent pointer heuristics. Emit a reproducible
metadata-only report for solving actual source BRES material linkage.
No VPK, no texture data output, no private raw asset export.
"""
from __future__ import annotations
import argparse, collections, json, pathlib, re, struct, zipfile

ARCH=pathlib.Path("research/B11_C1L1_Source_Parser.zip")
def rd(buf,at):
    return struct.unpack_from("<I",buf,at)[0] if 0<=at<=len(buf)-4 else None
def inspect(name,buf):
    strings={}
    for m in re.finditer(rb"[\x20-\x7e]{4,}",buf):
        try:strings[m.start()]=m.group().decode("ascii")
        except UnicodeDecodeError:pass
    words=collections.defaultdict(list)
    for o in range(0,len(buf)-3,4):words[rd(buf,o)].append(o)
    textures=[]
    for o in range(0,len(buf)-19,4):
        a,b,c,d,e=(rd(buf,o+i) for i in (0,4,8,12,16))
        sa,sb,sc=(strings.get(a,""),strings.get(b,""),strings.get(c,""))
        if sa.lower().endswith(".tga") and sc.lower().endswith(".tga") and \
           sb.lower().endswith("_tga") and d==e==0 and \
           sa.lower()==sc.rsplit("/",1)[-1].lower():
            textures.append({"offset":o,"name":sa,"alias":sb,"path":sc,
              "str_offsets":{"name":a,"alias":b,"path":c}})
    materials=[]
    for o in range(0,len(buf)-11,4):
        a,b,c=(rd(buf,o),rd(buf,o+4),rd(buf,o+8))
        sa,sb=strings.get(a,""),strings.get(b,"")
        if sa.endswith("-fx") and sa[:-3]==sb and c==0:
            materials.append({"offset":o,"name":sb,"fx":sa,"name_ptr":b,"fx_ptr":a})
    tex_offsets={t["offset"]:t for t in textures}
    association=collections.defaultdict(set)
    no_link=[]
    for mat in materials:
        mo=mat["offset"]
        # Trace validated pointer-to-record occurrences. A pointer to a
        # string does not prove the material's assigned texture slot.
        mrefs=words.get(mo,[])
        rows=[]
        for tex in textures:
            to=tex["offset"]
            trefs=words.get(to,[])
            direct=[]
            for off in range(mo+12,min(len(buf)-3,mo+256),4):
                if rd(buf,off)==to:direct.append(off)
            near=[]
            if mrefs and trefs:
                for mr in mrefs:
                    for tr in trefs:
                        delta=tr-mr
                        if abs(delta)<=192:near.append((mr,tr,delta))
            if direct or near:
                rows.append({"texture":tex["name"],"texture_record":to,
                  "direct_material_trailing_fields":direct[:6],
                  "parent_pointer_adjacencies":near[:6],
                  "evidence":"record_adjacency_ONLY_NOT_MATERIAL_SLOT"})
                association[tex["name"]].add(mat["name"])
        material_row={"material":mat["name"],"material_record":mo,
                      "material_record_references":mrefs[:12],
                      "candidate_texture_records":rows[:30],
                      "candidate_count":len(rows),
                      "proven_material_texture_link":False}
        if not rows:no_link.append(mat["name"])
        mat.update(material_row)
    return {
        "bdae":name,"bytes":len(buf),"valid_texture_records":len(textures),
        "valid_material_records":len(materials),
        "unique_texture_names":sorted({t["name"] for t in textures}),
        "material_candidates_only_no_assignments":materials,
        "unconnected_material_names":no_link,
        "direct_links_PROVEN":0,
        "any_unambiguous_material_texture_binding_claim":False,
        "texture_records":[{"offset":t["offset"],"name":t["name"],
                            "str_offsets":t["str_offsets"],
                            "record_backreference_count":len(words.get(t["offset"],[]))}
                            for t in textures]
    }
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=pathlib.Path,required=True)
    args=ap.parse_args()
    results=[]
    with zipfile.ZipFile(ARCH) as z:
        assert z.testzip() is None
        for member in sorted(x for x in z.namelist() if x.endswith(".bdae")):
            name=member.rsplit("/",1)[-1]
            results.append(inspect(name,z.read(member)))
    counts=collections.Counter()
    for r in results:
        counts["files"]+=1
        counts["texture_records"]+=r["valid_texture_records"]
        counts["material_records"]+=r["valid_material_records"]
        counts["materials_with_pointer_proximity_candidates"]+=sum(bool(m["candidate_count"]) for m in r["material_candidates_only_no_assignments"])
        counts["material_records_without_candidates"]+=len(r["unconnected_material_names"])
        print("BDAE",r["bdae"],"tex",r["valid_texture_records"],"materials",r["valid_material_records"],
              "adjacency_candidates",sum(bool(m["candidate_count"]) for m in r["material_candidates_only_no_assignments"]))
        for m in r["material_candidates_only_no_assignments"][:7]:
            print("  MATERIAL",m["material"],"record",hex(m["material_record"]),
                  "backrefs",len(m["material_record_references"]),
                  "possible_records",[(c["texture"],len(c["direct_material_trailing_fields"]),len(c["parent_pointer_adjacencies"])) for c in m["candidate_texture_records"][:6]])
    data={"status":"B11 SOURCE POINTER DIAGNOSTIC NOT MATERIAL BINDING",
          "counts":dict(counts),"actual_mat_to_diffuse_link_proven":False,
          "files":results,
          "next":"Reverse BRES material sampler structures and texture slot pointers, not proximity guesses."}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
    assert counts["files"]>=10
    assert counts["texture_records"]>=190
    print("PASS original source material pointer graph forensic inventory; no false diffuse assignments, no VPK")
if __name__=="__main__":main()
