#!/usr/bin/env python3
"""G264 original 2010 MC 0x5c Position typed record *pre-TRS* source
metadata + native AttachType=1 register path. Research only; the 36
bytes before tagged XYZ are not presumed Bind_To_Entity without true
CLARA attribute names and layout. Neither authored local MC-Z nor raw
source fields are real Vita boot world/feet coordinates.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,struct,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from b24_owner_pack_extract import decode,get_exact
from b24_g24_original_clara_source_601_nodes_663_parent_links import audit

def run(ipa:Path,g260:Path,g263:Path,out:Path):
 prior=json.loads(g263.read_text());native=json.loads(g260.read_text())
 if prior["real_original_MC_Position_component_child_ID"]!=1064:
  raise ValueError("G264 original source MC Position child not authenticated")
 m=next(x for x in native["real_2010_PositionData_native_cpp_methods_ARM"]
   if x["original_native_CPP_method"]=="PositionData::RefreshPosition(int)")
 if m["real_original_VM"]!="0xc7f4c":raise ValueError("original 2010 RefreshPosition owner changed")
 ops=m["original_ARM_opcodes"]
 region=[x for x in ops if 0xc804c<=int(x["original_VM"],16)<=0xc80b4]
 if len(region)<17:raise ValueError("G264 original mode1 native register trace too short")
 by={x["original_VM"]:x for x in ops}
 for address,target in [("0xc8054","0xafd8c"),("0xc805c","0xafb54"),("0xc8084",None)]:
  item=by.get(address)
  if not item or "real_native_direct_call_VM" not in item or (target and item["real_native_direct_call_VM"]!=target):
   raise ValueError(f"G264 genuine original mode1 BL target absent: {address}")
 if ipa.stat().st_size!=248613763:raise ValueError("G264 original owner IPA source mismatch")
 with zipfile.ZipFile(ipa) as z:
  packed=z.read("Payload/IronMan2.app/clev")
  raw=get_exact(packed,decode(packed,".bclara"),"level1.bclara")
 if len(raw)!=339733:raise ValueError("G264 source C1L1 bytes drift")
 report=audit(raw)
 transforms=report["all_663_source_rigid_transforms_with_native_parent_child_name_ID_chain"]
 if len(transforms)!=663:raise ValueError("G264 original transform count mismatch")
 all_pre=collections.Counter()
 records=[]
 for row in transforms:
  p=row["native_transform_source_offset"]
  if struct.unpack_from("<H",raw,p-48)[0]!=92 or raw[p-46]!=1:
   raise ValueError("G264 original typed 92-byte Position source blob layout changed")
  if (struct.unpack_from("<I",raw,p-45)[0],struct.unpack_from("<I",raw,p-40)[0])!=(
    row["original_child_node_ID"],row["original_named_parent_source_ID"]):
   raise ValueError("G264 source child-parent header differs")
  pre=raw[p-36:p]
  if len(pre)!=36:raise ValueError("G264 original pre-TRS value bytes wrong")
  all_pre[pre.hex()]+=1
  if row["original_named_parent"] in {"MC","SpawnPoint000","SpawnPoint001","Sun001"}:
   records.append({"source_named_parent":row["original_named_parent"],
    "source_parent_ID":row["original_named_parent_source_ID"],
    "original_Position_child_ID":row["original_child_node_ID"],
    "original_Position_92_payload_offset":p-48,
    "original_position_tagged_vector_offset":p,
    "original_raw_36byte_pre_TRS_prefix_hex":pre.hex(),
    "candidate_le_u32_at_offsets_0_4_8_12_16_20_24_28_32":[
      struct.unpack_from("<I",pre,j)[0] for j in range(0,36,4)],
    "raw_prefix_cannot_be_labeled_Bind_or_Attach_without_CLARA_schema":True})
 mc=[x for x in records if x["source_named_parent"]=="MC"]
 if len(mc)!=1:raise ValueError("G264 unique MC prefix not found")
 summary={
  "source":"G264 original 2010 iOS level1 MC genuine 92byte typed Position component and full native mode1 RefreshPosition opcode path",
  "original_c1l1_sha256":hashlib.sha256(raw).hexdigest(),
  "total_original_2010_tag92_source_position_components":len(transforms),
  "distinct_original_36byte_prefix_patterns_count":len(all_pre),
  "most_common_raw_prefix_pattern_counts":[{"raw_original_36byte_prefix_hex":s,"original_source_count":n}
     for s,n in all_pre.most_common(6)],
  "original_typed_MC_and_reference_Preload_component_records":records,
  "true_original_2010_AttachType1_RefreshPosition_ARM_block_0xC804c_0xC80b4":region,
  "authentic_2010_AttachType_mode1_c8054_GetInstance_and_c805c_FindEntityById":True,
  "MC_raw_36byte_prefix_values_correctly_named_as_2010_Bind_To_Entity":False,
  "MC_raw_36byte_prefix_values_correctly_named_as_2010_AttachType":False,
  "source_real_MC_runtime_world_matrix_computed":False,
  "Vita_ground_collider_position_camera_lighting_or_armor_modified":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
 for entry in records:print("G264 2010 true typed Position pre-TRS",entry)
 print("G264 original 663 position components prefix pattern count",len(all_pre),"most common frequencies",all_pre.most_common(5))
 for entry in region:print("G264 genuine original ARM attach-type mode1",entry)
 print("G264 PASS source original 92byte MC child component structure and native attachment dynamic EntityMgr lookup; no guessed Bind/World Z, NO VPK")
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--ipa",required=True,type=Path)
 a.add_argument("--g260",required=True,type=Path)
 a.add_argument("--g263",required=True,type=Path)
 a.add_argument("--out",required=True,type=Path)
 x=a.parse_args();run(x.ipa,x.g260,x.g263,x.out)
