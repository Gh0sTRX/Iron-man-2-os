#!/usr/bin/env python3
"""G213C EXACT original iOS 2010 source 55 StateSet header names and
379 AttackType state raw value records mapping to owned set boundaries.
The full native 2010 StateData reader is not yet complete: original
IronMan Idle event/transition branch ambiguity remains (G213B).
This report *does not* claim every name belongs to a specific state
record, just a SOURCE-PROVEN StateSet archive interval.

StateSetData constructor original: ReadString() set name, virtual
Read u32 Lua size, virtual Read Lua blob, then u16 aliases+state
objects. Native Lua51 parse determines exact S+LuaLen source offsets.
55 original signature starts, zero owner pack ambiguity.
No synthetic events/hit frames or Vita VPK.
"""
from __future__ import annotations
import argparse,bisect,collections,hashlib,json,struct,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from b24_g27_original_source_lua51_native_global_call_sites import NativeLua,HEADER
EXPECTED=248613763
def main(ipa:Path,g207:Path,g212:Path,out:Path):
 if ipa.stat().st_size!=EXPECTED:raise ValueError("exact 2010 owner original iOS IPA required")
 attack=json.loads(g207.read_text())
 candidate=json.loads(g212.read_text())
 if attack["original_raw_exact_AttackType_record_count"]!=379 or candidate["source_original_full_2010_attack_track_named_6ASCII_candidate_total"]!=365:
  raise ValueError("G207/G212 earlier owner source data prerequisite mismatch")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("owner original ZIP CRC failed")
  raw=z.read("Payload/IronMan2.app/states")
 if len(raw)!=361393:raise ValueError("source 2010 states asset drift")
 starts=[i for i in range(len(raw)-5) if raw[i:i+5]==HEADER[:5]]
 if len(starts)!=55:raise ValueError("genuine 2010 source Lua 51 groups not 55")
 count=struct.unpack_from("<H",raw)[0]
 if count!=55:raise ValueError("genuine 2010 StateDatabase count not 55")
 sets=[]
 for k,source in enumerate(starts):
  # The known source StateSetData native constructor calls ReadString()
  # immediately followed by 4-byte Lua length and that exact chunk.
  source_lua_bytes=struct.unpack_from("<I",raw,source-4)[0]
  if not 12<=source_lua_bytes<=20000:raise ValueError("state Lua blob size invalid group "+str(k))
  # Authentic original Lua51 metadata must consume exactly stored chunk.
  lua=NativeLua(raw,source);lua.fetch(12);lua.function()
  if lua.pos-source!=source_lua_bytes:
   raise ValueError(f"G213C source owner state {k} Lua byte length mismatch {lua.pos-source} vs {source_lua_bytes}")
  possible=[]
  for label_len in range(1,128):
   pos=source-4-label_len-2
   if pos<2:continue
   if struct.unpack_from("<H",raw,pos)[0]!=label_len:continue
   encoded=raw[pos+2:source-4]
   if any(x<33 or x>126 for x in encoded):continue
   try:label=encoded.decode("ascii")
   except UnicodeError:continue
   possible.append((pos,label))
  if len(possible)!=1:raise ValueError(f"StateSet#{k} header name not unique source {hex(source)} candidates {possible}")
  pos,name=possible[0]
  if k==0 and pos!=2:raise ValueError("first 2010 group must start after u16 count")
  if k>0 and pos<=sets[-1]["source_StateSet_header_offset"]:
   raise ValueError("set source headers not monotonic")
  sets.append({
   "original_source_StateSet_index":k,
   "source_original_StateSet_header_offset":pos,
   "source_original_StateSet_name":name,
   "source_native_original_Lua51_start":source,
   "source_original_Lua51_nbytes":source_lua_bytes,
   "source_original_Lua51_SHA256":hashlib.sha256(raw[source:source+source_lua_bytes]).hexdigest(),
   "source_native_full_StateData_records_decoded_PROVEN":False,
  })
 offsets=[r["source_original_StateSet_header_offset"] for r in sets]
 bykey=collections.Counter();bytrack=collections.Counter()
 for row in attack["source_actual_attactype_key_records_with_named_nearby_animation_candidates"]:
  off=row["owner_state_file_actual_AttackType_key_start_offset"]
  i=bisect.bisect_right(offsets,off)-1
  if i<0:raise ValueError("genuine raw AttackType key before first StateSet")
  bykey[i]+=1
 for row in candidate["source_original_native_Attack_named_12byte_event_candidates"]:
  off=row["original_authored_source_name_prefixed_offset"]
  i=bisect.bisect_right(offsets,off)-1
  if i<0:raise ValueError("real candidate before first set")
  bytrack[i]+=1
 for i,r in enumerate(sets):
  end=offsets[i+1] if i+1<len(sets) else len(raw)
  r["source_original_StateSet_next_header_or_EOF"]=end
  r["source_original_binary_interval_length"]=end-offsets[i]
  r["source_original_AttackType_raw_key_count_in_set"]=bykey[i]
  r["source_original_named_Attack_attack_raw_candidate_count_in_set"]=bytrack[i]
  print("G213C original source complete set",i,r["source_original_StateSet_name"],"start",offsets[i],
        "bytes",end-offsets[i],"AttkType",bykey[i],"named Attack raw candidates",bytrack[i],flush=True)
 if sum(bykey.values())!=379 or sum(bytrack.values())!=365:
  raise ValueError("original source entire-key set mapping count mismatch")
 # This is NOT end-to-end native StateData nested serializer parse:
 # header interval mapping / Lua blob exact length is genuinely
 # source-validated and useful; the original 55 native nested
 # StateData parsing remains open and explicitly marked incomplete.
 report={
  "origin":"2010 owner original 55 StateSet native header names and full pack interval crosswalk to authentic G207 attacktype and G212 track candidates",
  "original_StateDatabase_true_source_set_count":len(sets),
  "original_states_asset_byte_length":len(raw),
  "source_original_55_named_StateSet_archive_intervals":sets,
  "original_exact_AttackType_u32_records_mapped_to_a_source_StateSet_interval":sum(bykey.values()),
  "original_named_Attack_attack_raw_candidate_records_mapped_to_a_source_StateSet_interval":sum(bytrack.values()),
  "source_55_group_names_exact_original_StateSetData_header_read_PROVEN":True,
  "source_all_55_original_embedded_Lua51_chunks_exact_lengths_PROVEN":True,
  "source_native_all_55_StateData_nested_records_and_tracks_parser_PROVEN":False,
  "source_2010_G212_named_Attack_tracks_are_runtime_authenticated":False,
  "source_AttackType_value_to_actual_original_current_armor_attack_INPUT_PROVEN":False,
  "source_G83_G169_original_2010_gameplay_animator_updated":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G213C PASS 55 real named original 2010 state sets and EXACT 379 AttackType + 365 raw Attack candidates assigned to nonoverlapping authentic group intervals. Native per-state events still NOT PROVEN, no VPK.")
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for arg in ("ipa","g207","g212","out"):p.add_argument("--"+arg,type=Path,required=True)
 a=p.parse_args()
 main(a.ipa,a.g207,a.g212,a.out)
