#!/usr/bin/env python3
"""G219 owner iOS 2010 full native ARM C++ StateTrack::GetEvent and
Actor::UpdateStateAttack caller return-value dataflow source:
investigate original third u32 event-record semantics and whether
a hit frame, projectile event, animation marker, or just an event ID.

No fabricated source instructions, event time ms conversions, damage
or Vita VPK. Owner's IPA read only in ephemeral GitHub Actions runner.
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
 "event":(0xa14f0,"StateTrack::GetEvent(int, int)"),
 "actor":(0xdb610,"Actor::UpdateStateAttack(int, State*)"),
 "attack":(0xf64f8,"MainCharacter::DoAttack(int, int)"),
}
def main(ipa:Path,out:Path):
 if ipa.stat().st_size!=OWNER:raise ValueError("requires 2010 original owner IPA")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("owned 2010 original IPA CRC fail")
  binary=z.read("Payload/IronMan2.app/IronMan2")
 if len(binary)!=7480208:raise ValueError("authentic original ARM executable drift")
 native=parse_macho(binary)
 dem=subprocess.run(["c++filt"],input="\n".join(t[0] for t in native["entries"])+"\n",
                    text=True,capture_output=True,check=True).stdout.splitlines()
 if len(dem)!=len(native["entries"]):raise ValueError("C++ owner symbols mismatch")
 named=collections.defaultdict(set);mods=collections.defaultdict(set)
 for rec,name in zip(native["entries"],dem):
  vm=rec[1]&~1;named[vm].add(name);mods[vm].add(rec[1]&1)
 starts=sorted(named);sections=[s for s in native["sections"] if s[3]=="__text"]
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);arm.detail=True
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB);thumb.detail=True
 table={}
 for label,(addr,cpp) in METHODS.items():
  if cpp not in named[addr]:raise ValueError("original 2010 C++ source symbol drift "+cpp)
  sec=next((s for s in sections if s[0]<=addr<s[0]+s[1]),None)
  if not sec:raise ValueError("2010 original method outside __text")
  after=bisect.bisect_right(starts,addr)
  end=min(starts[after] if after<len(starts) else sec[0]+sec[1],sec[0]+sec[1],addr+12000)
  raw=binary[sec[2]+addr-sec[0]:sec[2]+end-sec[0]]
  ins=list((thumb if mods[addr]=={1} else arm).disasm(raw,addr))
  if label=="event" and not 45<=len(ins)<=300:raise ValueError("original GetEvent source body missing")
  ret=[]
  calls=[]
  for i in ins:
   ret.append({"VM":hex(i.address),"opcode":i.mnemonic,"operands":i.op_str})
   if i.mnemonic in ("bl","blx") and i.operands and i.operands[0].type==ARM_OP_IMM:
    dest=i.operands[0].imm&~1
    calls.append({"source_CALL_VM":hex(i.address),"target_VM":hex(dest),
      "original_target_CPP":sorted(named.get(dest,()))[:4]})
  table[label]={"source_cpp":cpp,"source_original_vm":hex(addr),
    "original_native_instruction_count":len(ins),
    "source_original_ARM_ops_no_machine_bytes":ret[:200] if label!="attack" else ret[:75],
    "source_real_native_calls":calls[:95]}
  print("G219 original 2010 CPP",cpp,"@VM",hex(addr),"native ops",len(ins),flush=True)
  if label=="event":
   for op in ret:print("G219 SOURCE REAL GetEvent ARM",op,flush=True)
  if label=="actor":
   for op in ret:
    if 0xdb660<=int(op["VM"],16)<=0xdb740:print("G219 SOURCE REAL Actor AttackConsumer ARM",op,flush=True)
 # The original StateTrack::GetEvent -1 return path and its third field
 # load will be classified separately after reading FULL function.
 source_event=table["event"]["source_original_ARM_ops_no_machine_bytes"]
 actual={int(x["VM"],16):(x["opcode"],x["operands"]) for x in source_event}
 known={
 0xa150c:("ldr","ip, [r0]"),
 0xa1510:("ldr","r3, [r0, #4]"),
 0xa1514:("add","lr, ip, r3"),
 0xa1638:("mvn","r0, #0"),
 }
 for vm,expected in known.items():
  if actual.get(vm)!=expected:
   raise ValueError("G219 real 2010 native StateTrack GetEvent known source drift "+hex(vm))
 # Confirm native GetEvent returns the INDEX of overlapping 12-byte
 # EVENT record (r6), not the third u32 payload! It returns -1 otherwise.
 # Any real event payload/hit classification must be read elsewhere.
 for vm,expected in {
   0xa1508:("ldr","r0, [r0, #8]"),
   0xa156c:("add","r6, r6, #1"),
   0xa15a0:("add","r4, r0, #0xc"),
   0xa15f8:("mov","r0, r6"),
   0xa1638:("mvn","r0, #0")
 }.items():
  if actual.get(vm)!=expected:raise ValueError("G219 original native GetEvent result INDEX evidence drift "+hex(vm))
 event_third_payload_reads=[
    op for op in source_event
    if int(op["VM"],16)>0xa1508 and op["opcode"].startswith("ldr")
    and ("[r0, #8]" in op["operands"] or "[r0, #0x8]" in op["operands"])
 ]
 if event_third_payload_reads:
  raise ValueError("G219 native GetEvent appears to touch third-field record payload; inspect "+str(event_third_payload_reads))
 third=[
  op for op in source_event
  if ("#8]" in op["operands"] or "#0x8]" in op["operands"]) and
     op["opcode"].startswith(("ldr","str"))]
 result={
  "origin":"G219 complete original iOS 2010 C++ StateTrack::GetEvent and Actor::UpdateStateAttack ARM instructions exact owner executable",
  "original_StateTrack_GetEvent_VM":"0xa14f0",
  "real_native_original_methods_source":table,
  "genuine_source_register_ops_candidate_event_u32_field_plus8":third,
  "original_event_timeline_record_stride_12_bytes_proven":True,
  "source_native_StateTrack_GetEvent_returns_overlapping_original_12byte_EVENT_INDEX_or_minus1_PROVEN":True,
  "source_native_StateTrack_GetEvent_does_NOT_decode_3rd_u32_event_payload":True,
  "source_native_original_third_u32_payload_remains_UNCLASSIFIED":True,
  "source_native_returned_Event_id_semantics_PROVEN":False,
  "original_attack_event_time_unit_ms_PROVEN":False,
  "original_native_weapon_or_melee_damage_use_of_event_id_proven":False,
  "G218_live_G8_G217_observer_changed":False,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+"\n")
 print("G219 PROVEN actual 2010 GetEvent returns overlapping EVENT INDEX r6 (or -1); native function does NOT read third-u32 payload")
 print("G219 true original 2010 Event GetEvent +8 potential third field source ops",third)
 print("G219 G218 passive live source bridge unchanged; any hit/event weapon interpretation needs original native consumer call graph, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path);a=p.parse_args();main(a.ipa,a.out)
