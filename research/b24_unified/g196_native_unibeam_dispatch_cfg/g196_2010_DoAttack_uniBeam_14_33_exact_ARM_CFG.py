#!/usr/bin/env python3
"""G196 real original iOS 2010 MainCharacter::DoAttack(int,int) ARM
control-flow guard analysis for three genuine BL DoUniBeamAttack sites.

Native evidence IDs:
  0xf6638: MOV r1,#14 -> DoUniBeamAttack
  0xf6d8c: MOV r1,#14 -> DoUniBeamAttack
  0xf6e04: MOV r1,#33 -> DoUniBeamAttack

Analyze actual ARM comparison/control branches and local CFG, preserving
uncertainty about original weapon selector and game mode state. Only source
opcode metadata and a real-source CFG screenshot; NO VPK or Vita patch.
"""
from __future__ import annotations
import argparse,bisect,collections,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
OWNER=248613763
FN=0xf64f8
UNI=0xf60ac
CASES={0xf6638:(14,0xf662c),0xf6d8c:(14,0xf6d74),0xf6e04:(33,0xf6de4)}
def main(ipa:Path,out:Path,png:Path):
 if ipa.stat().st_size!=OWNER:raise ValueError("owner iOS original 2010 size changed")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("original IPA CRC fail")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("source MachO mismatch")
 native=parse_macho(exe)
 names=subprocess.run(["c++filt"],input="\n".join(x[0] for x in native["entries"])+"\n",capture_output=True,check=True,text=True).stdout.splitlines()
 if len(names)!=len(native["entries"]):raise ValueError("source C++ table bad")
 symbol=collections.defaultdict(set)
 for raw,name in zip(native["entries"],names):symbol[raw[1]&~1].add(name)
 if "MainCharacter::DoAttack(int, int)" not in symbol[FN]:raise ValueError("native source symbol changed")
 if not any("MainCharacter::DoUniBeamAttack(" in name for name in symbol[UNI]):
  raise ValueError("native source UniBeam callee symbol changed")
 sect=next(s for s in native["sections"] if s[3]=="__text" and s[0]<=FN<s[0]+s[1])
 addrs=sorted(symbol)
 k=bisect.bisect_right(addrs,FN)
 length=min(addrs[k]-FN if k<len(addrs) else sect[1],sect[0]+sect[1]-FN,12000)
 if length<0xf6e04-FN+4:raise ValueError("G196 method truncates 33 call")
 off=sect[2]+FN-sect[0]
 cs=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);cs.detail=True
 ins=list(cs.disasm(exe[off:off+length],FN))
 table={i.address:i for i in ins};sorted_vm=sorted(table)
 if len(ins)<600:raise ValueError("Source native 2010 DoAttack too short")
 originals=[]
 for call,(idx,writer) in CASES.items():
  op=table.get(call);prev=table.get(writer)
  if not op or op.mnemonic!="bl" or op.operands[0].type!=ARM_OP_IMM or (op.operands[0].imm&~1)!=UNI:
   raise ValueError("Source direct CALL divergence "+hex(call))
  if not prev or prev.mnemonic!="mov" or prev.op_str!=f"r1, #{hex(idx) if idx>9 else idx}":
   raise ValueError("original native r1 argument writer divergence "+hex(writer))
  for x in ins:
   if not writer<x.address<call:continue
   if (x.mnemonic in ("bl","blx") or
       (x.op_str.startswith("r1,") and x.mnemonic.startswith(("mov","ldr","add","sub","mvn","and","orr")))):
    raise ValueError("native source argument r1 changed after original MOV "+hex(x.address))
  originals.append({"source_uniBeam_direct_CALL_VM":hex(call),
        "actual_source_native_integer_dummy_group":idx,
        "actual_source_native_group_name":"Dummy_Chest" if idx==14 else "Dummy_Foot_L",
        "actual_source_register_r1_writer_VM":hex(writer)})
 edges=[];branches=[];calls=[];returns=[]
 addresses=set(table)
 for op in ins:
  mn=op.mnemonic.lower().split(".")[0]
  a=op.address
  nxt=a+op.size
  if mn in ("bl","blx"):
   target=op.operands[0].imm&~1 if op.operands and op.operands[0].type==ARM_OP_IMM else None
   calls.append({"site":hex(a),"target":hex(target) if target is not None else None,
     "target_cpp":sorted(symbol.get(target,()))[:3] if target is not None else []})
  # Conservatively ignore internal subroutine return classification except
  # recognized BX lr or POP {..., pc}.
  # ARM native return sequence often includes LDMxx sp!,{pc}.
  is_return=(mn=="bx" and op.op_str.strip()=="lr") or \
            (mn in ("pop","ldm","ldmia") and "pc" in op.op_str and "sp" in op.op_str) or \
            (mn.startswith("ldr") and op.op_str.startswith("pc,"))
  if is_return:
   returns.append({"vm":hex(a),"source_opcode":mn,"operand":op.op_str})
   continue
  direct_branch=(mn.startswith("b") and mn not in ("bl","blx","bic","bfi","bfc","bfx"))
  if direct_branch and op.operands and op.operands[0].type==ARM_OP_IMM:
   target=op.operands[0].imm&~1
   branch={"vm":hex(a),"mnemonic":mn,"target_vm":hex(target),
           "preceding_original_8_opcodes":[
             {"vm":hex(x.address),"mnemonic":x.mnemonic,"args":x.op_str}
             for x in ins[max(0,ins.index(op)-8):ins.index(op)]],
           "target_within_source_method":target in addresses}
   branches.append(branch)
   if target in addresses:edges.append((a,target,"unconditional" if mn=="b" else "conditional_true"))
   if mn=="b":continue
  if nxt in addresses:edges.append((a,nxt,"fallthrough"))
 # Basic predecessor graph for exact callsite. Path existence is only
 # structural, NOT evidence of runtime reachable game/menu branch.
 preds=collections.defaultdict(list)
 for a,b,kind in edges:preds[b].append({"from":a,"kind":kind})
 outputs=[]
 for call,(group,writer) in CASES.items():
  i=sorted_vm.index(call)
  from_128=ins[max(0,i-128):i+1]
  nearby_branches=[b for b in branches if call-600<=int(b["vm"],16)<=call+48]
  closer={x.address:x for x in from_128}
  control=[{"vm":hex(x.address),"opcode":x.mnemonic,"args":x.op_str}
            for x in from_128 if x.mnemonic.startswith(("cmp","tst","teq","cbz","cbnz"))]
  valid_preds=[]
  queue=collections.deque([(call,0)])
  seen={call}
  while queue:
   addr,distance=queue.popleft()
   if distance>=170:continue
   for p in preds.get(addr,()):
    origin=p["from"]
    if origin in seen:continue
    seen.add(origin)
    if p["kind"]=="conditional_true":
     branch=table[origin]
     valid_preds.append({"original_predicate_jump_VM":hex(origin),
       "native_conditional_branch":branch.mnemonic,"native_operands":branch.op_str,
       "depth_instruction_edges_to_UniBeam_call":distance+1})
    queue.append((origin,distance+1))
  outputs.append({
   "actual_original_direct_CALL_VM":hex(call),
   "actual_original_dummy_key":group,
   "source_guard_method_name":"MainCharacter::DoAttack(int, int)",
   "immediate_precall_128_real_ARM_instructions":[
       {"VM":hex(x.address),"opcode":x.mnemonic,"args":x.op_str} for x in from_128],
   "control_flow_compares_in_precall_128":control,
   "source_true_ARM_branch_sites_near_call":nearby_branches,
   "source_direct_reverse_cfg_conditional_edges_reaching_CALL":valid_preds[:90],
   "original_game_state_or_weapon_enum_predicate_semantics_proven":False,
  })
 report={
  "source":"G196 owner original iOS 2010 MainCharacter DoAttack real ARM control flow and authenticated 14/33 call arguments",
  "native_source_method_VM":hex(FN),
  "original_cpp_method":"MainCharacter::DoAttack(int, int)",
  "original_native_source_instruction_count":len(ins),
  "source_original_named_direct_CALL_count":len(calls),
  "source_original_branch_instructions_total":len(branches),
  "source_original_return_sites_total":len(returns),
  "original_unibeam_callsite_14_14_33_in_source":originals,
  "source_real_original_CALL_128_opcode_CFG_context":outputs,
  "source_reachable_start_vs_14_33_runtime_game_state_proven":False,
  "native_real_original_suit_or_weapon_mode_binding_for_foot_L_proven":False,
  "no_forced_override_foot_to_chest_in_Vita":True,
  "NO_NEW_VITA_VFX_DAMAGE_INPUT_PATCH":True,
  "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 import matplotlib
 matplotlib.use("Agg")
 import matplotlib.pyplot as plt
 fig,ax=plt.subplots(figsize=(11,5),dpi=135)
 fig.patch.set_facecolor("#121c2c");ax.set_facecolor("#121c2c");ax.set_axis_off()
 nodes=[("0xF6638","14 — Dummy_Chest"),
       ("0xF6D8C","14 — Dummy_Chest"),("0xF6E04","33 — Dummy_Foot_L")]
 ax.text(.5,.92,"Iron Man 2 (2010) • TRUE SOURCE DoAttack → UniBeam CALLS",
  ha="center",color="white",fontsize=14,transform=ax.transAxes)
 ax.text(.5,.83,"Original native ARM: three distinct CALL sites, same target 0xF60AC",
  ha="center",color="#aabdd6",fontsize=10,transform=ax.transAxes)
 for i,(loc,label) in enumerate(nodes):
  x=.16+.34*i
  ax.text(x,.55,loc+"\n"+label,ha="center",va="center",
     fontsize=12,color="white",transform=ax.transAxes,
     bbox={"facecolor":("#1d6574" if i<2 else "#765329"),"edgecolor":"#a6c0d0","boxstyle":"round,pad=0.65"})
  ax.annotate("",xy=(.5,.28),xytext=(x,.42),xycoords="axes fraction",textcoords="axes fraction",
       arrowprops={"color":"#95aacc","arrowstyle":"->","lw":1.5})
 ax.text(.5,.19,"0xF60AC  MainCharacter::DoUniBeamAttack",ha="center",va="center",
    fontsize=12,color="white",transform=ax.transAxes,
    bbox={"facecolor":"#34485b","edgecolor":"#a6c0d0","boxstyle":"round,pad=0.55"})
 ax.text(.5,.035,"ATTENTION: 14/33 names SOURCE-PROVEN; branch game-state and actual Vita emitter NOT YET PROVEN",
    ha="center",fontsize=9,color="#cbd3e0",transform=ax.transAxes)
 fig.tight_layout()
 png.parent.mkdir(parents=True,exist_ok=True);fig.savefig(png,facecolor=fig.get_facecolor())
 plt.close(fig)
 print("G196 REAL 2010 native DoAttack",len(ins),"ARM instructions",len(branches),"branch instructions")
 for row in outputs:
  print("G196 source native original call",row["actual_original_direct_CALL_VM"],
      "dummy key",row["actual_original_dummy_key"],
      "CFG predecessor candidate conditional edges",len(row["source_direct_reverse_cfg_conditional_edges_reaching_CALL"]))
  for o in row["immediate_precall_128_real_ARM_instructions"][-35:]:
   print("G196 SOURCE PRIOR",row["actual_original_direct_CALL_VM"],o)
 print("G196 created source-only readable PNG original three ARM source calls, NO native gameplay behaviour fabricated, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 p.add_argument("--png",required=True,type=Path)
 args=p.parse_args()
 main(args.ipa,args.out,args.png)
