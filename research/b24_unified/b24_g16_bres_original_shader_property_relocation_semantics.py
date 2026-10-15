#!/usr/bin/env python3
"""G16 2010 BRES native 40/60B shader property relocations and field names.

Resolve only genuine BRES relocated pointer fields, not accidental integers.
For unknown 40B/60B properties, classify native 20B slot records, literal
pointer targets and original source string names, DO NOT claim RGBA semantics.
"""
from __future__ import annotations
import argparse,collections,contextlib,io,json,zipfile,struct
from pathlib import Path
from b24_map_first_source_BRES_real_relocation_materials import (
    BDAEZIP,SOURCES,load,string,u
)
from b24_map_first_2010_source_60byte_material_texture_index_recovery import decode

TARGETS={"material__20","c1l1_3building","standard_16dd","orig_07___default"}
def audit(stem,raw):
    meta=load(stem,raw)
    with contextlib.redirect_stdout(io.StringIO()):
        props,_=decode(stem,raw)
    num=u(raw,16); pointer=u(raw,20)
    relocated={u(raw,pointer+i*4) for i in range(num)}
    # Real pointer positions include relocation table, not the destination.
    mat_start=min(m["source_record_offset"] for m in meta["materials"])
    start_positions=sorted({u(raw,r["shader_88_offset"]+12) for r in props})
    records=[]
    for p in props:
        name=p["original_material_name"]
        offset=p["property_60_offset"]
        next_offset=next((x for x in start_positions if x>offset),mat_start)
        size=next_offset-offset
        if size<20 or size>120:
            raise ValueError(f"unhandled genuine shader property length: {stem}:{name}:{size}")
        if size%4:raise ValueError("unaligned property size")
        ptrs=[]
        allwords=[]
        for k in range(0,size,4):
            v=u(raw,offset+k)
            isptr=offset+k in relocated
            # Only interpretation guaranteed: pointer relocation marks this slot as an address.
            destination=string(raw,v) if isptr else None
            ptrs.append({"field_byte_offset":k,"native_value":v,
                         "real_relocation_pointer":isptr,
                         "native_relocated_string_if_valid":destination}) if isptr else None
            allwords.append({"field_byte_offset":k,"hex":f"0x{v:08X}",
                "relocated_pointer":isptr,
                "value_is_source_string":bool(destination)})
        row={"source_file":stem+".bdae","material":name,"original_native_property_bytes":size,
             "source_authored_TGA":p["candidate_true_source_TGA"],
             "shader88_record_offset":p["shader_88_offset"],
             "shader88_property_pointer":offset,
             "source_native_20byte_records": [
                 {"record_index":i//20,
                  "slot_start":i,
                  "u32_hex":[w["hex"] for w in allwords[i//4:(i+20)//4]],
                  "relocated_strings":[r["native_relocated_string_if_valid"]
                                       for r in ptrs if i<=r["field_byte_offset"]<i+20 and r["native_relocated_string_if_valid"]]}
                 for i in range(0,size,20)] if size%20==0 else [],
             "all_relocated_ptrs":ptrs,"all_original_u32_words":allwords,
             "RGBA_ALPHA_BLEND_SHADER_SEMANTICS_VERIFIED":False}
        records.append(row)
    return records

def main(outfile):
    records=[]
    with zipfile.ZipFile(BDAEZIP) as z:
        assert z.testzip() is None
        for stem in SOURCES:
            records+=audit(stem,z.read("original_models/"+stem+".bdae"))
    focus=[r for r in records if r["material"].casefold() in TARGETS]
    patterns=collections.defaultdict(list)
    for r in records:
        strings=tuple((k["field_byte_offset"],k["native_relocated_string_if_valid"])
                      for k in r["all_relocated_ptrs"] if k["native_relocated_string_if_valid"])
        group=(r["original_native_property_bytes"],strings,bool(r["source_authored_TGA"]))
        patterns[str(group)].append(r["source_file"]+":"+r["material"])
    out={"source_files":10,"original_material_records":len(records),
         "source_native_property_signature_patterns":[
             {"signature":k,"count":len(v),"samples":v[:12]} for k,v in patterns.items()],
         "real_2010_bres_material_property_records":records,
         "priority_relocated_shader_fields":focus,
         "original_RGBA_semantics_verified":False,
         "original_alpha_blend_semantics_verified":False,
         "original_level_spawn_verified":False,
         "VPK_built":False}
    assert len(records)==194 and len(focus)>12
    outfile.parent.mkdir(parents=True,exist_ok=True)
    outfile.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    for r in focus:
        if r["material"].casefold() in {"material__20","c1l1_3building"}:
            print("G16 FOCUS",r["source_file"],r["material"],
                  "property",r["original_native_property_bytes"],
                  "PTR",[(x["field_byte_offset"],x["native_relocated_string_if_valid"])
                         for x in r["all_relocated_ptrs"]],
                  "U32", [x["hex"] for x in r["all_original_u32_words"]])
    print("PASS G16 194 original native shader material entries, pointer relocations and source names, no invented color. NO VPK.")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True,type=Path)
    args=p.parse_args();main(args.out)
