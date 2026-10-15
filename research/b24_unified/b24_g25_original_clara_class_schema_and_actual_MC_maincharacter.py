#!/usr/bin/env python3
"""G25 source-authored 2010 CLARA class schema and named entity type mapping.

A class prototype in source level1.bclara is an exact
  uint32 native_class_id, uint16 ascii_name_length, ASCII class_name.
An actual named entity has
  uint32 original_node_ID, byte1, uint16 name_len, name,
  0x80FFFFFFFF, uint32 source_native_class_id.
Cross-matching them proves which of the 601 named entries are real
classed objects, without guessing a class from a name prefix.

MC is a real class-112 MainCharacter instance with native transform
childID1064 xyz(-1.319,-6.747,25.054); original runtime START point
still unproven.
"""
from __future__ import annotations
import argparse,collections,json,re,struct,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact
from b24_g24_original_clara_source_601_nodes_663_parent_links import native_names,audit

PATTERN=re.compile(rb"[\x20-\x7E]{2,90}")
def source_schema(raw):
    schema={}
    for hit in PATTERN.finditer(raw[:38719]):
        loc=hit.start()
        if loc<6 or struct.unpack_from("<H",raw,loc-2)[0]!=len(hit.group()):continue
        class_id=struct.unpack_from("<I",raw,loc-6)[0]
        if not 0<class_id<=400:continue
        if class_id in schema:raise ValueError("2010 duplicated class ordinal "+str(class_id))
        schema[class_id]={"original_class_id":class_id,
          "original_class_name":hit.group().decode("ascii"),
          "original_class_name_file_offset":loc}
    if len(schema)!=193:raise ValueError("owner original class template changed")
    return schema

def summarize(raw):
    schema=source_schema(raw)
    records=native_names(raw)
    typed=[]
    for r in records:
        p=r["original_name_offset"]+len(r["original_name"])
        if raw[p:p+5]!=b"\x80\xFF\xFF\xFF\xFF":continue
        class_id=struct.unpack_from("<I",raw,p+5)[0]
        if class_id not in schema:raise ValueError("instance references nonexistent class")
        typed.append({**r,"original_class_id":class_id,
          "original_class_name":schema[class_id]["original_class_name"],
          "class_pointer_after_native_name_source_verified":True})
    by_name={r["original_name"]:r for r in typed}
    mc=by_name.get("MC")
    if mc is None or mc["original_class_id"]!=112 or mc["original_class_name"]!="MainCharacter":
        raise ValueError("original MC is not native main character")
    graph=audit(raw)
    mc_links=[r for r in graph["all_663_source_rigid_transforms_with_native_parent_child_name_ID_chain"]
         if r["original_named_parent"]=="MC"]
    if len(mc_links)!=1 or mc_links[0]["original_child_node_ID"]!=1064:
        raise ValueError("MC actual typed transform not found")
    scene_xyz=mc_links[0]["native_vec3_position"]
    if max(abs(scene_xyz[i]-[-1.319,-6.747,25.054][i]) for i in range(3))>0.002:
        raise ValueError("2010 native MC source XYZ mismatch")
    freq=collections.Counter(r["original_class_name"] for r in typed)
    if len(records)!=601 or len(typed)!=587 or freq["PositionDummy"]!=137 or freq["CameraPreset"]!=57:
        raise ValueError("original owner typed scene objects drift")
    return {
      "source_2010_original_level1_bytes":len(raw),
      "source_class_definitions":len(schema),
      "source_native_type1_named_nodes_or_fields":len(records),
      "source_real_named_instances_with_proven_class_ID":len(typed),
      "source_unclassified_short_fields_or_untyped_name_candidates":len(records)-len(typed),
      "source_2010_class_schema":[schema[i] for i in sorted(schema)],
      "source_2010_typed_class_instances":typed,
      "source_class_distribution":dict(freq),
      "source_exact_MC_real_MainCharacter_instance":mc,
      "source_exact_MC_native_parent_child_transform":mc_links[0],
      "source_2010_MC_instance_class112_MainCharacter_PROVEN":True,
      "source_original_MC_is_playable_character_association_probable_but_gameplay_NOT_tested":True,
      "source_player_first_runtime_spawn_trigger_PROVEN":False,
      "original_source_class_methods_or_cutscene_camera_engine_recreated":False,
      "NO_VPK":True,
    }

def main(ipa,out):
    with zipfile.ZipFile(ipa) as z:
        packed=z.read("Payload/IronMan2.app/clev")
        raw=get_exact(packed,decode(packed,".bclara"),"level1.bclara")
    j=summarize(raw)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
    print("G25 source 2010 class schema",j["source_class_definitions"],
       "typed original entity instances",j["source_real_named_instances_with_proven_class_ID"])
    print("G25 original class counts",sorted(j["source_class_distribution"].items(),
          key=lambda p:-p[1])[:20])
    print("G25 source exact MC class",j["source_exact_MC_real_MainCharacter_instance"])
    print("G25 original MC source transform",j["source_exact_MC_native_parent_child_transform"])
    print("PASS authentic owner original 2010 193 native class prototypes 587 exact native typed entities and MainCharacter MC source anchor; no Vita VPK or playable spawn proven.")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--ipa",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path);a=p.parse_args()
    main(a.ipa,a.out)
