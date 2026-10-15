#!/usr/bin/env python3
"""G16.1: follow genuine relocated non-string 2010 BRES shader field pointer.

Authentically decode the *bytes* at referred target, not inventing a texture,
RGBA, lightmap, bone or blend semantic. CHANNEL1 original source field is a
grounded name but role remains unproven until iOS engine call-site linking.
"""
from __future__ import annotations
import argparse,collections,contextlib,io,json,struct,zipfile
from pathlib import Path
from b24_map_first_source_BRES_real_relocation_materials import BDAEZIP,SOURCES,load,string,u
from b24_map_first_2010_source_60byte_material_texture_index_recovery import decode

TARGETS={"material__20","c1l1_3building","standard_16dd","orig_07___default"}
def examine(name,blob):
    info=load(name,blob)
    with contextlib.redirect_stdout(io.StringIO()):
        props,_=decode(name,blob)
    n=u(blob,16); start=u(blob,20)
    reloc={u(blob,start+i*4) for i in range(n)}
    mat0=min(q["source_record_offset"] for q in info["materials"])
    positions=sorted({q["property_60_offset"] for q in props})
    out=[]
    for prop in props:
        label=prop["original_material_name"]
        if label.casefold() not in TARGETS:continue
        b=prop["property_60_offset"];e=next((p for p in positions if p>b),mat0)
        entries=[]
        for offset in range(b,e,4):
            if offset not in reloc:continue
            dest=u(blob,offset)
            if dest>=len(blob):raise ValueError("bad true source relocation destination")
            txt=string(blob,dest)
            excerpt=blob[dest:dest+48]
            words=[struct.unpack_from("<I",excerpt,k)[0]
                   for k in range(0,len(excerpt)-3,4)]
            vals=[struct.unpack_from("<f",excerpt,k)[0]
                  for k in range(0,len(excerpt)-3,4)]
            entries.append({
              "field_offset_rel_property":offset-b,
              "source_relocation_proven":True,
              "pointer_target_native_offset":dest,
              "pointer_target_actual_source_string":txt,
              "pointer_target_raw_first_48_bytes":excerpt.hex(),
              "pointer_target_u32_hex":[f"0x{v:08X}" for v in words],
              "pointer_target_first_12_float_candidate":[
                    round(f,7) if abs(f)<1e6 else None for f in vals],
              "pointer_target_string_or_data_kind_verified":bool(txt),
              "shader_effect_semantics_proven":False
            })
        out.append({"source_file":name+".bdae",
                    "original_material":label,
                    "source_native_property_size":e-b,
                    "all_source_relocated_shader_field_targets":entries})
    return out

def main(path):
    entries=[]
    with zipfile.ZipFile(BDAEZIP) as z:
        if z.testzip():raise ValueError("original BRES ZIP CRC")
        for stem in SOURCES:
            entries+=examine(stem,z.read("original_models/"+stem+".bdae"))
    channels=collections.Counter()
    for item in entries:
        for t in item["all_source_relocated_shader_field_targets"]:
            if t["pointer_target_actual_source_string"]:
                channels[t["pointer_target_actual_source_string"]]+=1
    report={"source_original_BRES_files":10,
            "source_material_target_rows":len(entries),
            "original_source_shader_relocated_string_frequency":dict(channels),
            "source_relocated_material_target_binary_snippets":entries,
            "CHANNEL1_original_address_literal_if_present":channels["CHANNEL1"]>0,
            "source_gpu_shading_semantics_verified":False,
            "no_render_color_claims":True,"no_VPK":True}
    assert len(entries)>12 and channels["CHANNEL1"]>0
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2)+"\n")
    for x in entries:
        if x["original_material"].lower() in ("material__20","c1l1_3building"):
            print("G16.1 ORIGINAL",x["source_file"],x["original_material"],
                  [(t["field_offset_rel_property"],
                    t["pointer_target_actual_source_string"],
                    t["pointer_target_raw_first_48_bytes"][:64],
                    t["pointer_target_first_12_float_candidate"][:4])
                    for t in x["all_source_relocated_shader_field_targets"]])
    print("PASS G16.1 native source actual 2010 BRES pointer-target bytes, CHANNEL1 source names; no shader emulation, no VPK")
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--out",required=True,type=Path)
    args=a.parse_args();main(args.out)
