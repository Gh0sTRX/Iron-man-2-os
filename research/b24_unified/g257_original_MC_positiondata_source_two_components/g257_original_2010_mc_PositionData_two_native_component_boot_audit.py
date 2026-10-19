#!/usr/bin/env python3
"""G257 source-original player transform seed:
2010 Entity3D::LoadFromFile(EntityData*) calls constructor
PositionData and TWO typed GetParamComponent loads. Verify direct
ARM source and inventory original C1L1 native authored MC transforms.
A classed MainCharacter node's authored transform is NOT automatically
the real first playable boot/feet world root or Z. Source only, NO VPK.
"""
from __future__ import annotations
import argparse,bisect,hashlib,json,struct,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM,ARM_INS_BL,ARM_INS_BLX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
from b24_owner_pack_extract import decode,get_exact
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
from b24_g24_original_clara_source_601_nodes_663_parent_links import audit
VM=0x12c78
SOURCE_CALLS={
 0x12c88:(0xaeb00,"Entity::LoadFromFile(EntityData*)"),
 0x12c98:(0xc8200,"PositionData::PositionData()"),
 0x12cb0:(0xd7bb4,"EntityData::GetParamComponent(char const*, Component*)"),
 0x12cd8:(0xd7bb4,"EntityData::GetParamComponent(char const*, Component*)")
}
def main(ipa:Path,g254:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("not original owner 2010 IPA")
 with zipfile.ZipFile(ipa) as z:
  exe=z.read("Payload/IronMan2.app/IronMan2")
  packed=z.read("Payload/IronMan2.app/clev")
 if len(exe)!=7480208:raise ValueError("original executable wrong size")
 scene=get_exact(packed,decode(packed,".bclara"),"level1.bclara")
 if len(scene)!=339733:raise ValueError("genuine C1L1 scene size drift")
 prev=json.loads(g254.read_text())
 funcs=prev["true_original_native_constructor_MainCharacter_LoadFromFile_and_Init_methods"]
 if funcs["0x12c78"]["original_cpp"]!="Entity3D::LoadFromFile(EntityData*)":
  raise ValueError("G257 preceding authentic Entity3D code not proven")
 native=parse_macho(exe)
 if native["nsyms"]!=65500:raise ValueError("original 2010 symbols count drift")
 entries=native["entries"]
 dem=subprocess.run(["c++filt"],input="\n".join(row[0] for row in entries)+"\n",
  capture_output=True,text=True,check=True).stdout.splitlines()
 if len(entries)!=len(dem):raise ValueError("native name table drift")
 names={}
 for e,name in zip(entries,dem):names.setdefault(e[1]&~1,set()).add(name)
 if "Entity3D::LoadFromFile(EntityData*)" not in names.get(VM,()):
  raise ValueError("native Entity3D C++ owner drift")
 sec=next(s for s in native["sections"] if s[3]=="__text" and s[0]<=VM<s[0]+s[1])
 stops=sorted(a for a in names if VM<a<sec[0]+sec[1])
 end=stops[0] if stops else sec[0]+sec[1]
 if not 96<=end-VM<=512:raise ValueError("unexpected original Entity3D method size")
 offset=sec[2]+VM-sec[0]
 dis=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);dis.detail=True
 ops=list(dis.disasm(exe[offset:offset+end-VM],VM))
 actual={}
 rows=[]
 for o in ops:
  row={"VM":hex(o.address),"native_instruction":o.mnemonic,"source_operands":o.op_str}
  if o.id in (ARM_INS_BL,ARM_INS_BLX) and o.operands and o.operands[0].type==ARM_OP_IMM:
   addr=o.operands[0].imm&~1
   row["actual_native_direct_cpp_BL_VM"]=hex(addr)
   row["target_native_Cpp"]=sorted(names.get(addr,()))[:5]
   actual[o.address]=addr
  rows.append(row)
 for site,(target,cpp) in SOURCE_CALLS.items():
  if actual.get(site)!=target or cpp not in names.get(target,()):
   raise ValueError(f"G257 genuine original Entity3D load code/source owner changed {site:#x}")
 typed=summarize(scene)
 shape=audit(scene)
 characters=[x for x in typed["source_2010_typed_class_instances"] if x["original_class_name"]=="MainCharacter"]
 if len(characters)!=1:raise ValueError("original first-level MC class source not unique")
 mc=characters[0]
 related=[x for x in shape["all_663_source_rigid_transforms_with_native_parent_child_name_ID_chain"]
   if x["original_named_parent_source_ID"]==mc["original_numeric_name_id"]]
 if len(related)!=1:raise ValueError("real original MC transform unique child relation absent")
 transform=related[0]
 report={
  "source":"G257 true original 2010 iOS C++ ARM Entity3D LoadFromFile and typed C1L1 MainCharacter rigid source transform",
  "original_MachO_SHA256":hashlib.sha256(exe).hexdigest(),
  "original_level1_SHA256":hashlib.sha256(scene).hexdigest(),
  "original_source_real_native_cpp":"Entity3D::LoadFromFile(EntityData*)",
  "original_native_method_VM":hex(VM),
  "original_native_method_bytes":end-VM,
  "real_2010_native_ARM_instructions":rows,
  "true_source_PositionData_ctor_direct_call_VM":"0x12c98",
  "true_source_EntityData_GetParamComponent_direct_calls":[hex(x) for x in (0x12cb0,0x12cd8)],
  "original_source_typed_MC_class":"MainCharacter",
  "original_source_typed_MC_class_id":mc["original_class_id"],
  "original_source_typed_MC_named_node_id":mc["original_numeric_name_id"],
  "original_2010_MC_authored_direct_child_transform_node":transform,
  "source_component_key_string_positions_fully_proven":False,
  "actual_runtime_player_initial_parent_world_matrix_proven":False,
  "original_Mission000_Player_initial_world_Z_feet_proven":False,
  "world_root_collision_vita_modified":False,
  "VPK":False
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 for row in rows:print("G257 original iOS Entity3D exact ARM",row)
 print("G257 original typed MC authored transform",transform)
 print("G257 PASS genuine original Entity3D source two typed components and original MC local transform; actual player boot world root unknown, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g254",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 args=p.parse_args();main(args.ipa,args.g254,args.out)
