#!/usr/bin/env python3
"""Extract bounded original user-owned 2010 ARM native NPC state checks,
MissionConditionKill update and GS_GamePlay::UpdateSkyBox branches.
The ONLY intended next step: source faithful implementation of small
actually proven conditions; DO NOT assume 2010 whole AI recreated.
Uses source-owner original Mach-O in ephemeral CI, no IPA, no VPK.
"""
import argparse,bisect,collections,json,re,subprocess,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
import capstone
TARGETS={
 "CNPC::isAttackState()":160,
 "CNPC::isMelee()":100,
 "CNPC::isInState(int, int)":180,
 "CNPC::shootFrequencyDone()":140,
 "CNPC::SetState(int, int)":140,
 "CNPC::pushState(int, int, long, void*, int)":100,
 "CNPC::UpdateStateCheckFire(int, CNPC::NPCStateNode&)":200,
 "MissionConditionKill::EvaluateComplete(int)":240,
 "MissionConditionKill::GetStatistic(int&, int&)":160,
 "MissionConditionKill::Init()":100,
 "GS_GamePlay::UpdateSkyBox(int)":220,
}
def run(ipa,out):
 if ipa.stat().st_size!=248613763:raise ValueError("verified user original 2010 IPA")
 with zipfile.ZipFile(ipa) as z:binary=z.read("Payload/IronMan2.app/IronMan2")
 m=parse_macho(binary)
 names=[q[0] for q in m["entries"]]
 dem=subprocess.run(["c++filt"],input="\n".join(names)+"\n",text=True,
   capture_output=True,check=True).stdout.splitlines()
 assert len(dem)==len(names)
 rows=list(zip(m["entries"],dem))
 sections=[x for x in m["sections"] if x[3]=="__text"]
 raw_addr=sorted(set(q[0][1]&~1 for q in rows))
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 report={}
 for target,count in TARGETS.items():
  possible=[a for a,n in rows if n==target]
  if not possible:raise ValueError("No original native C++ target symbol "+target)
  addresses=sorted(set(a[1]&~1 for a in possible))
  entries=[]
  for addr in addresses:
   sec=next((s for s in sections if s[0]<=addr<s[0]+s[1]),None)
   if sec is None:continue
   end=raw_addr[bisect.bisect_right(raw_addr,addr)] if bisect.bisect_right(raw_addr,addr)<len(raw_addr) else sec[0]+sec[1]
   size=min(end-addr,count*4,sec[0]+sec[1]-addr)
   if size<=0:continue
   off=sec[2]+addr-sec[0]
   row=next(a for a in possible if (a[1]&~1)==addr)
   instructions=list((thumb if row[1]&1 else arm).disasm(binary[off:off+size],addr))
   if not instructions:continue
   outasm=[]
   for ins in instructions[:count]:
    if ins.mnemonic.startswith("v") and ins.mnemonic not in ("vldr","vstr"):continue
    outasm.append({"source_original_arm_pc_hex":hex(ins.address),
                   "original_instruction":ins.mnemonic,
                   "register_immediate_or_branch":ins.op_str,
                   "native_iOS_original_source_not_B24":True})
   entries.append({"native_vm_hex":hex(addr),"native_thumb":bool(row[1]&1),
     "actual_owner_function_span_until_next_native_symbol_bytes":end-addr,
     "bounded_instructions":outasm,
     "full_native_method_reconstructed":False})
  if not entries:raise ValueError("Original ARM target has no decoded instructions "+target)
  report[target]=entries
 out.mkdir(parents=True,exist_ok=True)
 j={"source_user_2010_iOS_own_Arm_MachO":True,
     "original_binary_architecture":"ARM native executable (not homebrew reconstructed)",
     "bounded_original_class_method_provenance":report,
     "original_CNPC_full_AI_gameplay_state_machine_ported":False,
     "original_mission_system_restored":False,
     "source_GL_sky_shader_parity_recreated":False,
     "new_vpk_created":False}
 (out/"G123_REAL_2010_NPC_CONDITIONS_MISSIONKILL_SKYBOX_ARM_NATIVE_SOURCE_BRANCHES.json").write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
 for method,variants in report.items():
  print("\nG123 OWNER ORIGINAL 2010 ARM",method)
  for v in variants:
   print("G123 ADDRESS",v["native_vm_hex"],"source bounded function bytes",v["actual_owner_function_span_until_next_native_symbol_bytes"])
   for ins in v["bounded_instructions"][:105]:
    print("G123 DISASSEMBLY",ins["source_original_arm_pc_hex"],ins["original_instruction"],ins["register_immediate_or_branch"])
 print("G123 source only, ARM small predicate evidence, no NPC AI guess, no VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();run(a.ipa,a.out)
