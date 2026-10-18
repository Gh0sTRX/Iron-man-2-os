#!/usr/bin/env python3
"""G212 original 2010 Iron Man 2 iOS authored 'states' binary source:
inspect potential ORIGINAL StateTrack named "Attack"/"attack", using the
known G211 native StateTrack constructor structure:
  ReadString -> 2 bytes stored in StateTrack +4
  2-byte event count
  N records of 12 bytes (3 x original u32), where GetEvent reads
  record+0 as start and record+4 as duration.

Records are CANDIDATES until exact state reader control flow and group
binding proven. Do not label third u32 hitbox/damage/weapon ID.
No return to guessed "fire at 0.4s" or Vita synthetic animations.
No VPK, game input or controller adjustments.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re,struct,zipfile
from pathlib import Path
SIZE=248613763
SOURCE_NAMES=("Attack","attack")
MAX_EVENT_RECORDS=64
def scan(ipa:Path,out:Path):
 if ipa.stat().st_size!=SIZE:raise ValueError("2010 original owner IPA required")
 with zipfile.ZipFile(ipa) as z:
  if z.testzip():raise ValueError("user owned 2010 IPA source CRC fail")
  state=z.read("Payload/IronMan2.app/states")
 if len(state)!=361393:raise ValueError("original states file changed")
 results=[];hist=collections.Counter()
 for name in SOURCE_NAMES:
  token=name.encode("ascii")
  needle=struct.pack("<H",len(token))+token
  at=state.find(needle)
  hits=0
  while at>=0:
   hits+=1
   pos=at+len(needle)
   if pos+4<=len(state):
    flags,count=struct.unpack_from("<HH",state,pos)
    end=pos+4+12*count
    if 1<=count<=MAX_EVENT_RECORDS and end<=len(state):
     tuples=[]
     valid=True
     for i in range(count):
      vm=pos+4+i*12
      start,length,unknown=struct.unpack_from("<III",state,vm)
      # Source original event tracks use integer ticks. Never
      # silently convert to milliseconds; native scale unproven.
      if start>10000000 or length>10000000:
       valid=False;break
      tuples.append({
       "original_2010_serialized_record_OFFSET":vm,
       "source_real_2010_start_raw_tick":start,
       "source_real_2010_duration_raw_tick":length,
       "source_real_2010_end_start_plus_duration":start+length,
       "original_2010_3rd_u32_field_UNCLASSIFIED":unknown,
       "source_2010_value_is_proven_hitbox_frame_or_damage":False,
      })
     if valid:
      h={"source_original_track_name":name,
         "original_authored_source_name_prefixed_offset":at,
         "source_u16_name_length":len(token),
         "source_post_name_original_2byte_field_unclassified":flags,
         "original_event_record_count_candidate":count,
         "source_original_2010_12byte_event_candidate_records":tuples,
         "source_original_StateTrack_bound_to_active_actor_or_attack_state_PROVEN":False,
         "source_Native_BufferStream_ReadString_single_field_start_proven":False,
         "source_original_animation_seconds_unit_PROVEN":False,
         }
      results.append(h)
      hist[name]+=count
      if len(results)<=12:
       print("G212 real 2010 raw candidate native track",name,
          "file_offset",at,"unknown flags",flags,"count",count,
          "first event raw",tuples[:3],flush=True)
   at=state.find(needle,at+1)
  print("G212 owner source original name",name,"actual exact name-prefix matches",hits)
 report={
  "origin":"G212 actual original Iron Man 2 iOS 2010 states byte scan compared to genuine StateTrack constructor original 12-byte event record layout",
  "source_original_2010_states_bytes":len(state),
  "source_original_full_2010_attack_track_named_6ASCII_candidate_total":len(results),
  "source_original_native_Attack_named_12byte_event_candidates":results,
  "candidate_original_event_counts_by_track_name":dict(hist),
  "original_native_StateTrack_ctor_source_VM":"0xa167c",
  "original_native_StateTrack_GetEvent_source_VM":"0xa14f0",
  "original_native_source_event_record_is_12bytes":True,
  "source_original_2010_file_reader_control_flow_all_candidate_records_confirmed":False,
  "source_original_2010_any_combat_hit_window_time_proven":False,
  "source_original_attacktrack_integer_ticks_are_milliseconds_PROVEN":False,
  "original_2010_runtime_gameplay_or_Vita_native_movement_modified":False,
  "NO_VPK":True
 }
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print("G212 complete source 'states' candidate Attack/attack 12B event records",len(results),
       "event entries",sum(len(r["source_original_2010_12byte_event_candidate_records"]) for r in results))
 print("G212 source candidate only; not direct input, actual hit time, mission weapon ID or milliseconds. NO VPK")
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--ipa",type=Path,required=True)
 ap.add_argument("--out",type=Path,required=True)
 a=ap.parse_args()
 scan(a.ipa,a.out)
