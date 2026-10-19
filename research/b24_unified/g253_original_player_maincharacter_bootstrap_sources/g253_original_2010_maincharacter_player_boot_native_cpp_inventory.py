#!/usr/bin/env python3
"""G253 find authentic original 2010 iOS MainCharacter & GS_GamePlay
initial actor creation/position functions using 65500 symbol MachO.
Bounded disassembly emits original native call metadata for candidate
constructor/Init/LoadFromFile/SetPosition. No bootstrap position guessed.
"""
from __future__ import annotations
import argparse,bisect,collections,hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM, ARM_INS_BL, ARM_INS_BLX
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

NAME_RE=re.compile(r"^(MainCharacter|GS_GamePlay|Actor|SceneImpl|Entity3D)::")
BOOT_RE=re.compile(r"(?:\bInit\b|\bDoInit|\bLoad(?:FromFile|Entities)?\b|Spawn|Start|Create|SetPos|SetPosition|SetTransform|MoveTo|Restore|Reset|Constructor|MainCharacter::MainCharacter|GS_GamePlay::GS_GamePlay)",re.I)
def run(ipa:Path,g252:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("G253 not original 2010 IPA size")
 with zipfile.ZipFile(ipa) as z:exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("G253 original iOS executable size drift")
 prior=json.loads(g252.read_text())
 if prior["actual_original_class71_branch_target_VM"]!="0xc3538" or prior["source_original_Mission000_OnStart_direct_SpawnPoint_refs"]!=0:
  raise ValueError("G253 requires real G252 SpawnPoint not native player start inference")
 macho=parse_macho(exe)
 if macho["nsyms"]!=65500:raise ValueError("original source C++ count drift")
 syms=macho["entries"]
 dem=subprocess.run(["c++filt"],input="\n".join(s[0] for s in syms)+"\n",
   capture_output=True,text=True,check=True).stdout.splitlines()
 if len(dem)!=len(syms):raise ValueError("C++ symbol table drift")
 labelmap=collections.defaultdict(set);isamap=collections.defaultdict(set)
 for s,name in zip(syms,dem):
  addr=s[1]&~1
  labelmap[addr].add(name)
  isamap[addr].add("thumb" if s[1]&1 else "arm")
 source_boot=[]
 all_character=[]
 for addr,labels in labelmap.items():
  for name in labels:
   if name.startswith("MainCharacter::"):all_character.append({"VM":hex(addr),"cpp":name})
   if NAME_RE.search(name) and BOOT_RE.search(name):
    source_boot.append((addr,name))
 source_boot=sorted(set(source_boot))
 all_character.sort(key=lambda x:x["VM"])
 if len(all_character)<20 or len(source_boot)<15:
  raise ValueError("too few original 2010 MainCharacter/GS_GamePlay bootstrap candidates")
 textsec=[s for s in macho["sections"] if s[3]=="__text"]
 starts=sorted(addr for addr in labelmap if any(s[0]<=addr<s[0]+s[1] for s in textsec))
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 for machine in (arm,thumb):machine.detail=True
 rows=[]
 for addr,name in source_boot:
  section=next((s for s in textsec if s[0]<=addr<s[0]+s[1]),None)
  if section is None:continue
  if len(isamap[addr])!=1:continue
  idx=bisect.bisect_right(starts,addr)
  stop=starts[idx] if idx<len(starts) else section[0]+section[1]
  length=min(6144,stop-addr,section[0]+section[1]-addr)
  if length<4:continue
  off=section[2]+addr-section[0]
  cs=thumb if "thumb" in isamap[addr] else arm
  direct=[]
  for ins in cs.disasm(exe[off:off+length],addr):
   if ins.id not in (ARM_INS_BL,ARM_INS_BLX) or not ins.operands or ins.operands[0].type!=ARM_OP_IMM:continue
   target=ins.operands[0].imm&~1
   tgt_names=sorted(labelmap.get(target,()))[:5]
   if len(direct)<110:
    direct.append({"original_VM":hex(ins.address),"target_VM":hex(target),
        "source_CPP_target_names":tgt_names})
  rows.append({"actual_original_cpp_source_name":name,
     "original_native_VM":hex(addr),
     "native_ISA":next(iter(isamap[addr])),
     "method_source_scan_bytes":length,
     "source_direct_calls_truncated_to_110":len(direct)>=110,
     "source_true_direct_BL_BLX_calls":direct,
     "original_live_player_world_transform_confirmed":False})
 if not rows:raise ValueError("original 2010 candidate native source decode failure")
 reports={
  "source":"G253 genuine original user-owned iOS 2010 MachO MainCharacter GS_GamePlay Actor SceneImpl bootstrap source methods",
  "source_original_MachO_SHA256":hashlib.sha256(exe).hexdigest(),
  "actual_original_maincharacter_all_named_cpp_methods":all_character,
  "original_bootstrap_function_candidate_source_direct_calls":rows,
  "source_CPP_bootstrap_candidates_total":len(rows),
  "source_cpp_spawnpoint_constructor_native_class71_confirmed":True,
  "genuine_2010_Player_start_World_XYZ_or_SpawnPoint_association_proven":False,
  "original_iOS_MainCharacter_runtime_initialization_executed":False,
  "Vita_source_physics_render_animation_or_mission_mutated":False,
  "VPK":False,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(reports,indent=2,ensure_ascii=False)+"\n")
 print("G253 native original MainCharacter method labels",len(all_character))
 for item in all_character[:110]:print("G253 ORIGINAL MainCharacter CPP",item)
 print("G253 genuine original player/scene init candidate methods",len(rows))
 for item in rows:
  print("G253 original 2010 BOOT CPP",item["actual_original_cpp_source_name"],item["original_native_VM"],"CALLS",len(item["source_true_direct_BL_BLX_calls"]))
  interesting=[c for c in item["source_true_direct_BL_BLX_calls"]
    if any(re.search("Position|Transform|MainCharacter|Spawn|LoadFromFile|Camera|Actor",nm,re.I)
      for nm in c["source_CPP_target_names"])]
  for c in interesting[:16]:print("G253 ORIGINAL potential actor/transform native call",c)
 print("G253 PASS source mapping real 2010 native player bootstrap candidates; real mission player start NOT INFERRED NO VPK")
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--ipa",type=Path,required=True)
 a.add_argument("--g252",type=Path,required=True)
 a.add_argument("--out",type=Path,required=True)
 q=a.parse_args()
 run(q.ipa,q.g252,q.out)
