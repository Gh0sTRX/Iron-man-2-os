#!/usr/bin/env python3
"""G24 authentic 2010 C1L1 scene nodes and binary source child-parent linkage.

The owner original level1.bclara contains native ID+type1+u16 length names,
and typed transform subrecords with exactly:
  0x005C (uint16), 0x01, child-id uint32, 0x00, parent-id uint32, ...
  48 bytes afterwards: 0x000C vec3 xyz, 0x0010 quat xyzw, 0x000C scale.
Every one of 663 source transform triples MUST link to a named parent ID.
This proves original source child->named-parent record relationships but does
NOT prove an original graphics world scene parent matrix, real player start,
camera timeline or gameplay execution. No VPK.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,math,re,struct,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact

NAMES=re.compile(rb"[\x20-\x7E]{2,90}")
def native_names(raw):
    rows=[]
    for m in NAMES.finditer(raw):
        p=m.start()
        if p<7 or raw[p-3]!=1:continue
        if struct.unpack_from("<H",raw,p-2)[0]!=len(m.group()):continue
        nodeid=struct.unpack_from("<I",raw,p-7)[0]
        if 0<nodeid<50000:
            rows.append({"original_name":m.group().decode("ascii"),
                "original_name_offset":p,"original_numeric_name_id":nodeid})
    return rows

def audit(raw):
    names=native_names(raw)
    byid=collections.defaultdict(list)
    for row in names:byid[row["original_numeric_name_id"]].append(row)
    all_children=[]
    child_typed_92={}
    for pos in range(2,len(raw)-11):
        if raw[pos]!=1 or raw[pos+5]!=0:continue
        child=struct.unpack_from("<I",raw,pos+1)[0]
        parent=struct.unpack_from("<I",raw,pos+6)[0]
        if child<=parent or child>parent+20 or parent not in byid:continue
        tag=struct.unpack_from("<H",raw,pos-2)[0]
        if tag>2000:continue
        entry={"native_child_record_prefix_offset":pos-2,
               "original_child_id":child,
               "original_parent_id":parent,"source_typed_record_field":tag}
        all_children.append(entry)
        if tag==92:
            child_typed_92[pos-2]=entry
    matches=[]
    used=set()
    for p in range(len(raw)-46):
        if raw[p:p+2]!=b"\x0c\x00" or raw[p+14:p+16]!=b"\x10\x00" or raw[p+32:p+34]!=b"\x0c\x00":
            continue
        pos=struct.unpack_from("<3f",raw,p+2)
        quat=struct.unpack_from("<4f",raw,p+16)
        scale=struct.unpack_from("<3f",raw,p+34)
        if not all(math.isfinite(v) for v in pos+quat+scale):continue
        if abs(sum(v*v for v in quat)-1)>0.002:continue
        if any(not 0.001<abs(v)<300 for v in scale) or any(abs(v)>10000 for v in pos):
            continue
        source_child=child_typed_92.get(p-48)
        if source_child is None:
            raise ValueError("source tagged transform missing native 0x005C child->named-parent entry "+str(p))
        parentid=source_child["original_parent_id"]
        parents=byid[parentid]
        if len(parents)!=1:
            raise ValueError("source transform parent name ID not unique")
        parent=parents[0]
        matches.append({
            "native_transform_source_offset":p,
            "original_named_parent":parent["original_name"],
            "original_named_parent_source_ID":parentid,
            "original_child_node_ID":source_child["original_child_id"],
            "original_parent_name_source_offset":parent["original_name_offset"],
            "native_vec3_position":[round(v,6) for v in pos],
            "native_quaternion_xyzw":[round(v,6) for v in quat],
            "native_vec3_scale":[round(v,6) for v in scale],
            "native_typed_transform_tag_sizes":[12,16,12],
            "native_child_parent_binary_record_proven":True})
        used.add(parentid)
    source_group_counts=collections.Counter()
    for r in names:
        nm=r["original_name"]
        if re.fullmatch(r"SpawnPoint\d{3}",nm):g="spawnpoint"
        elif nm.startswith(("Camera","CC_","CP_")):g="camera"
        elif nm.startswith(("PD_","Mission","Trigger","MCondition","MissionGoto")):g="mission_trigger"
        elif nm.startswith(("Deco_","Bomb_","InteractiveObj","Collidable")):g="actor_decor"
        elif nm.startswith(("GE_","GEM_","Billboard_","Global_","Attack_","Trails_")):g="fx_config"
        else:g="other"
        source_group_counts[g]+=1
    expected_spawns={f"SpawnPoint{i:03d}" for i in range(16)}
    observed_spawns={r["original_named_parent"] for r in matches if r["original_named_parent"] in expected_spawns}
    assert expected_spawns==observed_spawns
    assert len(names)==601 and len(matches)==663 and len(all_children)==1604
    assert len(used)==389 and len(child_typed_92)==684
    return {
        "original_game":"Gameloft Iron Man 2 2010 owner iOS level1.bclara",
        "authored_source_level1_bytes":len(raw),
        "authored_source_level1_sha256":hashlib.sha256(raw).hexdigest(),
        "source_native_2plus_character_name_id_records":len(names),
        "native_name_record_family_counts":dict(source_group_counts),
        "source_native_typed_child_parent_record_count":len(all_children),
        "source_native_0x005C_transform_child_parent_prefix_count":len(child_typed_92),
        "native_source_verified_12_16_12_transform_parent_links":len(matches),
        "named_parents_with_valid_transforms":len(used),
        "original_source_static_parent_record_links":all_children,
        "all_663_source_rigid_transforms_with_native_parent_child_name_ID_chain":matches,
        "original_2010_live_render_world_parent_matrices_verified":False,
        "original_player_start_or_mission_trigger_execution_verified":False,
        "original_camera_path_timeline_reconstructed":False,
        "original_2010_BRES_3D_model_attachment_per_node_proven":False,
        "VPK_built":False,
    }

def main(ipa,out):
    with zipfile.ZipFile(ipa) as z:
        packed=z.read("Payload/IronMan2.app/clev")
        raw=get_exact(packed,decode(packed,".bclara"),"level1.bclara")
    r=audit(raw)
    assert r["authored_source_level1_bytes"]==339733
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    print("G24 real C1L1 named scene ID records",r["source_native_2plus_character_name_id_records"])
    print("G24 source tagged child-parent record count",r["source_native_typed_child_parent_record_count"])
    print("G24 original 0x005C transform child records",r["source_native_0x005C_transform_child_parent_prefix_count"])
    print("G24 ALL SOURCE native xyz+quat+scale parent/child links:",r["native_source_verified_12_16_12_transform_parent_links"])
    print("G24 root names owning those transforms:",r["named_parents_with_valid_transforms"])
    print("G24 original source families:",r["native_name_record_family_counts"])
    print("PASS original raw CLARA source deterministic 663/663 transform->child->parent source ID links, NOT real runtime scene graph or VPK.")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--ipa",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    main(args.ipa,args.out)
