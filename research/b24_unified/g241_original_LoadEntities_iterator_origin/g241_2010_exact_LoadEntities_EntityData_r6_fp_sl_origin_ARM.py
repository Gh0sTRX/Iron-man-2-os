#!/usr/bin/env python3
"""G241 original 2010 iOS GS_GamePlay::LoadEntities EntityData iterator
and true class-dispatch ARM/Thumb native neighborhoods. Does NOT assign
file order to runtime WeaponDB index. Only publishes opcode metadata
and exact original C++ symbols. Read-only, no game engine changes/VPK.
"""
from __future__ import annotations
import argparse,bisect,hashlib,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
VM=0xc2e8c
LOOP=0xc2eb8
LOOP_CONT=0xc32d0
CALLS={0xc365c:0xabbd4,0xc3678:0xabf14,0xc3694:0xab894}
CPP="GS_GamePlay::LoadEntities()"
WINDOWS={
 "entry_and_iterator_start":(0xc2e8c,0xc2fc8),
 "shared_iterator_restart":(0xc2eb0,0xc3030),
 "end_iterator_or_switch_source":(0xc31e0,0xc33b0),
 "type_dispatch_tail":(0xc3460,0xc36ac),
}
def opinfo(op,names):
 d={"vm":hex(op.address),"mnemonic":op.mnemonic,"args":op.op_str}
 if op.mnemonic.startswith(("bl","blx")) and op.operands and op.operands[0].type==ARM_OP_IMM:
  d["source_direct_BL_target_VM"]=hex(op.operands[0].imm&~1)
  d["source_exact_Cpp_labels"]=sorted(names.get(op.operands[0].imm&~1,()))[:3]
 return d
def run(ipa:Path,g240:Path,out:Path):
 if ipa.stat().st_size!=248613763:raise ValueError("source IPA mismatch")
 with zipfile.ZipFile(ipa) as z:
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("source executable size mismatch")
 source=parse_macho(exe)
 if source["nsyms"]!=65500:raise ValueError("native original 2010 nsyms drift")
 syms=source["entries"]
 text=subprocess.run(["c++filt"],input="\n".join(r[0] for r in syms)+"\n",capture_output=True,text=True,check=True).stdout.splitlines()
 if len(syms)!=len(text):raise ValueError("original native symbol count and demangler disagree")
 labels={}
 for s,name in zip(syms,text):
  labels.setdefault(s[1]&~1,set()).add(name)
 if CPP not in labels.get(VM,()):raise ValueError("2010 native LoadEntities exact C++ method mismatch")
 parent=json.loads(g240.read_text())
 if (parent.get("true_original_native_method_VM")!=hex(VM) or
     not parent.get("source_original_three_typed_AddNew_share_iteration_backedge_0xC2EB8")):
  raise ValueError("G241 requires independently successful G240 true source audit")
 sec=next((s for s in source["sections"] if s[3]=="__text" and s[0]<=VM<s[0]+s[1]),None)
 if not sec:raise ValueError("original __text method disappeared")
 starts=sorted(a for a in labels if sec[0]<=a<sec[0]+sec[1])
 ix=bisect.bisect_right(starts,VM)
 end=starts[ix] if ix<len(starts) else sec[0]+sec[1]
 if not 0<end-VM<14000 or end<max(CALLS)+16:raise ValueError("LoadEntities authentic source function bounds drift")
 fileoff=sec[2]+VM-sec[0]
 cs=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 cs.detail=True
 ops=list(cs.disasm(exe[fileoff:fileoff+end-VM],VM))
 byaddr={o.address:o for o in ops}
 for site,target in CALLS.items():
  o=byaddr.get(site)
  if o is None or o.mnemonic!="bl" or not o.operands or o.operands[0].type!=ARM_OP_IMM or (o.operands[0].imm&~1)!=target:
   raise ValueError(f"G241 2010 type switch callsite changed @{site:#x}")
  for shift,opcode,arg in [(-8,"add","sl, sl, #1"),(-4,"mov","r1, r6"),(8,"bne","#0xc2eb8"),(12,"b","#0xc32d0")]:
   q=byaddr.get(site+shift)
   if not q or (q.mnemonic,q.op_str)!=(opcode,arg):
    raise ValueError(f"G241 no source true loop return @{site+shift:#x}")
 # Enumerate direct/writer instructions in the ORIGINAL method, but
 # be conservative: a textual writer is not a proven reaching definition.
 writes=[]
 for op in ops:
  if op.mnemonic.startswith(("cmp","tst","str","b","stm","push","svc")):
   continue
  lhs=op.op_str.split(",",1)[0].strip()
  if lhs in ("r6","fp","sl"):
   writes.append(opinfo(op,labels))
 resultwindows=[]
 for title,(a,z) in WINDOWS.items():
  sectionops=[opinfo(op,labels) for op in ops if a<=op.address<=z]
  if len(sectionops)<8:raise ValueError(f"G241 original method insufficient source code {title}")
  resultwindows.append({"source_native_region_name":title,"authentic_original_first_VM":hex(a),
       "authentic_original_last_VM":hex(z),
       "original_native_ARM_opcode_metadata":sectionops,
       "source_instructions_are_static_NOT_observed_runtime":True})
 hits=[opinfo(op,labels) for op in ops if op.mnemonic.startswith(("bl","blx"))
       and op.operands and op.operands[0].type==ARM_OP_IMM]
 result={
  "source":"G241 actual 2010 original owner MachO GS_GamePlay::LoadEntities exact ARM code source-only",
  "true_original_ARM_method_VM":hex(VM),
  "original_method_cpp_name":CPP,
  "original_binary_MachO_SHA256":hashlib.sha256(exe).hexdigest(),
  "original_loadentities_native_instruction_count":len(ops),
  "original_loadentities_native_bytes":end-VM,
  "source_authentic_ARM_iterator_loop_start_VM":hex(LOOP),
  "source_authentic_ARM_iterator_postloop_VM":hex(LOOP_CONT),
  "source_authentic_2010_native_r6_fp_sl_candidate_writes":writes,
  "original_native_iterate_and_type_switch_source_windows":resultwindows,
  "original_native_direct_calls_in_LoadEntities_source_only":hits,
  "three_AddNew_arm_calls_share_one_native_iterator":True,
  "native_ARM_r6_reaching_definition_across_all_paths_PROVEN":False,
  "actual_2010_C1L1_runtime_EntityData_list_order_PROVEN":False,
  "actual_2010_WeaponDB_array_entries_0_1_4_names_PROVEN":False,
  "source_input_damage_or_in_game_WeaponDB_modified":False,
  "source_generated_VPK":False,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
 print("G241 true original native LoadEntities",len(ops),"instructions",end-VM,"bytes")
 for q in writes[:80]:
  print("G241 SOURCE R6/SL/FP WRITER CANDIDATE",q)
 for w in resultwindows:
  print("G241 ORIGINAL WINDOW",w["source_native_region_name"],"opcode count",len(w["original_native_ARM_opcode_metadata"]))
  for v in w["original_native_ARM_opcode_metadata"][:125]:
   print("G241 ORIGINAL ARM",w["source_native_region_name"],v)
 print("G241 PASS actual original GS_GamePlay::LoadEntities loop/source only; no fake WeaponDB index/order/VPK")
 return result
if __name__=="__main__":
 a=argparse.ArgumentParser()
 a.add_argument("--ipa",required=True,type=Path)
 a.add_argument("--g240",required=True,type=Path)
 a.add_argument("--out",required=True,type=Path)
 q=a.parse_args()
 run(q.ipa,q.g240,q.out)
