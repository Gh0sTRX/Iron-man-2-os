#!/usr/bin/env python3
"""G209 original 2010 iOS source native StateDatabase/StateSetData
file loader/deserializer audit for genuine 379 AttackType raw U32 values.

G207 strict: 379 'AttackType' fields in original 'states' stored
 u16 key_len=10, ASCII AttackType, u32 numeric literal (all 0..25).
G208 strict: StateData::GetParam compares an 8-byte C++ key/value pair
 and loads +4 int on match, step8. G209 now seeks BINARY source decoder
 and its connection from 'states' resource to StateData in memory.

Avoid inventing actual weapon/ammo/joystick mappings before original
loader/StateSet names are proven. Native source metadata only, NO VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,re,subprocess,sys,zipfile
from pathlib import Path
import capstone
from capstone.arm import ARM_OP_IMM
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
SIZE=248613763
CLASSES=re.compile(r'^(StateDatabase|StateSetData|StateSet|StateData|StateTrack|StatesMgr)::')
LOAD=re.compile(r'load|read|import|parse|serial|create|init|file|stream|param|add|copy|set|state|resource',re.I)
def analyze(ipa:Path,g207:Path,out:Path):
 if ipa.stat().st_size!=SIZE:raise ValueError("must have original user owned 2010 IPA")
 record=json.loads(g207.read_text())
 if record["original_raw_exact_AttackType_record_count"]!=379:
  raise ValueError("original 2010 source AttackType record count not proven")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("original source ZIP CRC failed")
  exe=z.read("Payload/IronMan2.app/IronMan2")
 if len(exe)!=7480208:raise ValueError("original iOS MachO changed")
 native=parse_macho(exe)
 dem=subprocess.run(["c++filt"],input="\n".join(r[0] for r in native["entries"])+"\n",
                     capture_output=True,text=True,check=True).stdout.splitlines()
 if len(dem)!=len(native["entries"]):raise ValueError("original source C++ symbol mismatch")
 by=collections.defaultdict(set);mode=collections.defaultdict(set)
 for r,name in zip(native["entries"],dem):
  addr=r[1]&~1;by[addr].add(name);mode[addr].add(r[1]&1)
 addresses=sorted(by);secs=[s for s in native["sections"] if s[3]=="__text"]
 arm=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);arm.detail=True
 thumb=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB);thumb.detail=True
 original={a:n for a,labels in by.items() for n in labels if CLASSES.match(n)}
 output=[]
 for addr,name in sorted(original.items()):
  if not LOAD.search(name):continue
  sec=next((s for s in secs if s[0]<=addr<s[0]+s[1]),None)
  if sec is None:continue
  k=bisect.bisect_right(addresses,addr)
  bound=addresses[k] if k<len(addresses) else sec[0]+sec[1]
  n=min(bound-addr,sec[0]+sec[1]-addr,22000)
  if n<4:continue
  pos=sec[2]+addr-sec[0]
  source=list((thumb if mode[addr]=={1} else arm).disasm(exe[pos:pos+n],addr))
  if not source:continue
  calls=[]
  for ins in source:
   if ins.mnemonic not in ("bl","blx") or not ins.operands or ins.operands[0].type!=ARM_OP_IMM:continue
   target=ins.operands[0].imm&~1
   calls.append({"source_original_CALL_SITE_VM":hex(ins.address),
      "source_original_target_VM":hex(target),
      "genuine_cpp_callee":sorted(by.get(target,()))[:8]})
  output.append({
   "original_CPP_native_method":name,
   "source_original_native_VM":hex(addr),
   "original_source_ARM_or_Thumb":"THUMB" if mode[addr]=={1} else "ARM",
   "source_native_opcode_count":len(source),
   "source_original_direct_call_methods":calls[:160],
   "source_original_first_100_ARM_opcode_provenance":[
     {"VM":hex(i.address),"mnemonic":i.mnemonic,"args":i.op_str}
      for i in source[:100]],
   "original_native_lua_mission_weapon_mapping_proven":False
  })
 report={
  "origin":"G209 original 2010 iOS C++ StateDatabase / StateSetData / StatesMgr native symbol and method bytes",
  "original_native_CPP_state_database_method_names_and_address":[
    {"cpp":n,"VM":hex(a)} for a,n in sorted(original.items())],
  "original_native_state_database_class_symbol_count":len(original),
  "original_real_state_loader_candidate_methods":output,
  "source_2010_AttackType_379_u32_literals_verified":True,
  "source_native_state_loader_puts_original_379_strings_into_StateData_proven":False,
  "original_touchscreen_input_and_selector_ALL_PROVEN":False,
  "Vita_gameplay_logic_unchanged":True,
  "NO_VPK":True,
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G209 owner 2010 SOURCE StateDatabase/StateSetData native CPP methods",len(original),"candidate",len(output))
 for x in output:
  print("G209 original native State C++ SOURCE",x["source_original_native_VM"],x["original_CPP_native_method"],"opcodes",x["source_native_opcode_count"])
  for edge in x["source_original_direct_call_methods"][:22]:
   print("G209 original State DB CALL",x["original_CPP_native_method"],edge)
  if any(t in x["original_CPP_native_method"] for t in
        ("StateDatabase::","StateSetData::")):
   for op in x["source_original_first_100_ARM_opcode_provenance"][:55]:
    print("G209 original StateDatabase opcode",x["original_CPP_native_method"],op)
 print("G209 authentic source serialized loader relation not assumed until original reader followup. NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--g207",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 analyze(a.ipa,a.g207,a.out)
