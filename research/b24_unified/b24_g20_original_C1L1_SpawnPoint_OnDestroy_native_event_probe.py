#!/usr/bin/env python3
"""G20 source-only 2010 C1L1 native SpawnPoint OnDestroy actions.

Four original callbacks in the owner BCLARA; three have an original
Enable/Disable string and a tagged type-3 binary number. Neither actor role
nor the semantics of the following number is proven. No gameplay/VPK.
"""
from __future__ import annotations
import argparse,hashlib,json,re,struct,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact
from b24_g19_original_2010_level1_spawn_transforms_city_xy_map import exact_spawns

def audit(raw):
    nodes=exact_spawns(raw)
    d={}
    for m in re.finditer(rb"SpawnPoint(\d{3})_OnDestroy\x00",raw):
        name="SpawnPoint"+m.group(1).decode("ascii")
        if name in d:raise ValueError("duplicate event")
        act=[]
        for word in (b"Enable\x00",b"Disable\x00"):
            at=raw.find(word,m.end(),min(len(raw),m.end()+116))
            if at<0:continue
            if raw[at-5:at]!=b"\x04"+struct.pack("<I",len(word)):
                raise ValueError("original string length/type mismatch")
            tag=raw[at+len(word)]
            number=struct.unpack_from("<f",raw,at+len(word)+1)[0] if tag==3 else None
            act.append({"native_original_action":word[:-1].decode(),
                "actual_source_action_offset":at,
                "source_next_numeric_type_tag":tag,
                "source_following_f32_if_type3":number,
                "original_action_target_entity_not_verified":True})
        if len(act)>1:raise ValueError("ambiguous repeated actions")
        d[name]={"callback_source_offset":m.start(),"source_original_callback_name":m.group()[:-1].decode(),
                 "source_native_action_records":act}
    if sorted(d)!=["SpawnPoint004","SpawnPoint012","SpawnPoint014","SpawnPoint015"]:
        raise ValueError("source callback inventory differs")
    if sum(len(x["source_native_action_records"]) for x in d.values())!=3:
        raise ValueError("authentic original tagged opcode inventory drift")
    return {"original_level1_sha256":hashlib.sha256(raw).hexdigest(),
        "source_level1_bytes":len(raw),
        "all_source_16_spawnpoint_transforms":nodes,
        "four_original_SpawnPoint_OnDestroy_callbacks":d,
        "callbacks":4,"typed_Enable_Disable_actions":3,
        "original_player_spawn_not_yet_identified":True,
        "original_target_numeric_semantics_not_yet_proven":True,
        "no_gameplay_or_VPK_changes":True}

def run(ipa,out):
    with zipfile.ZipFile(ipa) as z:
        p=z.read("Payload/IronMan2.app/clev")
        level=get_exact(p,decode(p,".bclara"),"level1.bclara")
    j=audit(level)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n")
    for k,v in j["four_original_SpawnPoint_OnDestroy_callbacks"].items():
        print("G20 REAL 2010 CALLBACK",k,v)
    print("PASS authentic first level native 4 OnDestroy event callbacks, 3 typed Enable/Disable action string and number; NO VPK")
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--ipa",required=True,type=Path);a.add_argument("--out",required=True,type=Path)
    p=a.parse_args();run(p.ipa,p.out)
