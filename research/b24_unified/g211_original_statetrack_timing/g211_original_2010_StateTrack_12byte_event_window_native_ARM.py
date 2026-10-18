#!/usr/bin/env python3
"""G211 original Iron Man 2 iOS (2010) state animation event timing:
actual ARM StateTrack::StateTrack(BufferStream&) reads native
serialized entries and native StateTrack::GetEvent(int,int) tests
source original interval boundaries. Authentic source methods only.

This is original *animation/state event* structure, not proof of
melee hit frame, UniBeam projectile damage or controller button.
Actual data records and their event Type field remain to be decoded.
No Vita VPK/ELF. Avoid invented motion windows.
"""
from __future__ import annotations
import argparse,bisect,collections,json,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho

OWNER=248613763
METHODS={
 "get_event":(0xa14f0,"StateTrack::GetEvent(int, int)"),
 "track_constructor":(0xa167c,"StateTrack::StateTrack(BufferStream&)"),
 "track_constructor_thunk":(0xa196c,"StateTrack::StateTrack(BufferStream&)"),
 "state_constructor":(0x9c528,"StateData::StateData(BufferStream&, StateSetData*)"),
 "actor_update":(0xdb610,"Actor::UpdateStateAttack(int, State*)"),
}
OPCODES={
 "get_event":{
  0xa14fc:("ldr","r8, [r0, #0x10]"), # count
  0xa1508:("ldr","r0, [r0, #8]"),     # event sequence ptr
  0xa150c:("ldr","ip, [r0]"),        # start
  0xa1510:("ldr","r3, [r0, #4]"),    # duration
  0xa1514:("add","lr, ip, r3"),      # end
  0xa1518:("cmp","r2, ip"),         # boundary tested
  0xa1524:("cmp","r1, lr"),         # other boundary
  0xa157c:("ldr","ip, [r0, #0xc]"), # next record start stride12
  0xa1580:("ldr","r4, [r0, #0x10]"),# next record duration
  0xa15a0:("add","r4, r0, #0xc"),   # stride12
  0xa1638:("mvn","r0, #0"),         # -1 if no event
 },
 "track_constructor":{
  0xa16c8:("bl","#0x75fa4"),       # source BufferStream::ReadString
  0xa16e4:("ldr","pc, [r4, #0xc]"),# owner BufferStream virtual Read
  0xa16fc:("ldr","pc, [r3, #0xc]"),# Read 2 bytes event count
  0xa1700:("ldrh","r4, [sp, #0xa]"),
  0xa174c:("lsl","r1, r5, #4"),    # capacity 16*count
  0xa1760:("sub","r1, r1, r5, lsl #2"),# 12*count
  0xa17a4:("ldmne","r4, {r0, r1, r2}"),
  0xa17ac:("stmne","r5, {r0, r1, r2}"),
 },
 "state_constructor":{
  0x9cfe4:("bl","#0xa196c"),       # original StateTrack thunk
 },
 "track_constructor_thunk":{
  0xa196c:("b","#0xa167c")
 },
}
def source(ipa:Path,out:Path):
 if ipa.stat().st_size!=OWNER:raise ValueError("authentic 2010 owner IPA expected")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("owner 2010 IPA ZIP CRC fail")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("original game iOS ARM file size drift")
 orig=parse_macho(exe)
 names=subprocess.run(["c++filt"],input="\n".join(r[0] for r in orig["entries"])+"\n",
                      capture_output=True,text=True,check=True).stdout.splitlines()
 if len(names)!=len(orig["entries"]):raise ValueError("original C++ source names mismatch")
 by=collections.defaultdict(set);bits=collections.defaultdict(set)
 for row,name in zip(orig["entries"],names):
  vm=row[1]&~1;by[vm].add(name);bits[vm].add(row[1]&1)
 for label,(vm,cpp) in METHODS.items():
  if cpp not in by[vm]:raise ValueError("G211 genuine source symbol drift "+cpp+" "+hex(vm))
 indices=sorted(by)
 sections=[s for s in orig["sections"] if s[3]=="__text"]
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);arm.detail=True
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB);thumb.detail=True
 decoded={}
 for label,(vm,_) in METHODS.items():
  sec=next((s for s in sections if s[0]<=vm<s[0]+s[1]),None)
  if sec is None:raise ValueError("native original CPP not in text "+label)
  k=bisect.bisect_right(indices,vm)
  end=min(indices[k] if k<len(indices) else sec[0]+sec[1],sec[0]+sec[1],vm+8000)
  raw=exe[sec[2]+vm-sec[0]:sec[2]+end-sec[0]]
  code=list((thumb if bits[vm]=={1} else arm).disasm(raw,vm))
  if not code:raise ValueError("no genuine ARM code "+label)
  decoded[label]={ins.address:ins for ins in code}
  print("G211 SOURCE native",label,hex(vm),"authentic opcodes",len(code),flush=True)
  for addr,(expect,args) in OPCODES.get(label,{}).items():
   ins=decoded[label].get(addr)
   if not ins or ins.mnemonic!=expect or ins.op_str!=args:
    raise ValueError("G211 real original timing opcode drift "+hex(addr)+" expected "+expect+" "+args+" actual "+str(ins))
   print("G211 PASS original opcode",hex(addr),expect,args,flush=True)
 # In real native GetEvent, time windows compare as
 #   LDR start [entry+0], duration [entry+4]; end=start+duration
 #   tests against the caller's two int time args, not user buttons.
 # Record size 12 bytes has 3 int fields; third field's semantics
 # remain unknown. We do not invent damage hit timing.
 matches=[]
 for label in ("get_event","track_constructor"):
  rows=decoded[label]
  calls=[]
  for i in rows.values():
   if i.mnemonic in ("bl","blx") and i.operands and i.operands[0].type==ARM_OP_IMM:
    a=i.operands[0].imm&~1
    calls.append({"source_REAL_call_VM":hex(i.address),"real_CPP_target_names":sorted(by[a])[:5],
                  "source_native_target_VM":hex(a)})
  matches.append({"source_native_method":label,
    "cpp":METHODS[label][1],
    "original_native_opcodes_total":len(rows),
    "original_source_named_direct_calls":calls[:45]})
 report={
  "origin":"G211 genuine 2010 iOS ARM original StateTrack constructor and time interval event reader",
  "actual_original_StateTrack_constructor_VM":"0xa167c",
  "actual_original_StateTrack_GetEvent_VM":"0xa14f0",
  "source_original_StateData_construct_Track_vm":"0x9cfe4",
  "source_real_2010_StateTrack_entry_stride_bytes":12,
  "source_original_StateTrack_entry_start_at_offset_0":True,
  "source_original_StateTrack_entry_duration_at_offset_4":True,
  "original_native_StateTrack_event_end_equals_start_plus_duration_PROVEN":True,
  "source_original_StateTrack_native_event_count_at_track_plus_0x10":True,
  "source_original_StateTrack_no_event_returns_negative_one":True,
  "source_original_StateTrack_read_source_name_via_BufferStream_ReadString":True,
  "source_original_StateTrack_constructor_event_count_reads_u16":True,
  "source_original_2010_StateTrack_constructor_and_GetEvent_method_sources":matches,
  "source_native_2010_StateTrack_3rd_32bit_field_semantics_PROVEN":False,
  "native_2010_original_per_attack_hit_frame_timing_inferred":False,
  "source_2010_WeaponDB_AttackType_input_and_anim_bindings_PROVEN":False,
  "Vita_actual_one_animator_G83_wired_to_this_source":False,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G211 PASS original 2010 native 12-byte event timeline stride, start+duration and no-event sentinel -1, no fake combat hitframes / Vita VPK",flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 source(a.ipa,a.out)
