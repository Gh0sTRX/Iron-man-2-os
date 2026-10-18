#!/usr/bin/env python3
"""G210 original Iron Man 2 iOS (2010) actual native ARM loader
  StateDatabase(char const*) -> FileStream open,size,read,close
  -> BufferStream(...) -> StateSetData(BufferStream&)
  -> StateData(BufferStream&,StateSetData*)
  -> BufferStream::ReadString / virtual Read
  and Actor::UpdateStateAttack -> StateData::GetParam("AttackType",-1)
  -> MainCharacter override DoAttack via virtual slot68.

Source-only proof: 379 original length-tagged ASCII AttackType + u32
values, 0..25. This validates loader METHOD CHAIN; a fully verified
byte-for-byte schema deserializer for every StateData field / active
actor runtime mapping is NOT YET proven. No Vita runtime or VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,struct,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

OWNER=248613763
METHODS={
 "database":(0x9e1a8,"StateDatabase::StateDatabase(char const*)"),
 "state_set":(0x9d85c,"StateSetData::StateSetData(BufferStream&)"),
 "state_data":(0x9c528,"StateData::StateData(BufferStream&, StateSetData*)"),
 "get_param":(0x9c340,"StateData::GetParam(char const*, int)"),
 "track":(0xa196c,"StateTrack::StateTrack(BufferStream&)"),
 "actor_update":(0xdb610,"Actor::UpdateStateAttack(int, State*)"),
}
# All sites/targets are actual original 2010 ABI VM addresses:
EDGES=[
 ("database","filestream_open",0x9e200,0x50ec8,"FileStream::FileStream(char const*, int)"),
 ("database","file_size",0x9e208,0x50b1c,"FileStream::Size()"),
 ("database","file_read",0x9e234,0x50be8,"FileStream::Read(void*, int)"),
 ("database","file_close",0x9e240,0x50c08,"FileStream::Close()"),
 ("database","buffer_from_real_file",0x9e254,0x7659c,"BufferStream::BufferStream(int, int, void*)"),
 ("database","construct_stateset",0x9e55c,0x9d85c,"StateSetData::StateSetData(BufferStream&)"),
 ("state_set","construct_statedata",0x9df60,0x9c528,"StateData::StateData(BufferStream&, StateSetData*)"),
 ("state_set","read_stateset_name",0x9d8d0,0x75fa4,"BufferStream::ReadString()"),
 ("state_data","read_state_name",0x9c5f0,0x75fa4,"BufferStream::ReadString()"),
 ("state_data","read_state_field_name_1",0x9c84c,0x75fa4,"BufferStream::ReadString()"),
 ("state_data","read_state_field_name_2",0x9cbb0,0x75fa4,"BufferStream::ReadString()"),
 ("state_data","read_state_field_name_3",0x9cd2c,0x75fa4,"BufferStream::ReadString()"),
 ("state_data","construct_anim_event_track",0x9cfe4,0xa196c,"StateTrack::StateTrack(BufferStream&)"),
 ("state_data","read_state_field_name_4",0x9d24c,0x75fa4,"BufferStream::ReadString()"),
 ("actor_update","read_attack_type_named_state_param",0xdb65c,0x9c340,"StateData::GetParam(char const*, int)"),
]
VIRTUAL_READS=[
 ("database",0x9e274,0x9e278,0xc,"r4"),
 ("state_set",0x9d8f0,0x9d8f4,0xc,"r6"),
 ("state_data",0x9c608,0x9c60c,0xc,"r3"),
]
FIELD_GETPARAM={
 0x9c354:("ldr","fp, [r0, #0x24]"),    # original item count
 0x9c364:("ldr","r5, [r0, #0x1c]"),   # original 8-byte array key/value entries
 0x9c3e0:("lsl","ip, r4, #3"),
 0x9c4e4:("ldr","r6, [r6, #4]"),      # exact source loaded matching integer value
 0x9c4e8:("str","r6, [sp, #4]"),
}
SOURCE_STATE_FILE_SIZE=361393
SOURCE_KEY=b"AttackType"

def read(ipa:Path,source_json:Path,out:Path):
 if ipa.stat().st_size!=OWNER:raise ValueError("G210 exact original owner 2010 IPA required")
 d=json.loads(source_json.read_text())
 if d.get("original_raw_exact_AttackType_record_count")!=379:
  raise ValueError("G207 source record count mismatch")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("owner IPA archive CRC fail")
  exe=z.read("Payload/IronMan2.app/IronMan2")
  states=z.read("Payload/IronMan2.app/states")
 if len(exe)!=7480208 or len(states)!=SOURCE_STATE_FILE_SIZE:
  raise ValueError("original native MachO or states file not as proven")
 actual=[]
 idx=states.find(SOURCE_KEY)
 while idx>=0:
  if idx<2 or idx+len(SOURCE_KEY)+4>len(states):
   raise ValueError("original source byte key bounds mismatch")
  if struct.unpack_from("<H",states,idx-2)[0]!=10:
   raise ValueError("original source key length not 10")
  value=struct.unpack_from("<I",states,idx+10)[0]
  if value>25:raise ValueError("source ARM selector 0..25 is inconsistent with genuine serialized state")
  actual.append({"owner_state_file_VM_offset":idx,"raw_source_value":value})
  idx=states.find(SOURCE_KEY,idx+1)
 if len(actual)!=379:
  raise ValueError("actual source original state 379 bytes changed")
 check=[(row["owner_state_file_actual_AttackType_key_start_offset"],
         row["source_native_contiguous_original_u32_little_endian_value"])
         for row in d["source_actual_attactype_key_records_with_named_nearby_animation_candidates"]]
 if check!=[(r["owner_state_file_VM_offset"],r["raw_source_value"]) for r in actual]:
  raise ValueError("G210 379 exact file offset/value crosswalk to G207 source evidence drift")
 n=parse_macho(exe)
 dem=subprocess.run(["c++filt"],input="\n".join(x[0] for x in n["entries"])+"\n",
                    capture_output=True,text=True,check=True).stdout.splitlines()
 if len(dem)!=len(n["entries"]):raise ValueError("source native original names mismatched")
 named=collections.defaultdict(set);bits=collections.defaultdict(set)
 for rec,name in zip(n["entries"],dem):
  base=rec[1]&~1;named[base].add(name);bits[base].add(rec[1]&1)
 for key,(addr,name) in METHODS.items():
  if name not in named[addr]:
   raise ValueError(f"2010 source original {key} C++ symbol drift {hex(addr)} expected {name}")
 sections=[s for s in n["sections"] if s[3]=="__text"]
 addrs=sorted(named)
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);arm.detail=True
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB);thumb.detail=True
 assembly={}
 for label,(addr,_) in METHODS.items():
  sec=next((s for s in sections if s[0]<=addr<s[0]+s[1]),None)
  if sec is None:raise ValueError("original 2010 C++ method no text "+label)
  pos=bisect.bisect_right(addrs,addr)
  end=min(addrs[pos] if pos<len(addrs) else sec[0]+sec[1],sec[0]+sec[1],addr+21000)
  raw=exe[sec[2]+addr-sec[0]:sec[2]+end-sec[0]]
  code=list((thumb if bits[addr]=={1} else arm).disasm(raw,addr))
  if not code:raise ValueError("original source method not decoded "+label)
  assembly[label]={ins.address:ins for ins in code}
  print("G210 SOURCE C++ method",label,hex(addr),"authentic source instructions",len(code),flush=True)
 confirmed=[]
 for label,description,vm,target,name in EDGES:
  ins=assembly[label].get(vm)
  if (not ins or ins.mnemonic!="bl" or len(ins.operands)<1 or
      ins.operands[0].type!=ARM_OP_IMM or ins.operands[0].imm&~1!=target):
   raise ValueError(f"G210 original native source callsite diverged: {label} {hex(vm)}")
  if name not in named[target]:
   raise ValueError(f"original 2010 native target C++ name changed {hex(target)} {name}")
  confirmed.append({"source_cpp_class":label,"source_real_CALL_VM":hex(vm),
    "source_original_target_VM":hex(target),
    "source_original_CPP_called_method":name,
    "original_2010_native_CALL_SITE_PROVEN":True})
  print("G210 PASS REAL NATIVE EDGE",label,description,hex(vm),"->",name,flush=True)
 virtual_read_source=[]
 for label,mov_lr,call_site,offset,source_vtable_reg in VIRTUAL_READS:
  i=assembly[label].get(mov_lr);j=assembly[label].get(call_site)
  if (not i or i.mnemonic!="mov" or i.op_str!="lr, pc" or
      not j or j.mnemonic!="ldr" or j.op_str!=f"pc, [{source_vtable_reg}, #{hex(offset)}]"):
   # Different register used at different compiled callsite;
   # document instead of asserting false source equivalence.
   raise ValueError(f"G210 genuine 2010 BufferStream virtual read site changed {label} {hex(call_site)}")
  virtual_read_source.append({"source_native_class":label,
    "native_original_indirect_VM":hex(call_site),
    "source_virtual_slot_offset_bytes":offset,
    "source_proven_C++_receiver_type_BufferStream":False})
 for vm,(expected_op,expected_args) in FIELD_GETPARAM.items():
  ins=assembly["get_param"].get(vm)
  if not ins or ins.mnemonic!=expected_op or ins.op_str!=expected_args:
   raise ValueError("G210 real native StateData GetParam source item-field mismatch "+hex(vm))
 # Original 2010 Source architecture named loader + original bytes proven,
 # but constructing StateData on a real device with a given file path has
 # not yet been observed under GDB, and exact field/schema still TBD.
 report={
  "origin":"G210 real 2010 native ARM file loading and state deserializer method chain to 379 original AttackType key/value records",
  "owner_original_2010_IPA_verified_file_length":OWNER,
  "source_original_states_archive_bytes":len(states),
  "source_original_StateData_numeric_379_AttackType_values_revalidated_against_original_bytes":len(actual),
  "original_source_StateData_attacktype_unique_raw_number_values":sorted(set(r["raw_source_value"] for r in actual)),
  "source_actual_state_key_value_pairs_equal_G207_source_by_byte_offsets":True,
  "source_original_2010_exact_named_ARM_cpp_loader_edges":confirmed,
  "source_original_2010_virtual_BufferStream_reads_at_code_offsets":virtual_read_source,
  "source_original_native_GetParam_8_byte_items_and_offset_plus4_proven":True,
  "original_Native_FileStream_to_BufferStream_to_StateSetData_to_StateData_method_chain_PROVEN":True,
  "2010_actual_Lua_input_button_or_touch_mode_names_derived":False,
  "2010_exact_StateData_deserializer_379_owner_bin_record_per_object_boundary_PROVEN":False,
  "2010_real_active_MainCharacter_original_IOS_WeaponType_and_AnimMapped_PROVEN":False,
  "original_2010_attacks_from_33_Foot_source_context_resolved":False,
  "new_Vita_combat_or_InputSystem_patch_applied":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G210 PASS all original 2010 named source loader edges",len(confirmed),
       "and exact original 379 state key-value pairs rechecked, no VPK",flush=True)

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g207",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 read(a.ipa,a.g207,a.out)
