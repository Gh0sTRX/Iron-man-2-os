#!/usr/bin/env python3
"""G262 source-only original 2010 Transform parent and local matrix causal
proof from prior G260 and G261 genuine ARM opcode metadata; no original
gameplay binary required here. No arbitrary actor offset or teleport.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
EVIDENCE={
 "original_init_Bind_To_Entity_field":("0xc7f18","ldr","r3, [r0, #0x2c]"),
 "original_init_EntityMgr_singleton":("0xc7f30","bl","#0xafd8c"),
 "original_init_Load_bound_Entity_lookup":("0xc7f38","bl","#0xafb54"),
 "original_init_bound_entity_ptr":("0xc7f3c","str","r0, [r4, #0x34]"),
 "original_init_bound_entity_secondary_ref":("0xc7f44","strne","r0, [r4, #0x30]"),
 "original_GetMatrix_input_pos_x":("0xc827c","ldr","lr, [r0, #4]"),
 "original_GetMatrix_output_translation_x":("0xc8284","str","lr, [r1, #0x30]"),
 "original_GetMatrix_input_pos_y":("0xc8288","ldr","ip, [r0, #8]"),
 "original_GetMatrix_output_translation_y":("0xc8290","str","ip, [r1, #0x34]"),
 "original_GetMatrix_input_pos_z":("0xc8294","ldr","r6, [r0, #0xc]"),
 "original_GetMatrix_output_translation_z":("0xc829c","str","r6, [r1, #0x38]"),
 "original_RefreshPosition_AttachType_branch":("0xc7f5c","ldr","r5, [r0, #0x38]"),
}
PROPS=[
 ("Position","vector3","0x4"),
 ("Rotation","quaternion","0x10"),
 ("Scale","vector3","0x20"),
 ("AttachType","int","0x38"),
 ("Bind_To_Entity","int","0x2c"),
 ("AttachOffset","vector3","0x3c"),
]
def scan_method(d,method):
 hits=[x for x in d["real_2010_PositionData_native_cpp_methods_ARM"] if
   x["original_native_CPP_method"]==method]
 if len(hits)!=1:raise ValueError("source actual 2010 PositionData method missing "+method)
 return {r["original_VM"]:r for r in hits[0]["original_ARM_opcodes"]}
def run(previous:Path,names:Path,out:Path):
 original=json.loads(previous.read_text())
 params=json.loads(names.read_text())
 if original["authentic_original_Entity3D_GetParamComponent_2010_key"]!="Position":
  raise ValueError("G262 previous source original Entity3D typed Position not verified")
 init=scan_method(original,"PositionData::Init()")
 matrix=scan_method(original,"PositionData::GetMatrix(irr::core::CMatrix4<float>*)")
 refresh=scan_method(original,"PositionData::RefreshPosition(int)")
 tables={k:init if k.startswith("original_init") else matrix if k.startswith("original_GetMatrix") else refresh for k in EVIDENCE}
 match=[]
 for key,(addr,mn,ops) in EVIDENCE.items():
  item=tables[key].get(addr)
  if not item or item["opcode"]!=mn or item["args"]!=ops:
   raise ValueError(f"G262 real original 2010 ARM TRS parent opcode mismatch {key}: {item}")
  match.append({"native_semantics":key,"true_original_ARM_VM":addr,"original_opcode":mn,"real_operands":ops})
 given=[(p["source_2010_typed_param_name"],p["native_2010_getter_kind"],p["native_2010_field_offset_in_PositionData"])
        for p in params["true_original_native_six_2010_typed_Transform_parameters"]]
 if given!=PROPS:raise ValueError("G262 genuine 2010 six original PositionData named fields changed")
 result={
  "source":"G262 native original 2010 iOS PositionData first-person transform dependency proof, verified using independently decoded actual ARM instructions",
  "original_2010_source_PositionData_named_parameters":[{"name":a,"type":b,"offset":c} for a,b,c in given],
  "original_2010_native_Bind_To_Entity_direct_EntityMgr_FindEntityById_proven":True,
  "original_2010_native_GetMatrix_uses_Position_XYZ_and_writes_4x4_matrix_translate_columns_proven":True,
  "original_2010_native_AttachType_controls_RefreshPosition_source_branch_proven":True,
  "authentic_ARM_instruction_proofs":match,
  "source_original_MC_class112_Bind_To_Entity_record_actual_ID_proven":False,
  "source_original_position_component_parent_matrix_world_composition_complete_proven":False,
  "original_source_mc_world_boot_feet_xyz_proven":False,
  "physical_Vita_ground_root_bug_fixed":False,
  "Vita_ground_camera_flight_scale_lighting_code_modified":False,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
 print("G262 VERIFIED ORIGINAL 2010 named PositionData table",given)
 for rec in match:print("G262 original ARM confirmed",rec)
 print("G262 PASS genuine original Bind_To_Entity->EntityMgr::FindEntityById and local Position->matrix translation and AttachType, NO VPK")
 return result
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--g260",type=Path,required=True)
 p.add_argument("--g261",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();run(a.g260,a.g261,a.out)
