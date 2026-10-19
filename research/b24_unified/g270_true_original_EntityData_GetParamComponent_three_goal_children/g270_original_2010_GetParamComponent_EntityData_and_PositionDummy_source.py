#!/usr/bin/env python3
"""G270 genuine 2010 iOS EntityData::GetParamComponent(char const*,
Component*) original ARM iteration versus Mission000 PD goal three
position-like source children. Original source audit only, no VPK or Vita
gameplay/lighting reordering. Native loader may SELECT one component;
do NOT infer selected child before verifying exact matching algorithm.
"""
from __future__ import annotations
import argparse,bisect,collections,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM,ARM_INS_BL,ARM_INS_BLX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from b24_owner_pack_extract import decode,get_exact
from b24_g24_original_clara_source_601_nodes_663_parent_links import audit
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
from g76_2010_native_arm_combat_method_provenance import parse_macho
GET=0xd7bb4
GAME=0xc2e8c
TABLE=0xc2ee0
def main(ipa:Path,g269:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("owner original 2010 iOS IPA mismatch")
 with zipfile.ZipFile(ipa) as z:
  exe=z.read("Payload/IronMan2.app/IronMan2")
  pack=z.read("Payload/IronMan2.app/clev")
 if len(exe)!=7480208:raise ValueError("not original iOS2010 MachO")
 scene=get_exact(pack,decode(pack,".bclara"),"level1.bclara")
 if len(scene)!=339733:raise ValueError("original C1L1 source drift")
 prior=json.loads(g269.read_text())
 goal=prior["genuine_original_goal_3_different_typed_component_records"]
 if [x["child_ID"] for x in goal]!=[1893,1894,1895]:
  raise ValueError("G270 source owner prior does not authenticate triple")
 typed=summarize(scene)
 lookup={x["original_numeric_name_id"]:x for x in typed["source_2010_typed_class_instances"]}
 d={x["original_class_name"]:x["original_class_id"] for x in typed["source_2010_class_schema"]}
 if lookup[1892]["original_class_name"]!="PositionDummy":
  raise ValueError("G270 actual original PD class owner lost")
 class_id=d["PositionDummy"]
 graph=audit(scene)
 pos=collections.defaultdict(list)
 for rec in graph["all_663_source_rigid_transforms_with_native_parent_child_name_ID_chain"]:
  parent=lookup.get(rec["original_named_parent_source_ID"])
  if parent and parent["original_class_name"]=="PositionDummy":
   pos[parent["original_name"]].append({
      "original_parent_source_named_ID":rec["original_named_parent_source_ID"],
      "original_child_ID":rec["original_child_node_ID"],
      "original_authored_local_XYZ":rec["native_vec3_position"],
      "source_data_is_runtime_playback_position_proven":False})
 count=collections.Counter(len(v) for v in pos.values())
 triple={name:items for name,items in pos.items() if len(items)==3}
 macho=parse_macho(exe)
 if macho["nsyms"]!=65500:raise ValueError("original native C++ symbols changed")
 syms=macho["entries"]
 dem=subprocess.run(["c++filt"],input="\n".join(x[0] for x in syms)+"\n",capture_output=True,text=True,check=True).stdout.splitlines()
 if len(syms)!=len(dem):raise ValueError("native owner name table mismatch")
 named=collections.defaultdict(set)
 for e,label in zip(syms,dem):named[e[1]&~1].add(label)
 if "EntityData::GetParamComponent(char const*, Component*)" not in named.get(GET,()):
  raise ValueError("G270 GetParamComponent original C++ method VM drift")
 if "GS_GamePlay::LoadEntities()" not in named.get(GAME,()):
  raise ValueError("G270 original level entity type case switch method VM drift")
 sections=[s for s in macho["sections"] if s[3]=="__text"]
 symbols=sorted(k for k in named if any(s[0]<=k<s[0]+s[1] for s in sections))
 cs=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);cs.detail=True
 def original_method(vm:int,maxbyte:int=8192):
  sec=next(s for s in sections if s[0]<=vm<s[0]+s[1])
  ix=bisect.bisect_right(symbols,vm)
  end=symbols[ix] if ix<len(symbols) else sec[0]+sec[1]
  size=min(maxbyte,end-vm,sec[0]+sec[1]-vm)
  if size<4:raise ValueError(f"original method too short at {vm:#x}")
  offset=sec[2]+vm-sec[0]
  ops=list(cs.disasm(exe[offset:offset+size],vm))
  output=[]
  for o in ops:
   row={"native_vm":hex(o.address),"opcode":o.mnemonic,"args":o.op_str}
   if o.id in (ARM_INS_BL,ARM_INS_BLX) and o.operands and o.operands[0].type==ARM_OP_IMM:
    addr=o.operands[0].imm&~1
    row["source_direct_call_target_VM"]=hex(addr)
    row["source_original_cpp_name"]=sorted(named.get(addr,()))[:5]
   output.append(row)
  return output
 func=original_method(GET)
 if len(func)<10:raise ValueError("original GetParamComponent native method disassembled too short")
 case_table=original_method(GAME,12288)
 lookup_jump=TABLE+4*(class_id-1)
 switch=next((x for x in case_table if int(x["native_vm"],16)==lookup_jump),None)
 if not switch or switch["opcode"]!="b":
  raise ValueError("PositionDummy original scene class lacks exact native LoadEntities type jump")
 dest=int(switch["args"].removeprefix("#"),0)
 class_ops=[x for x in case_table if dest-24<=int(x["native_vm"],16)<=dest+140]
 result={
  "source":"G270 true original 2010 iOS GetParamComponent native ARM component selection and C1L1 all PositionDummy triple-source positions; no emulator executed",
  "source_original_2010_executable_SHA256":hashlib.sha256(exe).hexdigest(),
  "source_original_clara_level1_SHA256":hashlib.sha256(scene).hexdigest(),
  "original_PositionDummy_class_template_ID":class_id,
  "original_C1L1_PositionDummy_entities_with_at_least_one_strict_TRS":len(pos),
  "original_source_PositionDummy_strict_TRS_child_count_distribution":{str(k):n for k,n in sorted(count.items())},
  "original_source_three_child_PositionDummy_names_and_local_transforms":triple,
  "original_EntityData_GetParamComponent_CPP":"EntityData::GetParamComponent(char const*, Component*)",
  "original_EntityData_GetParamComponent_native_VM":hex(GET),
  "genuine_native_GetParamComponent_full_ARM_instructions":func,
  "original_native_GS_GamePlay_LoadEntities_class_jump_source_VM":hex(lookup_jump),
  "original_native_GS_GamePlay_LoadEntities_PositionDummy_class_case_VM":hex(dest),
  "original_native_PositionDummy_class_dispatch_ARM_window":class_ops,
  "source_2010_C1L1_three_children_1893_1894_1895_expected":True,
  "original_EntityData_GetParamComponent_selected_child_index_or_field_runtime_proven":False,
  "original_MC_actual_runtime_world_position_proven":False,
  "Vita_runtime_movement_collider_camera_lighting_modified":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
 print("G270 source original PositionDummy CLARA class",class_id,"strict child cardinalities",dict(count),"three-child count",len(triple))
 for name,items in list(triple.items())[:25]:print("G270 original three child scene authored",name,items)
 print("G270 native original PositionDummy LoadEntities class table",hex(lookup_jump),"->",hex(dest))
 for x in class_ops:print("G270 original native class dispatch",x)
 print("G270 true original GetParamComponent C++ method ARM opcount",len(func))
 for x in func[:250]:print("G270 ORIGINAL GetParamComponent native ARM",x)
 print("G270 PASS original iOS source component selection program and PD class dispatch audited; target world pos not guessed, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g269",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 main(a.ipa,a.g269,a.out)
