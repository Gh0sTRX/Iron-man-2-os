#!/usr/bin/env python3
"""G213A source investigation: native 2010 iOS serializer exact ARM
structural byte counts and true original StateDatabase 55 block offsets.
Outputs bounded opcode metadata and surrounding field previews, never
publishes full original IPA/ARM executable or game assets. No Vita VPK.
"""
import argparse,zipfile,struct,sys,json,bisect,subprocess,collections
from pathlib import Path
import capstone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"g76_original_combat"))
from g76_2010_native_arm_combat_method_provenance import parse_macho
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_g27_original_source_lua51_native_global_call_sites import NativeLua,HEADER
OWNER=248613763
METHODS={"state_data":(0x9c528,[(0x9c5e0,0x9c640),(0x9c828,0x9c9b0),(0x9cb68,0x9ce50),(0x9ceb0,0x9d100),(0x9d200,0x9d2c0)]),
"state_set":(0x9d85c,[(0x9d8c0,0x9d970),(0x9dba0,0x9df80)]),
"track":(0xa167c,[(0xa16a0,0xa1840)]),
"database":(0x9e1a8,[(0x9e1f0,0x9e29c),(0x9e510,0x9e5a0)])}
def main(ipa,out):
 if ipa.stat().st_size!=OWNER:raise ValueError("owner original IPA not found")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("owner IPA CRC")
  exe=z.read("Payload/IronMan2.app/IronMan2")
  raw=z.read("Payload/IronMan2.app/states")
 native=parse_macho(exe);dem=subprocess.run(["c++filt"],input="\n".join(a[0] for a in native["entries"])+"\n",text=True,capture_output=True,check=True).stdout.splitlines()
 by=collections.defaultdict(set)
 for r,n in zip(native["entries"],dem):by[r[1]&~1].add(n)
 sections=[s for s in native["sections"] if s[3]=="__text"];sort=sorted(by)
 cs=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_ARM);cs.detail=True
 probes={}
 for label,(a,ranges) in METHODS.items():
  sec=next(s for s in sections if s[0]<=a<s[0]+s[1]);k=bisect.bisect_right(sort,a)
  end=min(sort[k] if k<len(sort) else sec[0]+sec[1],sec[0]+sec[1])
  code=list(cs.disasm(exe[sec[2]+a-sec[0]:sec[2]+end-sec[0]],a))
  ins=[{"vm":hex(t.address),"mnemonic":t.mnemonic,"args":t.op_str} for t in code if any(lo<=t.address<hi for lo,hi in ranges)]
  probes[label]=ins
  print("G213A ORIGINAL SOURCE METHOD",label,a,"selected opcodes",len(ins))
  for op in ins:print("G213A ARM",label,op["vm"],op["mnemonic"],op["args"])
 starts=[];head=struct.unpack_from("<H",raw,0)[0];print("G213A ORIGINAL states first U16",head,"source bytes",len(raw))
 for i in range(len(raw)-5):
  if raw[i:i+5]==HEADER[:5]:starts.append(i)
 print("G213A REAL LUA signature count",len(starts))
 for k,i in enumerate(starts[:7]):
  parse=NativeLua(raw,i);parse.fetch(12);root=parse.function();end=parse.pos
  # first bytes following Lua stub: StateSetData's unknown count or hash.
  at=min(len(raw),end+88)
  sample=raw[end:at]
  print("G213A REAL SOURCE Lua chunk",k,"start",i,"end",end,
       "NEXT90_HEX",sample.hex(),"ASCII","".join(chr(t) if 32<=t<=126 else "." for t in sample))
 print("G213A states ORIGINAL first64",raw[:64].hex())
 first=raw[:min(starts[0],512)]
 print("G213A exact prefix to first Lua header",first.hex(),"ASCII","".join(chr(c) if 32<=c<=126 else "." for c in first))
 report={"original_source":"2010 owner ARM StateData/StateSetData/StateTrack full serializer probe",
  "original_states_length":len(raw),"original_states_first_u16":head,
  "original_lua51_original_source_signature_count":len(starts),
  "original_lua_original_positions":starts,
  "original_selected_state_deserializer_ARM":probes,
  "native_full_Binary_StateData_schema_end_to_end_proven":False,
  "NO_VPK":True}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+"\n")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args();main(a.ipa,a.out)
