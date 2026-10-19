#!/usr/bin/env python3
"""G245 original 2010 EntityData::LoadFromFile(DataStream&) record grammar
probe; exact source ARM C++ address came from G244 direct real call.
Only original disassembly metadata; no source asset dump. Does not
equate numeric scene IDs / class numbers to WeaponDB indices.
"""
from __future__ import annotations
import argparse,bisect,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
VM=0xd356c
CPP="EntityData::LoadFromFile(DataStream&)"
def run(ipa:Path,g244:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("original 2010 IPA size mismatch")
 with zipfile.ZipFile(ipa) as z:exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("wrong real original source executable bytes")
 native=parse_macho(exe)
 if native["nsyms"]!=65500:raise ValueError("original native symbol count changed")
 syms=native["entries"]
 dem=subprocess.run(["c++filt"],input="\n".join(x[0] for x in syms)+"\n",
    capture_output=True,text=True,check=True).stdout.splitlines()
 if len(dem)!=len(syms):raise ValueError("original native symbols desynchronized")
 names={}
 for x,name in zip(syms,dem):names.setdefault(x[1]&~1,set()).add(name)
 if CPP not in names.get(VM,()):raise ValueError("not original 2010 EntityData::LoadFromFile")
 prior=json.loads(g244.read_text())
 if (prior.get("original_2010_EntityData_per_record_Cpp_method_VM")!=hex(VM) or
     not prior.get("original_native_successful_EntitiesData_LoadFromFile_advances_current_slot_36_bytes_in_file_stream_order")):
  raise ValueError("G245 original sequential parent parser evidence missing")
 sec=next((s for s in native["sections"] if s[3]=="__text" and s[0]<=VM<s[0]+s[1]),None)
 if sec is None:raise ValueError("original EntityData source section absent")
 starts=sorted(a for a in names if sec[0]<=a<sec[0]+sec[1])
 k=bisect.bisect_right(starts,VM)
 end=starts[k] if k<len(starts) else sec[0]+sec[1]
 size=end-VM
 if not 32<=size<=35000:raise ValueError("real owner EntityData method untrusted bounds")
 off=sec[2]+VM-sec[0]
 cs=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);cs.detail=True
 ops=list(cs.disasm(exe[off:off+size],VM))
 if not ops or ops[0].address!=VM:raise ValueError("2010 original ARM method not decoded")
 rows=[];reads=[];member_ops=[]
 for op in ops:
  row={"VM":hex(op.address),"op":op.mnemonic,"args":op.op_str}
  if op.mnemonic.startswith(("bl","blx")) and op.operands and op.operands[0].type==ARM_OP_IMM:
   target=op.operands[0].imm&~1
   row["target_VM"]=hex(target)
   row["genuine_original_Cpp_method"]=sorted(names.get(target,()))[:4]
   if "DataStream::" in " ".join(row["genuine_original_Cpp_method"]) or "EntityData::" in " ".join(row["genuine_original_Cpp_method"]):
    reads.append(row)
  if ("[r4" in op.op_str or "[r5" in op.op_str or "[r6" in op.op_str or
      "[r0, #0x14]" in op.op_str) and (op.mnemonic.startswith(("str","ldr"))):
   member_ops.append(row)
  rows.append(row)
 report={
  "source":"G245 genuine 2010 iOS 65500-symbol owner MachO EntityData::LoadFromFile exact C++ ARM body",
  "original_owner_MachO_SHA256":hashlib.sha256(exe).hexdigest(),
  "real_native_2010_EntityData_load_cpp_name":CPP,
  "native_source_method_VM":hex(VM),
  "native_method_bytes":size,
  "source_original_ARM_instruction_count":len(rows),
  "actual_native_EntityData_source_ARM_opcode_metadata":rows,
  "original_native_DataStream_and_EntityData_direct_calls":reads,
  "candidate_source_native_instance_object_member_loads_stores":member_ops[:160],
  "parent_EntitiesData_sequential_36byte_array_insert_proven":True,
  "source_native_EntityData_reader_full_serialization_grammar_proven":False,
  "actual_2010_WeaponDB_index_0_1_4_to_C1L1_Attack_source_objects_proven":False,
  "actual_device_Vita_ground_motion_fix_proven":False,
  "vita_player_weapon_damage_render_or_mission_modified":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G245 original EntityData reader",size,"bytes",len(rows),"native ARM instructions")
 for row in reads:print("G245 true original per-entity stream CALL",row)
 for row in rows[:200]:print("G245 true original EntityData ARM",row)
 print("G245 PASS genuine original 2010 per-record stream reader code, still no WeaponDB index claim/VPK")
 return report
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--ipa",required=True,type=Path)
 ap.add_argument("--g244",required=True,type=Path)
 ap.add_argument("--out",required=True,type=Path)
 a=ap.parse_args()
 run(a.ipa,a.g244,a.out)
