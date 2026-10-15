#!/usr/bin/env python3
"""G28: source-authentic original 2010 CLARA nested CameraPreset records.

All 57 CameraPreset typed instances have the SAME verified native nested
child-parent relationships (tags 0x018D, 0x002C, 0x0134), 18 consecutive
tagged float3 triples. Source original 18 triples are ALL 0, so must NOT
interpret them as actual camera world positions. The true camera position
may be relative/dynamic or defined by other linked fields; it is unknown.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,math,struct,zipfile
from pathlib import Path
from b24_owner_pack_extract import decode,get_exact
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize

RECORDS=((15,0x018D,1,0),(37,0x002C,2,1),(95,0x0134,3,1))
def report(raw):
    classed=summarize(raw)
    cameras=[r for r in classed["source_2010_typed_class_instances"]
           if r["original_class_name"]=="CameraPreset"]
    if len(cameras)!=57:raise ValueError("native original CameraPreset count drift")
    out=[]
    for cam in cameras:
        idnum=cam["original_numeric_name_id"]
        p=cam["original_name_offset"]+len(cam["original_name"])
        actual=[]
        for loc,kind,addchild,addparent in RECORDS:
            native=struct.unpack_from("<H",raw,p+loc)[0]
            label=raw[p+loc+2]
            child=struct.unpack_from("<I",raw,p+loc+3)[0]
            parent=struct.unpack_from("<I",raw,p+loc+8)[0]
            if (native,label,child,parent)!=(kind,1,idnum+addchild,idnum+addparent):
                raise ValueError("2010 native camera child hierarchy mismatch "+cam["original_name"])
            actual.append({"original_native_tag":kind,
              "genuine_source_local_offset_after_name":loc,
              "source_child_id":child,"source_parent_id":parent,
              "source_typed_child_parent_link_verified":True})
        if raw[p+115:p+117]!=b"\x18\x00":
            raise ValueError("original camera 0x18 config parent field missing")
        vectors=[]
        for index in range(18):
            offset=p+117+14*index
            if raw[offset:offset+2]!=b"\x0c\x00":
                raise ValueError("original camera source vec3 tag mismatch")
            xyz=struct.unpack_from("<fff",raw,offset+2)
            if not all(math.isfinite(x) for x in xyz):
                raise ValueError("original camera source numeric nonfinite")
            vectors.append({"tagged_vector_index":index,
                "original_float3":[round(x,7) for x in xyz],
                "source_file_offset":offset,
                "camera_world_space_value_semantics_not_proven":True})
        out.append({"original_CameraPreset_name":cam["original_name"],
             "source_native_entity_id":idnum,"native_source_offset":cam["original_name_offset"],
             "three_source_nested_type_ID_links":actual,
             "eighteen_authentic_12byte_source_vector_records":vectors})
    if sum(any(any(abs(v)>1e-8 for v in r["original_float3"])
        for r in cam["eighteen_authentic_12byte_source_vector_records"]) for cam in out)!=0:
        raise ValueError("original camera default zero 18x vec3 source records unexpectedly changed")
    names={r["original_CameraPreset_name"]:r for r in out}
    for n,idnum in (("Camera_start_show",1864),("Camera_start_show2",1868)):
        if names[n]["source_native_entity_id"]!=idnum:
            raise ValueError("original scripted intro camera source ID mismatch")
    return {"source_original_2010_first_level_sha256":hashlib.sha256(raw).hexdigest(),
      "source_original_named_CameraPreset_instances":57,
      "source_nested_CameraPreset_3_child_parent_links_proven":171,
      "source_camera_native_0x000C_vec3_records_proven":1026,
      "source_camera_native_nonzero_candidate_vec3_count":0,
      "source_original_main_Mission000_SetCamera_IDs_1864_1868_present":True,
      "source_57_CameraPreset_class_specific_records":out,
      "source_actual_camera_world_positions_and_look_at_matrices_PROVEN":False,
      "source_actual_camera_runtime_lerp_and_cutscene_camera_path_PROVEN":False,
      "SOURCE_ONLY_NOT_ORIGINAL_GAME_SCREENSHOT":True,
      "NO_VPK":True}
def main(ipa,out):
    with zipfile.ZipFile(ipa) as z:
        pack=z.read("Payload/IronMan2.app/clev")
        raw=get_exact(pack,decode(pack,".bclara"),"level1.bclara")
    j=report(raw)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n")
    print("G28 authentic owner original CameraPreset 57 nodes, 171 source child→parent links, 1026 exact 12byte vec3 records (all source zero); NOT camera world pose")
    print("G28 intro two source classed camera IDs 1864 and 1868, real script reference but no in-game output")
    print("PASS G28 original first level 2010 camera data structural proof, no VPK.")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--ipa",required=True,type=Path);p.add_argument("--out",required=True,type=Path)
    a=p.parse_args();main(a.ipa,a.out)
