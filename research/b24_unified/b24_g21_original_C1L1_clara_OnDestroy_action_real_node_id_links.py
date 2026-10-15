#!/usr/bin/env python3
"""G21 source-only authentic iOS 2010 level1 CLARA callback target node graph.

Proof chain: typed original OnDestroy action -> length-tagged Enable/Disable
-> type-3 float32 with EXACT integer value -> original named CLARA record
with same integer in its 4-byte source node identifier slot (offset name-7).
Three independent targets resolve: SpawnPoint015, Deco_fence2, Deco_fence6.
NO original gameplay engine, actor state transitions or Vita GPU test claimed.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re,struct,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact
from b24_g20_original_C1L1_SpawnPoint_OnDestroy_native_event_probe import audit

NAMED=re.compile(rb"[\x20-\x7e]{3,90}")
def native_name_ids(data:bytes):
    inventory=[]
    for match in NAMED.finditer(data):
        p=match.start()
        name=match.group().decode("ascii")
        if p<7 or data[p-3]!=1:continue
        if struct.unpack_from("<H",data,p-2)[0]!=len(name):continue
        nid=struct.unpack_from("<I",data,p-7)[0]
        if not 0<nid<50000:continue
        inventory.append({"authored_CLARA_numeric_name_record":nid,
             "record_source_name":name,"source_text_offset":p,
             "native_4byte_node_record_id_field_offset":p-7,
             "validated_type1_length_prefix":True})
    if len(inventory)<500:raise ValueError("Source name directory incomplete")
    return inventory

def link(data):
    records=native_name_ids(data)
    byid=collections.defaultdict(list)
    for r in records:byid[r["authored_CLARA_numeric_name_record"]].append(r)
    original=audit(data)
    edges=[]
    for source,callback in original["four_original_SpawnPoint_OnDestroy_callbacks"].items():
        for action in callback["source_native_action_records"]:
            value=action["source_following_f32_if_type3"]
            if value is None or int(value)!=value or not 0<value<50000:
                raise ValueError("source event numeric field cannot be a named node identifier")
            matched=byid[int(value)]
            if len(matched)!=1:
                raise ValueError("native action numeric target not uniquely source-record-backed")
            dest=matched[0]
            edges.append({"source_node":source,
                "source_callback":source+"_OnDestroy",
                "original_source_named_action":action["native_original_action"],
                "source_native_f32_integer_target":int(value),
                "resolved_original_source_destination_node":dest["record_source_name"],
                "destination_native_source_name_offset":dest["source_text_offset"],
                "native_typed_value_to_unique_name_id_record_proven":True,
                "runtime_action_operation_verified":False})
    expected={
       ("SpawnPoint012","Enable",1616,"SpawnPoint015"),
       ("SpawnPoint014","Disable",2489,"Deco_fence2"),
       ("SpawnPoint015","Disable",2509,"Deco_fence6")}
    observed={(e["source_node"],e["original_source_named_action"],
               e["source_native_f32_integer_target"],e["resolved_original_source_destination_node"])
              for e in edges}
    if observed!=expected:raise ValueError("original exact event graph changed")
    return {
      "source_owner_original_level1_sha256":hashlib.sha256(data).hexdigest(),
      "source_size":len(data),"native_name_id_records":len(records),
      "source_unique_IDs":len(byid),
      "source_named_type1_CLARA_id_registry":records,
      "source_real_CLARA_OnDestroy_action_named_event_edges":edges,
      "event_graph_edge_count":len(edges),
      "source_orphan_CALLBACK_SpawnPoint004_named_but_no_typed_action":True,
      "source_static_graph_recovered":True,
      "source_runtime_event_execution_verified":False,
      "original_player_start_location_proven":False,
      "no_gameplay_or_VPK_changes":True}

def main(ipa:Path,out:Path):
    with zipfile.ZipFile(ipa) as z:
        pack=z.read("Payload/IronMan2.app/clev")
        raw=get_exact(pack,decode(pack,".bclara"),"level1.bclara")
    report=link(raw)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    for e in report["source_real_CLARA_OnDestroy_action_named_event_edges"]:
        print("G21 VERIFIED ORIGINAL 2010 SOURCE EVENT EDGE",
              e["source_node"],e["original_source_named_action"],
              e["source_native_f32_integer_target"],e["resolved_original_source_destination_node"])
    print("PASS G21 three exact CLARA callback native action target name-ID crossreferences, no VPK.")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--ipa",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args();main(a.ipa,a.out)
