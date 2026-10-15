#!/usr/bin/env python3
"""G15 source-only BRES shader raw parameter probe, no invented lighting.

Looks inside ORIGINAL 2010 BRES bytes addressed by each 88-byte shader
record's property pointer. Unlike the G11 texture index recovery this
inspects *non-diffuse* shader families as raw bytes, without assuming the
same 60-byte structure as textured records. It must not assign a color,
blend operation, emissive strength or texture without provenance.
"""
from __future__ import annotations
import argparse
import collections
import contextlib
import io
import json
import struct
import zipfile
from pathlib import Path
from b24_map_first_source_BRES_real_relocation_materials import (
    BDAEZIP,SOURCES,load,u
)
from b24_map_first_2010_source_60byte_material_texture_index_recovery import (
    decode as decode60
)

def probe(stem,blob):
    base=load(stem,blob)
    with contextlib.redirect_stdout(io.StringIO()):
        props,_=decode60(stem,blob)
    # First native 64B material table is a definite structural bound.
    mat_begin=min(r["source_record_offset"] for r in base["materials"])
    positions=[]
    for x in props:
        pos=u(blob,x["shader_88_offset"]+12)
        if not 0<=pos<mat_begin: raise ValueError("source shader prop pointer outside source area")
        positions.append(pos)
    if len(set(positions))!=len(positions):
        raise ValueError("duplicate shader parameter address")
    ordered=sorted(positions)
    res=[]
    for x in props:
        off=x["shader_88_offset"]
        words=[u(blob,off+4*i) for i in range(22)]
        p=words[3]
        nxt=next((v for v in ordered if v>p),mat_begin)
        bound=max(0,min(nxt,mat_begin)-p)
        if bound<20:raise ValueError("unexpected original shader properties shorter than 20: "+stem+" "+x["original_material_name"])
        data=blob[p:p+min(bound,96)]
        vals=[struct.unpack_from("<I",data,i)[0] for i in range(0,len(data)-3,4)]
        # Raw hex only: bytes >=0xFF000000 might be RGBA, sentinel, a mask,
        # a pointer or unrelated bitfield. They are CANDIDATES, not colors.
        packed=[{"u32_index":i,"value":f"0x{v:08X}"}
                for i,v in enumerate(vals) if (v>>24)==255]
        flags=(words[2],words[12],words[17],words[18],words[20])
        res.append({
            "source_file":stem+".bdae",
            "material":x["original_material_name"],
            "native_shader88_flag_words_2_12_17_18_20":flags,
            "source_shader_property_pointer_offset":p,
            "property_bytes_before_next_parameter_pointer_upper_bound":bound,
            "property_raw_first_up_to_96_hex_bytes":data.hex(),
            "property_raw_first_up_to_96_u32_hex":[f"0x{v:08X}" for v in vals],
            "packed_ARGB_or_unrelated_raw_candidates":packed[:18],
            "same_source_shader_native_named_TGA_if_ANY":x["candidate_true_source_TGA"],
            "this_probe_proves_interpreted_RGBA":False,
            "this_probe_proves_blend_alpha_emissive":False,
        })
    return res

def main(out):
    rows=[]
    with zipfile.ZipFile(BDAEZIP) as z:
        assert z.testzip() is None
        for stem in SOURCES:
            rows+=probe(stem,z.read("original_models/"+stem+".bdae"))
    cases=collections.defaultdict(list)
    for r in rows:
        k=tuple(r["native_shader88_flag_words_2_12_17_18_20"])+(bool(r["same_source_shader_native_named_TGA_if_ANY"]),)
        cases[k].append(r["source_file"]+":"+r["material"])
    groups=[
        {"source_shader_flag_signature":list(k[:5]),
         "has_authenticated_TGA_pointer":k[5],
         "native_material_instances":len(v),
         "sample_source_files_and_materials":v[:12]}
        for k,v in sorted(cases.items(),key=lambda kv:-len(kv[1]))
    ]
    focus=[r for r in rows if r["material"].casefold() in
       {"material__20","c1l1_3building","standard_16dd","orig_07___default"}]
    assert len(rows)>=190 and len(groups)>=5
    assert len(focus)>12
    j={"source":"authentic 2010 private owner BRES archive",
       "source_original_10_files":len(SOURCES),
       "source_material_instances":len(rows),
       "native_shader_flag_signatures":groups,
       "priority_original_shader_property_raw_records":focus,
       "all_source_shader_parameter_records":rows,
       "source_color_semantics_proven":False,
       "source_emissive_transparency_semantics_proven":False,
       "source_spawn_and_level_lighting_proven":False,
       "no_mesh_texture_overrides":True,"no_VPK":True}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
    for g in groups:
        print("G15 SOURCE SHADER SIGNATURE",g["source_shader_flag_signature"],
              "PVR",g["has_authenticated_TGA_pointer"],
              "native original material instances",g["native_material_instances"],
              "names",g["sample_source_files_and_materials"][:3])
    for r in focus:
        if r["material"].casefold() in {"material__20","c1l1_3building"}:
            print("G15 TARGET",r["source_file"],r["material"],
                  "prop_bound",r["property_bytes_before_next_parameter_pointer_upper_bound"],
                  "nativeU32",r["property_raw_first_up_to_96_u32_hex"][:18])
    print("PASS G15 original 2010 BRES shader family native source parameter bytes, NO interpreted render colors NO VPK.")

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--out",type=Path,required=True)
    args=a.parse_args()
    main(args.out)
