#!/usr/bin/env python3
"""G207 original 2010 iOS 379 StateData non-Lua AttackType key/value
literal records. Decode ONLY exact source bytes as:
  u16 little endian string byte count = 10
  'AttackType' ASCII ten bytes
  u32 little endian consecutive native raw value
with source original offsets, source condition/context & distribution.

This proves bytes and an immediately trailing raw u32; typed native
StateData::GetParam matching value after XML/CLARA/serializer load
remains UNPROVEN until native parser methods verified. Also value >25
MUST NOT be silently clamped: original G197 DoAttack switch has only
0..25 entries, native default handles other integers.

Do NOT infer every distinct numeric value is a user button. No VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,json,re,struct,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_g27_original_source_lua51_native_global_call_sites import NativeLua,HEADER
OWNER=248613763;KEY=b"AttackType";LENGTH=10
def analyze(ipa:Path,out:Path):
 if ipa.stat().st_size!=OWNER:raise ValueError("require original owner IronMan2 iOS2010 1.0.0 IPA")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("owner file CRC changed")
  state=z.read("Payload/IronMan2.app/states")
 if len(state)!=361393:raise ValueError("original source states payload changed")
 source_starts=[m.start() for m in re.finditer(re.escape(HEADER[:5]),state)]
 if len(source_starts)!=55:raise ValueError("original 55 Lua stub groups changed")
 intervals=[]
 for source in source_starts:
  p=NativeLua(state,source)
  assert p.fetch(12)==HEADER
  p.function()
  intervals.append((source,p.pos))
 literal=[]
 for m in re.finditer(KEY,state):
  off=m.start()
  index=bisect.bisect_right(source_starts,off)-1
  if index<0:raise ValueError("serialized key outside owner state")
  if intervals[index][0]<=off<intervals[index][1]:
   raise ValueError("This AttackType key inside Lua 5.1 program, not serialized data")
  if off+LENGTH+4>len(state):raise ValueError("StateData typed value truncated")
  declared=struct.unpack_from("<H",state,off-2)[0]
  if declared!=LENGTH:raise ValueError("AttackType original explicit u16 key-length not 10 at "+hex(off))
  u32=struct.unpack_from("<I",state,off+LENGTH)[0]
  # Raw source-specific state reference names that occur before this
  # key in the same very local record, without making them binding facts.
  context=state[max(intervals[index][1],off-100):off]
  strings=[m.group().decode("ascii") for m in re.finditer(
           rb"(?:Attack|Aim|Float|Slide|Walk|Run|Rush|Beam|Combo)[A-Za-z0-9_]{2,64}",context)]
  preceding_name=strings[-1] if strings else None
  literal.append({
   "original_state_group_lua_stub_index":index,
   "owner_state_file_actual_AttackType_key_start_offset":off,
   "source_native_u16_original_key_name_byte_length":declared,
   "source_native_contiguous_original_u32_little_endian_value":u32,
   "source_native_literal_value_over_DoAttack_25":u32>25,
   "source_nearby_anim_state_name_printable_candidate":preceding_name,
   "source_name_association_is_proven_authorized_state_anim_link":False,
   "source_u32_native_2010_GetParam_integer_endianness_semantics_proven":False,
   "source_AttackType_is_touchscreen_button_id_PROVEN":False,
  })
 if len(literal)!=379:raise ValueError("2010 authentic states exact keyed 379 AttackType count drift")
 hist=collections.Counter(x["source_native_contiguous_original_u32_little_endian_value"] for x in literal)
 source_selector_supported=collections.Counter(x["source_native_contiguous_original_u32_little_endian_value"]
        for x in literal if x["source_native_contiguous_original_u32_little_endian_value"]<=25)
 exceeds=[v for v,n in hist.items() if v>25]
 overview={
   "origin":"2010 original owner iOS source serialized states 55 groups/379 authentic AttackType u16 string length and following raw u32 values",
   "original_owner_state_payload_bytes":len(state),
   "original_state_lua_stub_count":len(source_starts),
   "original_raw_exact_AttackType_record_count":len(literal),
   "original_source_attacktype_keyed_u32_value_distribution":{str(k):v for k,v in sorted(hist.items())},
   "original_2010_values_in_G197_native_switch_0_to_25":sum(source_selector_supported.values()),
   "original_2010_values_OUTSIDE_G197_native_switch_0_to_25":sum(hist[v] for v in exceeds),
   "original_2010_distinct_u32_values_OUTSIDE_native_switch":[int(v) for v in sorted(exceeds)],
   "source_actual_attactype_key_records_with_named_nearby_animation_candidates":literal,
   "original_all_379_u16_attacktype_key_fields_are_exact_length10":True,
   "original_native_StateData_GetParam_real_parser_that_reads_this_file_PROVEN":False,
   "original_attacktype_u32_value_equals_native_source_DoAttack_selector_directly_PROVEN":False,
   "source_numeric_values_are_NOT_touch_input_codes":True,
   "source_2010_anyone_has_guessed_Aim_M_missile_binding":False,
   "source_real_2010_user_game_animations_have_been_CHANGED":False,
   "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(overview,indent=2,ensure_ascii=False)+"\n")
 print("G207 SOURCE ORIGINAL 2010 STATE AttackType key/value native data entries",len(literal))
 print("G207 SOURCE exact 2010 raw U32 values",dict(sorted(hist.items())))
 print("G207 indexed 0..25 records",sum(source_selector_supported.values()),
       "OUTSIDE 26-entry DoAttack switch",sum(hist[v] for v in exceeds),
       "out of range values",sorted(exceeds))
 for x in literal[:40]:
  print("G207 SOURCE value",x["owner_state_file_actual_AttackType_key_start_offset"],
        "state_group",x["original_state_group_lua_stub_index"],
        "RAW",x["source_native_contiguous_original_u32_little_endian_value"],
        "nearby",x["source_nearby_anim_state_name_printable_candidate"])
 print("G207 original 2010 key schema still only u16-length + u32 raw value until C++ loader traced; NO VPK")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--ipa",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 args=p.parse_args()
 analyze(args.ipa,args.out)
