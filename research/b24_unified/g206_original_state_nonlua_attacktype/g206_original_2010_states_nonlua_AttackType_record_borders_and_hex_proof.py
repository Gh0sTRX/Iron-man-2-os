#!/usr/bin/env python3
"""G206 2010 original owner iOS 'states' 361393B real bytes;
379 exact AttackType string key hits are outside 55 individual
56-byte Lua source stubs (G204 overlooked non-Lua StateData payload).

Do not mistake Lua program constants for the attached 2010 serialized
StateData records. Report record boundaries/typed bytes and minimal
bounded hex windows at first few occurrences for rigorous G207 parser.

No pretending adjacent bytes are confirmed attack numbers before native
StateData deserializer resolves the serialization schema. NO VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,re,sys,struct,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_g27_original_source_lua51_native_global_call_sites import NativeLua,HEADER
SIZE=248613763
TARGET=b"AttackType"
def main(ipa:Path,out:Path):
 if ipa.stat().st_size!=SIZE:raise ValueError("requires authentic user owned source IPA")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("2010 IPA CRC failed")
  raw=z.read("Payload/IronMan2.app/states")
 if len(raw)!=361393:raise ValueError("original 2010 source StateData size drift")
 starts=[m.start() for m in re.finditer(re.escape(HEADER[:5]),raw)]
 if len(starts)!=55:raise ValueError("original 55 source Lua helper stubs changed")
 spans=[]
 for idx,a in enumerate(starts):
  parser=NativeLua(raw,a)
  if parser.fetch(12)!=HEADER:raise ValueError("source signature error")
  fn=parser.function()
  spans.append((a,parser.pos))
  if parser.pos> (starts[idx+1] if idx+1<len(starts) else len(raw)):
   raise ValueError("original Lua stub exceeds next metadata block")
 counts=collections.Counter();examples=[];keys=[]
 hits=[m.start() for m in re.finditer(TARGET,raw)]
 if len(hits)!=379:raise ValueError("original 2010 state key count not 379")
 for i,hit in enumerate(hits):
  index=bisect.bisect_right(starts,hit)-1
  if index<0:raise ValueError("original key before script metadata header")
  start,end=spans[index]
  within=start<=hit<end
  counts["INSIDE_LUA_51_PROTO" if within else "OUTSIDE_LUA_PROTO"]=counts["INSIDE_LUA_51_PROTO" if within else "OUTSIDE_LUA_PROTO"]+1
  record={
   "source_2010_states_exact_key_offset":hit,
   "source_original_statedata_block_Lua_stub_index":index,
   "source_original_statedata_block_Lua_stub_start":start,
   "source_original_Lua_stub_end":end,
   "source_2010_key_is_in_lua51_program_bytecode":within,
   "source_key_position_from_last_lua_stub_end":hit-end,
   "source_static_2010_AttackType_integer_value_PROVEN":False,
  }
  keys.append(record)
  if len(examples)<27 or i in (50,100,180,260,330,378):
   near=raw[max(0,hit-80):min(len(raw),hit+90)]
   preview="".join(chr(x) if 32<=x<=126 else "." for x in near)
   window=raw[max(0,hit-16):min(len(raw),hit+40)]
   # Small typed value probes are UNCLASSIFIED without original C++ deserialize.
   recordexample=dict(record)
   recordexample.update({
    "original_state_binary_window_start_offset":max(0,hit-16),
    "bounded_2010_source_near_key_HEX":window.hex(),
    "source_nearby_original_printable_metadata":preview,
    "native_source_BYTES_ARE_NOT_INT_VALUES_UNTIL_SCHEMA_PROVEN":True})
   examples.append(recordexample)
 for k,x in enumerate(examples):
  print("G206 REAL 2010 STATE",k,"offset",x["source_2010_states_exact_key_offset"],
        "block",x["source_original_statedata_block_Lua_stub_index"],
        "is within Lua",x["source_2010_key_is_in_lua51_program_bytecode"])
  print("G206 ORIGINAL RECORD BOUNDED HEX",x["bounded_2010_source_near_key_HEX"])
  print("G206 ORIGINAL RECORD ASCII",repr(x["source_nearby_original_printable_metadata"]))
 report={
  "origin":"original owned 2010 iOS states serialized Lua stub vs non-Lua keyed StateData payload boundaries",
  "states_native_file_size":len(raw),
  "original_Lua51_stub_count":len(spans),
  "original_Lua51_stub_source_endpoints":[{"start":a,"end":b,"native_bytes":b-a}
     for a,b in spans],
  "original_2010_AttackType_exact_state_raw_occurrences":len(hits),
  "original_AttackType_Lua_proto_vs_nonLua_bytes":dict(counts),
  "source_every_original_AttackType_byte_key_offset":keys,
  "source_original_minimal_bounded_HEX_record_examples":examples,
  "original_AttackType_key_source_storage_outside_Lua_51_program_is_real":counts.get("OUTSIDE_LUA_PROTO",0)==379,
  "source_native_StateData_serialization_key_type_and_value_proven":False,
  "original_2010_file_format_numeric_attack_types_proven":False,
  "original_iOS_touch_input_all_recovered":False,
  "NO_ORIGINAL_STATES_BINARY_DUMP_EXPORTED":True,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("G206 source original StateData key ownership",dict(counts),"total",len(hits))
 print("G206 original 2010 numerical AttackType values NOT yet native serializer proven, NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True);a=p.parse_args()
 main(a.ipa,a.out)
