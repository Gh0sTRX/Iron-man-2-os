#!/usr/bin/env python3
"""G252 original iOS 2010 class-71 SpawnPoint actor role/source ARM:
combine G250 authentic scene/Lua links and GS_GamePlay::LoadEntities
class-71 native dispatch with real Mach-O C++ SpawnPoint symbols.
Source only: direct Lua references are NOT player-start selection;
jump-table target alone does NOT show full runtime semantics.
"""
from __future__ import annotations
import argparse,bisect,collections,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM,ARM_INS_BL,ARM_INS_BLX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
FUNC=0xc2e8c
CLSID=71
ENTRY=0xc2ee0+4*(CLSID-1)
def main(ipa:Path,g250:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("original owner 2010 IPA wrong size")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip() is not None:raise ValueError("owner IPA corrupted")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("original 2010 MachO size drift")
 prev=json.loads(g250.read_text())
 nodes=prev["actual_original_16_source_SpawnPoint_transforms"]
 if len(nodes)!=16 or not prev["original_native_2010_exact_tagged_12_16_12_source_transform"]:
  raise ValueError("G252 requires verified original 16 SpawnPoint data")
 if prev["source_original_all_Lua_CALL_typed_SpawnPoint_node_links_count"]!=24:
  raise ValueError("G252 G250 original source static Lua SpawnPoint site count drift")
 macho=parse_macho(exe)
 sym=macho["entries"]
 dem=subprocess.run(["c++filt"],input="\n".join(row[0] for row in sym)+"\n",
    text=True,capture_output=True,check=True).stdout.splitlines()
 if macho["nsyms"]!=65500 or len(dem)!=len(sym):raise ValueError("original native C++ names drift")
 names=collections.defaultdict(set)
 for s,name in zip(sym,dem):
  names[s[1]&~1].add(name)
 if "GS_GamePlay::LoadEntities()" not in names.get(FUNC,()):
  raise ValueError("true original native game loader missing")
 sec=next((s for s in macho["sections"] if s[3]=="__text" and s[0]<=FUNC<s[0]+s[1]),None)
 if not sec:raise ValueError("native text mapping missing")
 starts=sorted(x for x in names if sec[0]<=x<sec[0]+sec[1])
 nextidx=bisect.bisect_right(starts,FUNC)
 stop=starts[nextidx] if nextidx<len(starts) else sec[0]+sec[1]
 if stop<0xc369c:raise ValueError("loader does not cover previous native Attack branch")
 dis=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);dis.detail=True
 startoff=sec[2]+FUNC-sec[0]
 ops=list(dis.disasm(exe[startoff:startoff+stop-FUNC],FUNC))
 byvm={o.address:o for o in ops}
 native_switch=byvm.get(ENTRY)
 if native_switch is None or native_switch.mnemonic!="b" or not native_switch.operands or native_switch.operands[0].type!=ARM_OP_IMM:
  raise ValueError(f"class71 jump table entry {ENTRY:#x} not a source unconditional ARM B")
 dest=native_switch.operands[0].imm&~1
 if dest not in byvm:raise ValueError("class71 original branch target not in LoadEntities")
 snippet=[o for o in ops if dest-28<=o.address<=dest+124]
 source_ops=[{"native_VM":hex(o.address),"mnemonic":o.mnemonic,"args":o.op_str,
     **({"direct_call_VM":hex(o.operands[0].imm&~1),
         "authentic_Cpp_callee_names":sorted(names.get(o.operands[0].imm&~1,()))[:5]}
        if o.id in (ARM_INS_BL,ARM_INS_BLX) and o.operands and o.operands[0].type==ARM_OP_IMM
        else {})}for o in snippet]
 native_spawns=[
   {"original_CPP_name":name,"original_VM":hex(vm)}
   for vm,entries in names.items() for name in entries if
   "SpawnPoint::" in name or "SpawnPointEntity" in name or "SpawnPointMgr" in name]
 native_spawns.sort(key=lambda item:(item["original_CPP_name"],item["original_VM"]))
 refs=collections.Counter()
 allrefs=[]
 for p in nodes:
  if len(p["matching_native_typed_source_nodes"])!=1 or p["matching_native_typed_source_nodes"][0]["source_cpp_class_ID"]!=71:
   raise ValueError("source scene name did not bind genuine class 71")
  for ref in p["original_C1L1_static_Lua_direct_node_call_mentions"]:
   refs[ref["original_native_global_CALL_name"]]+=1
   allrefs.append({"source_spawn":p["node"],**ref})
 if len(allrefs)!=24:raise ValueError("static source Lua reference count changed")
 report={
  "source":"G252 authentic original 2010 iOS GS_GamePlay::LoadEntities class71 ARM + C1L1 typed spawn nodes and original Lua static uses",
  "2010_owner_MachO_sha256":hashlib.sha256(exe).hexdigest(),
  "genuine_original_cpp_loader":"GS_GamePlay::LoadEntities()",
  "genuine_loader_entry_VM":hex(FUNC),
  "native_original_source_SpawnPoint_class_ID":71,
  "actual_original_class71_jump_table_entry_VM":hex(ENTRY),
  "actual_original_class71_branch_target_VM":hex(dest),
  "actual_native_source_class71_branch_neighborhood":source_ops,
  "original_named_SpawnPoint_Cpp_native_method_symbols":native_spawns,
  "actual_original_Lua_source_spawnpoint_static_call_function_frequency":dict(refs),
  "original_24_typed_SpawnPoint_direct_callback_refs":allrefs,
  "source_original_Mission000_OnStart_direct_SpawnPoint_refs":len(prev["original_Mission000_OnStart_static_typed_SpawnPoint_DIRECT_links"]),
  "source_spawnpoints_typing_and_native_class_branch_proven":True,
  "original_native_spawnpoint_runtime_player_start_route_proven":False,
  "original_native_MainCharacter_initial_world_transform_proven":False,
  "source_Class71_EntityData_load_is_not_PlayerBoot_proven":False,
  "Vita_runtime_world_player_or_combat_changed":False,
  "VPK_produced":False}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print(f"G252 native original C1L1 source class71 B {ENTRY:#x}->{dest:#x}")
 for item in source_ops:print("G252 class71 original ARM",item)
 print("G252 native source method names count",len(native_spawns))
 for item in native_spawns[:60]:print("G252 genuine native SpawnPoint C++",item)
 print("G252 original scene Lua call frequency",dict(refs))
 print("G252 original Mission000 direct 16 spawn names",len(prev["original_Mission000_OnStart_static_typed_SpawnPoint_DIRECT_links"]))
 print("G252 PASS authenticated class71 native switch and original Lua entity roles; player start not guessed, NO VPK")
 return report
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--ipa",required=True,type=Path)
 a.add_argument("--g250",required=True,type=Path)
 a.add_argument("--out",required=True,type=Path)
 q=a.parse_args();main(q.ipa,q.g250,q.out)
