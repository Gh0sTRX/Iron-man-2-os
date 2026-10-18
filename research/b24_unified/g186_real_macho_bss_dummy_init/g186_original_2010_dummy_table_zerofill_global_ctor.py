#!/usr/bin/env python3
"""G186 check actual 2010 iOS Mach-O LC_SEGMENT/__common section flags
before treating SceneImpl::s_dummiesTable bytes as file content.

Inspect matching genuine native global constructors and SceneImpl
initializers for possible startup filling, without guessing 14/33 names.
The G184/G185 source '972,5127504,2' from mapping __common offset
without S_ZEROFILL awareness must NOT be claimed initialized table values.
"""
from __future__ import annotations
import argparse,bisect,collections,json,struct,subprocess,sys,zipfile
from pathlib import Path
import capstone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
ORIGINAL_SIZE=248613763
TABLE_VM=0x4edca0
def run(ipa:Path,out:Path):
 if ipa.stat().st_size!=ORIGINAL_SIZE:raise ValueError("original owner 2010 iOS IPA expected")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("owner 2010 archive failed CRC")
  binary=z.read("Payload/IronMan2.app/IronMan2")
 if len(binary)!=7480208:raise ValueError("2010 game ARM executable changed")
 parsed=parse_macho(binary)
 names=subprocess.run(["c++filt"],input="\n".join(a[0] for a in parsed["entries"])+"\n",
                       capture_output=True,text=True,check=True).stdout.splitlines()
 if len(names)!=len(parsed["entries"]):raise ValueError("native symbol demangling mismatch")
 symbols=collections.defaultdict(set);origin=collections.defaultdict(set)
 for row,name in zip(parsed["entries"],names):
  key=row[1]&~1
  symbols[key].add(name)
  origin[key].add(row[1]&1)
 if "SceneImpl::s_dummiesTable" not in symbols[TABLE_VM]:
  raise ValueError("2010 native original table symbol address/type changed")
 # Parse full actual section header flags rather than old parse_macho's
 # intentionally compact (vmaddr, vmsize, offset, name, segment) view.
 header=struct.unpack_from("<IiiIIII",binary,0)
 pos=28;sections=[]
 for _ in range(header[4]):
  cmd,size=struct.unpack_from("<II",binary,pos)
  if cmd==1:
   count=struct.unpack_from("<I",binary,pos+48)[0]
   for i in range(count):
    at=pos+56+68*i
    section_name=binary[at:at+16].split(b"\0")[0].decode("latin1")
    segment_name=binary[at+16:at+32].split(b"\0")[0].decode("latin1")
    addr,nbytes,offset=struct.unpack_from("<III",binary,at+32)
    flags=struct.unpack_from("<I",binary,at+56)[0]
    if addr<=TABLE_VM<addr+nbytes:
     sections.append({"sectname":section_name,"segname":segment_name,
                      "address_VM":hex(addr),"length":nbytes,
                      "file_offset_from_header":offset,
                      "native_section_flags_hex":hex(flags),
                      "native_section_type":flags&0xff,
                      "original_MachO_S_ZEROFILL":(flags&0xff)==1,
                      "macho_file_bytes_at_offset_are_initialized_data":(flags&0xff)!=1})
  pos+=size
 if len(sections)!=1 or not sections[0]["original_MachO_S_ZEROFILL"]:
  raise ValueError("Actual original 2010 SceneImpl dummy table was not zero fill! Need re-review")
 # All the old 's_dummiesTable raw 972 ...' values were from treating
 # this zero-fill section's (non-file-backed) offset as file bytes.
 # We do not republish these numbers as original runtime pointers.
 byname=[]
 for addr,group in sorted(symbols.items()):
  chosen=[name for name in group if any(t in name for t in (
    "s_dummiesTable","global constructors keyed to SceneImpl",
    "SceneImpl::SceneImpl(","SceneImpl::Initialize(","CollectDummies(","DummySorter",
    "SceneImpl::s_dummy"))]
  if chosen:byname.append({"original_VM":hex(addr),"real_native_source_names":chosen[:8]})
 textsects=[x for x in parsed["sections"] if x[3]=="__text"]
 addresses=sorted(symbols)
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 for cs in (arm,thumb):cs.detail=True
 candidates=[]
 for addr,group in sorted(symbols.items()):
  match=[n for n in group if "global constructors keyed to" in n and
         ("SceneImpl" in n or "dummy" in n.lower())]
  if not match:continue
  sec=next((s for s in textsects if s[0]<=addr<s[0]+s[1]),None)
  if sec is None:continue
  j=bisect.bisect_right(addresses,addr)
  right=addresses[j] if j<len(addresses) else sec[0]+sec[1]
  length=min(right-addr,sec[0]+sec[1]-addr,3000)
  if length<4:continue
  begin=sec[2]+addr-sec[0]
  instructions=list((thumb if origin[addr]=={1} else arm).disasm(
                    binary[begin:begin+length],addr))
  candidates.append({"original_native_ctor_VM":hex(addr),"original_CPP_symbols":match,
    "native_bounded_instruction_count":len(instructions),
    "source_first_120_opcode_rows_no_binary":[
       {"VM":hex(i.address),"mnemonic":i.mnemonic,"arguments":i.op_str}
       for i in instructions[:120]]})
 all_global=[{"native_VM":hex(a),"names":[n for n in ns if "global constructors keyed to" in n][:2]}
             for a,ns in symbols.items() if
             any("global constructors keyed to" in n for n in ns)]
 report={
  "origin":"2010 original iOS 1.0.0 Mach-O, section flags decoded from native section_32",
  "genuine_dummies_symbol":"SceneImpl::s_dummiesTable",
  "native_real_data_VM":"0x4edca0",
  "source_actual_native_macho_section":sections[0],
  "source_original_global_ctor_SceneImpl_or_dummy_candidates":candidates,
  "source_related_native_CPP_names":byname,
  "source_original_global_constructor_symbol_count":len(all_global),
  "source_original_global_constructor_first_60_named_entries":all_global[:60],
  "old_G184_G185_unbacked_section_file_word_decoding_INVALID":True,
  "G184_claim_initial_972_5127504_2_are_real_s_dummiesTable_runtime_fields":False,
  "native_dummy_scene_group_14_33_to_model_node_names_PROVEN":False,
  "native_dynamic_s_dummiesTable_content_in_original_runtime_observed":False,
  "zero_fill_section_runtime_initializer_direct_write_verified":False,
  "NO_IPA_BINARY_OR_BDAE_ASSET_EXPORTED":True,
  "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G186 REAL 2010 MachO SceneImpl s_dummiesTable __common zerofill",sections)
 print("G186 REAL original related names",byname[:45])
 print("G186 global ctor count",len(all_global),
       "matching native ctor methods",len(candidates))
 for x in candidates:
  print("G186 REAL 2010 C++ INIT",x["original_native_ctor_VM"],x["original_CPP_symbols"])
  for i in x["source_first_120_opcode_rows_no_binary"]:
   print("G186 REAL C++ CTOR ARM",i["VM"],i["mnemonic"],i["arguments"])
 print("G186 INVALIDATED G184/G185 raw __common file word 972/5127504/2 as live data. Model names 14/33 remain UNKNOWN. NO VPK")
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--ipa",type=Path,required=True)
 a.add_argument("--out",type=Path,required=True)
 t=a.parse_args()
 run(t.ipa,t.out)
