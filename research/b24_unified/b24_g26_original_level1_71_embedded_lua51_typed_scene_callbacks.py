#!/usr/bin/env python3
"""G26: original 2010 CLARA embedded Lua5.1 static callback inventory.

71 genuine Lua 5.1 signature entries are complete native bytecode chunks
embedded directly in original user-owned level1.bclara (not just strings).
Strictly read-only. Cross-reference ORIGINAL 2010 class-tagged entity ID and
native callbacks. This does not execute/port Lua, animate cameras or prove
original real runtime mission call order.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact
from b24_g10_original_lua51_state_and_bclara_record_decode import Parser,HEADER,values
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize

SUFFIXES=("_OnInteractComplete","_OnComplete","_OnDestroy","_OnEnter","_OnStart")
def source_report(raw:bytes):
    typed=summarize(raw)
    byname={r["original_name"]:r for r in typed["source_2010_typed_class_instances"]}
    offsets=[m.start() for m in re.finditer(re.escape(HEADER[:5]),raw)]
    if len(offsets)!=71:raise ValueError("original 2010 source embedded Lua51 signatures not exactly 71")
    records=[];coverage=collections.Counter()
    for i,off in enumerate(offsets):
        p=Parser(raw,off)
        if p.fetch(12)!=HEADER:raise ValueError("wrong source Lua 5.1 header at "+str(off))
        root=p.function()
        handler=root["constants"][0] if root["constants"] else None
        if not isinstance(handler,str):raise ValueError("native Lua root has no original handler label")
        suffix=next((s for s in SUFFIXES if handler.endswith(s)),None)
        if not suffix:raise ValueError("unknown original level1 callback type: "+handler)
        node=handler[:-len(suffix)]
        if node not in byname:raise ValueError("native Lua callback cannot link to original classed node "+handler)
        owner=byname[node]
        if p.pos>len(raw) or (i<len(offsets)-1 and p.pos>offsets[i+1]):
            raise ValueError("source Lua chunk overlapping next source chunk")
        strs=values(root)
        original=[v for v in strs if isinstance(v,str)]
        records.append({"original_chunk_start":off,
             "source_original_encoded_lua_chunk_bytes":p.pos-off,
             "callback_name":handler,
             "callback_event_suffix":suffix,
             "source_authored_owner_node":node,
             "original_owner_node_ID":owner["original_numeric_name_id"],
             "original_owner_native_class":owner["original_class_name"],
             "original_owner_class_id":owner["original_class_id"],
             "script_source_constant_strings":original,
             "original_source_constants_are_not_live_executed_calls":True,
             "confirmed_Lua51_chunk_full_parse":True})
        coverage[owner["original_class_name"]]+=1
    if dict(coverage)!={"SpawnPoint":4,"Mission":45,"Trigger":17,"InteractiveObj":5}:
        raise ValueError("source callback count/type mismatch")
    important=("SetCamera","CutsceneIn","CutsceneOut","PlayAnim","PlaySFX","PlayVoice",
        "PlayMusic","SetInputEnabled","MoveEntityToEntity","MissionPause","MissionResume")
    histogram=collections.Counter(
        v for row in records for v in set(row["script_source_constant_strings"]) if v in important
    )
    return {
      "original_level1_sha256":hashlib.sha256(raw).hexdigest(),
      "original_level1_bytes":len(raw),
      "source_authentic_embedded_Lua5_1_chunks":len(records),
      "source_parsed_Lua5_1_chunks":len(records),
      "source_all_callbacks_matched_exact_original_classed_CLARA_entity_ID":True,
      "source_actual_callback_owner_native_class_counts":dict(coverage),
      "source_named_interpretable_native_engine_API_strings_occurrences":dict(histogram),
      "native_2010_all_original_level1_lua_callbacks":records,
      "original_2010_source_lua_programs_ran":False,
      "original_2010_exact_control_flow_and_cutscene_timeline_proven":False,
      "original_Mission000_is_initial_executed_mission_proven":False,
      "no_gameplay_or_VPK_changes":True
    }
def main(ipa,out):
    with zipfile.ZipFile(ipa) as z:
        pack=z.read("Payload/IronMan2.app/clev")
        raw=get_exact(pack,decode(pack,".bclara"),"level1.bclara")
    r=source_report(raw)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
    print("G26 ORIGINAL 2010 EMBEDDED Lua 5.1",r["source_parsed_Lua5_1_chunks"],"/",r["source_authentic_embedded_Lua5_1_chunks"])
    print("G26 ORIGINAL 2010 native class-owner callback distribution",r["source_actual_callback_owner_native_class_counts"])
    print("G26 confirmed source engine function names",r["source_named_interpretable_native_engine_API_strings_occurrences"])
    print("PASS G26 original first level 71 complete real Lua source callbacks linked to native CLARA classed owner IDs, NO execution/VPK.")
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--ipa",required=True,type=Path)
    a.add_argument("--out",required=True,type=Path);args=a.parse_args();main(args.ipa,args.out)
