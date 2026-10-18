#!/usr/bin/env python3
"""G185 genuine 2010 iOS ARM native SceneImpl::CollectDummies registration
and 14/33 source-indices, context in 0x63108..0x63714.

Goal: recover *only observed* ARM writes to scene+0x278 and global name
dictionary, not naively match BDAE parsed traversal order with int14/33.

Read user-supplied original 1.0.0 IPA in an ephemeral CI runner. Emit
no executable/assets/IPA, ONLY bounded opcode and named symbol evidence.
"""
from __future__ import annotations
import argparse,bisect,collections,json,re,struct,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM, ARM_OP_MEM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

SIZE=248613763
FUNC=0x62ea4
LOOKUP=0x61724
GROUP_DATA=0x4edca0
RANGE_LO=0x63108
RANGE_HI=0x63714

def main(ipa:Path,out:Path):
 if ipa.stat().st_size!=SIZE:raise ValueError("Not the original user-provided 2010 IPA")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("2010 owner archive corruption")
  elf=z.read("Payload/IronMan2.app/IronMan2")
 if len(elf)!=7480208:raise ValueError("2010 owner ARM Mach-O size drift")
 original=parse_macho(elf)
 dem=subprocess.run(["c++filt"],input="\n".join(x[0] for x in original["entries"])+"\n",
                    text=True,capture_output=True,check=True).stdout.splitlines()
 if len(dem)!=len(original["entries"]):raise ValueError("original symbol table length changed")
 sym=collections.defaultdict(set)
 raw=collections.defaultdict(set)
 for t,n in zip(original["entries"],dem):
  a=t[1]&~1
  sym[a].add(n)
  raw[a].add(t[1]&1)
 if "SceneImpl::CollectDummies(irr::scene::ISceneNode*)" not in sym[FUNC]:
  raise ValueError("original native collector symbol changed")
 if "SceneImpl::GetDummy(int, unsigned int)" not in sym[LOOKUP]:
  raise ValueError("native original GetDummy symbol mismatch")
 secs=original["sections"]
 def vmread(addr,n):
  section=next((s for s in secs if s[0]<=addr and addr+n<=s[0]+s[1]),None)
  if section is None:return None
  off=section[2]+addr-section[0]
  if off<0 or off+n>len(elf):return None
  return elf[off:off+n]
 def u32(addr):
  v=vmread(addr,4)
  return struct.unpack_from("<I",v)[0] if v else None
 source={"VM":hex(GROUP_DATA),"content_sections":[
  {"name":s[3],"segment":s[4] if len(s)>4 else "",
   "start":hex(s[0]),"size":s[1]}
  for s in secs if s[0]<=GROUP_DATA<s[0]+s[1]],
  "raw_four_word_values":[u32(GROUP_DATA+i*4) for i in range(4)],
  "raw_words_are_live_runtime_initialized":False,
  "raw_words_form_valid_group_14_33_pointer_list_PROVEN":False
 }
 nearest=sorted((abs(a-GROUP_DATA),hex(a),sorted(ns)[:6]) for a,ns in sym.items())[:25]
 source["nearby_original_symbols"]=nearest
 section=next((s for s in secs if s[3]=="__text" and s[0]<=FUNC<s[0]+s[1]),None)
 if section is None:raise ValueError("native original CollectDummies not in __text")
 addresses=sorted(sym)
 i=bisect.bisect_right(addresses,FUNC)
 right=addresses[i] if i<len(addresses) else section[0]+section[1]
 size=min(12000,right-FUNC,section[0]+section[1]-FUNC)
 if size<RANGE_HI-FUNC:raise ValueError("Collector body truncated before registration end")
 cs=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);cs.detail=True
 off=section[2]+FUNC-section[0]
 ins=list(cs.disasm(elf[off:off+size],FUNC))
 if not ins or not any(x.address==RANGE_HI for x in ins):
  raise ValueError("No original registration code")
 registry=[]
 calls=[]
 branches=[]
 stores=[]
 for x in ins:
  if not RANGE_LO<=x.address<=RANGE_HI:continue
  rec={"VM":hex(x.address),"mnemonic":x.mnemonic,"args":x.op_str}
  registry.append(rec)
  if x.mnemonic in ("bl","blx") and x.operands and x.operands[0].type==ARM_OP_IMM:
   target=x.operands[0].imm&~1
   calls.append({**rec,"target":hex(target),"native_real_names":sorted(sym.get(target,()))[:5]})
  if x.mnemonic.startswith("b") and x.mnemonic not in ("bl","blx"):
   branches.append(rec)
  if x.mnemonic.startswith(("str","stm","vstr")):
   stores.append(rec)
 if not any(x["VM"]=="0x63230" and "[r8, #0x278]" in x["args"] for x in registry):
  raise ValueError("G185 native +0x278 group reader missing")
 if not any(x["VM"]=="0x63714" and "[r0, #0x278]" in x["args"] for x in registry):
  raise ValueError("G185 final native 2010 group array member access missing")
 report={
  "origin":"2010 original user-owned iOS ARM Mach-O no proprietary bytes released",
  "original_scene_collect_method_VM":"0x62ea4",
  "registration_range_original_ARM_VMs":["0x63108","0x63714"],
  "original_registration_opcode_rows_not_binary":registry,
  "original_direct_CPP_calls_in_registration":calls,
  "original_branches_in_registration":branches,
  "original_native_memory_stores_in_registration":stores,
  "native_original_shared_group_pattern_global":source,
  "original_individual_UniBeam_group_selector_indices":[14,33],
  "native_original_scene_group_array_offset":0x278,
  "registered_scene_group14_true_named_dummy_proven":False,
  "registered_scene_group33_true_named_dummy_proven":False,
  "pattern_table_direct_association_with_dummy_group_idx14_33_proven":False,
  "BDAE_node_parser_ordinal_equal_to_scene_group_index_proven":False,
  "requires_original_runtime_GetDummyName_or_full_initializer_trace":True,
  "original_2010_original_IPA_asset_written_to_repo":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G185 Native original 2010 registry range",len(registry),
       "source opcodes",len(stores),"stores",len(calls),"calls",
       "PIC global",source,"nearby symbol",nearest[:8],flush=True)
 for row in registry:
  print("G185 2010 REGISTER",row["VM"],row["mnemonic"],row["args"])
 for row in calls:
  print("G185 REGISTRATION CALL",row["VM"],row["native_real_names"])
 print("G185 native 14/33 author original names UNPROVEN, NO VPK")
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--ipa",required=True,type=Path)
 ap.add_argument("--out",required=True,type=Path)
 a=ap.parse_args()
 main(a.ipa,a.out)
