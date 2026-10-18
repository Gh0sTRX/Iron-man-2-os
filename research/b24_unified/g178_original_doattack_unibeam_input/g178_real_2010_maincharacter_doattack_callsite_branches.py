#!/usr/bin/env python3
"""G178 original owner 2010 iOS MainCharacter::DoAttack(int,int)
native ARM branches before its THREE authentic direct UniBeam call sites.

No assumption first input int is weapon kind, nor actual controller input.
Never publish owner's private executable/IPA. Metadata only, NO VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,subprocess,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

OWNER_SIZE=248613763
NAME="MainCharacter::DoAttack(int, int)"
ADDR=0xF64F8
UNI=0xF60AC
CALLS=(0xF6638,0xF6D8C,0xF6E04)

def analyze(ipa:Path,g175:Path,out:Path):
 if ipa.stat().st_size!=OWNER_SIZE:raise ValueError("G178 genuine 2010 owner IPA length required")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("2010 owner IPA CRC failed")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("2010 original iOS Mach-O changed")
 native=parse_macho(exe)
 rows=native["entries"]
 names=subprocess.run(["c++filt"],input="\n".join(x[0] for x in rows)+"\n",
                      capture_output=True,text=True,check=True).stdout.splitlines()
 if len(names)!=len(rows):raise ValueError("2010 native symbol demangle mismatch")
 found={(a&~1,n) for (_,a,*_),n in zip(rows,names) if n==NAME}
 if (ADDR,NAME) not in found:raise ValueError("G178 missing native MainCharacter DoAttack original symbol")
 graph=json.loads(g175.read_text())
 if not graph["NO_VPK"]:raise ValueError("G178 requires real original G175 ARM proof")
 source_edges=[e for e in graph["source_direct_weapon_animation_related_callsite_evidence"]
               if e["original_caller_address"]==hex(ADDR)
                and e["direct_callee_VM"]==hex(UNI)]
 sites={int(e["original_callsite_VM"],16) for e in source_edges}
 if sites!=set(CALLS):raise ValueError("G178 3 original UniBeam native caller sites changed "+repr(sites))
 sec=next((s for s in native["sections"] if s[3]=="__text"
            and s[0]<=ADDR<s[0]+s[1]),None)
 if not sec:raise ValueError("original DoAttack not in __text")
 addresses=sorted({r[1]&~1 for r in rows})
 i=bisect.bisect_right(addresses,ADDR)
 nxt=addresses[i] if i<len(addresses) else sec[0]+sec[1]
 size=min(nxt-ADDR,sec[0]+sec[1]-ADDR,8192)
 if size<=CALLS[-1]-ADDR+4:raise ValueError("DoAttack actual source method bound truncation")
 start=sec[2]+ADDR-sec[0]
 cs=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);cs.detail=True
 ins=list(cs.disasm(exe[start:start+size],ADDR))
 if not ins:raise ValueError("Native DoAttack disassembly failed")
 for op in ins:
  if op.address in CALLS:
   if not op.mnemonic.startswith(("bl","blx")) or not op.operands or op.operands[0].type!=ARM_OP_IMM or (op.operands[0].imm&~1)!=UNI:
    raise ValueError("G178 source 3 x BL DoUniBeamAttack mismatches")
 windows=[]
 for site in CALLS:
  k=next(i for i,x in enumerate(ins) if x.address==site)
  before=ins[max(0,k-38):k+1]
  branch_sites=[{"arm_VM":hex(x.address),"opcode":x.mnemonic,"args":x.op_str}
                for x in before if x.mnemonic.startswith(("b","cmp","tst","teq"))]
  window={"original_real_owner_DoAttack_callsite_VM":hex(site),
          "confirmed_2010_direct_callee":"MainCharacter::DoUniBeamAttack(int, Actor*, float, float, vector3d const&)",
          "authentic_callsite_previous_38_instructions_NOT_MACHINE_BYTES":[
           {"arm_VM":hex(x.address),"opcode":x.mnemonic,"args":x.op_str} for x in before],
          "native_2010_nearby_control_flow_insns":branch_sites,
          "original_source_first_integer_UniBeam_param_exact_runtime_VALUE_PROVEN":False,
          "source_branch_condition_to_real_controller_event_PROVEN":False}
  windows.append(window)
 calls=[{"source_VM":hex(i.address),"target_VM":hex(i.operands[0].imm&~1),
         "source_op":i.mnemonic}
         for i in ins if i.mnemonic.startswith(("bl","blx")) and
         i.operands and i.operands[0].type==ARM_OP_IMM]
 summary={
  "source":"2010 actual owner original iOS 1.0.0 ARM code disassembled READ-ONLY exact genuine C++ DoAttack method and G175 native CALL edges",
  "source_native_method_NAME":NAME,
  "source_native_method_VM":hex(ADDR),
  "source_native_real_instructions_decoded":len(ins),
  "native_original_method_direct_call_total":len(calls),
  "native_three_original_direct_UniBeam_calls_PROVEN":True,
  "actual_original_UniBeam_callsite_VMs":[hex(i) for i in CALLS],
  "native_callsite_source_context_no_bytes":windows,
  "native_original_DoAttack_method_local_direct_callsite_graph":calls[:180],
  "original_three_UniBeam_runtime_branches_proven":False,
  "original_User_touch_controller_button_or_weapon_enum_proven":False,
  "source_correct_G83_Aim_M_animation_weapon_mapping_PROVEN":False,
  "source_original_first_level_armor_loadout_rule_PROVEN":False,
  "original_iOS_owner_IPA_or_executable_exported":False,
  "no_attack_damage_or_missile_Vita_code_changed":True,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
 print("G178 genuine 2010 DoAttack native ARM",hex(ADDR),
       "instructions",len(ins),"direct calls",len(calls))
 for w in windows:
  print("G178 verified source 2010 original CALL",w["original_real_owner_DoAttack_callsite_VM"],
        "->",hex(UNI))
  for o in w["authentic_callsite_previous_38_instructions_NOT_MACHINE_BYTES"]:
   print("G178 ORIGINAL PRECALL",o["arm_VM"],o["opcode"],o["args"])
 print("G178 exact original weapon-Aim_M/Ui input attack dispatcher mapping UNKNOWN; no VPK")
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--ipa",type=Path,required=True)
 a.add_argument("--g175",type=Path,required=True)
 a.add_argument("--out",type=Path,required=True)
 p=a.parse_args()
 analyze(p.ipa,p.g175,p.out)
