#!/usr/bin/env python3
"""G183: original 2010 iOS named dummy registrar and name resolver.
Source native ARM / owner game ONLY. Determine how SceneImpl::CollectDummies
touches its +0x278 dummy groups, and how Object3D::GetDummyName queries
SceneImpl. No arbitrary 14/33 bone name assignments or Vita VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,subprocess,sys,zipfile,re
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM,ARM_OP_MEM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

ORIGINAL_SIZE=248613763
TARGETS={
 "Object3D_GetDummyName":("Object3D::GetDummyName(int, int)",0x15894),
 "SceneImpl_CollectDummies":("SceneImpl::CollectDummies(irr::scene::ISceneNode*)",0x62ea4),
 "SceneImpl_Initialize":("SceneImpl::Initialize(char const*)",0x67150),
 "SceneImpl_Constructor":("SceneImpl::SceneImpl(SceneMgr*, irr::scene::ISceneNode*)",0x65374),
 "SceneImpl_UpdateDummies":("SceneImpl::UpdateDummies(irr::core::vector3d<float> const&)",0x61da0),
 "SceneImpl_GetDummy":("SceneImpl::GetDummy(int, unsigned int)",0x61724),
}
def run(ipa,out):
 if ipa.stat().st_size!=ORIGINAL_SIZE:raise ValueError("g183 require owner original 2010 IPA")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("original iOS IPA CRC fail")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("g183 unexpected original MachO length")
 native=parse_macho(exe)
 names=subprocess.run(["c++filt"],input="\n".join(s[0] for s in native["entries"])+"\n",
                      capture_output=True,text=True,check=True).stdout.splitlines()
 if len(names)!=len(native["entries"]):raise ValueError("source original demangle mismatch")
 byaddr=collections.defaultdict(set);isa=collections.defaultdict(set)
 for row,name in zip(native["entries"],names):
  a=row[1]&~1;byaddr[a].add(name);isa[a].add(row[1]&1)
 for key,(label,addr) in TARGETS.items():
  if label not in byaddr[addr]:raise ValueError(f"g183 original named C++ source drift {key}: {hex(addr)}")
 keys=sorted(byaddr)
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 for d in (arm,thumb):d.detail=True
 secs=[s for s in native["sections"] if s[3]=="__text"]
 output={}
 for key,(label,addr) in TARGETS.items():
  sec=next((s for s in secs if s[0]<=addr<s[0]+s[1]),None)
  if sec is None:raise ValueError(f"g183 {key} not in __text")
  nextidx=bisect.bisect_right(keys,addr)
  right=keys[nextidx] if nextidx<len(keys) else sec[0]+sec[1]
  size=min(right-addr,sec[0]+sec[1]-addr,14000)
  if size<12:raise ValueError(f"g183 original C++ owner method truncated: {key}")
  ofs=sec[2]+addr-sec[0]
  code=list((thumb if isa[addr]=={1} else arm).disasm(exe[ofs:ofs+size],addr))
  if not code:raise ValueError("g183 source disasm empty "+key)
  assembly=[{"VM":hex(i.address),"opcode":i.mnemonic,"args":i.op_str} for i in code]
  direct=[];member=[];near=[]
  for k,ins in enumerate(code):
   for op in ins.operands:
    if op.type==ARM_OP_MEM and op.mem.disp==0x278:
     member.append({"instruction_VM":hex(ins.address),"mnemonic":ins.mnemonic,
       "op_args":ins.op_str,"base_register":ins.reg_name(op.mem.base)})
     near.extend(assembly[max(0,k-10):min(len(assembly),k+11)])
   if ins.mnemonic in ("bl","blx") and ins.operands and ins.operands[0].type==ARM_OP_IMM:
    target=ins.operands[0].imm&~1
    direct.append({"call_VM":hex(ins.address),"callee_VM":hex(target),
       "actual_native_cpp_symbol":sorted(byaddr.get(target,()))[:4]})
  head=assembly[:120]
  # Source metadata may include full bounded method. This is original 
  # arm assembly, not binary bytes. Limit large output to 1200 opcodes.
  output[key]={
   "original_native_name":label,"VM":hex(addr),"bounded_ARM_bytes":size,
   "authored_2010_source_ARM_instruction_count":len(code),
   "actual_direct_native_calls":direct[:350],
   "native_memory_offset_0x278_occurrences":member,
   "original_source_opcode_head_no_binary_bytes":head,
   "original_source_opcode_0x278_context_no_binary_bytes":near[:550],
   "source_dummy_name_from_static_model_index14_33_PROVEN":False,
  }
 if not any(c["callee_VM"]=="0x61724" for c in output["Object3D_GetDummyName"]["actual_direct_native_calls"]):
  raise ValueError("G183 original native GetDummyName->SceneImpl GetDummy not proved")
 if len(output["SceneImpl_CollectDummies"]["native_memory_offset_0x278_occurrences"])<1:
  raise ValueError("G183 original dummy collector does not reference authentic registry")
 doc={
  "source":"Original owner 2010 iOS ARM native SceneImpl dummy name and collection code",
  "original_class_methods":output,
  "source_2010_GetDummyName_dynamically_calls_SceneImpl_GetDummy":True,
  "source_2010_SceneImpl_CollectDummies_references_registry_0x278":True,
  "source_2010_Native_RegistryGroup14_or33_to_actual_dummy_name_PROVEN":False,
  "source_2010_which_animation_dummy_is_chest_and_missile_PROVEN":False,
  "source_2010_Vita_unibeam_emitter_or_Actor_modified":False,
  "NO_ORIGINAL_IPA_OR_BDAE_BYTES_PUBLISHED":True,"NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n")
 for key,v in output.items():
  print("G183 ORIGINAL 2010 NATIVE",key,v["VM"],"instructions",v["authored_2010_source_ARM_instruction_count"],
        "native calls",len(v["actual_direct_native_calls"]),"offset278",len(v["native_memory_offset_0x278_occurrences"]))
  for a in v["actual_direct_native_calls"][:65]:
   if key in ("Object3D_GetDummyName","SceneImpl_CollectDummies"):
    print("G183 NATIVE CALL",key,a)
  for a in v["native_memory_offset_0x278_occurrences"]:
   print("G183 REAL DUMMY FIELD",key,a)
  if key in ("Object3D_GetDummyName","SceneImpl_CollectDummies"):
   for a in v["original_source_opcode_head_no_binary_bytes"][:90]:
    print("G183 NATIVE ARM",key,a)
 print("G183 exact source API leads to named original dummy at runtime, but id14/33 to BDAE mapping not yet proven; no VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args()
 run(a.ipa,a.out)
