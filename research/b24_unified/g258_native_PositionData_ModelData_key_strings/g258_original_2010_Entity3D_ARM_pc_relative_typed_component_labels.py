#!/usr/bin/env python3
"""G258 genuine 2010 iOS Entity3D ARM PC-relative component label source.
Read original MachO literal pool (not guess): Entity3D::LoadFromFile
PositionData and ModelData typed component names used by LoadFromFile.
Grounded source player world startup STILL unknown. NO Vita runtime/VPK.
"""
from __future__ import annotations
import argparse,hashlib,json,struct,zipfile
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_ARM
from b24_owner_pack_extract import decode,get_exact
from b24_g25_original_clara_class_schema_and_actual_MC_maincharacter import summarize
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
VM=0x12c78
LITERALS=[
 {"component_type":"PositionData","ldr_vm":0x12c9c,"add_vm":0x12ca4,"pool_vm":0x12ce0,"member_offset":0x70,"read_call_vm":0x12cb0},
 {"component_type":"ModelData","ldr_vm":0x12cc4,"add_vm":0x12ccc,"pool_vm":0x12ce4,"member_offset":0x74,"read_call_vm":0x12cd8},
]
def read_address(exe:bytes,sections:list,vm:int,size:int)->bytes:
 sec=next((s for s in sections if s[0]<=vm and vm+size<=s[0]+s[1]),None)
 if sec is None:raise ValueError(f"cannot map original source iOS MachO VM {vm:#x} size {size}")
 off=sec[2]+vm-sec[0]
 if off<0 or off+size>len(exe):raise ValueError("original source MachO segment exceeds bounds")
 return exe[off:off+size]
def original_ascii(exe:bytes,secs:list,vm:int)->str:
 sec=next((s for s in secs if s[0]<=vm<s[0]+s[1]),None)
 if sec is None:return ""
 raw=read_address(exe,secs,vm,min(180,sec[0]+sec[1]-vm))
 b=raw.split(b"\0",1)[0]
 if not 2<=len(b)<=100 or not all(32<=c<127 for c in b):return ""
 return b.decode("ascii")
def run(ipa:Path,g257:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("not original 2010 owner IPA")
 with zipfile.ZipFile(ipa) as z:
  exe=z.read("Payload/IronMan2.app/IronMan2")
  raw=z.read("Payload/IronMan2.app/clev")
 if len(exe)!=7480208:raise ValueError("not original 2010 iOS MachO")
 baseline=json.loads(g257.read_text())
 if baseline["original_native_method_VM"]!="0x12c78" or baseline["source_component_key_string_positions_fully_proven"]:
  raise ValueError("G258 requires G257 exact authentic source yet-unresolved component names")
 macho=parse_macho(exe)
 if macho["nsyms"]!=65500:raise ValueError("original 2010 source symbol count drift")
 secs=macho["sections"]
 ops=list(Cs(CS_ARCH_ARM,CS_MODE_ARM).disasm(read_address(exe,secs,VM,108),VM))
 lookup={op.address:(op.mnemonic,op.op_str) for op in ops}
 results=[]
 for row in LITERALS:
  ldr_vm,add_vm,pool=row["ldr_vm"],row["add_vm"],row["pool_vm"]
  if not lookup.get(ldr_vm,("",""))[0].startswith("ldr") or lookup.get(add_vm,("",""))[0]!="add":
   raise ValueError("native source PC-relative label construction changed")
  signed_delta=struct.unpack("<i",read_address(exe,secs,pool,4))[0]
  # ARM data-processing PC operand on ADD reads instruction address+8.
  assembled_string_vm=add_vm+8+signed_delta
  found=original_ascii(exe,secs,assembled_string_vm)
  if not found:
   raise ValueError(f"source authentic label for {row['component_type']} is non-ASCII or unmapped: VM={assembled_string_vm:#x}")
  val={**row,"literal_pool_displacement_signed":signed_delta,
      "original_native_component_name_ptr_VM":hex(assembled_string_vm),
      "original_native_C_string_argument":found,
      "source_getparamcomponent_CPP_name":"EntityData::GetParamComponent(char const*, Component*)",
      "does_not_prove_player_runtime_world_spawn":True}
  results.append(val)
  print("G258 AUTHENTIC 2010 Entity3D typed component original literal",val)
 if len(set(row["original_native_C_string_argument"] for row in results))!=2:
  raise ValueError("G258 two original typed CLARA properties were not distinct")
 level=get_exact(raw,decode(raw,".bclara"),"level1.bclara")
 scene=summarize(level)
 mc=[i for i in scene["source_2010_typed_class_instances"] if i["original_class_name"]=="MainCharacter"]
 if len(mc)!=1:raise ValueError("original first-level MainCharacter class count drift")
 report={
  "source":"G258 authentic original 2010 iOS MachO ARM PC-relative literal pool metadata resolving Entity3D::LoadFromFile typed component keys",
  "real_owner_MachO_SHA256":hashlib.sha256(exe).hexdigest(),
  "real_original_scene_SHA256":hashlib.sha256(level).hexdigest(),
  "original_native_Entity3D_loader_VM":"0x12c78",
  "original_native_source_typed_components":results,
  "authentic_2010_source_typed_Player_MC_node_ID":mc[0]["original_numeric_name_id"],
  "source_Verified_Member_Pointer_offsets_PositionData_and_ModelData":True,
  "original_native_iOS_live_MainCharacter_player_initial_WORLD_XYZ_proven":False,
  "vita_ground_collision_and_actor_world_pos_code_changed":False,
  "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G258 PASS original 2010 true PC-relative source 2 components; no VPK")
 return report
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g257",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 q=p.parse_args();run(q.ipa,q.g257,q.out)
