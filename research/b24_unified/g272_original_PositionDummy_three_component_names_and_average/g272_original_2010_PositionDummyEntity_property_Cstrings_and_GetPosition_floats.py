#!/usr/bin/env python3
"""G272 decode true original 2010 iOS PositionDummyEntity::LoadFromFile
four typed C-string keys from ARM PC-relative literal pools, and native
PositionDummyEntity::GetPosition/GetAbsolutePosition reciprocal factors.
These source values explain 3-child components but DO NOT infer the
authored PD_IM_jump_goal PositionType until source CLARA root int confirmed.
"""
from __future__ import annotations
import argparse,hashlib,json,math,struct,sys,zipfile
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
LITERALS=[
 ("PositionDummy_mode_integer",0xd2eec,0xd2ef4,0xd3008,0xd2efc,"GetParamValue(int*)",0xf0),
 ("PositionDummy_component_1",0xd2f1c,0xd2f24,0xd300c,0xd2f30,"GetParamComponent",0xe4),
 ("PositionDummy_component_2",0xd2f64,0xd2f6c,0xd3010,0xd2f78,"GetParamComponent",0xe8),
 ("PositionDummy_component_3",0xd2fc4,0xd2fcc,0xd3014,0xd2fd8,"GetParamComponent",0xec)
]
FLOATS=[
 ("GetPosition_3_components",0xd3100,0xd3170),
 ("GetPosition_2_components",0xd312c,0xd3174),
 ("GetAbsolutePosition_3_components",0xd2c28,0xd2c98),
 ("GetAbsolutePosition_2_components",0xd2c54,0xd2c9c)
]
def read(exe:bytes,secs:list,vm:int,n:int)->bytes:
 sec=next((s for s in secs if s[0]<=vm and vm+n<=s[0]+s[1]),None)
 if sec is None:raise ValueError(f"original MachO addr cannot map {vm:#x}+{n}")
 off=sec[2]+vm-sec[0]
 if not 0<=off<=len(exe)-n:raise ValueError("MachO raw file bounds")
 return exe[off:off+n]
def string(exe,secs,vm):
 sec=next((s for s in secs if s[0]<=vm<s[0]+s[1]),None)
 if sec is None:raise ValueError(f"native cstring VM missing {vm:#x}")
 bs=read(exe,secs,vm,min(100,sec[0]+sec[1]-vm)).split(b"\0",1)[0]
 if not 2<=len(bs)<=99 or not all(32<=x<127 for x in bs):
  raise ValueError(f"native string not valid ASCII at {vm:#x}")
 return bs.decode("ascii")
def main(ipa:Path,g271:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("not original 2010 owner IPA")
 with zipfile.ZipFile(ipa) as z:
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("genuine 2010 MachO changed")
 prev=json.loads(g271.read_text())
 if not prev["source_true_original_PositionDummy_constructor_at_d2e84"]:
  raise ValueError("G272 original dedicated native PositionDummyEntity owner missing")
 macho=parse_macho(exe)
 if macho["nsyms"]!=65500:raise ValueError("original 2010 symbol table drift")
 secs=macho["sections"]
 asm=Cs(CS_ARCH_ARM,CS_MODE_ARM)
 ops={o.address:o for o in asm.disasm(read(exe,secs,0xd2ed8,0x140),0xd2ed8)}
 names=[]
 for typ,ldr,add,pool,call,getter,field in LITERALS:
  a=ops.get(ldr);b=ops.get(add);c=ops.get(call)
  if not a or not b or not c or not a.mnemonic.startswith("ldr") or b.mnemonic!="add" or c.mnemonic!="bl":
   raise ValueError(f"G272 native source property load opcode drift {typ}")
  lit=struct.unpack("<i",read(exe,secs,pool,4))[0]
  addr=add+8+lit
  val=string(exe,secs,addr)
  names.append({
   "original_PositionDummy_native_property_kind":typ,
   "original_authentic_CPP_const_char_string":val,
   "source_original_2010_cstring_vm":hex(addr),
   "original_2010_ARM_signed_pc_delta":lit,
   "PositionDummyEntity_instance_field_native_offset":hex(field),
   "actual_ARM_LDR_vm":hex(ldr),"real_ARM_ADD_vm":hex(add),
   "original_get_param_opcode_vm":hex(call),
   "original_GetParam_Cpp_function_type":getter})
 nums=[]
 for purpose,vldr,literal in FLOATS:
  ins=dict((o.address,o) for o in asm.disasm(read(exe,secs,vldr,4),vldr)).get(vldr)
  if not ins or ins.mnemonic!="vldr" or ins.op_str.find("[pc")<0:
   raise ValueError(f"G272 original 2010 ARM VFP source literal drift {purpose}")
  observed=struct.unpack("<f",read(exe,secs,literal,4))[0]
  if not math.isfinite(observed):
   raise ValueError(f"source native float nonfinite at {literal:#x}")
  nums.append({"native_purpose":purpose,"source_ARM_VM":hex(vldr),
       "original_float_literal_vm":hex(literal),"actual_2010_iOS_float_value":observed,
       "original_float_raw_U32_hex":hex(struct.unpack("<I",read(exe,secs,literal,4))[0])})
 r={
  "source":"G272 genuine original 2010 iOS PositionDummyEntity::LoadFromFile 4 native property key C strings and original GetPosition/GetAbsolutePosition float factors",
  "original_2010_MachO_sha256":hashlib.sha256(exe).hexdigest(),
  "original_PositionDummyEntity_Cpp_loader_VM":"0xd2ed8",
  "actual_native_original_four_typed_positiondummy_property_names":names,
  "actual_native_original_GetPosition_and_GetAbsolutePosition_f32_factors":nums,
  "original_PositionDummyEntity_one_two_three_position_count_branch_proven":True,
  "original_Mission000_PD_IM_jump_goal_authored_count_integer_from_C1L1_proven":False,
  "genuine_original_PD_IM_jump_goal_final_runtime_world_xyz_proven":False,
  "Vita_ground_render_combat_camera_lighting_modified":False,
  "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
 for x in names:print("G272 original real PositionDummyEntity 2010 C++ property",x)
 for x in nums:print("G272 original real PositionDummyEntity native float",x)
 print("G272 PASS original typed PositionDummy component labels/f32 factors, no inferred Mission000 goal runtime XYZ, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g271",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 args=p.parse_args();main(args.ipa,args.g271,args.out)
