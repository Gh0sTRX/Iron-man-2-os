#!/usr/bin/env python3
"""G208 Original iOS 2010 StateData::GetParam(char const*,int) native ARM
implementation and serialized 2010 states property reader/loader methods.
Cross-check G207 proved 379 genuine 'AttackType' u16 len+u32 bytes
without conflating original StateData loader linkage or weapon meaning.

Original owner IPA only in CI temporary job. Output C++ symbol/method
source-op metadata, no raw game code, no Vita VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,re,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
SIZE=248613763
GETPARAM=0x9c340
NAMES=re.compile(r'^(StateData|StateTrack|StatesMgr|State)::',re.I)
READER=re.compile(r'load|read|parse|create|init|param|file|deseri|serial|add|get',re.I)
def analyze(ipa:Path,source_values:Path,out:Path):
 if ipa.stat().st_size!=SIZE:raise ValueError("requires user's 2010 owned IPA")
 g207=json.loads(source_values.read_text())
 if g207["original_raw_exact_AttackType_record_count"]!=379:
  raise ValueError("source owner 379 original state entries prerequisite")
 if not g207["original_all_379_u16_attacktype_key_fields_are_exact_length10"]:
  raise ValueError("authentic source field key byte length mismatch")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("original 2010 iOS owner IPA CRC fail")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("original 2010 native MachO size changed")
 m=parse_macho(exe)
 dem=subprocess.run(["c++filt"],input="\n".join(x[0] for x in m["entries"])+"\n",
                     text=True,capture_output=True,check=True).stdout.splitlines()
 if len(dem)!=len(m["entries"]):raise ValueError("source C++ labels length drift")
 named=collections.defaultdict(set);bits=collections.defaultdict(set)
 for rec,name in zip(m["entries"],dem):
  addr=rec[1]&~1; named[addr].add(name);bits[addr].add(rec[1]&1)
 if "StateData::GetParam(char const*, int)" not in named[GETPARAM]:
  raise ValueError("real original StateData GetParam source address changed")
 sorted_addrs=sorted(named)
 textsecs=[s for s in m["sections"] if s[3]=="__text"]
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);arm.detail=True
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB);thumb.detail=True
 subset=[(a,n) for a,v in named.items() for n in sorted(v) if NAMES.match(n)]
 allnames=[n for a,n in subset]
 selected=[]
 for addr,label in sorted(subset):
  sec=next((s for s in textsecs if s[0]<=addr<s[0]+s[1]),None)
  if sec is None:continue
  ix=bisect.bisect_right(sorted_addrs,addr)
  stop=sorted_addrs[ix] if ix<len(sorted_addrs) else sec[0]+sec[1]
  limit=min(stop-addr,sec[0]+sec[1]-addr,13000)
  if limit<4:continue
  f=sec[2]+addr-sec[0]
  ins=list((thumb if bits[addr]=={1} else arm).disasm(exe[f:f+limit],addr))
  if not ins:continue
  is_target=addr==GETPARAM
  if not is_target and not READER.search(label):continue
  calls=[]
  for x in ins:
   if x.mnemonic not in ("bl","blx") or not x.operands or x.operands[0].type!=ARM_OP_IMM:continue
   callee=x.operands[0].imm&~1
   if len(calls)<100:
    calls.append({"source_original_CALL_VM":hex(x.address),
      "target_native_C++_VM":hex(callee),
      "target_original_cpp_names":sorted(named.get(callee,()))[:5]})
  selected.append({
    "original_native_cpp_method":label,
    "source_original_address_VM":hex(addr),
    "source_original_source_ins_count":len(ins),
    "source_real_native_CALL_sites":calls,
    "source_first_150_bounded_original_ARM_instructions_NO_RAW_BYTES":[
      {"vm":hex(x.address),"mnemonic":x.mnemonic,"args":x.op_str} for x in ins[:150]],
    "source_original_2010_exact_serialized_states_binary_decoding_confirmed":False})
 if not any(z["source_original_address_VM"]==hex(GETPARAM) for z in selected):
  raise ValueError("genuine native GetParam absent")
 report={
  "origin":"G208 genuine 2010 owner original iOS MachO StateData source native and G207 exact states bytes",
  "original_StateData_GetParam_CPP":"StateData::GetParam(char const*, int)",
  "source_original_StateData_GetParam_VM":hex(GETPARAM),
  "all_original_2010_State_class_named_Cpp_methods":len(subset),
  "source_real_2010_StateLoader_method_symbol_list":sorted(set(allnames)),
  "selected_native_StateData_StateTrack_StatesMgr_cpp_implementation_samples":selected,
  "original_AttackType_key_u16_data_len":10,
  "source_original_AttackType_u32_state_record_count":379,
  "original_2010_all_source_numeric_key_value_u32_in_range_0_to25":g207["original_2010_values_OUTSIDE_G197_native_switch_0_to_25"]==0,
  "source_statedata_2010_getparam_actually_loads_states_asset_proven":False,
  "original_game_weaponID_attacktype_aim_m_binding_PROVEN":False,
  "source_original_file_binary_asset_distributed":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G208 native 2010 state methods",len(subset),"relevant decoded",len(selected))
 for row in selected:
  print("G208 TRUE owner StateData",row["source_original_address_VM"],row["original_native_cpp_method"],
        "instructions",row["source_original_source_ins_count"])
  if row["source_original_address_VM"]==hex(GETPARAM):
   for x in row["source_first_150_bounded_original_ARM_instructions_NO_RAW_BYTES"]:
    print("G208 SOURCE StateData GetParam",x)
  for x in row["source_real_native_CALL_sites"][:14]:
   print("G208 owner original StateData native CALL",row["original_native_cpp_method"],x)
 print("G208 serialized owner 2010 AttackType count 379, source native loader proof remains separate; NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--g207",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args()
 analyze(a.ipa,a.g207,a.out)
