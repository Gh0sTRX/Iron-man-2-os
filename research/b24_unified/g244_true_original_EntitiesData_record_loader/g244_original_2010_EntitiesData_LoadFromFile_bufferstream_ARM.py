#!/usr/bin/env python3
"""G244 actual 2010 Gameloft iOS EntitiesData::LoadFromFile(BufferStream&,int)
original ARM reader. Follows a real direct BL inside ClaraFile::Load
G243. Tests original count/data structure but does not infer or fabricate
C1L1 runtime Attack array ids, weapons, animation or Vita gameplay.
"""
from __future__ import annotations
import argparse,bisect,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
VM=0xd56c8
METHOD="EntitiesData::LoadFromFile(BufferStream&, int)"
CALL_VM=0xd5af0
def run(ipa:Path,g243:Path,out:Path)->dict:
 if ipa.stat().st_size!=248613763:raise ValueError("not owner's exact original source IPA")
 with zipfile.ZipFile(ipa) as z: exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("2010 native executable exact bytes mismatch")
 native=parse_macho(exe)
 if native["nsyms"]!=65500:raise ValueError("original 2010 LC_SYMTAB name count drift")
 sym=native["entries"]
 dem=subprocess.run(["c++filt"],input="\n".join(x[0] for x in sym)+"\n",
  capture_output=True,text=True,check=True).stdout.splitlines()
 if len(dem)!=len(sym):raise ValueError("2010 demangled names count mismatch")
 names={}
 for x,n in zip(sym,dem):names.setdefault(x[1]&~1,set()).add(n)
 if METHOD not in names.get(VM,()):raise ValueError("native EntitiesData::LoadFromFile exact symbol absent")
 g=json.loads(g243.read_text())
 if (g.get("native_original_method_VM")!="0xd5a94" or
     not any(x["authentic_CALL_VM"]==hex(CALL_VM)
      and x["target_VM"]==hex(VM)
      and METHOD in x["exact_original_cpp_names"]
        for x in g["source_Clara_EntityData_BufferStream_direct_CALL_candidates"])):
  raise ValueError("G244 direct original ClaraFile->EntitiesData loader link not proved")
 sec=next((s for s in native["sections"] if s[3]=="__text" and s[0]<=VM<s[0]+s[1]),None)
 if sec is None:raise ValueError("genuine 2010 native __text missing")
 starts=sorted(x for x in names if sec[0]<=x<sec[0]+sec[1])
 idx=bisect.bisect_right(starts,VM)
 stop=starts[idx] if idx<len(starts) else sec[0]+sec[1]
 size=stop-VM
 if size<64 or size>30000:raise ValueError(f"unexpected EntitiesData loader size {size}")
 offset=sec[2]+VM-sec[0]
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);arm.detail=True
 ops=list(arm.disasm(exe[offset:offset+size],VM))
 if not ops or ops[0].address!=VM:raise ValueError("genuine EntitiesData loader native ARM decode failed")
 source_native={o.address:(o.mnemonic,o.op_str) for o in ops}
 # Concrete 2010 source allocation:
 # DataStream::ReadUnsignedShort() returns source number of EntityData
 # records; r0*4+r0*32=36 per record; +4 for array header; new[].
 for site,expected in {
   0xd56fc:("bl","#0x768f8"),
   0xd5700:("lsl","r3, r0, #2"),
   0xd5704:("lsl","r1, r0, #5"),
   0xd570c:("str","r0, [r5, #4]"),
   0xd5710:("add","r0, r3, r1"),
   0xd5714:("add","r0, r0, #4"),
   0xd5718:("bl","#0x5034"),
   0xd588c:("mov","sl, #0"),
   0xd5890:("mov","r6, sl"),
   0xd589c:("add","r0, r6, r8"),
   0xd58a0:("bl","#0xd356c"),
   0xd5a58:("add","sl, sl, #1"),
   0xd5a5c:("cmp","r3, sl"),
   0xd5a60:("add","r6, r6, #0x24"),
   0xd5a64:("bgt","#0xd5894"),
   0xd5a80:("add","sl, sl, #1"),
   0xd5a84:("cmp","r3, sl"),
   0xd5a88:("add","r6, r6, #0x24"),
   0xd5a8c:("bgt","#0xd5894"),
 }.items():
  if source_native.get(site)!=expected:
   raise ValueError(f"G244 exact original 2010 EntitiesData count or 36-byte allocation source drift @ {site:#x}: {source_native.get(site)}")
 if "EntityData::LoadFromFile(DataStream&)" not in names.get(0xd356c,()):
  raise ValueError("G244 original per-entity DataStream class loader C++ name drift")
 def serialize(o):
  q={"VM":hex(o.address),"mnemonic":o.mnemonic,"args":o.op_str}
  if o.mnemonic.startswith(("bl","blx")) and o.operands and o.operands[0].type==ARM_OP_IMM:
   tgt=o.operands[0].imm&~1
   q["real_original_direct_callee_VM"]=hex(tgt)
   q["true_Cpp_target_names"]=sorted(names.get(tgt,()))[:5]
  return q
 src=[serialize(o) for o in ops]
 special=[x for x in src if "direct_callee" in x]
 # Entire method is typically small; export instruction metadata only,
 # not original byte contents, levels or full copyrighted assets.
 report={
  "source":"G244 original owner 2010 iOS native EntitiesData::LoadFromFile exact MachO symbol and bounded ARM method",
  "original_owner_MachO_SHA256":hashlib.sha256(exe).hexdigest(),
  "original_source_CPP_method":METHOD,"original_source_VM":hex(VM),
  "original_native_method_2010_bytes":size,
  "original_native_method_ARM_opcode_count":len(src),
  "genuine_2010_original_method_ARM_metadata":src,
  "original_source_Cpp_direct_callees":special,
  "original_ClaraFile_Load_BL_EntitiesData_loader_VM":hex(CALL_VM),
  "original_ClaraFile_GetEntityData_index_stride_bytes":36,
  "original_native_entity_data_count_from_DataStream_ReadUnsignedShort":True,
  "original_native_36_byte_stride_allocation_count_times_36_plus_4":True,
  "native_original_EntityData_LoadFromFile_called_for_indexed_slot":True,
  "original_native_successful_EntitiesData_LoadFromFile_advances_current_slot_36_bytes_in_file_stream_order":True,
  "original_native_loop_index_advances_one_and_rechecks_count":True,
  "source_C1L1_scene_binary_names_sorted_by_offset_proven_to_be_same_as_native_clara_EntityData_order":False,
  "source_C1L1_native_WeaponDB_record_index_order_proven":False,

  "original_2010_EntityData_per_record_Cpp_method_VM":"0xd356c",

  "source_EntitiesData_original_load_contains_runtime_execution_proven":False,
  "actual_original_C1L1_list_layout_and_per_Attack_id_0_1_4_registration_proven":False,
  "original_WarMachine_AimM_missile_gatling_control_proven":False,
  "vita_gameplay_ground_world_or_weapon_code_modified":False,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G244 original EntitiesData::LoadFromFile",size,"source bytes",len(src),"ARM opcodes")
 for item in special:print("G244 original source loader calls",item)
 for row in src:print("G244 2010 native EntitiesData ARM",row)
 print("G244 PASS exact genuine original 2010 EntitiesData::LoadFromFile method and ClaraFile call provenance; no fake weapon index/VPK")
 return report
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--ipa",type=Path,required=True)
 a.add_argument("--g243",type=Path,required=True)
 a.add_argument("--out",type=Path,required=True)
 q=a.parse_args();run(q.ipa,q.g243,q.out)
