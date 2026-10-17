#!/usr/bin/env python3
"""G158 provenance: identity-match original 2010 G66 render RGBA to the
pre-existing authentic G64 original 2010 named PVR PNG records.

Do not assume generated G66 texture index == native TGA index. Match exact
decoded RGBA bytes AND width/height; if not matched keep 'unresolved'.
No imagery/model is written. In particular, do NOT rename a group with an
unproven source model or map texture where the RGBA is not a byte match.
"""
import argparse
import base64
import collections
import hashlib
import io
import json
import re
import struct
import zipfile
from pathlib import Path

from PIL import Image

def run(g104,g64,out):
    html=g64.read_text(encoding="utf-8")
    m=re.search(r'<script id="payload"[^>]*>(.*?)</script>',html,re.S)
    if not m:raise ValueError("G64 original source viewer payload absent")
    p=json.loads(m.group(1))
    originals=p.get("originalPVRs")
    if not isinstance(originals,list) or len(originals)!=24:
        raise ValueError("G64 original source PVR source 24 named records changed")
    lookup=collections.defaultdict(list)
    for a in originals:
        name=a.get("name","")
        raw=base64.b64decode(a.get("base64",""),validate=True)
        with Image.open(io.BytesIO(raw)) as im:
            rgba=im.convert("RGBA")
            identity=(rgba.width,rgba.height,hashlib.sha256(rgba.tobytes()).hexdigest())
        if not name.lower().endswith(".tga"):
            raise ValueError("G64 sourced real named owner image unexpected name")
        lookup[identity].append(name)
    findings=[]
    with zipfile.ZipFile(g104) as z:
        if z.testzip() is not None:raise ValueError("G104 source VPK checksum mismatch")
        for atlas_id in range(31):
            raw=z.read(f"assets/G66_city_tex_{atlas_id:02d}.g66t")
            if raw[:4]!=b"G66T":raise ValueError("G104 source PVR atlas bytes invalid")
            v,w,h=struct.unpack_from("<3I",raw,4)
            if v!=1 or w<8 or w>1024 or h<8 or h>1024 or len(raw)!=16+w*h*4:
                raise ValueError("G104 original source city G66 texture format drift")
            identity=(w,h,hashlib.sha256(raw[16:]).hexdigest())
            names=sorted(set(lookup.get(identity,[])))
            findings.append({
                "G66_render_atlas_id":atlas_id,
                "source_image_RGBA_exact_match_to_G64_named_PVR":bool(names),
                "original_G64_real_named_PVRs":names,
                "unresolved_not_proof_of_unmapped_original":not bool(names)
            })
    r={
        "method":"Original 2010 owner G104 G66T 16B header + exact width, height, uncompressed RGBA sha256 against owner original G64 decoded named PVR PNG",
        "G64_original_named_PVR_records":len(originals),
        "G66_actual_2010_source_atlases":len(findings),
        "matched_atlases":sum(bool(x["original_G64_real_named_PVRs"]) for x in findings),
        "actual_G66_source_atlas_index_12":findings[12],
        "actual_G66_source_atlas_index_17":findings[17],
        "all_original_atlas_names":findings,
        "G65_additional_atlases_not_present_in_G64_can_remain_unresolved":True,
        "name_match_is_exact_pixel_provenance_not_source_object_or_solidness":True,
        "no_original_pixel_payload_exported":True,
        "no_new_vpk":True
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    print("G158 authentic real original 2010 pixel atlas match",r["matched_atlases"],"/31")
    print("G158 actual G66 city source Atlas12:",findings[12])
    print("G158 actual G66 city source Atlas17:",findings[17])
    print("G158 PASS exact byte match, no invented source atlas names, no raw source export, no VPK")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--g104-original-vpk",required=True,type=Path)
    p.add_argument("--g64-source-html",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    run(a.g104_original_vpk,a.g64_source_html,a.out)

if __name__=="__main__":main()
