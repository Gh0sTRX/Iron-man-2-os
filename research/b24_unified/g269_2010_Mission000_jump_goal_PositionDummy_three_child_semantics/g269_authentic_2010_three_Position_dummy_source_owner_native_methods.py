#!/usr/bin/env python3
"""G269 authentic original 2010 iOS C1L1 Mission000 goal's THREE
different source transforms (child1893-1895): type/class ownership,
serialized order, typed position fields and source native PositionDummy
methods. Never treat all three or an arbitrary first record as game world
goal. No Vita gameplay edits, no original binary included in artifacts.
"""
from __future__ import annotations
import argparse,bisect,collections,hashlib,json,subprocess,struct,sys,zipfile
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

def source(ipa:Path,g268:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("not genuine user-owned iOS 2010 IPA")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip() is not None:raise ValueError("original IPA archive CRC failed")
  exe=z.read("Payload/IronMan2.app/IronMan2")
  pack=z.read("Payload/IronMan2.app/clev")
 if len(exe)!=7480208:raise ValueError("real 2010 MachO size differs")
 raw=get_exact(pack,decode(pack,".bclara"),"level1.bclara")
 if len(raw)!=339733:raise ValueError("original first-level scene bytes mismatch")
 j268=json.loads(g268.read_text())
 goal=j268["source_true_original_Mission000_MC_initial_scripted_goal_PositionDummy_typed_transform_and_binding"]
 if (goal["original_2010_script_destination_PositionDummy_ID"],goal["original_2010_source_mc_actor_class112_ID"],goal["original_source_script_third_arg_raw_3000"])!=(1892,1062,3000):
  raise ValueError("G269 source-authenticated script target owner drift")
 typed=summarize(raw)
 ng=audit(raw)
 byname={v["original_name"]:v for v in typed["source_2010_typed_class_instances"]}
 if byname["PD_IM_jump_goal"]["original_class_name"]!="PositionDummy":
  raise ValueError("original native goal class identity changed")
 parent=byname["PD_IM_jump_goal"]
 if parent["original_numeric_name_id"]!=1892:raise ValueError("native goal source ID drift")
 matches=[x for x in ng["original_source_static_parent_record_links"]
    if x["original_parent_id"]==1892]
 selected=[]
 for row in matches:
  at=row["native_child_record_prefix_offset"]
  p=at+48
  shape=raw[p:p+2]==bytes([12,0]) and raw[p+14:p+16]==bytes([16,0]) and raw[p+32:p+34]==bytes([12,0])
  rec={
   "child_ID":row["original_child_id"],"native_component_tlv_type_tag":row["source_typed_record_field"],
   "source_serialized_component_offset":at,
   "position_trs_offset":p,
   "original_source_12_16_12_typed_trs_present":shape
  }
  if shape:
   before=raw[p-36:p]
   if before[8:12]!=bytes([6,0,4,0]) or before[16:18]!=bytes([4,0]) or before[22:24]!=bytes([12,0]):
    raise ValueError("G269 actual PositionData 3-mode typed label sizes drift")
   rec.update({
    "local_position_xyz":[round(x,6) for x in struct.unpack_from("<3f",raw,p+2)],
    "local_quaternion_xyzw":[round(x,6) for x in struct.unpack_from("<4f",raw,p+16)],
    "local_scale_xyz":[round(x,6) for x in struct.unpack_from("<3f",raw,p+34)],
    "source_AttachType":struct.unpack_from("<i",before,12)[0],
    "source_Bind_To_Entity":struct.unpack_from("<i",before,18)[0],
    "source_AttachOffset":[round(x,6) for x in struct.unpack_from("<3f",before,24)],
    "this_source_component_is_single_real_runtime_goal_world_pos_proven":False})
  selected.append(rec)
 selected.sort(key=lambda x:x["source_serialized_component_offset"])
 if [x["child_ID"] for x in selected] != [1893,1894,1895]:
  raise ValueError("G269 expected exactly three genuine original child Position transform candidate records")
 if not all(x["original_source_12_16_12_typed_trs_present"] for x in selected):
  raise ValueError("G269 original goal three true typed source transforms mismatch")
 whole=parse_macho(exe)
 if whole["nsyms"]!=65500:raise ValueError("original native MachO symbol count drift")
 syms=whole["entries"]
 dem=subprocess.run(["c++filt"],input="\n".join(row[0] for row in syms)+"\n",
  capture_output=True,text=True,check=True).stdout.splitlines()
 if len(syms)!=len(dem):raise ValueError("native C++ symbols mismatch")
 named=collections.defaultdict(set)
 for x,name in zip(syms,dem):named[x[1]&~1].add(name)
 pd_symbols=sorted([{"cpp":name,"native_VM":hex(vm)} for vm,names in named.items() for name in names
  if name.startswith("PositionDummy::")],key=lambda x:(x["cpp"],x["native_VM"]))
 if not pd_symbols:raise ValueError("source original PositionDummy class symbols not found")
 code_secs=[s for s in whole["sections"] if s[3]=="__text"]
 starts=sorted(k for k in named if any(s[0]<=k<s[0]+s[1] for s in code_secs))
 dis=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);dis.detail=True
 methods=[]
 for ent in pd_symbols:
  vm=int(ent["native_VM"],16)
  sec=next((s for s in code_secs if s[0]<=vm<s[0]+s[1]),None)
  if not sec:continue
  idx=bisect.bisect_right(starts,vm)
  end=starts[idx] if idx<len(starts) else sec[0]+sec[1]
  length=min(3000,end-vm,sec[0]+sec[1]-vm)
  if length<8:continue
  off=sec[2]+vm-sec[0]
  ops=list(dis.disasm(exe[off:off+length],vm))
  ins=[]
  for o in ops[:190]:
   item={"VM":hex(o.address),"mnemonic":o.mnemonic,"args":o.op_str}
   if o.id in (ARM_INS_BL,ARM_INS_BLX) and o.operands and o.operands[0].type==ARM_OP_IMM:
    dest=o.operands[0].imm&~1
    item["real_CPP_target_name"]=sorted(named.get(dest,()))[:5]
    item["direct_called_VM"]=hex(dest)
   ins.append(item)
  methods.append({"2010_original_CPP_method":ent["cpp"],"native_VM":ent["native_VM"],
       "first_190_native_ARM_instructions":ins,"method_was_ran_at_iOS_runtime_proven":False})
 report={
  "source":"G269 authentic original 2010 iOS level1.bclara PD_IM_jump_goal has three tagged Position-like children and native PositionDummy method callsite audit, not Vita runtime",
  "source_original_2010_C1L1_SHA256":hashlib.sha256(raw).hexdigest(),
  "real_2010_script_Mission000_move_target":"PD_IM_jump_goal",
  "original_native_MoveEntityToEntity_source_args":[1062,1892,3000],
  "genuine_PoistionDummy_class_name":"PositionDummy",
  "genuine_original_goal_3_different_typed_component_records":selected,
  "source_original_PositionDummy_native_cpp_symbols":pd_symbols,
  "source_original_PositionDummy_method_ARM_windows":methods,
  "genuine_original_3_source_transform_child_ordinal_proven":True,
  "genuine_runtime_get_position_selects_child_index_proven":False,
  "first_original_Mission000_MoveEntityToEntity_call_executed_proven":False,
  "original_player_actual_boot_or_cinematic_goal_world_XYZ_proven":False,
  "Vita_runtime_gameplay_or_collider_modified":False,
  "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 for c in selected:print("G269 original C1L1 real goal typed child",c)
 print("G269 original PositionDummy C++ symbol count",len(pd_symbols))
 for s in pd_symbols:print("G269 original native PD method",s)
 for method in methods:
  print("G269 PD method source ARM",method["2010_original_CPP_method"],method["native_VM"],len(method["first_190_native_ARM_instructions"]))
  for o in method["first_190_native_ARM_instructions"]:
   if "direct_called_VM" in o:print("G269 original PositionDummy genuine native BL",o)
 print("G269 PASS original 2010 PD_IM_jump_goal three distinct typed components; native method source; runtime target still uncertain, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g268",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 q=p.parse_args();source(q.ipa,q.g268,q.out)
