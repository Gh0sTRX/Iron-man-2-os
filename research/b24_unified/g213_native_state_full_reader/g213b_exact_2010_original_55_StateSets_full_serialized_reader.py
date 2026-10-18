#!/usr/bin/env python3
"""G213B exact original 2010 Iron Man 2 iOS StateDatabase binary
StateSetData -> StateData -> StateTrack reader. Original ARM G213A
determines every serialized field in native C++ constructor.

EXPECT: read full 361,393-byte owner 'states', all 55 original StateSets,
state names, 379 authentic AttackType records, original attached
Attack/attack StateTrack timelines; EOF must exactly match file length.
Cross-match EVERY G207 AttackType key offset/value; do not infer combat
hit windows or weapon/damage/touch assignments.

Fail closed if any inferred block count, event track or serialized
field diverges. Owner archive remains temporary in CI, output
ONLY source state names, integer values and timing metadata. NO VPK.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re,struct,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_g27_original_source_lua51_native_global_call_sites import NativeLua,HEADER

OWNER_SIZE=248613763
STATE_LEN=361393

class Reader:
 def __init__(self,data:bytes):
  self.data=data;self.pos=0
 def fail(self,message):
  raise ValueError(f"2010 native StateDatabase source parse error at states offset {self.pos}: {message}, source_next24_bytes_hex={self.data[self.pos:min(len(self.data),self.pos+24)].hex()}")
 def fetch(self,size):
  if size<0 or self.pos+size>len(self.data):self.fail("short read "+str(size))
  off=self.pos;self.pos+=size
  return self.data[off:self.pos]
 def u8(self):return self.fetch(1)[0]
 def u16(self):return struct.unpack("<H",self.fetch(2))[0]
 def i16(self):return struct.unpack("<h",self.fetch(2))[0]
 def u32(self):return struct.unpack("<I",self.fetch(4))[0]
 def string(self):
  start=self.pos
  size=self.u16()
  if size>250:self.fail("invalid original source string length "+str(size))
  raw=self.fetch(size)
  try:t=raw.decode("ascii")
  except UnicodeError:self.fail("original serialized state nonascii at "+str(start))
  return t,start+2
 def array_count(self,cap,desc):
  value=self.u16()
  if value>cap:self.fail("source "+desc+" excessive count "+str(value))
  return value

def parse_track(p:Reader):
 start=p.pos
 name,_=p.string()
 unknown_u16=p.u16()
 count=p.array_count(256,"StateTrack events")
 events=[]
 for index in range(count):
  off=p.pos
  st,duration,third=p.u32(),p.u32(),p.u32()
  events.append({"native_source_event_index":index,"source_original_offset":off,
   "start_source_raw_integer":st,"duration_source_raw_integer":duration,
   "end_start_plus_duration":st+duration,
   "third_u32_unknown_semantics":third,
   "source_event_is_melee_hit_damage_or_projectile_PROVEN":False})
 return {"native_source_track_start":start,"native_original_track_name":name,
  "original_u16_track_mode_field_unclassified":unknown_u16,
  "native_source_12byte_event_count":count,
  "source_authentic_2010_event_records":events,
  "source_original_complete_track_end":p.pos}

def parse_state(p:Reader,group_index:int):
 start=p.pos
 name,_=p.string()
 params_n=p.array_count(256,"StateData ordinary param key-value records")
 if group_index==24 and start<66000:print("G213 DIAG IronMan first state",start,name,"param_count",params_n,"param bytes start",p.pos,flush=True)
 params=[];attack=[]
 for i in range(params_n):
  key,off=p.string()
  value=p.u32()
  params.append({"name":key,"source_value_u32":value,"key_offset":off})
  if key=="AttackType":
   attack.append({"key_offset":off,"value":value})
 if group_index==24 and start<66000:print("G213 DIAG IronMan",name,"AFTER param",p.pos,"first",params[:10],flush=True)
 extra_n=p.array_count(256,"StateData 44-byte actor movement/action metadata")
 if group_index==24 and start<66000:print("G213 DIAG IronMan",name,"extra_n",extra_n,"at",p.pos,flush=True)
 extras=[]
 for k in range(extra_n):
  off=p.pos
  if group_index==24 and start<66000:
   print("G213 AUTHENTIC IronMan EXTRA",k,"start",off,
     "near_original_source80",p.data[off:off+80].hex(),flush=True)
  source_name,_=p.string()
  raw5=[p.u32() for i in range(5)]
  native_bool=p.u8()
  if group_index==24 and start<66000:
   print("G213 AUTHENTIC IronMan EXTRA",k,"name",source_name,
     "five",raw5,"flag",native_bool,"after-byte",p.pos,flush=True)
  # Original ARM 0x9CCB8..0x9CCC0: LDRB record+0x14, CMP #0,
  # BNE 0x9CBAC (next record) if NONZERO. Only zero means
  # additional u32 + optional ReadString are present.
  if native_bool==0:
   additional=p.u32()
   extra_name,_=p.string()
  else:
   additional=None
   extra_name=None
  if group_index==24 and start<66000:
   print("G213 AUTHENTIC IronMan EXTRA",k,"additional",additional,
     "extra_name",extra_name,"END",p.pos,flush=True)
  extras.append({"original_entry_off":off,"original_name":source_name,
   "native_2010_5x_u32_unclassified":raw5,
   "native_2010_u8_unclassified":native_bool,
   "native_2010_u32_unclassified":additional,
   "native_2010_additional_string":extra_name})
 if group_index==24 and start<66000:print("G213 DIAG IronMan",name,"AFTER extras",p.pos,"first_extra",extras[:2],flush=True)
 channel_n=p.array_count(256,"StateData source event track channels")
 if group_index==24 and start<66000:print("G213 DIAG IronMan",name,"channel_n",channel_n,"at",p.pos,flush=True)
 channels=[];ntracks=0
 for c in range(channel_n):
  off=p.pos;native_id=p.u32();kind=p.u16();n=p.i16()
  if n<0 or n>128:p.fail("invalid signed original track count "+str(n))
  tracks=[parse_track(p) for i in range(n)]
  channels.append({"source_record_offset":off,"native_u32_anim_or_event_id_unclassified":native_id,
   "native_source_u16_channel_type_unclassified":kind,
   "source_original_track_count":n,
   "source_2010_attached_track_records":tracks})
  ntracks+=n
 if group_index==24 and start<66000:print("G213 DIAG IronMan",name,"AFTER channels",p.pos,"first_ch",channels[:2],flush=True)
 flags_n=p.array_count(256,"StateData named state flag entries")
 if group_index==24 and start<66000:print("G213 DIAG IronMan",name,"flags_n",flags_n,"at",p.pos,flush=True)
 flags=[]
 for i in range(flags_n):
  name,_=p.string();a=p.u16();b=p.u16()
  flags.append({"name":name,"source_u16_flag1":a,"source_u16_flag2":b})
 return {"source_original_state_record_index":None,
  "source_original_group_index":group_index,
  "source_native_binary_record_start":start,
  "source_original_state_name":name,
  "source_original_state_params":params,
  "source_original_attacktype_exact_definitions":attack,
  "source_original_extra_metadata_count":len(extras),
  "source_original_extra_metadata_records":extras,
  "source_original_event_channel_count":len(channels),
  "source_original_tracks_in_event_channels":ntracks,
  "source_original_event_channels":channels,
  "source_original_named_flags":flags,
  "source_native_binary_record_end":p.pos}

def parse_set(p:Reader,k:int):
 start=p.pos
 name,_=p.string()
 raw_count=p.u32()
 if raw_count<12 or raw_count>150000:p.fail("original source LUA byte count unreasonable "+str(raw_count))
 lua_source_start=p.pos
 raw=p.fetch(raw_count)
 if raw[:12]!=HEADER:p.fail("source original state Lua51 chunk magic/header mismatch")
 lua=NativeLua(raw,0);lua.fetch(12);lua.function()
 if lua.pos!=len(raw):p.fail("native Lua source length not fully parsed")
 aliases_n=p.array_count(512,"original StateSet id-name aliases")
 aliases=[]
 for i in range(aliases_n):
  name_id=p.u32()
  alias,_=p.string()
  aliases.append({"source_native_state_name_id":name_id,"source_native_state_alias":alias})
 n=p.array_count(512,"original StateSet included StateData records")
 states=[]
 for i in range(n):
  st_start=p.pos
  try:
   st=parse_state(p,k)
  except Exception as exc:
   raise ValueError(f"source StateSet {k}={name!r} / StateData record {i}/{n}, start={st_start}: {exc}") from exc
  st["source_original_state_record_index"]=i
  states.append(st)
 return {"source_original_index":k,
  "original_2010_StateSet_name":name,
  "original_2010_lua_block_start":lua_source_start,
  "source_original_lua_block_size":len(raw),
  "original_lua51_SHA256":hashlib.sha256(raw).hexdigest(),
  "source_original_alias_record_count":aliases_n,
  "source_original_alias_records":aliases,
  "source_original_StateData_record_count":len(states),
  "source_authentic_2010_StateData":states,
  "source_original_set_start":start,"source_original_set_end":p.pos}

def main(ipa:Path,g207:Path,g212:Path,out:Path):
 if ipa.stat().st_size!=OWNER_SIZE:raise ValueError("need original iOS 2010 1.0.0 user owner IPA")
 d207=json.loads(g207.read_text())
 d212=json.loads(g212.read_text())
 if d207["original_raw_exact_AttackType_record_count"]!=379 or \
  d212["source_original_full_2010_attack_track_named_6ASCII_candidate_total"]!=365:
  raise ValueError("G207/G212 genuine previous source proofs required")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("owner iOS original ZIP damaged")
  raw=z.read("Payload/IronMan2.app/states")
 if len(raw)!=STATE_LEN:raise ValueError("original owner states bytes length mismatch")
 reader=Reader(raw)
 n=reader.array_count(55,"original total StateSet count")
 if n!=55:raise ValueError("source original 55 StateSet groups changed")
 sets=[]
 for k in range(n):
  try:
   x=parse_set(reader,k)
  except Exception as e:
   raise ValueError(f"Source true 2010 StateSet#{k} at byte {reader.pos} failed: {e}") from e
  sets.append(x)
  print("G213 REAL 2010 original set",k,x["original_2010_StateSet_name"],
    "states",x["source_original_StateData_record_count"],
    "aliases",x["source_original_alias_record_count"],
    "bytes",x["source_original_set_end"]-x["source_original_set_start"],flush=True)
 if reader.pos!=len(raw):
  raise ValueError(f"Full native 2010 source state parser residual {len(raw)-reader.pos} bytes: STOP, no guessed field skip")
 state_list=[st for ss in sets for st in ss["source_authentic_2010_StateData"]]
 source_attack=[(a["key_offset"],a["value"],st["source_original_state_name"],ss["original_2010_StateSet_name"])
    for ss in sets for st in ss["source_authentic_2010_StateData"]
    for a in st["source_original_attacktype_exact_definitions"]]
 original207=[(a["owner_state_file_actual_AttackType_key_start_offset"],
   a["source_native_contiguous_original_u32_little_endian_value"])
   for a in d207["source_actual_attactype_key_records_with_named_nearby_animation_candidates"]]
 if [(a,b) for a,b,_,__ in source_attack]!=original207:
  raise ValueError("true owner source key/value parse differs in exact original G207 379 offset/value entries")
 if len(source_attack)!=379:
  raise ValueError("original StateData key count should exactly match 379")
 parsed_track=[t for ss in sets for st in ss["source_authentic_2010_StateData"]
               for ch in st["source_original_event_channels"]
               for t in ch["source_2010_attached_track_records"]]
 verified_named=[t for t in parsed_track if t["native_original_track_name"] in ("Attack","attack")]
 candidate_offs={a["original_authored_source_name_prefixed_offset"]
                 for a in d212["source_original_native_Attack_named_12byte_event_candidates"]}
 verified_offs={t["native_source_track_start"]+2 for t in verified_named}
 if not verified_offs.issubset(candidate_offs):
  raise ValueError("G213 actual native parsed tracks conflict with earlier G212 raw source candidates")
 hist=collections.Counter(t["native_original_track_name"] for t in parsed_track)
 report={
  "source":"G213 full original 2010 iOS states strict original C++ ARM binary serializer decoder, COMPLETE EOF",
  "source_original_states_binary_total_bytes":len(raw),
  "source_original_2010_StateSet_count":len(sets),
  "source_original_2010_StateData_count":len(state_list),
  "source_original_AttackType_key_u32_value_count":len(source_attack),
  "source_2010_attack_type_g207_ALL_379_offset_value_matches":True,
  "source_original_StateTrack_count":len(parsed_track),
  "source_original_track_name_distribution":dict(hist),
  "source_original_named_Attack_attack_track_count":len(verified_named),
  "source_G212_named_Attack_candidates":len(candidate_offs),
  "source_G212_named_Attack_candidates_confirmed_by_full_StateData_native_Cpp_schema":len(verified_offs),
  "source_G212_named_Attack_candidates_rejected_outside_actual_state_structure":len(candidate_offs-verified_offs),
  "source_original_2010_state_sets_all":sets,
  "source_original_all_bytes_consumed_exactly":True,
  "source_original_input_and_suit_controller_bindings_PROVEN":False,
  "source_event_track_3rd_u32_melee_damage_semantics_proven":False,
  "original_iOS_Vita_runtime_weapon_animation_event_wiring_changed":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G213 TRUE ORIGINAL STATE NAMES by set")
 for x in sets:
  print("G213 owner",x["original_2010_StateSet_name"],
    "AttackType state count",sum(len(s["source_original_attacktype_exact_definitions"]) for s in x["source_authentic_2010_StateData"]),
    "event track count",sum(s["source_original_tracks_in_event_channels"] for s in x["source_authentic_2010_StateData"]))
 print("G213 PASS genuine 55 sets +",len(state_list),"states + 379 exact u32 AttackType +",len(parsed_track),
    "tracks, G212 exact named actual",len(verified_offs),"candidate",len(candidate_offs),
    "byte-for-byte 361393 ALL FILE CONSUMED, no guessed attacker controller/hit frame/VPK",flush=True)
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for x in ("ipa","g207","g212","out"):p.add_argument("--"+x,required=True,type=Path)
 a=p.parse_args();main(a.ipa,a.g207,a.g212,a.out)
