#!/usr/bin/env python3
"""G199 original 2010 iOS MainCharacter::DoAttack int,int indirect
dispatch forensic: source-initialized __DATA,__const method pointer at
0x4BD974 from G198, true adjacent named Itanium C++ vtable symbol,
exact vtable slot/index and other original C++ virtual neighbor methods.

Function pointer exists != runtime call executed. Candidate ARM virtual
dispatch patterns are not proof of original button/weapon semantics.
Only native symbolic metadata, source-offsets and authored static PNG are
exported, not licensed raw executable bytes/IPA or guessed Vita behavior.
"""
from __future__ import annotations
import argparse,bisect,collections,json,re,struct,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_MEM, ARM_OP_IMM, ARM_OP_REG,ARM_REG_PC

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

SIZE=248613763
TARGET=0xf64f8
DATA_SITE=0x4bd974
DOATTACK="MainCharacter::DoAttack(int, int)"

def analyze(ipa:Path,out:Path,png:Path):
 if ipa.stat().st_size!=SIZE:raise ValueError("original 2010 owner iOS 1.0.0 needed")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("owned IPA CRC mismatch")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("native MachO source changed")
 m=parse_macho(exe)
 labels=subprocess.run(["c++filt"],input="\n".join(x[0] for x in m["entries"])+"\n",
                       text=True,capture_output=True,check=True).stdout.splitlines()
 if len(labels)!=len(m["entries"]):raise ValueError("2010 original symbols count mismatch")
 byaddr=collections.defaultdict(set)
 mode=collections.defaultdict(set)
 for raw,name in zip(m["entries"],labels):
  a=raw[1]&~1;byaddr[a].add(name);mode[a].add(raw[1]&1)
 if DOATTACK not in byaddr[TARGET]:raise ValueError("native target DoAttack symbol changed")
 positions=sorted(byaddr)
 section=next((s for s in m["sections"] if s[0]<=DATA_SITE<s[0]+s[1]),None)
 if not section or section[3]!="__const" or section[4]!="__DATA":
  raise ValueError("G198 original pointer isn't in genuine __DATA/__const")
 o=section[2]+DATA_SITE-section[0]
 assert 0<o<len(exe)-4
 value=struct.unpack_from("<I",exe,o)[0]
 if value&~1!=TARGET:raise ValueError("G198 real binary DoAttack pointer source mismatch")
 # Get *source* nearest symbols bracketing this exact initialized word.
 pre=bisect.bisect_right(positions,DATA_SITE)
 before=positions[max(0,pre-22):pre]
 after=positions[pre:pre+16]
 vicinity=[{"vm":hex(a),"offset_from_source_ptr":a-DATA_SITE,
            "cpp_original_native":sorted(byaddr[a])[:8]}
           for a in [*before,*after]]
 possible_vtable=[a for a in before if any(
  n.startswith("vtable for ") for n in byaddr[a])]
 owner=possible_vtable[-1] if possible_vtable else None
 owner_name=sorted(n for n in byaddr[owner] if n.startswith("vtable for ")) if owner is not None else []
 if owner is not None:
  # Itanium ABI c++ vtable: header offset-to-top, RTTI pointer; first
  # virtual function pointer begins 8 bytes from symbol. No assumption
  # that this is a vtable unless genuinely Itanium "vtable for" symbol.
  payload=DATA_SITE-owner
  if payload<8 or payload%4:raise ValueError("original owner vtable slot not aligned")
  slot=(payload-8)//4
 else:slot=None
 def read_ptr(vm):
  s=next((s for s in m["sections"] if s[0]<=vm and vm+4<=s[0]+s[1]
         and s[3] not in ("__common","__bss")),None)
  if s is None:return None
  pos=s[2]+vm-s[0]
  if pos+4>len(exe):return None
  return struct.unpack_from("<I",exe,pos)[0]
 def pointer_name(value):
  if value is None:return []
  return sorted(byaddr.get(value&~1,()))[:7]
 neighbors=[]
 for delta in range(-14,15):
  location=DATA_SITE+4*delta
  if location<section[0] or location+4>section[0]+section[1]:continue
  ptr=read_ptr(location)
  if ptr is None:continue
  neighbors.append({"section_data_VM":hex(location),
    "relative_vtable_slot":(slot+delta) if slot is not None else None,
    "relative_to_original_DoAttack_source_pointer":delta,
    "value_VM":hex(ptr),"original_CPP_method_names":pointer_name(ptr),
    "pointer_is_a_source_symbol_proven":bool(pointer_name(ptr))})
 # Method dispatch finds actual virtual member load offsets only.
 # All potential C++ class member callsites are static candidates:
 # memory LDR [vtable,#4*slot] followed by call via register/pc.
 interesting=("MainCharacter::","Actor::","Input","GamePlay","GS_Game",
             "Player","Controller","Weapon","UI::","Game::")
 decoder=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);decoder.detail=True
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB);thumb.detail=True
 nscanned=0;matches=[]
 for start,names in sorted(byaddr.items()):
  if not any(any(key in n for key in interesting) for n in names):continue
  secs=next((s for s in m["sections"] if s[3]=="__text" and s[0]<=start<s[0]+s[1]),None)
  if secs is None:continue
  ix=bisect.bisect_right(positions,start)
  bound=positions[ix] if ix<len(positions) else secs[0]+secs[1]
  size=min(bound-start,secs[0]+secs[1]-start,12000)
  if size<4:continue
  buf=exe[secs[2]+start-secs[0]:secs[2]+start-secs[0]+size]
  original=list((thumb if mode[start]=={1} else decoder).disasm(buf,start))
  if not original:continue
  nscanned+=1
  if slot is None:continue
  # Runtime C++ "this" could point to subobject: source vtable offset
  # only checks a possible load pattern, never proves this specific vtable.
  requested_byte=slot*4
  for k,op in enumerate(original):
   if not op.mnemonic.startswith("ldr"):continue
   mem=[x for x in op.operands if x.type==ARM_OP_MEM and x.mem.disp==requested_byte]
   if not mem:continue
   later=original[k+1:k+10]
   branches=[n for n in later if
      n.mnemonic in ("blx","bx") or
      (n.mnemonic.startswith("ldr") and n.op_str.startswith("pc,")) or
      (n.mnemonic.startswith("mov") and n.op_str.startswith("pc,"))]
   if not branches:continue
   matches.append({
    "original_C++_caller_addr":hex(start),
    "original_C++_caller_methods":sorted(names)[:4],
    "source_vtable_offset_bytes":requested_byte,
    "native_candidate_load_VM":hex(op.address),
    "source_native_load_opcode":op.mnemonic,
    "source_native_load_args":op.op_str,
    "original_nearby_indirect_branch_opcode":[
       {"vm":hex(b.address),"op":b.mnemonic,"args":b.op_str} for b in branches[:5]],
    "source_original_DoAttack_target_through_this_pattern_PROVEN":False,
    "native_controller_mapping_PROVEN":False})
 proof={
  "origin":"Original user 2010 iOS ARM Mach-O file-backed data, 2010 C++ symbol names, native method source",
  "source_original_DoAttack_VM":hex(TARGET),
  "original_DoAttack_CPP_name":DOATTACK,
  "source_initialized_function_pointer_VM":hex(DATA_SITE),
  "source_original_initialized_pointer_target_VM":hex(value&~1),
  "source_real_segment":"__DATA","source_real_section":"__const",
  "source_nearest_CPP_symbols":vicinity,
  "source_vtable_symbol_vm":hex(owner) if owner is not None else None,
  "source_vtable_symbol_CPP_name":owner_name,
  "original_vtable_slot_zero_based_if_owner_proven":slot,
  "original_vtable_slot_BYTE_OFFSET_if_owner_proven":slot*4 if slot is not None else None,
  "source_2010_neighbor_methods_at_original_data_ptr":neighbors,
  "source_original_relevant_CPP_methods_scanned":nscanned,
  "source_original_indirect_load_and_branch_candidates":matches[:120],
  "source_original_DoAttack_runtime_vtable_dispatch_caller_exact_PROVEN":False,
  "source_original_touchscreen_input_attack_ID_mapping_PROVEN":False,
  "original_MainCharacter_DoAttack_loaded_Vita_gameplay":False,
  "source_G198_zero_direct_calls_is_NOT_DoAttack_dead_function":True,
  "NO_ORIGINAL_EXECUTABLE_OR_ASSET_EXPORT":True,"NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(proof,indent=2,ensure_ascii=False)+"\n")
 print("G199 REAL 2010 DoAttack original file-backed pointer",hex(DATA_SITE),"method",hex(value))
 print("G199 original native vtable source",hex(owner) if owner is not None else None,owner_name,
       "zero-based slot",slot,"byte offset",slot*4 if slot is not None else None)
 for x in vicinity[-30:]:print("G199 ORIGINAL neighbor named symbol",x)
 for x in neighbors:print("G199 ORIGINAL vtable neighbor",x)
 print("G199 source relevant methods",nscanned,"indirect candidate patterns",len(matches))
 for x in matches[:35]:print("G199 INDIRECT possible caller",x)
 # A readable static visualization constructed only from ORIGINAL pointer slots.
 import matplotlib
 matplotlib.use("Agg")
 import matplotlib.pyplot as plt
 from matplotlib.patches import Rectangle
 near=[x for x in neighbors if -6<=x["relative_to_original_DoAttack_source_pointer"]<=6]
 fig,ax=plt.subplots(figsize=(12,8),dpi=140)
 fig.patch.set_facecolor("#111a28")
 ax.set_facecolor("#111a28");ax.set_axis_off()
 ax.set_xlim(0,10);ax.set_ylim(-.3,len(near)+2)
 for k,row in enumerate(near):
  y=len(near)-k
  here=row["relative_to_original_DoAttack_source_pointer"]==0
  ax.add_patch(Rectangle((.65,y-.4),8.7,.78,facecolor="#2a6d70" if here else "#273448",
                         edgecolor="#a3b3ca",linewidth=1))
  method=", ".join(row["original_CPP_method_names"]) if row["original_CPP_method_names"] else "(pointer not named in symbol table)"
  if len(method)>82:method=method[:79]+"..."
  label=f'{row["section_data_VM"]}  [{row["relative_vtable_slot"]}]  {method}'
  ax.text(.85,y,label,va="center",fontsize=10,color="white",family="monospace")
 ax.set_title("Original Iron Man 2 iOS (2010) • DoAttack native virtual source table\n"
              "REAL original symbol pointer addresses • NOT gameplay, animation or input binding",
              color="white",fontsize=12)
 ax.text(5,.02,"Source-only, original method names; index count assumes ABI 2-word vtable header",
    color="#d2dce8",ha="center",fontsize=9)
 png.parent.mkdir(parents=True,exist_ok=True)
 fig.savefig(png,bbox_inches="tight")
 plt.close(fig)
 print("G199 static original named function table PNG",png.name,"bytes",png.stat().st_size)
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("--ipa",type=Path,required=True)
 parser.add_argument("--out",type=Path,required=True)
 parser.add_argument("--png",type=Path,required=True)
 args=parser.parse_args()
 analyze(args.ipa,args.out,args.png)
