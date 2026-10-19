#!/usr/bin/env python3
"""G263 authentic original iOS 2010: real MC Position child #1064,
source typed attachment vs actual ARM PositionData::RefreshPosition paths.
Uses original user-owned level1.bclara and G260/G261 native ARM evidence.
Does not guess AttachType/Bind_To_Entity raw MC values where the source
TLV class+component schema is still unresolved. No Vita physics/teleport.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,struct,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from b24_owner_pack_extract import decode,get_exact
from b24_g24_original_clara_source_601_nodes_663_parent_links import audit
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize

def fetch(m,name):
 rows=[x for x in m["real_2010_PositionData_native_cpp_methods_ARM"] if
  x["original_native_CPP_method"]==name]
 if len(rows)!=1:raise ValueError("G263 missing authentic original C++ method "+name)
 return rows[0]

def check(m,addr,op,args):
 row=next((x for x in m["original_ARM_opcodes"] if x["original_VM"]==addr),None)
 if row is None or (row["opcode"],row["args"])!=(op,args):
  raise ValueError(f"G263 source native ARM path mismatch {m['original_native_CPP_method']} {addr} {row}")
 return row

def main(g260:Path,g261:Path,ipa:Path,out:Path):
 a=json.loads(g260.read_text());b=json.loads(g261.read_text())
 if a["authentic_original_Entity3D_GetParamComponent_2010_key"]!="Position":raise ValueError("G263 native component owner changed")
 props={x["source_2010_typed_param_name"]:x for x in b["true_original_native_six_2010_typed_Transform_parameters"]}
 for k,off in {"Position":"0x4","Rotation":"0x10","Scale":"0x20","AttachType":"0x38","Bind_To_Entity":"0x2c","AttachOffset":"0x3c"}.items():
  if props[k]["native_2010_field_offset_in_PositionData"]!=off:
   raise ValueError(f"original owner native PosData field changed {k}")
 refresh=fetch(a,"PositionData::RefreshPosition(int)")
 init=fetch(a,"PositionData::Init()")
 check(refresh,"0xc7f5c","ldr","r5, [r0, #0x38]")
 check(refresh,"0xc7f64","cmp","r5, #1")
 check(refresh,"0xc7f78","beq","#0xc8054")
 check(refresh,"0xc7f80","ldr","ip, [r4, #0x48]")
 check(init,"0xc7f18","ldr","r3, [r0, #0x2c]")
 check(init,"0xc7f38","bl","#0xafb54")
 if ipa.stat().st_size!=248613763:raise ValueError("G263 only actual owner 2010 IPA")
 with zipfile.ZipFile(ipa) as z:
  clev=z.read("Payload/IronMan2.app/clev")
  raw=get_exact(clev,decode(clev,".bclara"),"level1.bclara")
 if len(raw)!=339733:raise ValueError("source actual original level1 file changed")
 typed=summarize(raw)
 graph=audit(raw)
 mc=typed["source_exact_MC_real_MainCharacter_instance"]
 child=typed["source_exact_MC_native_parent_child_transform"]
 if mc["original_class_id"]!=112 or mc["original_numeric_name_id"]!=1062 or child["original_child_node_ID"]!=1064:
  raise ValueError("original main character typed class or authentic position record differs")
 p=child["native_transform_source_offset"]
 if raw[p:p+2]!=b"\x0c\x00" or raw[p+14:p+16]!=b"\x10\x00" or raw[p+32:p+34]!=b"\x0c\x00":
  raise ValueError("actual original MC Position/Rotation/Scale typed record tags drift")
 src_xyz=[round(x,6) for x in struct.unpack_from("<3f",raw,p+2)]
 src_rot=[round(x,6) for x in struct.unpack_from("<4f",raw,p+16)]
 src_scale=[round(x,6) for x in struct.unpack_from("<3f",raw,p+34)]
 if src_xyz!=child["native_vec3_position"] or src_rot!=child["native_quaternion_xyzw"] or src_scale!=child["native_vec3_scale"]:
  raise ValueError("original 2010 independently parsed MC tagged XYZ/quat/scale mismatch")
 if struct.unpack_from("<H",raw,p-48)[0]!=92 or raw[p-46]!=1:
  raise ValueError("original native MC attached Position component header drift")
 embedded_child=struct.unpack_from("<I",raw,p-45)[0]
 embedded_parent=struct.unpack_from("<I",raw,p-40)[0]
 if (embedded_child,embedded_parent)!=(1064,1062):
  raise ValueError("original 2010 Position child-parent source header mismatched")
 branches=[]
 for x in refresh["original_ARM_opcodes"]:
  if x["opcode"].startswith("b") and x["opcode"] not in ("bl","blx","bic"):
   branches.append({"2010_native_vm":x["original_VM"],"opcode":x["opcode"],"branch_target":x["args"],
                    "conditional_jump_is_not_function_call":True})
 calls=[{"callsite":x["original_VM"],"2010_cpp_targets":x.get("original_CPP_callee",[])}
        for x in refresh["original_ARM_opcodes"] if "real_native_direct_call_VM" in x]
 result={
  "source":"G263 original owner 2010 C1L1 actual typed MC class112 child position node1064 and true PositionData RefreshPosition ARM mode-1 branch",
  "original_2010_level1_sha256":hashlib.sha256(raw).hexdigest(),
  "genuine_original_MC_name":"MC",
  "genuine_original_MC_class112_ID":mc["original_numeric_name_id"],
  "real_original_MC_Position_component_child_ID":embedded_child,
  "real_original_MC_Position_parent_scene_node_ID":embedded_parent,
  "source_real_MC_child_position_xyz":src_xyz,
  "source_real_MC_child_rotation_xyzw":src_rot,
  "source_real_MC_child_scale_xyz":src_scale,
  "source_position_child_tagged_record_offset":p,
  "original_C1L1_field_92_child_parent_tag_structure_proven":True,
  "source_native_AttachType_one_branch_VM":"0xc7f78",
  "source_native_AttachType_one_branch_target_VM":"0xc8054",
  "original_iOS_RefreshPosition_native_conditional_and_unconditional_branches":branches,
  "original_iOS_RefreshPosition_native_direct_CPP_calls":calls,
  "original_MC_Position_component_AttachType_value_from_scene_proven":False,
  "original_MC_Position_component_Bind_To_Entity_value_from_scene_proven":False,
  "original_MC_actual_runtime_position_world_matrix_proven":False,
  "actual_Vita_ground_walk_on_hardware_fixed":False,
  "vita_B14_G75_movement_lighting_and_anim_modified":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
 print("G263 original source MC class/Position child",embedded_parent,embedded_child,src_xyz,src_rot,src_scale)
 print("G263 RefreshPosition native source mode1 branch 0xc7f78 -> 0xc8054, total branches",len(branches),"direct C++ calls",len(calls))
 for x in branches:print("G263 native ARM genuine branch",x)
 for x in calls:print("G263 native ARM genuine CPP call",x)
 print("G263 PASS original MC child Position and native attachment mode dispatch verified; player runtime WORLD Z still UNKNOWN, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--g260",required=True,type=Path)
 p.add_argument("--g261",required=True,type=Path)
 p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 x=p.parse_args();main(x.g260,x.g261,x.ipa,x.out)
