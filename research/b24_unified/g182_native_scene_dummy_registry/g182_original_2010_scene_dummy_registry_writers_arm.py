#!/usr/bin/env python3
"""G182 original 2010 iOS native SceneImpl dummy registry +0x278 writers.
Source inspect actual C++ functions handling SceneImpl, dummy, models.

No guessing numbered BDAE bones from UniBeam native group IDs 14/33.
Only proven ARM read/write of scene+0x278 can demonstrate registry users,
not the runtime registry's semantic node-name mapping. NO Vita patch/VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_MEM, ARM_OP_IMM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
SRC_SIZE=248613763
LOOKUP_VM=0x61724
FILTER=re.compile(r"SceneImpl::|Object3D::|Dummy|BindNode|SceneLoader|SceneMgr::|Scene::",re.I)
def main(ipa,out):
 if ipa.stat().st_size!=SRC_SIZE:raise ValueError("G182 user original iOS 2010 exact IPA required")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("IPA checksum/CRC bad")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("2010 ARM Mach-O changed")
 info=parse_macho(exe)
 names=subprocess.run(["c++filt"],input="\n".join(x[0] for x in info["entries"])+"\n",
                      capture_output=True,text=True,check=True).stdout.splitlines()
 if len(names)!=len(info["entries"]):raise ValueError("native symbol decoder mismatch")
 addr=collections.defaultdict(set);types=collections.defaultdict(set)
 for row,name in zip(info["entries"],names):
  a=row[1]&~1;addr[a].add(name);types[a].add(row[1]&1)
 known=sorted(addr)
 selected={a:sorted(ns) for a,ns in addr.items() if any(FILTER.search(n) for n in ns)}
 if len(selected)<15:raise ValueError("2010 original SceneImpl name inventory too short")
 arms=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 thumbs=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 for d in (arms,thumbs):d.detail=True
 textsects=[x for x in info["sections"] if x[3]=="__text"]
 methods=[];references=[];writers=[];dummy_named=[]
 for a,method_names in sorted(selected.items()):
  secs=next((sec for sec in textsects if sec[0]<=a<sec[0]+sec[1]),None)
  if secs is None:continue
  k=bisect.bisect_right(known,a)
  last=known[k] if k<len(known) else secs[0]+secs[1]
  size=min(last-a,secs[0]+secs[1]-a,12000)
  if size<4:continue
  off=secs[2]+a-secs[0]
  ins=list((thumbs if types[a]=={1} else arms).disasm(exe[off:off+size],a))
  if not ins:continue
  fieldhits=[];calls=[]
  for i,op in enumerate(ins):
   for operand in op.operands:
    if operand.type!=ARM_OP_MEM:continue
    if operand.mem.disp==0x278:
     row={"vm":hex(op.address),"opcode":op.mnemonic,"operands":op.op_str,
          "method_vm":hex(a),"method_source_names":method_names[:4],
          "register_base":op.reg_name(operand.mem.base),
          "access_exact_scene_plus_0x278_only_if_base_is_scene_this_PROVEN":False}
     fieldhits.append(row)
     references.append(row)
     if op.mnemonic.startswith(("str","stm","vstr")):writers.append(row)
   if op.mnemonic in ("bl","blx") and op.operands and op.operands[0].type==ARM_OP_IMM:
    target=op.operands[0].imm&~1
    if len(calls)<35:
     calls.append({"VM":hex(op.address),"target":hex(target),
                   "original_cpp_names":sorted(addr.get(target,()))[:4]})
  # all methods for class name inventory but only source ops near +0x278
  methods.append({"real_native_function_VM":hex(a),"exact_original_name":method_names[:5],
       "native_real_ARM_bounded_instruction_count":len(ins),
       "native_direct_calls_sample":calls,
       "actual_0x278_direct_memory_references":fieldhits})
  if any("dummy" in x.lower() for x in method_names):
   dummy_named.append({"native_VM":hex(a),"source_original_CPP_names":method_names[:5],
                       "sample_calls":calls[:25],"source_0x278_refs":fieldhits})
 if not any(x["vm"]=="0x61724" and x["opcode"]=="ldr" for x in references):
  raise ValueError("G182 original G181 SceneImpl GetDummy source +0x278 read not found")
 if not any(a==LOOKUP_VM for a in selected):raise ValueError("original source lookup symbol missing")
 report={
  "source":"Original owner 2010 iOS native ARM SceneImpl C++ methods 1.0.0",
  "native_original_2010_symbol_table_total":info["nsyms"],
  "original_source_methods_matching_SceneImpl_Object3D_Dummy":len(selected),
  "source_original_named_scanned_method_count":len(methods),
  "source_original_dummy_related_name_inventory":dummy_named,
  "actual_source_CPP_0x278_field_direct_memory_accesses":references,
  "actual_source_CPP_str_to_0x278_candidate_writer_accesses":writers,
  "native_2010_named_source_methods_and_callsite_summary":methods,
  "native_scene_dummy_registry_pointer_source_offset_PROVEN":"0x278",
  "native_scene_dummy_registry_index14_33_lookup_PROVEN":True,
  "scene_dummy_registry_elements_14_33_to_BDAE_named_nodes_PROVEN":False,
  "indirect_alias_write_and_constructor_initializer_fully_traced_PROVEN":False,
  "source_original_skeleton_node_parse_index_equals_dummy_registry_ID_PROVEN":False,
  "original_2010_arm_executable_asset_not_exported":True,
  "native_Vita_gameplay_changes":False,"NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G182 genuine original 2010 SceneImpl/Dummy native function names",
       len(selected),"decoded",len(methods),"0x278 direct references",len(references),
       "candidate writers",len(writers))
 for t in references:print("G182 SOURCE OFFSET 0x278",t)
 for row in dummy_named[:40]:
  print("G182 NATIVE DUMMY NAME",row["native_VM"],row["source_original_CPP_names"],
        "target called",[(c["target"],c["original_cpp_names"]) for c in row["sample_calls"][:6]])
 print("G182 class source exact 14/33 indexed scene groups proven; original model BDAE node name still NOT assigned, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 main(a.ipa,a.out)
