#!/usr/bin/env python3
"""G189 locate TRUE original 2010 iOS ARM direct CALLS into
SceneImpl::DummiesTableCreate(int), DummiesTableAdd(char const*), Destroy().

Recover bounded native ARM caller contexts and actual mapped source literal
candidates; only an actual call chain with deterministic constant strings
and ordering can justify index14/33-to-asset names. Dynamic runtime inputs
cannot be guessed from arbitrary BDAE node order. No IPA/VPK published.
"""
from __future__ import annotations
import argparse,bisect,collections,json,struct,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM,ARM_OP_MEM,ARM_REG_PC
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

SOURCE_SIZE=248613763
TARGETS={
 0x641b4:"SceneImpl::DummiesTableAdd(char const*)",
 0x64684:"SceneImpl::DummiesTableCreate(int)",
 0x61aac:"SceneImpl::DummiesTableDestroy()",
}
def run(ipa:Path,out:Path):
 if ipa.stat().st_size!=SOURCE_SIZE:raise ValueError("2010 owner original iOS IPA required")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("original 2010 owner archive CRC error")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("original Mach-O executable drift")
 native=parse_macho(exe)
 dem=subprocess.run(["c++filt"],input="\n".join(x[0] for x in native["entries"])+"\n",
                    capture_output=True,text=True,check=True).stdout.splitlines()
 if len(dem)!=len(native["entries"]):raise ValueError("native source symbol table parse mismatch")
 names=collections.defaultdict(set)
 for row,label in zip(native["entries"],dem):names[row[1]&~1].add(label)
 for a,n in TARGETS.items():
  if n not in names[a]:raise ValueError("original DummiesTable C++ symbol changed "+hex(a))
 secs=native["sections"]
 text_sections=[s for s in secs if s[3]=="__text"]
 if not text_sections:raise ValueError("no original 2010 ARM code")
 def readvm(a,length):
  sec=next((s for s in secs if s[3] not in ("__common","__bss") and
   s[0]<=a and a+length<=s[0]+s[1]),None)
  if sec is None:return None
  off=sec[2]+a-sec[0]
  if off<0 or off+length>len(exe):return None
  return exe[off:off+length]
 def literal_value(vm):
  d=readvm(vm,4)
  return struct.unpack("<I",d)[0] if d else None
 def source_ascii(vm):
  if not isinstance(vm,int):return None
  b=bytearray()
  for k in range(120):
   raw=readvm(vm+k,1)
   if raw is None:return None
   if raw==b"\0":
    if not 2<=len(b)<120:return None
    try:return b.decode("ascii")
    except UnicodeDecodeError:return None
   if raw[0]<32 or raw[0]>126:return None
   b.append(raw[0])
  return None
 # Scan genuine native ARM code for BL immediate. This excludes unresolved
 # virtual calls and thumb disassembly; report coverage limitations.
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 arm.detail=True
 found=[]
 total=0
 for section in text_sections:
  addr,size,off,_,_=section
  if size<4 or off+size>len(exe):raise ValueError("original ARM section OOB")
  for ins in arm.disasm(exe[off:off+size],addr):
   if ins.mnemonic not in ("bl","blx"):continue
   if not ins.operands or ins.operands[0].type!=ARM_OP_IMM:continue
   dest=ins.operands[0].imm&~1
   if dest not in TARGETS:continue
   found.append((ins.address,dest))
  total+=size
 symbol_addrs=sorted(names)
 report_rows=[]
 for callsite,target in sorted(set(found)):
  k=bisect.bisect_right(symbol_addrs,callsite)-1
  caller_addr=symbol_addrs[k] if k>=0 else 0
  method=sorted(names.get(caller_addr,()))
  src=next((s for s in text_sections if s[0]<=callsite<s[0]+s[1]),None)
  if src is None:continue
  # Window is diagnostic, not reconstructed full CFG; skip any unbacked data
  # or claim the register values reached the call under every code path.
  start=max(src[0],(callsite-120)&~3)
  end=min(src[0]+src[1],callsite+4)
  window=list(arm.disasm(exe[src[2]+start-src[0]:src[2]+end-src[0]],start))
  opcodes=[{"VM":hex(i.address),"opcode":i.mnemonic,"args":i.op_str}
           for i in window[-40:]]
  refs=[]
  for i in window:
   if not i.mnemonic.startswith("ldr"):continue
   mem=[o for o in i.operands if o.type==ARM_OP_MEM and o.mem.base==ARM_REG_PC and o.mem.index==0]
   if len(mem)!=1:continue
   vm=i.address+8+mem[0].mem.disp
   ptr=literal_value(vm)
   if ptr is None:continue
   refs.append({
      "native_source_ldr_VM":hex(i.address),
      "native_literal_pool_VM":hex(vm),
      "native_word_from_initialized_section":hex(ptr),
      "native_immediate_points_at_printable_string":source_ascii(ptr),
      "literal_load_reg":i.reg_name(i.operands[0].reg),
      "STRING_ARGUMENT_REACHES_ACTUAL_CALL_PROVEN":False
   })
  report_rows.append({
    "original_ARM_direct_CALL_VM":hex(callsite),
    "actual_target_source_CPP_function":TARGETS[target],
    "native_direct_CALL_target_VM":hex(target),
    "source_caller_nearest_named_symbol_VM":hex(caller_addr),
    "source_caller_nearest_named_symbol_candidates":method[:7],
    "caller_is_actual_function_boundary_PROVEN":False,
    "source_120_bytes_before_CALL_arm_opcodes_NOT_original_machine_bytes":opcodes,
    "source_PIC_lit_candidates_NOT_proven_args":refs,
    "original_runtime_call_condition_replayed":False,
   })
 counts={name:sum(x["native_direct_CALL_target_VM"]==hex(key)
                  for x in report_rows) for key,name in TARGETS.items()}
 report={
  "origin":"Real owner 2010 1.0.0 native iOS ARM Mach-O __text static callsites",
  "real_original_CPP_target_methods":{hex(a):n for a,n in TARGETS.items()},
  "original_text_sections_ARM_only_scanned_bytes":total,
  "original_named_source_direct_calls":report_rows,
  "original_named_direct_call_count_per_API":counts,
  "actual_dummy14_dummy33_source_names_proven":False,
  "source_CALL_context_literal_candidate_is_verified_runtime_r1_input":False,
  "source_SceneImpl_group_idx_from_DummiesTableAdd_insertion_order_proven":False,
  "source_iOS_original_method_virtual_or_Thumb_dispatch_fully_scanned":False,
  "original_2010_IPA_or_executable_exported":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G189 REAL original 2010 direct DummiesTable Create/Add/Destroy ARM source CALL sites",counts)
 for row in report_rows:
  print("G189 PROVEN native CALL",row["original_ARM_direct_CALL_VM"],
        "→",row["actual_target_source_CPP_function"],
        "nearest caller",row["source_caller_nearest_named_symbol_candidates"])
  for line in row["source_PIC_lit_candidates_NOT_proven_args"][-10:]:
   print("G189 SOURCE PIC candidate",line)
 print("G189 original 2010 SceneImpl DummiesTable source caller discovery completed; dummy14/33 names still not assumed, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 v=p.parse_args()
 run(v.ipa,v.out)
