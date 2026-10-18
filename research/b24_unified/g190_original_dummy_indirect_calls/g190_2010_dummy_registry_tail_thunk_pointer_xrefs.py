#!/usr/bin/env python3
"""G190: source-based ARM / Thumb / data-pointer xrefs to genuine 2010
SceneImpl::DummiesTableAdd/Create/Destroy, following G189's zero direct BL.

Prevention: Mach-O S_ZEROFILL (__common) NEVER has valid file-backed
initialized pointer bytes (G186). Conditional branches and literal values
are counted as CANDIDATES ONLY; source name-to-14/33 group remains unknown.

No licensed original machine bytes are exported. No Vita code/VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,struct,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM

TARGETS={0x641b4:"SceneImpl::DummiesTableAdd(char const*)",
         0x64684:"SceneImpl::DummiesTableCreate(int)",
         0x61aac:"SceneImpl::DummiesTableDestroy()"}
OWNER_SIZE=248613763

def analyze(ipa:Path,dest:Path):
 if ipa.stat().st_size!=OWNER_SIZE:raise ValueError("Not source-original 2010 owner IPA")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip() is not None:raise ValueError("Invalid original IPA CRC")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("Original 2010 MachO size changed")
 sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
 from g76_2010_native_arm_combat_method_provenance import parse_macho
 macho=parse_macho(exe)
 dem=subprocess.run(["c++filt"],input="\n".join(e[0] for e in macho["entries"])+"\n",
                    capture_output=True,text=True,check=True).stdout.splitlines()
 if len(dem)!=len(macho["entries"]):raise ValueError("Original native symbols mismatched")
 byaddr=collections.defaultdict(set);modes=collections.defaultdict(set)
 for rec,name in zip(macho["entries"],dem):
  addr=rec[1]&~1
  byaddr[addr].add(name);modes[addr].add(rec[1]&1)
 for target,name in TARGETS.items():
  if name not in byaddr[target]:raise ValueError(f"Native original symbol drift {target:#x}")
 symbols=sorted(byaddr)
 sections=macho["sections"]
 textsections=[s for s in sections if s[3]=="__text"]
 if not textsections:raise ValueError("Owner has no original ARM source __text")
 csarm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM)
 csthumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
 for d in (csarm,csthumb):d.detail=True
 hits=[];methods=0;armmethods=0;thumbmethods=0
 for addr in symbols:
  sec=next((s for s in textsections if s[0]<=addr<s[0]+s[1]),None)
  if sec is None:continue
  ix=bisect.bisect_right(symbols,addr)
  end=symbols[ix] if ix<len(symbols) else sec[0]+sec[1]
  length=min(end-addr,sec[0]+sec[1]-addr,16000)
  if length<4:continue
  off=sec[2]+addr-sec[0]
  isthumb=modes[addr]=={1}
  if isthumb:thumbmethods+=1
  else:armmethods+=1
  ins=list((csthumb if isthumb else csarm).disasm(exe[off:off+length],addr))
  if not ins:continue
  methods+=1
  for op in ins:
   mnemonic=op.mnemonic.split(".")[0].lower()
   if not op.operands or op.operands[-1].type!=ARM_OP_IMM:continue
   target=op.operands[-1].imm&~1
   if target not in TARGETS:continue
   if mnemonic in ("bl","blx"):kind="DIRECT_CALL"
   elif mnemonic in ("b","b.w","beq","bne","bgt","blt","ble","bge","bhi","bls","bcs","bcc"):
    kind="BRANCH_OR_TAIL_CALL_CANDIDATE"
   else:continue
   hits.append({
      "caller_VM":hex(addr),
      "caller_CPP_symbols":sorted(byaddr[addr])[:5],
      "native_machine_mode":"THUMB" if isthumb else "ARM",
      "source_branch_site_VM":hex(op.address),
      "source_native_mnemonic":op.mnemonic,
      "source_target_VM":hex(target),
      "source_target_method":TARGETS[target],
      "source_branch_reaches_true_call_semantics_PROVEN":kind=="DIRECT_CALL",
      "kind":kind})
 # Independently parse 32-bit sections, distinguishing S_ZEROFILL.
 hdr=struct.unpack_from("<IiiIIII",exe,0)
 position=28;sectionrows=[]
 for _ in range(hdr[4]):
  cmd,sz=struct.unpack_from("<II",exe,position)
  if cmd==1:
   count=struct.unpack_from("<I",exe,position+48)[0]
   for k in range(count):
    at=position+56+k*68
    sname=exe[at:at+16].split(b"\0")[0].decode("latin1")
    seg=exe[at+16:at+32].split(b"\0")[0].decode("latin1")
    va,nbytes,offset=struct.unpack_from("<III",exe,at+32)
    flags=struct.unpack_from("<I",exe,at+56)[0]
    if flags&0xff==1:continue
    if not 0<=offset<=len(exe) or offset+nbytes>len(exe):continue
    # Find absolute function pointers only in nonexecutable file-backed data
    if sname=="__text":continue
    for delta in range(0,nbytes-3,4):
     word=struct.unpack_from("<I",exe,offset+delta)[0]
     if word&~1 not in TARGETS:continue
     sectionrows.append({
       "source_data_address_VM":hex(va+delta),
       "source_data_segment":seg,
       "source_data_section":sname,
       "source_pointer_target_VM":hex(word&~1),
       "target_CPP":TARGETS[word&~1],
       "pointer_target_original_thumb_bit":word&1,
       "source_pointer_is_initialized_file_backed":True,
       "pointer_used_as_live_runtime_callback_PROVEN":False})
  position+=sz
 counts={TARGETS[a]:{
  "arm_thumb_bl_blx":sum(z["source_target_VM"]==hex(a) and z["kind"]=="DIRECT_CALL" for z in hits),
  "arm_thumb_possible_branch_tailcall":sum(z["source_target_VM"]==hex(a) and z["kind"]=="BRANCH_OR_TAIL_CALL_CANDIDATE" for z in hits),
  "initialized_pointer_candidates":sum(z["source_pointer_target_VM"]==hex(a) for z in sectionrows)}
  for a in TARGETS}
 output={
  "origin":"2010 owner original ARM MachO source symbols and file-backed LC_SEGMENT sections",
  "source_original_CPP_registrar_targets":{hex(a):n for a,n in TARGETS.items()},
  "original_function_symbols_scanned":methods,
  "original_ARM_methods_scanned":armmethods,
  "original_Thumb_methods_scanned":thumbmethods,
  "source_original_arm_thumb_direct_call_or_branch_candidates":hits,
  "source_original_initialized_nonzerofill_absolute_function_pointer_candidates":sectionrows[:1000],
  "source_verified_per_target_counts":counts,
  "original_Aim_M_source_missile_link_proven":False,
  "original_scene_dummy14_33_to_named_BDAE_socket_proven":False,
  "original_bss_common_initialized_from_file":False,
  "scanner_direct_calls_may_miss_dynamic_register_or_relocated_indirect_calls":True,
  "no_new_Vita_gameplay_changes":True,
  "NO_VPK":True}
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n")
 print("G190 ORIGINAL native method scan ARM",armmethods,"THUMB",thumbmethods)
 for key,value in counts.items():print("G190 ORIGINAL",key,value)
 for r in hits[:60]:print("G190 original native branch site",r)
 for r in sectionrows[:60]:print("G190 original initialized function ptr",r)
 print("G190 14/33 exact socket names not proven by static call/pointer coverage, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 args=p.parse_args()
 analyze(args.ipa,args.out)
